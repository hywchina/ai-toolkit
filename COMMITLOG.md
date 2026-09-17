# 提交变更记录

每条记录以英文 commit 标题关联 Git 提交，正文描述中文变更动机、范围及验证。

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
