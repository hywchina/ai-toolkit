# Ostris AI Toolkit

AI Toolkit 是一个易于使用的一体化扩散模型训练套件。我会尽量支持所有最新模型，并让它们能在消费级硬件上运行，包括图像和视频模型。它可以通过 GUI 或 CLI 运行。它的设计目标是既简单易用，又尽可能包含你能想到的各种功能。免费且开源。



## 支持的模型

### 图像
- [black-forest-labs/FLUX.1-dev](https://huggingface.co/black-forest-labs/FLUX.1-dev) (FLUX.1)
- [black-forest-labs/FLUX.2-dev](https://huggingface.co/black-forest-labs/FLUX.2-dev) (FLUX.2)
- [black-forest-labs/FLUX.2-klein-base-4B](https://huggingface.co/black-forest-labs/FLUX.2-klein-base-4B) (FLUX.2-klein-base-4B)
- [black-forest-labs/FLUX.2-klein-base-9B](https://huggingface.co/black-forest-labs/FLUX.2-klein-base-9B) (FLUX.2-klein-base-9B)
- [ostris/Flex.1-alpha](https://huggingface.co/ostris/Flex.1-alpha) (Flex.1)
- [ostris/Flex.2-preview](https://huggingface.co/ostris/Flex.2-preview) (Flex.2)
- [lodestones/Chroma1-Base](https://huggingface.co/lodestones/Chroma1-Base) (Chroma)
- [Alpha-VLLM/Lumina-Image-2.0](https://huggingface.co/Alpha-VLLM/Lumina-Image-2.0) (Lumina2)
- [Qwen/Qwen-Image](https://huggingface.co/Qwen/Qwen-Image) (Qwen-Image)
- [Qwen/Qwen-Image-2512](https://huggingface.co/Qwen/Qwen-Image-2512) (Qwen-Image-2512)
- [HiDream-ai/HiDream-I1-Full](https://huggingface.co/HiDream-ai/HiDream-I1-Full) (HiDream I1)
- [OmniGen2/OmniGen2](https://huggingface.co/OmniGen2/OmniGen2) (OmniGen2)
- [Tongyi-MAI/Z-Image-Turbo](https://huggingface.co/Tongyi-MAI/Z-Image-Turbo) (Z-Image Turbo)
- [Tongyi-MAI/Z-Image](https://huggingface.co/Tongyi-MAI/Z-Image) (Z-Image)
- [ostris/Z-Image-De-Turbo](https://huggingface.co/ostris/Z-Image-De-Turbo) (Z-Image De-Turbo)
- [stabilityai/stable-diffusion-xl-base-1.0](https://huggingface.co/stabilityai/stable-diffusion-xl-base-1.0) (SDXL)
- [stable-diffusion-v1-5/stable-diffusion-v1-5](https://huggingface.co/stable-diffusion-v1-5/stable-diffusion-v1-5) (SD 1.5)
- [baidu/ERNIE-Image](https://huggingface.co/baidu/ERNIE-Image) (ERNIE-Image)
- [NucleusAI/Nucleus-Image](https://huggingface.co/NucleusAI/Nucleus-Image) (Nucleus-Image)
- [HiDream-ai/HiDream-O1-Image](https://huggingface.co/HiDream-ai/HiDream-O1-Image) (HiDream O1)
- [Photoroom/prxpixel-t2i](https://huggingface.co/Photoroom/prxpixel-t2i) (PRXPixel)

### 指令 / 编辑
- [black-forest-labs/FLUX.1-Kontext-dev](https://huggingface.co/black-forest-labs/FLUX.1-Kontext-dev) (FLUX.1-Kontext-dev)
- [Qwen/Qwen-Image-Edit](https://huggingface.co/Qwen/Qwen-Image-Edit) (Qwen-Image-Edit)
- [Qwen/Qwen-Image-Edit-2509](https://huggingface.co/Qwen/Qwen-Image-Edit-2509) (Qwen-Image-Edit-2509)
- [Qwen/Qwen-Image-Edit-2511](https://huggingface.co/Qwen/Qwen-Image-Edit-2511) (Qwen-Image-Edit-2511)
- [HiDream-ai/HiDream-E1-1](https://huggingface.co/HiDream-ai/HiDream-E1-1) (HiDream E1)

### 视频
- [Wan-AI/Wan2.1-T2V-1.3B-Diffusers](https://huggingface.co/Wan-AI/Wan2.1-T2V-1.3B-Diffusers) (Wan 2.1 1.3B)
- [Wan-AI/Wan2.1-I2V-14B-480P-Diffusers](https://huggingface.co/Wan-AI/Wan2.1-I2V-14B-480P-Diffusers) (Wan 2.1 I2V 14B-480P)
- [Wan-AI/Wan2.1-I2V-14B-720P-Diffusers](https://huggingface.co/Wan-AI/Wan2.1-I2V-14B-720P-Diffusers) (Wan 2.1 I2V 14B-720P)
- [Wan-AI/Wan2.1-T2V-14B-Diffusers](https://huggingface.co/Wan-AI/Wan2.1-T2V-14B-Diffusers) (Wan 2.1 14B)
- [Wan-AI/Wan2.2-T2V-A14B-Diffusers](https://huggingface.co/Wan-AI/Wan2.2-T2V-A14B-Diffusers) (Wan 2.2 14B)
- [Wan-AI/Wan2.2-I2V-A14B-Diffusers](https://huggingface.co/Wan-AI/Wan2.2-I2V-A14B-Diffusers) (Wan 2.2 I2V 14B)
- [Wan-AI/Wan2.2-TI2V-5B-Diffusers](https://huggingface.co/Wan-AI/Wan2.2-TI2V-5B-Diffusers) (Wan 2.2 TI2V 5B)
- [Lightricks/LTX-2](https://huggingface.co/Lightricks/LTX-2) (LTX-2)
- [Lightricks/LTX-2.3](https://huggingface.co/Lightricks/LTX-2.3) (LTX-2.3)
- [krea/Krea-2-Raw](https://huggingface.co/krea/Krea-2-Raw) (Krea 2)

### 音频
- [ACE-Step/Ace-Step1.5](https://huggingface.co/ACE-Step/Ace-Step1.5) (Ace Step 1.5)
- [ACE-Step/acestep-v15-xl-base](https://huggingface.co/ACE-Step/acestep-v15-xl-base) (Ace Step 1.5 XL)

### 实验性
- [lodestones/Zeta-Chroma](https://huggingface.co/lodestones/Zeta-Chroma) (Zeta Chroma)
- [ideogram-ai/ideogram-4-fp8](https://huggingface.co/ideogram-ai/ideogram-4-fp8) (Ideogram 4 FP8)

## 安装

要求：
- python >=3.10（推荐 3.12）
- 具备足够显存、能满足你需求的 Nvidia GPU
- python venv
- git


Linux：
```bash
git clone https://github.com/ostris/ai-toolkit.git
cd ai-toolkit
python3 -m venv venv
source venv/bin/activate
# 先安装 torch
pip3 install --no-cache-dir torch==2.9.1 torchvision==0.24.1 torchaudio==2.9.1 --index-url https://download.pytorch.org/whl/cu128
pip3 install -r requirements.txt
```

对于运行 **DGX OS** 的设备（包括 DGX Spark），请遵循[这些](dgx_instructions.md)说明。


Windows：

如果你在 Windows 上遇到问题，我建议使用这个简易安装脚本：[https://github.com/Tavris1/AI-Toolkit-Easy-Install](https://github.com/Tavris1/AI-Toolkit-Easy-Install)

```bash
git clone https://github.com/ostris/ai-toolkit.git
cd ai-toolkit
python -m venv venv
.\venv\Scripts\activate
pip install --no-cache-dir torch==2.9.1 torchvision==0.24.1 torchaudio==2.9.1 --index-url https://download.pytorch.org/whl/cu128
pip install -r requirements.txt
```

MacOS：

目前已提供对 Apple Silicon Mac 的实验性支持。我没有一台内存足够大的 Mac 来进行完整测试，
所以如果遇到问题请告诉我。项目中有一个用于在 MacOS 上安装并运行的便捷脚本，
位于 `./run_mac.zsh`，它会在本地安装依赖并运行 UI。运行方式如下：

```bash
git clone https://github.com/ostris/ai-toolkit.git
cd ai-toolkit
chmod +x run_mac.zsh
./run_mac.zsh
```


# AI Toolkit UI

<img src="https://ostris.com/wp-content/uploads/2025/02/toolkit-ui.jpg" alt="AI Toolkit UI" width="100%">

AI Toolkit UI 是 AI Toolkit 的 Web 界面。你可以通过它轻松启动、停止和监控任务，也可以用几次点击完成模型训练。它还允许你为 UI 设置访问令牌，以防止未经授权的访问，因此在暴露到服务器上运行时总体上较为安全。

## 运行 UI

要求：
- Node.js > 20

任务运行时并不需要一直保持 UI 运行。UI 只用于启动、停止和监控任务。下面的命令会安装 / 更新 UI 及其依赖，并启动 UI。

```bash
cd ui
npm run build_and_start
```

现在你可以通过 `http://localhost:8675` 访问 UI；如果你是在服务器上运行，也可以通过 `http://<your-ip>:8675` 访问。

## 保护 UI

如果你将 UI 托管在云服务商上，或者运行在任何不安全的网络中，我强烈建议使用认证令牌进行保护。
你可以通过将环境变量 `AI_TOOLKIT_AUTH` 设置为一个非常安全的密码来完成。访问 UI 时将需要这个令牌。
启动 UI 时可以这样设置：

```bash
# Linux
AI_TOOLKIT_AUTH=super_secure_password npm run build_and_start

# Windows
set AI_TOOLKIT_AUTH=super_secure_password && npm run build_and_start

# Windows Powershell
$env:AI_TOOLKIT_AUTH="super_secure_password"; npm run build_and_start
```

### 训练
1. 将位于 `config/examples/train_lora_flux_24gb.yaml` 的示例配置文件（schnell 使用 `config/examples/train_lora_flux_schnell_24gb.yaml`）复制到 `config` 文件夹，并重命名为 `whatever_you_want.yml`
2. 按照文件中的注释编辑该文件
3. 像这样运行该文件：`python run.py config/whatever_you_want.yml`

开始训练时，会根据配置文件中的名称和训练文件夹创建一个文件夹。里面会包含所有 checkpoint 和图片。
你可以随时使用 ctrl+c 停止训练；恢复训练时，它会从最后一个 checkpoint 继续。

重要提示：如果你在保存过程中按下 crtl+c，很可能会损坏该 checkpoint。因此请等它保存完成。

### 需要帮助？

除非是代码中的 bug，否则请不要提交 bug report。欢迎你[加入我的 Discord](https://discord.gg/VXmU2f5WEU)
并在那里寻求帮助。不过，请避免直接私信我询问一般问题或支持事项。请在 Discord 中提问，
我会在有空时回复。

## Ostris Cloud

你可以使用许多云服务商租用 GPU。如果你想以最大程度支持这个项目，请考虑使用 [Ostris Cloud](https://cloud.ostris.com)。Ostris Cloud 由我 Ostris 拥有并运营，每一美元收入都会直接用于资助本项目的开发。

<a href="https://cloud.ostris.com" target="_blank"><img src="https://cloud.ostris.com/api/og" alt="Ostris Cloud" style="max-width:100%;width:600px;height:auto;"></a>


## 在 RunPod 中训练
如果你想使用 Runpod，但还没有注册，请考虑使用[我的 Runpod 推广链接](https://runpod.io?ref=h0y9jyr2)来帮助支持本项目。


我维护了一个官方 Runpod Pod 模板，可以从[这里](https://console.runpod.io/deploy?template=0fqzfjy6f3&ref=h0y9jyr2)访问。

我还制作了一个简短视频，展示如何在 Runpod 上开始使用 AI Toolkit，可以在[这里](https://youtu.be/HBNeS-F6Zz8)观看。

## 在 Modal 中训练

### 1. 设置
#### ai-toolkit：
```
git clone https://github.com/ostris/ai-toolkit.git
cd ai-toolkit
git submodule update --init --recursive
python -m venv venv
source venv/bin/activate
pip install torch
pip install -r requirements.txt
pip install --upgrade accelerate transformers diffusers huggingface_hub # 可选，如果遇到问题再运行
```
#### Modal：
- 运行 `pip install modal` 安装 modal Python 包。
- 运行 `modal setup` 进行认证（如果此命令无效，请尝试 `python -m modal setup`）。

#### Hugging Face：
- 从[这里](https://huggingface.co/settings/tokens)获取 READ token，并从[这里](https://huggingface.co/black-forest-labs/FLUX.1-dev)申请访问 Flux.1-dev 模型。
- 运行 `huggingface-cli login` 并粘贴你的 token。

### 2. 上传你的数据集
- 将包含 .jpg、.jpeg 或 .png 图片以及 .txt 文件的数据集文件夹拖放到 `ai-toolkit` 中。

### 3. 配置
- 将位于 ```config/examples/modal``` 的示例配置文件复制到 `config` 文件夹，并重命名为 ```whatever_you_want.yml```。
- 按照文件中的注释编辑配置，**<ins>请小心，并遵循示例中的 `/root/ai-toolkit` 路径</ins>**。

### 4. 编辑 run_modal.py
- 在 `code_mount = modal.Mount.from_local_dir` 处设置你本地完整的 `ai-toolkit` 路径，例如：
  
   ```
   code_mount = modal.Mount.from_local_dir("/Users/username/ai-toolkit", remote_path="/root/ai-toolkit")
   ```
- 在 `@app.function` 中选择 `GPU` 和 `Timeout`（默认是 A100 40GB 和 2 小时超时）。

### 5. 训练
- 在终端中运行配置文件：`modal run run_modal.py --config-file-list-str=/root/ai-toolkit/config/whatever_you_want.yml`。
- 你可以在本地终端中监控训练，也可以在 [modal.com](https://modal.com/) 上查看。
- 模型、样本和优化器会存储在 `Storage > flux-lora-models` 中。

### 6. 保存模型
- 运行 `modal volume ls flux-lora-models` 检查 volume 的内容。
- 运行 `modal volume get flux-lora-models your-model-name` 下载内容。
- 示例：`modal volume get flux-lora-models my_first_flux_lora_v1`。

### Modal 截图

<img width="1728" alt="Modal Traning Screenshot" src="https://github.com/user-attachments/assets/7497eb38-0090-49d6-8ad9-9c8ea7b5388b">

---

## 数据集准备

数据集通常需要是一个文件夹，其中包含图片及对应的文本文件。目前唯一支持的格式是 jpg、jpeg 和 png。Webp 目前存在问题。文本文件应与图片同名，
但扩展名为 `.txt`。例如 `image2.jpg` 和 `image2.txt`。文本文件中应只包含 caption。
你可以在 caption 文件中添加 `[trigger]` 这个词；如果你的配置中有 `trigger_word`，它会被自动替换。

图片不会被放大，但会被缩小并放入 buckets 中以便批处理。**你不需要裁剪 / 调整图片尺寸**。
加载器会自动调整它们的大小，并且可以处理不同的宽高比。


## 训练特定层

如果要使用 LoRA 训练特定层，可以使用 `only_if_contains` network kwargs。例如，如果你只想训练 The Last Ben 使用的 2 个层，
也就是[这篇帖子中提到的层](https://x.com/__TheBen/status/1829554120270987740)，可以像这样调整你的 network kwargs：

```yaml
      network:
        type: "lora"
        linear: 128
        linear_alpha: 128
        network_kwargs:
          only_if_contains:
            - "transformer.single_transformer_blocks.7.proj_out"
            - "transformer.single_transformer_blocks.20.proj_out"
```

层的命名约定采用 diffusers 格式，因此查看模型的 state dict 就能找到你想训练的层名称后缀。
你也可以用这种方法只训练特定的权重组。例如，如果只想训练 FLUX.1 的 `single_transformer`，可以使用如下配置：

```yaml
      network:
        type: "lora"
        linear: 128
        linear_alpha: 128
        network_kwargs:
          only_if_contains:
            - "transformer.single_transformer_blocks."
```

你也可以使用 `ignore_if_contains` network kwarg 按名称排除层。因此，如果要排除所有 single transformer blocks：


```yaml
      network:
        type: "lora"
        linear: 128
        linear_alpha: 128
        network_kwargs:
          ignore_if_contains:
            - "transformer.single_transformer_blocks."
```

`ignore_if_contains` 的优先级高于 `only_if_contains`。因此，如果某个权重同时被两者覆盖，
它会被忽略。

## LoKr 训练

要了解更多关于 LoKr 的信息，请阅读 [KohakuBlueleaf/LyCORIS](https://github.com/KohakuBlueleaf/LyCORIS/blob/main/docs/Guidelines.md) 中的相关内容。要训练 LoKr 模型，可以像这样调整配置文件中的 network type：

```yaml
      network:
        type: "lokr"
        lokr_full_rank: true
        lokr_factor: 8
```

其他内容应保持相同，包括层目标设置。


## 支持我的工作

如果你喜欢我的项目，或者将它们用于商业用途，请考虑赞助我。任何支持都有帮助！💖

<a href="https://ostris.com/sponsors" target="_blank"><img src="https://ostris.com/wp-content/uploads/2025/05/support-banner2.png" alt="Support my work" style="max-width:100%;height:auto;"></a>

### 当前赞助者

这些人 / 组织无私地让这个项目成为可能。非常感谢！！

<a href="https://ostris.com/sponsors"><img src="https://ostris.com/sponsors.svg" alt="Sponsors" style="width:100%;height:auto;"></a>
