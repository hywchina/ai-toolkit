# 提交变更记录

每条记录以英文 commit 标题关联 Git 提交，正文描述中文变更动机、范围及验证。

## build(docker): validate clean public-base deployment

- 动机：补齐不依赖本机旧训练基础镜像的可移植构建验收，解决构建时 GitHub HTTP/2 下载中断及代理未传入问题。
- 范围：只在 Python 安装构建步骤使用 Git HTTP/1.1；部署说明补充公开基础镜像站和环境代理传入方式，本地启动示例改用已验收 .venv，说明跨目录模型软链接的挂载限制；更新最终验收证据。
- 验证：通过镜像站公开 Python 基础与宿主机现有构建代理生成镜像 34842906b5ef，同一标签、同一服务容器替换成功。容器内依赖/GPU 检查及容器外 47 项 API 检查通过；两步真实 LoRA、运行中取消及重启后的任务/权重 SHA256 一致性通过。详见 SERVICE_TEST_REPORT.md 中 2026-09-18 记录。
- 注意：Docker Hub 直连在本机仍不可用，镜像站与代理为本次网络条件；代理值未写入代码或运行环境。未改变固定依赖版本，未提交用户 .gitignore 改动。生产模型 VAE 软链接仍需按业务模型配置单独挂载；不宣称 4090 或全量生产验收完成。

## test(api): extend serial coverage and validate the uv environment

- 动机：补齐项目内 uv 虚拟环境的运行验收，避免仅用 Conda 测试替代 .venv；扩大数据集标注等集成接口覆盖。
- 范围：串行测试增加 CPU、图片上传和列表、标注读取/修改/批量读取、图片删除、缺失插件查询，以及批量参数和 ZIP 参数错误响应。所有写入/删除只针对 UUID 命名的测试数据。
- 验证：2026-09-18 显式使用项目 .venv 启动本地 Worker，47 次 HTTP 检查及 2 次清理通过；真实两步 LoRA 任务 5bb1b834-2c4d-495f-9507-cbd5fbee7318 完成，指标和非零权重验证通过；取消任务 15022934-110c-4afc-ab7a-3d3e7fd85df0 最终 stopped/pid=null。Python 语法和 git diff --check 通过。
- 注意：ZIP 仅覆盖缺参数响应，不代表打包成功路径通过；微型随机模型不代表生产模型质量或 4090 实测。训练产物保留，测试结束关闭本次启动的本地服务。

## test(docker): record serial API and LoRA deployment acceptance

- 动机：区分接口响应、真正训练、主动取消与容器持久化的验收证据，避免将微型模型测试误报为生产模型/4090 验证。
- 范围：新增 SERVICE_TEST_REPORT.md，更新实施计划完成情况；修正取消测试输出字段名为 reported_step_after_stop，避免把回滚到最近已保存步数误认为取消前训练步数。
- 验证：最终镜像 28186b237647 在 RTX 3090 上运行健康，宿主机串行 API 35 次检查通过，另有 2 次清理请求。正常训练任务 6d277e08-f569-4d65-974e-741cccc4c791 完成两步且生成有效 LoRA；运行中取消任务 d6b822f9-241f-4b29-a208-4275de7e4655 最终 stopped/pid=null；已完成任务 stop 不改变状态。重启后任务状态与权重 SHA256 保持一致，GPU/CPU API 正常。
- 注意：测试保留自身生成的训练产物和停止队列记录；未打包生产模型。基础依赖/npm 告警及未验证的 Flux2 9B/4090/多卡场景均明确写入报告。原用户 .gitignore 改动未提交；随机测试令牌仅在受限临时配置中保存。

## feat(docker): package the LoRA API with mounted models and persistent state

- 动机：将当前本地 AI Toolkit 改造打包为单个可运行服务镜像，避免上游 Dockerfile 从 GitHub 覆盖本地源码或将业务模型打入镜像。
- 范围：新增 Dockerfile.service、专属构建排除文件、冻结依赖校验/安装器、运行时 Prisma 初始化入口及 compose.service.yaml；固定 Python 3.12 依赖、Node 24.16.0，使用 CUDA 12.8 PyTorch wheel，支持 Ubuntu NVIDIA 宿主机。API/Worker/Python 位于同一镜像，模型只读挂载，数据库/数据集/输出/HF缓存持久化；增加健康检查并要求令牌。UI 使用系统字体，消除 Google 字体构建网络依赖。新增部署文档和旧 API 文档索引。
- 验证：目标镜像 ai-toolkit-service:local 初次构建成功；冻结依赖全量比对、pip check、Worker 编译、Next.js 生产构建通过。CDI 可见 RTX 3090，容器外 36 次 HTTP 检查、两步真实 LoRA 及容器重启后的状态/权重 SHA256 一致检查通过。取消行为额外修复后的最终回归结果单独记录在 SERVICE_TEST_REPORT.md。
- 注意：实测复用了本机 rail-ai-toolkit:local-test 基础并校准依赖；公开 python:3.12-slim 从零构建路径已提供但未额外构建第二个目标镜像。容器用户空间为 Debian，可在 Ubuntu 宿主机运行；没有 4090 实测。公开资源鉴权等上游限制和已有 npm 告警见部署/验收文档，服务默认只监听宿主机回环端口。

## fix(api): preserve cancellation state until the training process exits

- 动机：容器真实运行中取消测试证明 SIGINT 被训练器写成 error；原停止接口过早释放队列，还可能向已完成任务的旧 PID 发送信号。
- 范围：运行中任务先标记 stopping，训练器在错误收尾时识别显式 stop 请求，退出后由 Worker 清空 PID；对终态 stop 返回原状态。Windows 使用 execFile 避免拼接 shell 命令。扩展微型训练测试增加运行中取消与终态 no-op 检查。
- 验证：本地串行 API 再次通过（35 次请求，轮询次数会随运行速度变化）；实际取消任务 85ea9d76-6dca-4d9b-b3f4-beb46b02637a 在 step=2 后为 stopped 且 pid=null。对已完成任务调用 stop 后保持 completed；Worker TypeScript 编译通过。容器重建后需复测同样流程。
- 注意：停止仍使用 SIGINT；不能保证强制中断 checkpoint 写入时产物完整。新增停止状态不会自动恢复被用户停止的训练。

## fix(training): support serial data loading and verify tiny LoRA training

- 动机：资源有限时需要 num_workers=0，实际训练发现 Linux 路径仍传 prefetch_factor，PyTorch 会拒绝初始化 DataLoader。
- 范围：仅在 num_workers>0 时传预取参数；新增真实训练 API 测试，离线生成随机微型 SD 模型，串行上传一张 64×64 图片、提交两步 rank=2 LoRA 训练、等待 completed、读取 loss/loss 并校验权重下载字节数。
- 验证：RTX 3090 上成功完成任务 9ddef67f-8be4-4d3f-b800-45894a6e1620，step=2、1 个指标点、1 个 LoRA 权重文件。前置失败分别定位到 DataLoader 参数及测试夹具的 Transformers 5 tokenizer 参数，已修正后重测。
- 注意：随机微型模型用于验证完整训练链路，不用于出图质量验证；本次未执行 Flux2 9B 全模型训练，也未在 RTX 4090 上实测。测试产物保留在忽略的 output 和 datasets 中，模型不进入 Git。

## build(env): pin the exported Python training environment

- 动机：容器及本地开发应复现现有 ai-toolkit_312 Conda 运行环境，避免依赖浮动导致训练结果难以复现。
- 范围：提交此前任务已生成的 requirements.txt（174 个依赖及 diffusers 固定提交）和 set_env.sh（uv 创建/同步项目 .venv），保留 requirements_base.txt 作为上游参考。
- 验证：原 Conda 环境 pip check 无冲突；Shell 语法检查通过。当前用户已有 uv sync 正在安装，因此本次本地 API 训练验证通过 AITK_PYTHON 选择完整的 Conda 环境，未把空 .venv 误报为可用。
- 注意：这份冻结文件面向 Python 3.12 / Linux NVIDIA 环境；CUDA wheel 的本地版本后缀可与基础版本固定值匹配。Git 源依赖在首次安装时需要网络。

## fix(api): handle queued cancellation and worker launch failures

- 动机：串行 HTTP 测试发现排队任务调用 stop 后仍为 queued；代码检查发现 Python 初始化失败会留在 running，且早期错误没有日志。
- 范围：增加唯一测试任务/数据集的串行 HTTP 测试，覆盖鉴权、文件上传/下载及 Range、任务创建/冲突/查询/更新/取消、状态、日志、loss、样例、队列与故障回写。新增实施计划。
- 修复：Worker 使用原子状态认领，捕获子进程 error/exit，保留训练器已写入的终态；从进程启动就记录 stdout/stderr；统一输出目录及任务名。增加 AITK_PYTHON 绝对路径覆盖配置，支持复用 Conda 环境。取消排队任务即时设置 stopped。
- 验证：本机 Next.js 端口 3000，显式使用原 Conda Python；修复后 36 次 HTTP 检查通过，另外完成测试任务及数据集清理。Worker TypeScript 编译通过。
- 注意：故障任务刻意使用无效 job 类型，不加载模型；这部分结果不代表真实 LoRA 训练通过。测试保留唯一的已停止队列记录用于追踪。
