# FlowScope 接入标准操作程序 (SOP)

本文档为其他项目接入 FlowScope 数据流观察与分析系统提供标准操作指南。

## 文档目标

**成功标准**：项目能够成功发射 OpenLineage 事件到 Marquez，并在 FlowScope 中观察到完整的数据血缘链路。

**适用场景**：
- ETL 任务（Airflow、Dagster、自定义脚本）
- API 服务（FastAPI、Flask、Django）
- 数据处理管道（Spark、Pandas、自定义处理）
- BI 报表和数据查询服务

---

## 一、前置条件检查

### 1.1 环境要求

- [ ] **Docker 和 Docker Compose**：用于运行 Marquez 服务
  ```bash
  docker --version  # 应显示 Docker 版本
  docker-compose --version  # 应显示 Docker Compose 版本
  ```

- [ ] **Python 3.8+**：用于运行 OpenLineage 客户端
  ```bash
  python3 --version  # 应显示 Python 3.8 或更高版本
  ```

- [ ] **网络访问**：确保能够访问 Marquez API（默认 `http://localhost:5002`）

### 1.2 端口可用性检查

确保以下端口未被占用：
- `5002`：Marquez API（容器内 5000，映射到主机 5002）
- `3000`：Marquez Web UI
- `5432`：PostgreSQL（可选，如果使用外部数据库）

```bash
# 检查端口占用（macOS/Linux）
lsof -i :5002
lsof -i :3000
lsof -i :5432

# 如果端口被占用，可以：
# 1. 停止占用端口的服务
# 2. 修改 docker-compose.yml 中的端口映射
```

---

## 二、FlowScope 基础设施部署

### 2.1 获取 FlowScope 配置

如果 FlowScope 已部署，获取以下信息：
- Marquez API URL（例如：`http://localhost:5002` 或 `http://marquez.example.com:5000`）
- 命名空间（Namespace）约定（例如：`your_project_name`）

如果需要在本地部署 FlowScope：

```bash
# 1. 克隆或获取 FlowScope 项目
git clone <flowspec-repo-url>
cd FlowScope

# 2. 启动 Marquez 服务
docker-compose up -d

# 3. 等待服务就绪（约 30-60 秒）
# 验证服务健康状态
curl http://localhost:5002/api/v1/namespaces

# 4. 访问 Marquez UI
# 浏览器打开：http://localhost:3000
```

### 2.2 验证 Marquez 可用性

```bash
# 检查 API 健康状态
curl http://localhost:5002/api/v1/namespaces

# 预期返回 JSON，包含 namespaces 数组
# 示例：{"namespaces": []}
```

---

## 三、项目集成步骤

### 3.1 安装 OpenLineage Python 客户端

在项目根目录或虚拟环境中安装：

```bash
# 方式 1：直接安装
pip install openlineage-python>=1.15.0

# 方式 2：添加到 requirements.txt
echo "openlineage-python>=1.15.0" >> requirements.txt
pip install -r requirements.txt

# 方式 3：使用虚拟环境（推荐）
python3 -m venv venv
source venv/bin/activate  # macOS/Linux
# 或 venv\Scripts\activate  # Windows
pip install openlineage-python>=1.15.0
```

### 3.2 配置环境变量

设置 Marquez API 地址：

```bash
# 方式 1：环境变量（推荐用于开发）
export MARQUEZ_URL=http://localhost:5002

# 方式 2：.env 文件（推荐用于生产）
echo "MARQUEZ_URL=http://localhost:5002" >> .env

# 方式 3：在代码中直接指定（不推荐，但可用于快速测试）
```

### 3.3 在代码中集成 OpenLineage 事件

#### 3.3.1 ETL 任务集成示例

```python
#!/usr/bin/env python3
"""
ETL 任务集成 OpenLineage 的标准模式
"""
import os
import uuid
from datetime import datetime
from openlineage.client import OpenLineageClient
from openlineage.client.run import RunEvent, RunState, Run, Job, Dataset
from openlineage.client.facet import SchemaDatasetFacet, SchemaField


def run_etl_job():
    """示例 ETL 任务，包含 OpenLineage 事件发射"""
    
    # 1. 初始化 OpenLineage 客户端
    marquez_url = os.getenv("MARQUEZ_URL", "http://localhost:5002")
    client = OpenLineageClient(url=marquez_url)
    
    # 2. 定义作业元数据
    namespace = os.getenv("OL_NAMESPACE", "your_project_name")  # 建议使用项目名
    job_name = "your_etl_job_name"  # 作业名称，建议使用有意义的标识
    run_id = str(uuid.uuid4())  # 每次运行生成唯一 ID
    
    job = Job(namespace=namespace, name=job_name)
    run = Run(run_id)
    
    # 3. 定义输入数据集（Schema 可选，但强烈推荐）
    input_schema = SchemaDatasetFacet(
        fields=[
            SchemaField(name="id", type="integer"),
            SchemaField(name="name", type="string"),
            # ... 更多字段
        ]
    )
    
    input_dataset = Dataset(
        namespace="postgresql://localhost:5432",  # 数据源标识
        name="raw.users",  # 数据集名称
        facets={"schema": input_schema}
    )
    
    # 4. 发射 START 事件
    start_event = RunEvent(
        eventType=RunState.START,
        eventTime=datetime.utcnow().isoformat() + "Z",
        run=run,
        job=job,
        inputs=[input_dataset],  # 输入数据集列表
        producer="https://github.com/your-org/your-project"  # 生产者标识
    )
    client.emit(start_event)
    
    # 5. 执行实际的 ETL 逻辑
    try:
        # 你的 ETL 代码在这里
        # read_data()
        # transform_data()
        # write_data()
        pass
        
        # 6. 定义输出数据集
        output_schema = SchemaDatasetFacet(
            fields=[
                SchemaField(name="user_id", type="integer"),
                SchemaField(name="full_name", type="string"),
                # ... 更多字段
            ]
        )
        
        output_dataset = Dataset(
            namespace="postgresql://localhost:5432",
            name="processed.users",
            facets={"schema": output_schema}
        )
        
        # 7. 发射 COMPLETE 事件（成功）
        complete_event = RunEvent(
            eventType=RunState.COMPLETE,
            eventTime=datetime.utcnow().isoformat() + "Z",
            run=run,
            job=job,
            inputs=[input_dataset],
            outputs=[output_dataset],  # 输出数据集列表
            producer="https://github.com/your-org/your-project"
        )
        client.emit(complete_event)
        
    except Exception as e:
        # 8. 发射 FAIL 事件（失败）
        fail_event = RunEvent(
            eventType=RunState.FAIL,
            eventTime=datetime.utcnow().isoformat() + "Z",
            run=run,
            job=job,
            inputs=[input_dataset],
            producer="https://github.com/your-org/your-project"
        )
        client.emit(fail_event)
        raise


if __name__ == "__main__":
    run_etl_job()
```

#### 3.3.2 API 服务集成示例

```python
"""
FastAPI 服务集成 OpenLineage 的标准模式
"""
from fastapi import FastAPI
from openlineage.client import OpenLineageClient
from openlineage.client.run import RunEvent, RunState, Run, Job, Dataset
import os
import uuid
from datetime import datetime

app = FastAPI()

# 全局 OpenLineage 客户端（可选，也可以每次请求创建）
marquez_url = os.getenv("MARQUEZ_URL", "http://localhost:5002")
ol_client = OpenLineageClient(url=marquez_url)


@app.get("/api/user-stats")
async def get_user_stats():
    """API 端点，记录数据使用血缘"""
    
    namespace = os.getenv("OL_NAMESPACE", "your_project_name")
    job_name = "user_stats_api"
    run_id = str(uuid.uuid4())
    
    job = Job(namespace=namespace, name=job_name)
    run = Run(run_id)
    
    # 定义输入数据集（API 消费的数据）
    input_dataset = Dataset(
        namespace="postgresql://localhost:5432",
        name="processed.users"
    )
    
    # 发射 START 事件
    start_event = RunEvent(
        eventType=RunState.START,
        eventTime=datetime.utcnow().isoformat() + "Z",
        run=run,
        job=job,
        inputs=[input_dataset],
        producer="https://github.com/your-org/your-project"
    )
    ol_client.emit(start_event)
    
    try:
        # 执行 API 逻辑
        # result = query_database(input_dataset.name)
        
        # 定义输出数据集（API 响应）
        output_dataset = Dataset(
            namespace="api://localhost:8000",
            name="user_stats"
        )
        
        # 发射 COMPLETE 事件
        complete_event = RunEvent(
            eventType=RunState.COMPLETE,
            eventTime=datetime.utcnow().isoformat() + "Z",
            run=run,
            job=job,
            inputs=[input_dataset],
            outputs=[output_dataset],
            producer="https://github.com/your-org/your-project"
        )
        ol_client.emit(complete_event)
        
        return {"status": "success"}
        
    except Exception as e:
        # 发射 FAIL 事件
        fail_event = RunEvent(
            eventType=RunState.FAIL,
            eventTime=datetime.utcnow().isoformat() + "Z",
            run=run,
            job=job,
            inputs=[input_dataset],
            producer="https://github.com/your-org/your-project"
        )
        ol_client.emit(fail_event)
        raise
```

#### 3.3.3 关键集成要点

1. **命名空间（Namespace）约定**
   - 建议使用项目名称或团队标识
   - 同一项目内的所有作业使用相同命名空间
   - 通过环境变量 `OL_NAMESPACE` 统一管理

2. **作业名称（Job Name）**
   - 使用有意义的标识符，例如：`user_processing_etl`、`daily_sales_report`
   - 避免使用随机字符串或时间戳

3. **数据集命名（Dataset Name）**
   - 使用分层命名：`layer.table_name`（例如：`raw.users`、`processed.users`）
   - 保持与真实数据源一致

4. **运行 ID（Run ID）**
   - 每次执行生成唯一 UUID
   - 用于关联同一作业的多次运行

5. **Schema 定义（可选但推荐）**
   - 提供 Schema 信息有助于数据发现和理解
   - 使用 `SchemaDatasetFacet` 定义字段和类型

---

## 四、验证和测试

### 4.1 运行测试事件

```bash
# 1. 设置环境变量
export MARQUEZ_URL=http://localhost:5002
export OL_NAMESPACE=your_project_name

# 2. 运行你的代码（ETL 或 API）
python your_etl_script.py

# 3. 检查事件是否成功发射
# 查看代码输出，应看到类似：
# ✓ Emitted START event
# ✓ Emitted COMPLETE event
```

### 4.2 在 Marquez UI 中验证

1. **打开 Marquez UI**：http://localhost:3000

2. **搜索作业或数据集**：
   - 在搜索框输入作业名称（例如：`user_processing_etl`）
   - 或输入数据集名称（例如：`raw.users`）

3. **查看血缘图**：
   - 点击作业或数据集
   - 应能看到完整的上下游链路
   - 验证输入输出关系是否正确

4. **验证运行记录**：
   - 在作业详情页查看运行历史
   - 确认每次运行都有对应的 START 和 COMPLETE 事件

### 4.3 使用 FlowScope Sync 同步数据（可选）

如果已部署 FlowScope Sync 服务：

```bash
# 从 Marquez 同步数据到 FlowScope
python scripts/sync_marquez.py

# 预期输出：
# ✅ Sync completed!
# Namespaces: 1
# Jobs: 2
# Datasets: 3
# Runs: 5
# Edges: 4
```

---

## 五、常见问题排查

### 5.1 事件未出现在 Marquez UI

**可能原因**：
1. Marquez API 不可访问
2. 事件格式错误
3. 网络连接问题

**排查步骤**：
```bash
# 1. 检查 Marquez API 健康状态
curl http://localhost:5002/api/v1/namespaces

# 2. 检查 Marquez 日志
docker-compose logs marquez-api

# 3. 验证环境变量
echo $MARQUEZ_URL

# 4. 检查事件发射代码
# 确保 client.emit() 调用成功，没有异常
```

### 5.2 端口冲突

**问题**：端口 5002、3000 或 5432 已被占用

**解决方案**：
1. 修改 `docker-compose.yml` 中的端口映射
2. 或停止占用端口的服务

```yaml
# docker-compose.yml
ports:
  - "5003:5000"  # 改为其他端口，例如 5003
  - "3001:3000"  # 改为其他端口，例如 3001
```

### 5.3 Python 依赖冲突

**问题**：`openlineage-python` 与其他包版本冲突

**解决方案**：
```bash
# 使用虚拟环境隔离依赖
python3 -m venv venv
source venv/bin/activate
pip install openlineage-python>=1.15.0

# 或使用 pip 的依赖解析
pip install --upgrade openlineage-python
```

### 5.4 事件格式错误

**问题**：Marquez API 返回 400 错误

**排查**：
- 检查事件结构是否符合 OpenLineage 规范
- 确保所有必需字段都已提供（`run`、`job`、`eventType`）
- 验证时间格式为 ISO 8601（例如：`2024-01-01T00:00:00Z`）

### 5.5 数据集命名不一致

**问题**：血缘图中断，无法连接上下游

**解决方案**：
- 确保上下游作业使用相同的数据集 `namespace` 和 `name`
- 使用统一的数据集命名规范
- 检查大小写是否一致（建议使用小写）

---

## 六、最佳实践

### 6.1 命名规范

- **命名空间**：使用项目或团队标识（例如：`data_platform`、`analytics_team`）
- **作业名称**：使用动词+名词格式（例如：`process_user_data`、`generate_daily_report`）
- **数据集名称**：使用分层命名（例如：`raw.users`、`ods.orders`、`dws.user_summary`）

### 6.2 事件发射时机

- **START 事件**：在作业开始执行时立即发射
- **COMPLETE 事件**：在作业成功完成后发射，包含所有输入输出
- **FAIL 事件**：在作业失败时发射，至少包含输入信息

### 6.3 错误处理

- 使用 try-except 确保失败时也能发射 FAIL 事件
- 不要因为事件发射失败而中断业务逻辑（考虑异步或后台发送）

### 6.4 性能考虑

- 事件发射应该是轻量级操作，不应影响业务性能
- 考虑使用异步发送或后台队列（生产环境）

### 6.5 Schema 维护

- 当数据集结构变化时，更新 Schema 定义
- 使用版本控制管理 Schema 变更

---

## 七、进阶配置（可选）

### 7.1 使用外部 Marquez 实例

如果使用远程 Marquez 服务：

```bash
export MARQUEZ_URL=http://marquez.example.com:5000
export MARQUEZ_API_KEY=your_api_key  # 如果启用认证
```

### 7.2 集成到 Airflow

如果使用 Airflow，可以使用 OpenLineage Airflow 集成：

```python
# requirements.txt
apache-airflow-providers-openlineage>=1.0.0

# airflow.cfg 或环境变量
OPENLINEAGE_URL=http://localhost:5002
OPENLINEAGE_NAMESPACE=your_project_name
```

### 7.3 集成到 Dagster

Dagster 原生支持 OpenLineage：

```python
# 在 Dagster 配置中启用 OpenLineage
from dagster_openlineage import OpenLineageResource

@resource(config_schema={"marquez_url": str})
def openlineage_resource(context):
    return OpenLineageResource(
        marquez_url=context.resource_config["marquez_url"]
    )
```

---

## 八、验收清单

完成接入后，请确认以下项目：

- [ ] Marquez 服务正常运行
- [ ] 能够成功发射 OpenLineage 事件
- [ ] 在 Marquez UI 中能看到作业和数据集
- [ ] 血缘图显示完整的上下游链路
- [ ] 运行记录正确记录每次执行
- [ ] 事件包含正确的 Schema 信息（如适用）
- [ ] 错误情况下能正确发射 FAIL 事件

---

## 九、获取帮助

- **FlowScope 项目文档**：查看 `README.md` 和 `openspec/` 目录
- **OpenLineage 文档**：https://openlineage.io/docs
- **Marquez 文档**：https://marquezproject.github.io/marquez/
- **问题反馈**：在 FlowScope 项目中提交 Issue

---

## 附录：快速参考

### 环境变量

| 变量名 | 说明 | 默认值 | 必需 |
|--------|------|--------|------|
| `MARQUEZ_URL` | Marquez API 地址 | `http://localhost:5002` | 是 |
| `OL_NAMESPACE` | OpenLineage 命名空间 | 无 | 推荐 |

### 关键端口

| 服务 | 端口 | 说明 |
|------|------|------|
| Marquez API | 5002 | OpenLineage 事件接收 |
| Marquez Web UI | 3000 | 血缘可视化界面 |
| PostgreSQL | 5432 | Marquez 数据存储 |

### 常用命令

```bash
# 启动 Marquez
docker-compose up -d

# 停止 Marquez
docker-compose down

# 查看日志
docker-compose logs -f marquez-api

# 同步数据到 FlowScope
python scripts/sync_marquez.py

# 检查 API 健康
curl http://localhost:5002/api/v1/namespaces
```

---

**文档版本**：v1.0  
**最后更新**：2024-12-15  
**维护者**：FlowScope 团队

