# AI Toolkit LoRA 训练 API 接入说明

> 文档状态：当前实现说明 + 上层项目集成约定  
> 适用版本：AI Toolkit UI `v0.1.0`  
> 更新日期：2026-08-25

> 2026-09-17 部署补充：单镜像构建、权重挂载与环境选择见 [SERVICE_DEPLOYMENT.md](SERVICE_DEPLOYMENT.md)，串行 API / 微型 LoRA 实测见 [SERVICE_TEST_REPORT.md](SERVICE_TEST_REPORT.md)。本文历史宿主机路径不应直接用于容器；容器模型和数据路径以部署说明为准。

## 1. 文档目的

本文说明如何将 AI Toolkit 作为 LoRA 训练能力接入另一个业务项目，包括：

- 启动训练服务；
- 上传和管理训练数据集；
- 创建、排队、查询和停止 LoRA 训练任务；
- 获取训练日志、loss 数据和 LoRA 产物；
- 说明当前内部 API 的限制；
- 给出面向生产环境的上层 API 封装建议。

当前 UI 已经提供 REST API、SQLite 任务状态库和 GPU 队列 Worker。它适合单机、内网、可信调用方场景。若面向公网或多个业务方，应在这些接口前增加一层受控的业务 API，不建议直接暴露当前内部 API。

## 2. 服务地址

### 2.1 开发模式

```bash
cd /data_ssd/projects/ai-toolkit/ui
npm run dev
```

默认地址：

```text
Web UI:  http://localhost:3000
API:     http://localhost:3000/api/*
```

局域网其他机器应将 `localhost` 替换为训练服务器 IP，例如：

```text
http://172.18.3.19:3000/api/jobs
```

### 2.2 生产模式

```bash
cd /data_ssd/projects/ai-toolkit/ui
AI_TOOLKIT_AUTH='replace-with-a-strong-random-token' npm run build_and_start
```

默认地址：

```text
Web UI:  http://localhost:8675
API:     http://localhost:8675/api/*
```

后续已经构建并初始化数据库时，可以直接运行：

```bash
AI_TOOLKIT_AUTH='replace-with-a-strong-random-token' npm run start
```

### 2.3 `/api` 返回 404 是正常现象

项目没有实现 `/api` 根路由，因此访问以下地址会得到 404：

```text
http://localhost:3000/api
```

必须访问具体接口，例如：

```text
http://localhost:3000/api/jobs
http://localhost:3000/api/gpu
http://localhost:3000/api/queue
```

## 3. 鉴权与调用约定

### 3.1 Bearer Token

未设置 `AI_TOOLKIT_AUTH` 时，当前 API 默认不鉴权。

设置 `AI_TOOLKIT_AUTH` 后，请求应携带：

```http
Authorization: Bearer <AI_TOOLKIT_AUTH>
```

示例：

```bash
curl \
  -H 'Authorization: Bearer replace-with-a-strong-random-token' \
  http://localhost:3000/api/jobs
```

鉴权失败返回：

```http
HTTP/1.1 401 Unauthorized
Content-Type: application/json
```

```json
{
  "error": "Unauthorized"
}
```

### 3.2 Content-Type

- 普通请求：`application/json`；
- 数据集上传：`multipart/form-data`；
- 文件下载：二进制流，支持 HTTP Range。

### 3.3 跨域说明

当前服务主要按同源 UI 使用方式实现，没有完整的业务级 CORS 配置：

- 服务端到服务端调用不受浏览器 CORS 限制，推荐采用这种方式；
- 不建议业务前端浏览器直接调用训练服务；
- 推荐由上层项目后端调用本服务，再向业务前端提供自己的 API。

## 4. 推荐调用流程

```text
准备或上传数据集
      │
      ▼
POST /api/jobs 创建任务
      │
      ▼
GET /api/jobs/{id}/start 将任务加入队列
      │
      ▼
GET /api/queue/{gpu_ids}/start 启动 GPU 队列
      │
      ▼
轮询 GET /api/jobs?id={id}
      │
      ├── running：查询日志、loss 和样例
      ├── completed：获取 LoRA 产物
      ├── error：读取 info 和日志
      └── stopped：任务已停止
```

注意：当前实现中“任务入队”和“启动 GPU 队列”是两个独立操作，只调用其中一个不能保证任务开始执行。

## 5. 数据集接口

训练数据集默认保存在服务端配置的 `DATASETS_FOLDER` 下。默认目录为项目根目录的 `datasets/`。

LoRA 图片训练通常要求图片和 caption 文件同名，例如：

```text
datasets/interior_001/
├── 0001.jpg
├── 0001.txt
├── 0002.png
└── 0002.txt
```

### 5.1 创建数据集目录

```http
POST /api/datasets/create
Content-Type: application/json
```

请求：

```json
{
  "name": "Interior 001"
}
```

服务会将名称转换为小写安全名称：

```json
{
  "success": true,
  "name": "interior_001"
}
```

调用示例：

```bash
curl -X POST http://localhost:3000/api/datasets/create \
  -H 'Content-Type: application/json' \
  -H 'Authorization: Bearer YOUR_TOKEN' \
  -d '{"name":"Interior 001"}'
```

后续上传时应使用接口返回的 `name`，不要继续使用原始名称。

### 5.2 上传文件

```http
POST /api/datasets/upload
Content-Type: multipart/form-data
```

表单字段：

| 字段 | 类型 | 必填 | 说明 |
|---|---|---:|---|
| `datasetName` | string | 是 | `/api/datasets/create` 返回的安全名称 |
| `files` | file[] | 是 | 可重复提交的图片、视频、音频或 caption 文件 |

示例：

```bash
curl -X POST http://localhost:3000/api/datasets/upload \
  -H 'Authorization: Bearer YOUR_TOKEN' \
  -F 'datasetName=interior_001' \
  -F 'files=@/path/to/0001.jpg' \
  -F 'files=@/path/to/0001.txt' \
  -F 'files=@/path/to/0002.jpg' \
  -F 'files=@/path/to/0002.txt'
```

响应：

```json
{
  "message": "Files uploaded successfully",
  "files": ["0001.jpg", "0001.txt", "0002.jpg", "0002.txt"]
}
```

当前上传实现会覆盖数据集中已存在的同名文件。调用方应自行控制批次、文件大小、总容量和重复上传。

### 5.3 查询数据集

```http
GET /api/datasets/list
```

响应：

```json
["interior_001", "person_002"]
```

## 6. 训练任务接口

### 6.1 创建任务

```http
POST /api/jobs
Content-Type: application/json
```

请求字段：

| 字段 | 类型 | 必填 | 说明 |
|---|---|---:|---|
| `name` | string | 是 | 任务名称；数据库中必须唯一，同时用于输出目录名 |
| `gpu_ids` | string | 是 | GPU 队列标识，例如 `"0"`、`"1"` 或 `"0,1"` |
| `job_config` | object | 是 | AI Toolkit 完整训练配置对象，不是 YAML 字符串 |
| `job_ref` | string | 否 | 上层业务订单或任务 ID，用于关联查询 |
| `job_type` | string | 否 | 建议 LoRA 训练固定传 `"train"` |
| `id` | string | 否 | 传入已有任务 ID 时表示更新任务，不传表示创建 |

创建请求结构：

```json
{
  "name": "interior_lora_20260825_001",
  "gpu_ids": "0",
  "job_ref": "business-order-20260825-001",
  "job_type": "train",
  "job_config": {
    "job": "extension",
    "config": {
      "name": "interior_lora_20260825_001",
      "process": [
        {
          "type": "diffusion_trainer",
          "training_folder": "output",
          "sqlite_db_path": "./aitk_db.db",
          "device": "cuda",
          "network": {},
          "save": {},
          "datasets": [],
          "train": {},
          "model": {},
          "sample": {},
          "logging": {
            "log_every": 1,
            "use_ui_logger": true
          }
        }
      ]
    },
    "meta": {
      "name": "[name]",
      "version": "1.0"
    }
  }
}
```

上面的空对象仅用于展示协议结构，并不是可直接训练的完整配置。实际接入时，应基于经过验证的配置模板生成 `job_config`。当前 Flux2 Klein 训练模板可参考：

```text
config/flux2_klein_9b_interior_lora.yaml
config/flux2_klein_9b_interior_lora_smoke.yaml
```

建议保留以下配置：

```json
{
  "type": "diffusion_trainer",
  "sqlite_db_path": "./aitk_db.db",
  "logging": {
    "log_every": 1,
    "use_ui_logger": true
  }
}
```

`diffusion_trainer` 会把 `status`、`step`、`info` 和 `speed_string` 回写任务数据库。若改为普通 `sd_trainer`，训练本身可以执行，但无法完整获得 UI/API 状态回写能力。

响应示例：

```json
{
  "id": "e4fef24d-2e06-4e82-93a7-5ec2af360a18",
  "name": "interior_lora_20260825_001",
  "gpu_ids": "0",
  "status": "stopped",
  "step": 0,
  "queue_position": 1000,
  "job_type": "train",
  "job_ref": "business-order-20260825-001"
}
```

任务名称冲突时返回：

```http
HTTP/1.1 409 Conflict
```

```json
{
  "error": "Job name already exists"
}
```

### 6.2 查询任务

查询单个任务：

```http
GET /api/jobs?id={job_id}
```

通过业务引用查询最近一条任务：

```http
GET /api/jobs?job_ref={job_ref}
```

查询全部任务：

```http
GET /api/jobs
```

只查询活动任务：

```http
GET /api/jobs?only_active=true
```

活动状态包括 `running`、`queued` 和 `stopping`。

典型响应：

```json
{
  "id": "e4fef24d-2e06-4e82-93a7-5ec2af360a18",
  "name": "interior_lora_20260825_001",
  "gpu_ids": "0",
  "status": "running",
  "step": 127,
  "total_steps": 2000,
  "info": "Training",
  "speed_string": "2.31 sec/iter",
  "pid": 12345,
  "job_ref": "business-order-20260825-001"
}
```

任务状态：

| 状态 | 说明 | 是否终态 |
|---|---|---:|
| `stopped` | 新建、人工停止或尚未开始 | 是 |
| `queued` | 等待对应 GPU 队列调度 | 否 |
| `running` | 正在加载模型、数据集或训练 | 否 |
| `stopping` | 正在停止 | 否 |
| `completed` | 训练完成 | 是 |
| `error` | 训练失败，错误摘要在 `info` | 是 |

### 6.3 将任务加入队列

```http
GET /api/jobs/{job_id}/start
```

示例：

```bash
curl \
  -H 'Authorization: Bearer YOUR_TOKEN' \
  http://localhost:3000/api/jobs/e4fef24d-2e06-4e82-93a7-5ec2af360a18/start
```

该接口会把任务状态更新为 `queued`，但不会自动把 GPU 队列的 `is_running` 设置为 `true`。

### 6.4 启动 GPU 队列

```http
GET /api/queue/{gpu_ids}/start
```

单卡 GPU 0：

```bash
curl \
  -H 'Authorization: Bearer YOUR_TOKEN' \
  http://localhost:3000/api/queue/0/start
```

Worker 每秒扫描一次队列。同一个 `gpu_ids` 队列同一时刻只运行一个任务，其他任务按 `queue_position` 排队。

查询所有队列：

```http
GET /api/queue
```

停止继续调度该 GPU 队列：

```http
GET /api/queue/{gpu_ids}/stop
```

停止队列不等同于立即杀死当前训练任务；需要停止具体任务时，请调用任务停止接口。

### 6.5 停止任务

```http
GET /api/jobs/{job_id}/stop
```

示例：

```bash
curl \
  -H 'Authorization: Bearer YOUR_TOKEN' \
  http://localhost:3000/api/jobs/e4fef24d-2e06-4e82-93a7-5ec2af360a18/stop
```

Linux 下服务会向训练进程发送 `SIGINT`。不要在 checkpoint 正在写入时强制终止进程，否则可能损坏 checkpoint。

### 6.6 请求立即保存

```http
GET /api/jobs/{job_id}/save_now
```

该接口只设置保存标记，训练进程会在后续训练步中检测并执行保存，不代表响应返回时已经完成保存。

### 6.7 删除任务

```http
GET /api/jobs/{job_id}/delete
```

该操作会递归删除对应的整个训练输出目录，然后删除数据库记录，属于不可恢复的破坏性操作。上层项目不应向普通用户直接开放此接口。

## 7. 日志、指标与训练样例

### 7.1 增量读取文本日志

```http
GET /api/jobs/{job_id}/log?offset={byte_offset}
```

首次请求可以省略 `offset` 或传 `0`：

```json
{
  "log": "Loading model...\nTraining...\n",
  "offset": 10240,
  "reset": true
}
```

后续请求携带上次返回的 `offset`：

```http
GET /api/jobs/{job_id}/log?offset=10240
```

```json
{
  "log": "step 128...\n",
  "offset": 10892,
  "reset": false
}
```

推荐轮询间隔为 2～5 秒，不要按训练 step 高频请求。

### 7.2 查询 loss 和其他指标

```http
GET /api/jobs/{job_id}/loss
```

查询参数：

| 参数 | 默认值 | 说明 |
|---|---:|---|
| `key` | `loss` | 指标名称 |
| `limit` | `2000` | 最大点数，上限 20000 |
| `since_step` | 无 | 只返回大于该 step 的点 |
| `stride` | `1` | 按 step 取样 |

示例：

```http
GET /api/jobs/{job_id}/loss?key=loss&since_step=100&stride=2
```

响应：

```json
{
  "key": "loss",
  "keys": ["loss", "lr"],
  "points": [
    {
      "step": 102,
      "wall_time": 1787630400.25,
      "value": 0.1842
    }
  ]
}
```

### 7.3 查询训练样例

```http
GET /api/jobs/{job_id}/samples
```

响应中的 `samples` 是训练服务器上的绝对路径列表。

## 8. LoRA 产物查询和下载

### 8.1 查询产物

```http
GET /api/jobs/{job_id}/files
```

当前接口返回任务根目录中的 `.safetensors` 文件，并在存在时包含 `optimizer.pt`：

```json
{
  "files": [
    {
      "path": "/data_ssd/projects/ai-toolkit/output/interior_lora_20260825_001/interior_lora_20260825_001_000002000.safetensors",
      "size": 187432960
    }
  ]
}
```

### 8.2 下载文件

下载地址格式：

```text
GET /api/files/{encodeURIComponent(absolute_file_path)}
```

JavaScript 示例：

```javascript
const apiBase = 'http://localhost:3000';
const absolutePath = file.path;
const downloadUrl = `${apiBase}/api/files/${encodeURIComponent(absolutePath)}`;
```

当前 `/api/files/` 被配置为公开路由，即使设置了 `AI_TOOLKIT_AUTH`，该下载接口也不校验 Bearer Token。只应在可信内网使用；生产环境必须改为鉴权下载或由上层服务生成短期签名 URL。

## 9. Python 接入示例

下面演示上层后端如何基于经过验证的 YAML 模板创建任务、启动训练并轮询状态。

```python
import copy
import time
import uuid
from pathlib import Path

import requests
import yaml

BASE_URL = "http://127.0.0.1:3000"
TOKEN = "YOUR_TOKEN"
GPU_IDS = "0"
DATASETS_ROOT = "/data_ssd/projects/ai-toolkit/datasets"

session = requests.Session()
session.headers.update({"Authorization": f"Bearer {TOKEN}"})


def load_template() -> dict:
    template_path = Path(
        "/data_ssd/projects/ai-toolkit/"
        "config/flux2_klein_9b_interior_lora.yaml"
    )
    with template_path.open("r", encoding="utf-8") as file:
        return yaml.safe_load(file)


def create_training(dataset_name: str, business_id: str) -> dict:
    name = f"lora_{business_id}_{uuid.uuid4().hex[:8]}"
    job_config = copy.deepcopy(load_template())

    job_config["config"]["name"] = name
    process = job_config["config"]["process"][0]
    process["type"] = "diffusion_trainer"
    process["datasets"][0]["folder_path"] = str(
        Path(DATASETS_ROOT) / dataset_name
    )
    process["sqlite_db_path"] = "./aitk_db.db"
    process.setdefault("logging", {})["use_ui_logger"] = True

    response = session.post(
        f"{BASE_URL}/api/jobs",
        json={
            "name": name,
            "gpu_ids": GPU_IDS,
            "job_ref": business_id,
            "job_type": "train",
            "job_config": job_config,
        },
        timeout=30,
    )
    response.raise_for_status()
    return response.json()


def start_training(job_id: str) -> None:
    response = session.get(
        f"{BASE_URL}/api/jobs/{job_id}/start",
        timeout=30,
    )
    response.raise_for_status()

    response = session.get(
        f"{BASE_URL}/api/queue/{GPU_IDS}/start",
        timeout=30,
    )
    response.raise_for_status()


def wait_for_training(job_id: str) -> dict:
    terminal_statuses = {"completed", "error", "stopped"}

    while True:
        response = session.get(
            f"{BASE_URL}/api/jobs",
            params={"id": job_id},
            timeout=30,
        )
        response.raise_for_status()
        job = response.json()

        print(
            job["status"],
            job.get("step"),
            job.get("total_steps"),
            job.get("info"),
        )

        if job["status"] in terminal_statuses:
            return job

        time.sleep(5)


job = create_training(
    dataset_name="interior_001",
    business_id="order-20260825-001",
)
start_training(job["id"])
result = wait_for_training(job["id"])

if result["status"] != "completed":
    raise RuntimeError(f"Training failed: {result.get('info')}")

files_response = session.get(
    f"{BASE_URL}/api/jobs/{job['id']}/files",
    timeout=30,
)
files_response.raise_for_status()
print(files_response.json())
```

注意：如果未设置 `AI_TOOLKIT_AUTH`，可以不设置 `Authorization` 请求头。生产环境必须设置鉴权。

## 10. 当前 API 的已知限制

当前接口是 AI Toolkit UI 的内部接口，不是稳定的公共 API，存在以下限制：

1. 使用一个全局静态 Bearer Token，没有用户、租户、角色和权限模型。
2. 多个修改状态的操作使用 `GET`，不符合标准 REST 语义。
3. 创建任务时允许调用方提交完整 `job_config`，包括本地路径和大量底层参数。
4. 缺少完整 JSON Schema 校验、参数白名单、显存预估和训练配额。
5. `job_ref` 不是唯一字段，不能单独保证幂等。
6. SQLite 适合单机任务控制，不适合多个控制节点并发写入。
7. `/api/files/` 当前绕过鉴权。
8. 上传接口缺少完善的文件类型、单文件大小、总容量和租户隔离限制。
9. 没有稳定的 API 版本号、OpenAPI 文档、webhook 或事件推送。
10. 没有统一的业务错误码，部分失败只返回通用 500。
11. API 返回训练服务器绝对路径，上层调用方与训练服务耦合较强。
12. 当前删除任务接口会同时删除训练目录，风险较高。

因此，当前 API 仅建议部署在受限内网，并由上层项目后端调用。

## 11. 推荐的上层业务 API

当 AI Toolkit 成为大项目中的 LoRA 训练模块时，建议保留本项目作为 GPU Worker，在前面增加一层稳定的业务 API：

```text
业务前端
   │
   ▼
大项目后端 / LoRA Training API
鉴权、参数校验、幂等、配额、模型白名单
   │
   ▼
AI Toolkit 内部 API / GPU Worker
   │
   ├── 数据集存储
   ├── 任务队列
   └── LoRA 产物存储
```

推荐对业务侧暴露：

```text
POST   /v1/lora/trainings
GET    /v1/lora/trainings/{id}
POST   /v1/lora/trainings/{id}/cancel
GET    /v1/lora/trainings/{id}/logs
GET    /v1/lora/trainings/{id}/metrics
GET    /v1/lora/trainings/{id}/artifacts
POST   /v1/lora/datasets
```

业务调用方不应直接提交完整 `job_config`，只提交业务允许的参数：

```json
{
  "request_id": "order-20260825-001",
  "model": "flux2-klein-9b",
  "dataset_id": "dataset-interior-001",
  "trigger_word": "interior_style_x",
  "steps": 2000,
  "rank": 16,
  "learning_rate": 0.0001,
  "resolution": 1024
}
```

上层服务负责：

- 校验 `request_id` 并保证幂等；
- 将 `model` 映射到服务器允许的模型路径和配置模板；
- 将 `dataset_id` 映射到受控的数据目录或对象存储地址；
- 限制训练步数、分辨率、LoRA rank、学习率和 GPU 资源；
- 生成内部 `job_config`；
- 调用本项目 `/api/jobs` 和队列接口；
- 将内部任务状态转换成稳定的业务状态；
- 将绝对文件路径转换为受保护的下载 URL；
- 记录审计日志、用户、租户、配额和计费信息；
- 通过 webhook、消息队列或 SSE 通知训练完成。

## 12. 生产部署检查表

- [ ] 使用 `npm run build_and_start` 或进程管理器运行生产模式；
- [ ] 设置高强度 `AI_TOOLKIT_AUTH`；
- [ ] 不直接向公网开放 3000/8675 端口；
- [ ] 由反向代理启用 HTTPS；
- [ ] 将调用限制在上层项目后端或可信网络；
- [ ] 修复 `/api/files/` 绕过鉴权的问题；
- [ ] 对模型和数据路径做服务端白名单校验；
- [ ] 对数据集上传设置文件类型、大小、总量和频率限制；
- [ ] 为业务请求实现真正的幂等键；
- [ ] 对任务删除操作增加权限和二次确认；
- [ ] 监控 GPU、磁盘空间、训练进程和队列状态；
- [ ] 定期备份任务数据库和重要 LoRA 产物；
- [ ] 为长时间无进度任务设置超时和清理策略；
- [ ] 将开发环境和生产环境的模型、数据、输出目录分离。

## 13. 相关源码

| 模块 | 文件 |
|---|---|
| API 鉴权 | `ui/src/middleware.ts` |
| 任务 CRUD | `ui/src/app/api/jobs/route.ts` |
| 任务启动 | `ui/src/app/api/jobs/[jobID]/start/route.ts` |
| 任务停止 | `ui/src/app/api/jobs/[jobID]/stop/route.ts` |
| GPU 队列 | `ui/src/app/api/queue/` |
| 队列扫描 Worker | `ui/cron/worker.ts` |
| Python 子进程启动 | `ui/cron/actions/startJob.ts` |
| 任务数据库结构 | `ui/prisma/schema.prisma` |
| 训练状态回写 | `extensions_built_in/sd_trainer/DiffusionTrainer.py` |
| 数据集接口 | `ui/src/app/api/datasets/` |
| 产物下载 | `ui/src/app/api/files/[...filePath]/route.ts` |
| 训练配置示例 | `config/examples/`、`config/flux2_klein_9b_interior_lora.yaml` |
