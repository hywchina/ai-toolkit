"""Serial HTTP integration checks. Only creates/deletes uniquely named test data.

Run with AI_TOOLKIT_AUTH set. --exercise-worker checks failure propagation using
an invalid job type (no model loading). This is NOT a successful LoRA training test.
"""
import argparse
import json
import os
import time
import uuid
from urllib.parse import quote

import requests


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--base-url', default='http://127.0.0.1:3000')
    parser.add_argument('--exercise-worker', action='store_true')
    args = parser.parse_args()
    session = requests.Session()
    session.trust_env = False
    session.headers['Authorization'] = 'Bearer ' + os.environ['AI_TOOLKIT_AUTH']
    base = args.base_url.rstrip('/')
    name = 'api_smoke_' + uuid.uuid4().hex
    # Unique empty-device queue; the invalid job never loads a GPU model.
    queue = name
    job_id = None
    checks = 0

    def call(method, route, expected=200, **kwargs):
        nonlocal checks
        response = session.request(method, base + route, timeout=120, **kwargs)
        assert response.status_code == expected, (route, response.status_code, response.text[:1000])
        checks += 1
        print(f'PASS {method} {route} -> {expected}', flush=True)
        return response

    try:
        call('GET', '/api/auth', headers={'Authorization': 'Bearer incorrect'}, expected=401)
        call('GET', '/api/auth')
        call('GET', '/api', expected=404)
        assert 'jobs' in call('GET', '/api/jobs').json()
        call('GET', '/api/jobs?only_active=true')
        assert 'queues' in call('GET', '/api/queue').json()
        assert 'gpus' in call('GET', '/api/gpu').json()
        settings = call('GET', '/api/settings').json()
        call('GET', '/api/datasets/list')
        assert call('POST', '/api/datasets/create', json={'name': name}).json()['name'] == name
        caption = b'API smoke caption\n'
        call('POST', '/api/datasets/upload', data={'datasetName': name},
             files={'files': ('sample.txt', caption, 'text/plain')})
        route = '/api/files/' + quote(settings['DATASETS_FOLDER'] + '/' + name + '/sample.txt', safe='')
        assert call('GET', route).content == caption
        assert call('GET', route, headers={'Range': 'bytes=0-2'}, expected=206).content == caption[:3]
        body = {'name': name, 'gpu_ids': queue, 'job_type': 'train', 'job_ref': name,
                'job_config': {'job': 'invalid_api_smoke', 'config': {'name': name, 'process': [{}]}}}
        job_id = call('POST', '/api/jobs', json=body).json()['id']
        call('POST', '/api/jobs', json=body, expected=409)
        job = call('GET', '/api/jobs?id=' + job_id).json()
        assert job['status'] == 'stopped'
        assert call('GET', '/api/jobs?job_ref=' + name).json()['id'] == job_id
        call('POST', '/api/jobs', json={**body, 'id': job_id})
        for suffix, field in [('log', 'log'), ('loss', 'points'), ('files', 'files'), ('samples', 'samples')]:
            assert field in call('GET', f'/api/jobs/{job_id}/{suffix}').json()
        call('GET', f'/api/jobs/{job_id}/start')
        assert call('GET', '/api/jobs?id=' + job_id).json()['status'] == 'queued'
        call('GET', f'/api/jobs/{job_id}/stop')
        assert call('GET', '/api/jobs?id=' + job_id).json()['status'] == 'stopped', 'queued job was not cancelled'
        call('GET', f'/api/jobs/{job_id}/save_now')
        assert call('GET', '/api/jobs?id=' + job_id).json()['save_now']
        if args.exercise_worker:
            call('GET', f'/api/jobs/{job_id}/start')
            call('GET', f'/api/queue/{queue}/start')
            deadline = time.monotonic() + 120
            while time.monotonic() < deadline:
                job = call('GET', '/api/jobs?id=' + job_id).json()
                if job['status'] == 'error':
                    break
                time.sleep(2)
            assert job['status'] == 'error', 'failed Python process left job stuck running'
            assert call('GET', f'/api/jobs/{job_id}/log').json()['log'], 'missing subprocess log'
        call('GET', f'/api/queue/{queue}/stop')
        print(json.dumps({'result': 'PASS', 'checks': checks, 'base_url': base,
                          'training_verified': False}), flush=True)
    finally:
        # Only the test's uniquely named dataset/job are eligible for deletion.
        if job_id:
            state = session.get(base + '/api/jobs', params={'id': job_id}, timeout=30).json()
            if state and state['status'] not in ('running', 'stopping'):
                call('GET', f'/api/jobs/{job_id}/delete')
            else:
                print('Retained active test job for inspection:', job_id)
        call('POST', '/api/datasets/delete', json={'name': name})


if __name__ == '__main__':
    main()
