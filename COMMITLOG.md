# 提交变更记录

每条记录以英文 commit 标题关联 Git 提交，正文描述中文变更动机、范围及验证。

## fix(api): handle queued cancellation and worker launch failures

- 动机：串行 HTTP 测试发现排队任务调用 stop 后仍为 queued；代码检查发现 Python 初始化失败会留在 running，且早期错误没有日志。
- 范围：增加唯一测试任务/数据集的串行 HTTP 测试，覆盖鉴权、文件上传/下载及 Range、任务创建/冲突/查询/更新/取消、状态、日志、loss、样例、队列与故障回写。新增实施计划。
- 修复：Worker 使用原子状态认领，捕获子进程 error/exit，保留训练器已写入的终态；从进程启动就记录 stdout/stderr；统一输出目录及任务名。增加 AITK_PYTHON 绝对路径覆盖配置，支持复用 Conda 环境。取消排队任务即时设置 stopped。
- 验证：本机 Next.js 端口 3000，显式使用原 Conda Python；修复后 36 次 HTTP 检查通过，另外完成测试任务及数据集清理。Worker TypeScript 编译通过。
- 注意：故障任务刻意使用无效 job 类型，不加载模型；这部分结果不代表真实 LoRA 训练通过。测试保留唯一的已停止队列记录用于追踪。
