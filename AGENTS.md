<!-- OPENSPEC:START -->
# OpenSpec Instructions

These instructions are for AI assistants working in this project.

Always open `@/openspec/AGENTS.md` when the request:
- Mentions planning or proposals (words like proposal, spec, change, plan)
- Introduces new capabilities, breaking changes, architecture shifts, or big performance/security work
- Sounds ambiguous and you need the authoritative spec before coding

Use `@/openspec/AGENTS.md` to learn:
- How to create and apply change proposals
- Spec format and conventions
- Project structure and guidelines

Keep this managed block so 'openspec update' can refresh the instructions.

<!-- OPENSPEC:END -->

FlowScope 项目计划方案（用于 Cursor / Trae 启动执行）

⸻

一、项目背景（Why now）

在 AI 与数据密集型系统快速演进的背景下，现代后端与数据系统呈现出以下共性问题：
	•	数据资产膨胀但价值密度下降：表、字段、ETL job 数量快速增长，但真正被业务/决策使用的数据链路并不清晰。
	•	数据流路径不可视：从 raw data → ETL → 中间层 → BI / API / 模型 的真实路径，往往只存在于工程师的脑中或零散 SQL 中。
	•	重构与治理成本高：缺乏“影响面感知”，导致 schema 调整、表合并、字段删除高度依赖经验与保守判断。
	•	现有工具的结构性错位：
	•	编排工具（Airflow/Dagster）关注 执行，不关注 理解；
	•	元数据平台（DataHub/OpenMetadata）偏平台化、治理化，对个人/小团队过重；
	•	静态流程图无法反映真实运行与业务使用情况。

因此，需要一个 以“真实运行数据流”为核心、以“辅助架构判断”为目标、以“本地轻量”为前提 的新型数据流观察与分析工具。

⸻

二、项目目标（What success looks like）

2.1 核心目标（不可妥协）

FlowScope 的成功标准不是“画出一张漂亮的 DAG 图”，而是：

在本地，通过一个可视化界面，工程师可以基于事实数据，做出关于数据架构的判断与行动决策。

2.2 可验证的目标陈述

系统必须能够回答以下问题：
	1.	溯源能力：
	•	任意一个 BI 表 / API / 决策指标，可以一键回溯到所有 raw 数据来源，并展示完整路径。
	2.	复杂度感知：
	•	数据链路的“长、绕、重”可以被量化（路径长度、节点数、fan-in/out）。
	3.	冗余识别：
	•	系统能识别并标记：孤儿表、重复中间表、长期未使用数据集。
	4.	业务视角引入：
	•	能区分“存在但没人用”的数据，与“高频业务依赖”的关键链路。
	5.	本地可用性：
	•	可在个人开发机本地运行，资源占用可控，不依赖云平台。

⸻

三、总体方案概览（High-level Design）

3.1 核心设计思想
	•	事实层与判断层分离：
	•	事实层（What happened）：由 OpenLineage + Marquez 提供。
	•	判断层（What it means / What to do）：由 FlowScope 增强层提供。
	•	旁路式观测，不接管执行：
	•	FlowScope 不负责任务调度、不替代 ETL，只观察真实运行结果。

3.2 总体架构

[ETL / API / 模型 / BI]
        |
        | OpenLineage Events
        v
[Marquez: 血缘事实层]
        |
        | Sync / Enrich
        v
[FlowScope 增强层]
        |
        v
[FlowScope UI / API]


⸻

四、系统拆解与职责边界（Analysis）

4.1 OpenLineage（标准层）

职责：
	•	定义数据流事件的统一语义模型（Job / Dataset / Run / Input / Output）。
	•	在关键数据流节点发射事件。

原则：
	•	不做分析、不做判断，只记录事实。

⸻

4.2 Marquez（事实存储 + 基础可视化）

职责：
	•	接收 OpenLineage 事件。
	•	存储血缘、运行记录。
	•	提供基础 lineage DAG UI。

使用策略：
	•	作为“血缘事实数据库”和调试工具。
	•	不在此层实现任何业务或架构判断逻辑。

⸻

4.3 FlowScope 增强层（核心价值所在）

FlowScope 是一个 以分析与决策支持为目标的数据流理解引擎。

模块 1：FlowScope Sync
	•	从 Marquez 同步 Job / Dataset / Run / Edge 数据。
	•	补充工程与业务语义：
	•	layer（raw / ods / dwd / dws / app / bi）
	•	system / domain / owner
	•	活跃度、重要度、业务使用情况

模块 2：路径分析引擎
	•	DAG 路径枚举与裁剪
	•	路径复杂度评分（hop、fan-in/out、transform 密度）
	•	主干路径识别（基于运行频率、数据量、业务使用）

模块 3：冗余与风险检测
	•	孤儿 Dataset 检测
	•	重复中间表候选识别
	•	路径过长 / 过复杂预警

模块 4：业务使用回流
	•	API / BI 查询轻量打点
	•	标记真实业务触达的数据链路
	•	用于区分“活数据”与“死数据”

⸻

五、技术栈建议（Tech Stack）

5.1 基础设施
	•	OpenLineage（事件标准）
	•	Marquez（Docker Compose 本地部署）

5.2 FlowScope 后端
	•	语言：Python
	•	Web 框架：FastAPI
	•	ORM：SQLAlchemy / SQLModel
	•	数据库：PostgreSQL（或 SQLite for local-only）
	•	图分析：Python（NetworkX 或自定义 DAG 算法）

5.3 前端（阶段性）
	•	初期：直接复用 Marquez UI
	•	后期（可选）：
	•	React + D3 / Cytoscape
	•	专注“路径高亮 + 风险提示”，而非全功能血缘平台

⸻

六、阶段性实施方案（Execution Plan）

Phase 0：最小可运行系统（MVP）

目标：看到一条真实数据链路的动态血缘。
	•	本地启动 Marquez
	•	在 1–2 个真实 ETL / API 中发射 OpenLineage 事件
	•	确认 lineage 在 UI 中可见

验收标准：
	•	能在 UI 中看到 job → dataset → job 的完整链路

⸻

Phase 1：FlowScope v0（分析起点）

目标：开始“理解”而非“展示”数据流。
	•	实现 FlowScope Sync
	•	建立 fs_dataset / fs_job / fs_edge / fs_run 表
	•	实现 upstream / downstream 路径查询 API

验收标准：
	•	给定一个 BI 表，能输出所有 raw → BI 路径列表

⸻

Phase 2：复杂度与冗余检测

目标：支持架构判断与重构决策。
	•	路径复杂度评分
	•	孤儿 Dataset 标记
	•	重复中间表候选识别

验收标准：
	•	系统能给出“可删除 / 可合并”的候选清单（即使需人工确认）

⸻

Phase 3：业务视角增强（可选）

目标：引入“真实价值流”。
	•	API / BI 使用打点
	•	lineage 图中高亮业务高频链路

验收标准：
	•	能清晰区分“存在但无人用”的数据链路与核心主干

⸻

七、风险与边界（Explicit Non-Goals）
	•	不做任务调度与编排（不替代 Airflow/Dagster）
	•	不追求企业级治理功能（权限、审批、血缘审计）
	•	不追求全自动 schema 级别语义理解（允许人工标注 layer / domain）

⸻

八、最终交付物定义（For Cursor / Trae）

该项目交付物不是“一个想法”，而是一套：
	1.	可运行的本地系统（Docker / Python）
	2.	明确的数据模型与模块边界
	3.	可扩展的分析能力（路径、冗余、使用度）
	4.	支持长期演进的个人数据基础设施内核

FlowScope 的本质不是一个工具，而是一个“让你敢对数据架构下判断”的系统。

