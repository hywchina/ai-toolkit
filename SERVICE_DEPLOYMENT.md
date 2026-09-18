# LoRA API 单镜像部署

本服务为 AI Toolkit，不是 ComfyUI。镜像包含 Next.js API、单个队列 Worker、Python 3.12 与冻结依赖。模型权重不打包，使用只读挂载；数据集、LoRA 输出和数据库使用持久卷。

## 硬件与系统

- 宿主机：Ubuntu/Linux amd64，NVIDIA GPU，Docker Engine 和 NVIDIA Container Toolkit。
- PyTorch 2.9.1 的 CUDA 12.8 用户态依赖适配 RTX 3090 / RTX 4090。宿主机驱动必须兼容 CUDA 12.8；无需在镜像里安装内核显卡驱动。
- 本次实际测试为 RTX 3090 24GB，驱动 595.91.07；4090 未实测。
- 默认镜像基础为 Debian 系的 `python:3.12-slim`，可以在 Ubuntu 宿主机运行；容器用户空间不要求和宿主机发行版相同。
- Compose 默认指定 `nvidia.com/gpu=0`（CDI），适合当前宿主机。老版本使用 NVIDIA runtime 的机器应删除 `devices` 并改用 `gpus: all`，不可机械叠加两种机制。
- 当前 API 面向受信任后端，保持单实例；按精确 `gpu_ids` 字符串排队不等于跨队列 GPU 资源锁，不要配置重叠的 GPU 集合。

## 构建一个服务镜像

在项目根目录执行：

```bash
docker build -f docker/Dockerfile.service -t ai-toolkit-service:local .
```

与上游 Dockerfile 不同，本文件直接复制当前本地源码，不从 GitHub 克隆并覆盖本地改造。专属 `.dockerignore` 排除模型、数据集、输出、数据库、虚拟环境、前端构建缓存和 Git。`toolkit/keymaps` 中随源码发布的映射用 safetensors 小文件保留，它们不是部署模型权重。

首次构建需要拉取基础镜像、Python/Git/npm 依赖。冻结文件包含传递依赖；安装后执行版本核对和 `pip check`。不要删除 diffusers 的 Git commit 固定值。

若 Docker Hub 直连不可用，可通过可访问的镜像站获取公开基础镜像（仍然从不含训练依赖的 Python 基础开始）：

```bash
docker build --network host \
  --build-arg NODE_IMAGE=m.daocloud.io/docker.io/library/node:24.16.0-bookworm-slim \
  --build-arg PYTHON_IMAGE=m.daocloud.io/docker.io/library/python:3.12-slim \
  -f docker/Dockerfile.service -t ai-toolkit-service:local .
```

镜像站是第三方来源，请按所在环境的供应链策略选择；不需要使用本机私有基础镜像。构建仍需能访问 GitHub、PyPI 和 npm。

如果宿主机依赖已配置的代理访问这些源，在上述命令增加 `--build-arg HTTP_PROXY --build-arg HTTPS_PROXY --build-arg ALL_PROXY`，让 Docker 从当前环境读取代理。不要把代理凭据写入 Dockerfile 或提交到 Git。宿主机回环代理需配合 `--network host`；这些参数只用于构建，不设置运行中服务的代理。

本机已有训练依赖基础镜像，可显式复用以减少重复下载：

```bash
docker build --network host \
  --build-arg NODE_IMAGE=m.daocloud.io/docker.io/library/node:24.16.0-bookworm-slim \
  --build-arg PYTHON_IMAGE=rail-ai-toolkit:local-test \
  -f docker/Dockerfile.service -t ai-toolkit-service:local .
```

`rail-ai-toolkit:local-test` 是本机已有镜像，不是可供其他机器直接拉取的公开基础。2026-09-17 首次验证使用此加速路径；2026-09-18 已补充通过镜像站与构建代理从公开 Python 基础镜像构建并部署的验证。构建会检查全部冻结依赖，并安装不匹配项，不能直接假定旧基础的依赖与导出环境相同。

## 创建容器并启动

```bash
export AI_TOOLKIT_AUTH='替换为足够长的随机令牌'
export AITK_MODELS_DIR='/绝对路径/模型目录'
docker compose -p aitk-service -f compose.service.yaml up -d --no-build
docker compose -p aitk-service -f compose.service.yaml ps
```

默认只发布 `127.0.0.1:8675`。远程业务系统应经内网反向代理访问，并在代理层统一鉴权；当前 `/api/files/` 和 `/api/img/` 仍沿用上游公开资源路由，不应直接向不受信任网络开放服务。

挂载位置：

| 内容 | 容器内路径 | 方式 |
|---|---|---|
| 模型权重 | `/app/ai-toolkit/models` | 宿主机目录，只读 |
| SQLite 数据库 | `/state/aitk_db.db` | 独立持久卷，通过项目根目录软链接引用 |
| 数据集 | `/app/ai-toolkit/datasets` | 独立持久卷 |
| 训练产物和日志 | `/app/ai-toolkit/output` | 独立持久卷 |
| Hugging Face 缓存 | `/hf-cache` | 独立持久卷 |

上传/训练配置必须使用容器可见的路径，例如 `models/unet/flux-2-klein-9b.safetensors`。宿主机的 `/home/...` 路径不能直接用作容器模型路径。离线模式默认开启，完整的文本编码器、tokenizer、VAE、scheduler 等依赖也必须准备好，只有 UNet 权重不足以运行完整 Flux2 训练。按具体模型配置本地路径或挂载已经准备好的 HF 缓存；API 微型模型测试不代表这些生产模型资源已验证。

注意跨目录软链接：Docker 只挂载指定目录，不会自动带入软链接指向的目录。本机 `models/vae/flux2-vae.safetensors` 指向 `../../comfyui_models/vae/flux2-vae.safetensors`，目前容器内不可读。正式 Flux 训练前，需将宿主机该真实文件单独只读挂载到例如 `/model-assets/flux2-vae.safetensors`，并把任务 `vae_path` 设置为这个容器路径；或按目录结构补充目标目录挂载。不要仅凭宿主机 `ls` 能看到文件就认为容器可读，需在容器中执行 `test -r` 验证。其他模型软链接同样需要检查。

服务启动时执行 Prisma `db push --skip-generate` 初始化/同步数据库，然后启动 UI 和 Worker。不使用 `--accept-data-loss`。镜像增加了 HTTP healthcheck，检查 API 与数据库读取是否成功。

停止容器前应停止接收新任务，等待已有训练结束或通过 API 停止后确认进程退出。强制终止容器可能中断 checkpoint 写入；重启本身不等于自动恢复训练。

## 容器外串行 API 验证

主机测试客户端需要 requests；真实训练测试还需 Pillow、torch、safetensors。

```bash
AI_TOOLKIT_AUTH="$AI_TOOLKIT_AUTH" \
  .venv/bin/python \
  testing/api_smoke.py --base-url http://127.0.0.1:8675 --exercise-worker
```

客户端禁用代理环境变量，避免 localhost 请求绕到代理。所有请求及任务串行执行。脚本创建唯一测试数据集与任务，结束后清理这些数据，保留唯一的停止队列记录。不要在业务有活动任务时运行 GPU 训练测试。

基础脚本验证 401、正常读取、创建/上传/下载/Range、任务冲突、查询更新、入队取消、保存标记、队列以及 Python 异常退出回写。`--exercise-worker` 使用无效任务类型，故意不加载模型；它只证明故障处理，不代表正常训练通过。

## 真实 LoRA 训练验收

先在主机创建一个离线随机微型 SD 模型（输出目录必须尚不存在）：

```bash
python testing/api_train_smoke.py --prepare-model output/api_test_model
```

在创建测试容器时增加只读挂载：

```text
宿主机 /绝对路径/output/api_test_model → 容器 /test-model（只读）
```

再从主机请求容器 API：

```bash
python testing/api_train_smoke.py \
  --base-url http://127.0.0.1:8675 --model-path /test-model --gpu 0
```

该脚本上传 64×64 图片并实际执行两步 rank=2 LoRA 训练，等待 completed，检查 loss 指标、下载的 safetensors 有限数值及非零 LoRA 更新，保留唯一命名的训练产物用于复核。此测试验证服务执行链路，不能评价模型质量、生产模型容量或 4090 性能。

在上一个测试完成后，再运行同一命令并附加 `--cancel`，验证运行中任务停止及 PID 清理。该模式会在首个可观察训练步后调用 stop，必须等到 stopped 且进程退出才算通过；不要同时运行两个 GPU 测试。

## 本地服务与 Python 选择

```bash
cd ui
export AI_TOOLKIT_AUTH='替换为随机令牌'
export AITK_PYTHON="$(cd .. && pwd)/.venv/bin/python"
npm run dev
```

`AITK_PYTHON` 必须是可用 Python 的绝对路径。未设置时仍按上游逻辑优先选择项目 `.venv`、`venv`，最后使用 PATH。一个尚未安装依赖的 `.venv` 不等于可用训练环境。

生产环境可以只用 `npm run start`，但必须提前 `npm run update_db && npm run build`。容器已经在构建/启动阶段完成对应步骤。

更多 API 请求字段见 `LORA_TRAINING_API.md`。验收实测结果见 `SERVICE_TEST_REPORT.md`，改造动机及验证记录见 `COMMITLOG.md`。
