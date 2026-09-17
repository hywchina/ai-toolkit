"""Real two-step LoRA training with a tiny randomly initialized SD model.

No external weights are downloaded. This checks the training plumbing, not model
quality or Flux2/4090 capacity. Prepare once on host, then mount the model read-only.
"""
import argparse
import io
import json
import os
from pathlib import Path
import time
import uuid
from urllib.parse import quote

import requests


def prepare(target):
    import torch
    from diffusers import AutoencoderKL, UNet2DConditionModel, DDPMScheduler, StableDiffusionPipeline
    from transformers import CLIPTokenizer, CLIPTextConfig, CLIPTextModel
    target = Path(target)
    target.mkdir(parents=True, exist_ok=False)
    torch.manual_seed(42)
    (target / 'vocab.json').write_text(json.dumps({'<|startoftext|>': 0, '<|endoftext|>': 1}))
    (target / 'merges.txt').write_text('#version: 0.2\n')
    tokenizer = CLIPTokenizer(vocab={'<|startoftext|>': 0, '<|endoftext|>': 1}, merges=[], model_max_length=77)
    text = CLIPTextModel(CLIPTextConfig(vocab_size=2, hidden_size=32, intermediate_size=64,
                                      num_hidden_layers=1, num_attention_heads=4, max_position_embeddings=77,
                                      bos_token_id=0, eos_token_id=1, pad_token_id=1))
    unet = UNet2DConditionModel(sample_size=32, in_channels=4, out_channels=4,
                               layers_per_block=1, block_out_channels=(32, 32),
                               down_block_types=('CrossAttnDownBlock2D', 'DownBlock2D'),
                               up_block_types=('UpBlock2D', 'CrossAttnUpBlock2D'), cross_attention_dim=32,
                               attention_head_dim=4, norm_num_groups=8)
    vae = AutoencoderKL(in_channels=3, out_channels=3, latent_channels=4,
                        block_out_channels=(32, 32), down_block_types=('DownEncoderBlock2D',)*2,
                        up_block_types=('UpDecoderBlock2D',)*2, norm_num_groups=8, sample_size=64)
    pipe = StableDiffusionPipeline(vae=vae, unet=unet, text_encoder=text, tokenizer=tokenizer,
                                   scheduler=DDPMScheduler(steps_offset=1, clip_sample=False), safety_checker=None, feature_extractor=None,
                                   requires_safety_checker=False)
    pipe.save_pretrained(target)
    print('Prepared random tiny SD fixture:', target)


def run(args):
    from PIL import Image
    session = requests.Session()
    session.trust_env = False
    session.headers['Authorization'] = 'Bearer ' + os.environ['AI_TOOLKIT_AUTH']
    name = 'train_smoke_' + uuid.uuid4().hex
    def call(method, route, **kwargs):
        r = session.request(method, args.base_url.rstrip('/') + route, timeout=120, **kwargs)
        r.raise_for_status()
        return r
    settings = call('GET', '/api/settings').json()
    call('POST', '/api/datasets/create', json={'name': name})
    data = io.BytesIO()
    Image.new('RGB', (64, 64), (123, 84, 51)).save(data, format='PNG')
    call('POST', '/api/datasets/upload', data={'datasetName': name},
         files=[('files', ('sample.png', data.getvalue(), 'image/png')),
                ('files', ('sample.txt', b'a test image', 'text/plain'))])
    process = {'type': 'diffusion_trainer', 'training_folder': settings['TRAINING_FOLDER'],
               'device': 'cuda', 'network': {'type': 'lora', 'linear': 2, 'linear_alpha': 2},
               'model': {'name_or_path': args.model_path, 'arch': 'sd1'},
               'datasets': [{'folder_path': settings['DATASETS_FOLDER'] + '/' + name,
                             'resolution': [64], 'caption_ext': 'txt', 'num_workers': 0}],
               'train': {'steps': 10000 if args.cancel else 2, 'batch_size': 1, 'dtype': 'float32', 'optimizer': 'adamw',
                         'lr': 0.0001, 'train_unet': True, 'train_text_encoder': False,
                         'noise_scheduler': 'ddpm', 'disable_sampling': True},
               'save': {'save_every': 2, 'dtype': 'float32', 'max_step_saves_to_keep': 1},
               'sample': {'sampler': 'ddpm', 'prompts': ['a test image']},
               'logging': {'use_ui_logger': True, 'log_every': 1}}
    job = call('POST', '/api/jobs', json={'name': name, 'gpu_ids': args.gpu,
               'job_ref': name, 'job_type': 'train',
               'job_config': {'job': 'extension', 'config': {'name': name, 'process': [process]}}}).json()
    job_id = job['id']
    print('Test job:', job_id, flush=True)
    call('GET', f'/api/jobs/{job_id}/start')
    call('GET', f'/api/queue/{args.gpu}/start')
    deadline = time.monotonic() + 180
    cancelled = False
    while time.monotonic() < deadline:
        job = call('GET', '/api/jobs', params={'id': job_id}).json()
        print(job['status'], job['step'], job['info'], flush=True)
        if args.cancel and not cancelled and job['step'] >= 1 and job['status'] == 'running':
            call('GET', f'/api/jobs/{job_id}/stop')
            cancelled = True
            # Allow SIGINT handling and the worker's exit handler to settle.
            time.sleep(3)
            continue
        if job['status'] in ('error', 'completed', 'stopped'):
            break
        time.sleep(3)
    else:
        call('GET', f'/api/jobs/{job_id}/stop')
        raise TimeoutError(f'Training timed out: {job_id}')
    log = call('GET', f'/api/jobs/{job_id}/log').json()['log']
    if args.cancel:
        assert cancelled and job['status'] == 'stopped', (job['status'], job['info'])
        assert job['pid'] is None, 'worker has not confirmed process exit'
        print(json.dumps({'result': 'PASS', 'cancelled_job': job_id, 'steps_before_cancel': job['step']}))
        return
    if job['status'] != 'completed':
        print(log[-12000:])
        raise RuntimeError('Training did not complete; retained test data for inspection')
    metrics = call('GET', f'/api/jobs/{job_id}/loss').json()
    if 'loss/loss' in metrics['keys']:
        metrics = call('GET', f'/api/jobs/{job_id}/loss', params={'key': 'loss/loss'}).json()
    assert metrics['points'], metrics
    files = call('GET', f'/api/jobs/{job_id}/files').json()['files']
    weights = [f for f in files if f['path'].endswith('.safetensors')]
    assert weights, files
    for item in weights:
        response = call('GET', '/api/files/' + quote(item['path'], safe=''))
        assert len(response.content) == item['size'] > 0
        from safetensors.torch import load
        import torch
        tensors = load(response.content)
        assert tensors and all(torch.isfinite(t).all() for t in tensors.values())
        assert any(torch.count_nonzero(t) > 0 for key, t in tensors.items() if 'lora_up' in key), 'LoRA weights were not updated'
    # Stopping a terminal job is a no-op and must not signal a stale/reused PID.
    assert call('GET', f'/api/jobs/{job_id}/stop').json()['status'] == 'completed'
    print(json.dumps({'result': 'PASS', 'job_id': job_id, 'steps': job['step'],
                      'loss_points': len(metrics['points']), 'lora_files': len(weights),
                      'training_verified': 'tiny random SD LoRA, not production quality'}))
    # Keep successful weights/logs as evidence. All fixtures use unique names.


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--prepare-model')
    p.add_argument('--model-path')
    p.add_argument('--base-url', default='http://127.0.0.1:3000')
    p.add_argument('--gpu', default='0')
    p.add_argument('--cancel', action='store_true', help='Cancel a real running job after its first training step')
    args = p.parse_args()
    if args.prepare_model:
        prepare(args.prepare_model)
    elif args.model_path:
        run(args)
    else:
        p.error('--prepare-model or --model-path is required')
