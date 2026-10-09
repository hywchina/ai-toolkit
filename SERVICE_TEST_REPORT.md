# LoRA 服务验收记录（2026-09-17）

## 2026-10-09：系统回归与 Next.js 类型门禁

- 修复 15 个动态 API 路由和 2 个客户端页面的参数类型，使用 Next.js 的 Promise 参数；客户端直接 `use(params)`，不再强制转为 `any`。文件、图片与音频 catch-all 参数按数组拼接路径，保留原有编码绝对路径协议及目录权限检查。
- 移除 `ignoreBuildErrors`，新增 `npm run typecheck`；Worker 编译、完整 UI 类型检查和开启类型验证的生产构建全部通过。校正工作区追踪根、弃用的 devIndicators 和 macOS 可选外部模块配置，原三类构建告警已消除。
- 新增 5 项路径单测（编码绝对路径、多段、中文/逗号/空格、遍历保留供资源层校验、非法编码），`npm test` 通过。测试使用现有 TypeScript 编译器加载真实源码，兼容不能直接加载 TypeScript 的 Node 20；没有把包改成 ESM，避免破坏 CommonJS Worker。
- `npm run lint` 发现上游缺少 ESLint 配置、会进入交互初始化；不记为通过，也未自动引入未经评估的规则或依赖。真实服务 HTTP、训练、取消及生产模型质量本轮没有复验；没有启动 GPU 队列、修改 SQLite 数据或覆盖历史训练产物。

> 2026-09-23 根 Compose 复测使用的镜像标签为 `rail-ai-toolkit:service-local`，容器名为 `rail-ai-toolkit-1`。服务 healthy；在根 Compose 新命名卷和集中模型挂载下，鉴权、数据集、文件 Range、任务、队列与 Worker 异常回写等 48 项检查通过并清理测试数据。Flux2 9B UNet、共享 VAE 和 Qwen 目录在容器两套约定路径下均真实可读，历史跨目录软链接问题已由根 Compose 挂载解决。未在本轮重复生产 Flux2 或微型真实 LoRA；以下历史记录保留真实训练证据。

> 命名说明：本报告保留验收时的 `ai-toolkit-service:local` 镜像和
> `aitk-service-ai-toolkit-1` 容器名作为历史证据。当前规范名分别是
> `rail-ai-toolkit:service-local` 和 `rail-ai-toolkit-validation-ai-toolkit-1`。当前正式标签为
> `rail-ai-toolkit:1.0.0`，与验收镜像指向同一个镜像 ID。

## 2026-09-18：项目 .venv 补充验收

项目 .venv（Python 3.12.13、PyTorch 2.9.1+cu128）已完成 174 个依赖安装与兼容检查，CUDA 可用。显式通过 AITK_PYTHON 指定该环境启动本地服务，所有测试依次执行。

- 扩展串行 API：47 次检查及 2 次清理通过，新增 CPU、图片列表、标注读写与批量查询、图片删除、缺失插件及参数错误响应。
- 正常训练：5bb1b834-2c4d-495f-9507-cbd5fbee7318，completed / 2 steps / 1 个指标点 / 1 个有效 LoRA，检查参数更新及下载。
- 运行中取消：15022934-110c-4afc-ab7a-3d3e7fd85df0，最终 stopped / pid=null，最终报告 step=6。
- 本次并未修改生产模型配置或停止其他业务服务；GPU 测试未并发运行。

## 2026-09-18：公开基础镜像构建与容器复验

- Docker Hub 直连失败；改用镜像站获取公开 `python:3.12-slim` 与 Node 基础镜像。GitHub 下载先遇到 HTTP/2 错误，HTTP/1.1 重试仍无法直连，最终通过宿主机已有代理完成构建。没有复用 `rail-ai-toolkit:local-test` 的训练依赖。
- Python 基础镜像 manifest：`sha256:2c941e860699f878900b0edc2403613c234d4b32eda3cc9fa7036991a2a63c4a`；最终服务镜像底部四层与其一致。
- 更新同一标签 `ai-toolkit-service:local`，镜像 ID：`sha256:34842906b5ef16fdd98c0ce62ce231e96dab1708e35273c5d1da6c7a8f9edce2`。未创建第二个服务实例。
- 重新创建原容器后，冻结依赖检查、pip check、CUDA 12.8 / PyTorch 2.9.1+cu128 / RTX 3090 可用检查通过；容器 healthy。
- 容器外扩展串行 API：47 次检查及 2 次清理通过。
- 正常训练任务 `77b4e41f-6a41-46c8-b830-f9b929953ff4`：completed / 2 steps / 1 个指标点 / 1 个数值有效且发生参数更新的 LoRA。
- 取消任务 `0fc52925-902c-4a5c-be98-bb83c74951b2`：观察到 step=3 后请求取消，最终 stopped / pid=null，报告 step=2。
- 重启后上述任务状态、权重校验和一致，GPU/CPU API 可用。权重 SHA256：`476ad735c749da904f0c4bc8fbd41422e458b5f94aa8ba74d67cbd1719ced06a`。
- 生产模型限制：本机 VAE 是跨挂载目录的软链接，当前容器内不可读。正式 Flux 训练前需补充真实文件挂载和容器路径配置。4090、完整生产模型、全部接口成功路径仍未验收；本次不是全量生产验收。

以下保留 2026-09-17 的首次验收记录；其中旧镜像 ID 和 .venv 未安装的描述是历史状态。

## 范围与环境

- 宿主机 Ubuntu 24.04.5 LTS，RTX 3090 24GB，NVIDIA 驱动 595.91.07；没有 RTX 4090 实测结果。
- Docker Engine 29.7.2，NVIDIA CDI 配置 `/var/run/cdi/nvidia.yaml` 可用。
- 本地 Python：原 Conda ai-toolkit_312（3.12.13）；项目 .venv 初始为空，另有用户安装进程，测试显式指定 AITK_PYTHON。
- 所有 API 请求顺序执行；本地测试服务关闭后再启动容器服务。没有停止用户的 ComfyUI 服务。

## 本地 API

`testing/api_smoke.py --exercise-worker` 在 `127.0.0.1:3000` 执行通过：36 次请求检查，以及两次测试任务/数据集清理。

覆盖：鉴权成功/失败、/api 根路径 404、任务/队列/GPU/设置/数据集查询、数据集创建上传、文件全量下载和 Range、任务创建/重名冲突/业务引用查询/更新、日志/指标/文件/样例查询、入队取消、立即保存标记、启动队列、Python 异常退出后 error 状态与日志。

首次测试暴露排队任务取消后仍为 queued，已修复并复测通过。额外修复 Worker 无法捕获 Python 初始化失败的情况，避免任务一直 running。

## 本地真实 LoRA 训练

使用离线生成的随机微型 Stable Diffusion 模型（约 2.4MB），1 张 64×64 图片，rank=2、2 steps、float32，关闭采样。

- 成功任务：`9ddef67f-8be4-4d3f-b800-45894a6e1620`。
- 结果：`completed`，step=2，1 个 loss/loss 指标点，1 个可下载 LoRA safetensors。
- 额外检查：LoRA tensor 全部为有限数，lora_up 参数存在非零更新。
- 修复：Linux DataLoader 在 num_workers=0 时不再传 prefetch_factor；测试夹具适配 Transformers 5 tokenizer 参数。
- 训练日志和权重保留在项目 output/train_smoke_*；测试数据位于 datasets/train_smoke_*。失败测试同样保留用于复核。

## 容器验收

最终镜像：`ai-toolkit-service:local`，ID `sha256:28186b23764777603cfa9674e1b465d3613114d5108d4db2a63055bfe5ba13f7`，Docker 显示大小约 20.7GB（含 CUDA/PyTorch 依赖和复用的基础层），不是模型权重体积。

容器：`aitk-service-ai-toolkit-1`；API：`http://127.0.0.1:8675`；最终状态为 running / healthy。只创建一个服务容器，修复后重建同一个目标镜像标签，没有并行运行多个训练服务。

| 验证项 | 结果 |
|---|---|
| 生产镜像构建 | 通过：冻结依赖校准、pip check、Worker tsc、Next.js production build |
| 容器 GPU | `torch 2.9.1+cu128`，CUDA 12.8，`is_available=True`，RTX 3090 |
| 容器外串行 HTTP | 最终一轮 35 次检查通过，另有 2 次清理请求；初轮 36 次也通过。数量随状态轮询次数变化 |
| 正常 LoRA 训练 | 任务 `6d277e08-f569-4d65-974e-741cccc4c791`，completed / step=2 |
| 指标及权重 | 1 个 loss/loss 点；1 个 LoRA 权重下载成功，数值全部有限且 lora_up 存在非零更新 |
| 运行中取消 | 任务 `d6b822f9-241f-4b29-a208-4275de7e4655`，观察到 step=2 后取消，最终 stopped / pid=null |
| 已完成任务再 stop | 保持 completed，不向旧 PID 发信号 |
| 重建容器 | 原有持久卷中的任务和产物仍存在 |
| 最终镜像重启 | 正常/取消任务状态保留，权重 SHA256 重启前后相同，GPU/CPU API 可调用 |
| 挂载 | `/app/ai-toolkit/models`、测试模型 `/test-model` 为只读；数据库、数据集、输出与 HF 缓存为持久卷 |

取消发生在保存过程中时，训练器会把 step 回写为最后已保存步数，本次最终为 0；不能把该字段误读为从未执行训练。取消测试不评价被中断 checkpoint 的完整性。

最终正常训练权重的 SHA256（重启前后相同）：`76262eb9c3d33170d4f662aebeb7c947e8ea086051389cfebc8ee3210e0c30fc`。

初次运行中取消测试出现 error，已在提交 `fix(api): preserve cancellation state until the training process exits` 修复，完成本地及最终容器回归。

本次运行配置保存在 `/tmp/aitk-service-validation.env`（权限 600，含随机 Token，不进 Git）和 `/tmp/aitk-service-validation.override.yaml`（额外挂载微型测试模型）。容器保持运行供继续测试；临时配置不保证宿主机重启后保留，长期部署请按 SERVICE_DEPLOYMENT.md 配置自己的令牌及挂载。报告不记录明文 Token。

## 验证边界

真实训练测试验证梯度更新、保存、数据库状态回写、指标查询和下载链路，不评价生成质量。未运行 Flux2 Klein 9B 完整训练、图片生成、自动打标、模型合并或多卡训练，也未做多租户安全验收。

原有 API 的 GET 修改操作、公开图片/文件路由、完整 job_config 信任模型等保持兼容，当前服务仅面向可信后端。详见 SERVICE_DEPLOYMENT.md。

构建日志中的现有告警：npm audit 汇总 16 项（3 low / 11 high / 2 critical），本次未执行破坏性依赖升级；Next.js 沿用上游 ignoreBuildErrors，完整 UI 类型检查被跳过，Worker 的 tsc 编译实际执行通过。另有弃用的 devIndicators 和 Linux 不使用的 macOS 温度模块警告；生产构建成功并不等同于全项目无类型/安全问题。
