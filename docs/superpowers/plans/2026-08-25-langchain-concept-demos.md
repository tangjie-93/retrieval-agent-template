# LangChain Concept Demos Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use `superpowers:executing-plans` to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 为 `doc/langchain-ecosystem/01-08` 中适合运行的核心概念补齐独立 Python 示例、中文注释和文档索引。

**Architecture:** 保留现有章节综合脚本，在同一 `examples` 目录新增按章节和概念编号的平级脚本。离线示例使用本地数据和 LangChain/LangGraph 基础对象，在线示例统一通过 `common.py` 读取 OpenAI 与 LangSmith 配置，并避免默认产生远端写入。

**Tech Stack:** Python `3.11+`、LangChain、LangGraph、LangSmith、Pydantic、OpenAI 兼容 API。

---

### Task 1: 建立覆盖检查

**Files:**
- Create: `tests/test_langchain_ecosystem_examples.py`

- [ ] 定义预期示例文件清单，并断言每个文件存在、可通过 `ast.parse()`、包含中文字符、包含 `main()` 入口。
- [ ] 扫描 `examples/README.md` 与 `01-08` 文档中的 `.py` 引用，断言目标文件存在。
- [ ] 运行 `uv run pytest tests/test_langchain_ecosystem_examples.py -q`，确认新增脚本前覆盖检查失败。

### Task 2: 补齐公共配置与 Core/模型示例

**Files:**
- Modify: `doc/langchain-ecosystem/examples/common.py`
- Create: `doc/langchain-ecosystem/examples/01_ecosystem/ecosystem_layers.py`
- Create: `doc/langchain-ecosystem/examples/02_core/messages.py`
- Create: `doc/langchain-ecosystem/examples/02_core/prompts.py`
- Create: `doc/langchain-ecosystem/examples/02_core/runnables.py`
- Create: `doc/langchain-ecosystem/examples/02_core/tools.py`
- Create: `doc/langchain-ecosystem/examples/02_core/output_parsers.py`
- Create: `doc/langchain-ecosystem/examples/03_models/chat_model.py`
- Create: `doc/langchain-ecosystem/examples/03_models/stream_and_batch.py`
- Create: `doc/langchain-ecosystem/examples/03_models/embeddings.py`
- Create: `doc/langchain-ecosystem/examples/03_models/model_selection.py`

- [ ] 在 `common.py` 增加统一的 Embedding 配置函数，继续支持 `OPENAI_BASE_URL`，且不记录密钥。
- [ ] 每个脚本只演示文件名对应的一个概念，提供中文 Docstring、关键注释和 `main()`。
- [ ] 对离线脚本执行真实运行，对在线脚本执行语法与导入检查。

### Task 3: 补齐 RAG 示例

**Files:**
- Create: `doc/langchain-ecosystem/examples/04_rag/documents.py`
- Create: `doc/langchain-ecosystem/examples/04_rag/loaders.py`
- Create: `doc/langchain-ecosystem/examples/04_rag/text_splitters.py`
- Create: `doc/langchain-ecosystem/examples/04_rag/vector_store.py`
- Create: `doc/langchain-ecosystem/examples/04_rag/retrievers.py`
- Create: `doc/langchain-ecosystem/examples/04_rag/context_building.py`

- [ ] 用临时文件演示 Loader，避免依赖仓库外数据。
- [ ] 使用可确定的本地 Embedding 演示向量库与 Retriever，保证离线可复现。
- [ ] Context 示例保留来源、章节、Chunk ID，并展示去重。
- [ ] 运行全部 `04_01` 至 `04_06` 离线脚本。

### Task 4: 补齐 Agent 与 LangGraph 示例

**Files:**
- Create: `doc/langchain-ecosystem/examples/05_agents/tool_definition.py`
- Create: `doc/langchain-ecosystem/examples/05_agents/tool_schema.py`
- Create: `doc/langchain-ecosystem/examples/05_agents/agent_loop.py`
- Create: `doc/langchain-ecosystem/examples/05_agents/agentic_rag.py`
- Create: `doc/langchain-ecosystem/examples/06_langgraph/state_node_edge.py`
- Create: `doc/langchain-ecosystem/examples/06_langgraph/conditional_edges.py`
- Create: `doc/langchain-ecosystem/examples/06_langgraph/bounded_loop.py`
- Create: `doc/langchain-ecosystem/examples/06_langgraph/checkpointer.py`
- Create: `doc/langchain-ecosystem/examples/06_langgraph/human_in_the_loop.py`
- Create: `doc/langchain-ecosystem/examples/06_langgraph/enterprise_rag_graph.py`

- [ ] Agent 示例展示工具成功、工具失败、最大步骤和中间记录。
- [ ] LangGraph 示例分别覆盖基础边、条件边、有限循环、线程隔离、中断恢复和企业 RAG 多节点图。
- [ ] 运行所有默认离线脚本，确认每个图能到达结束状态。

### Task 5: 补齐 LangSmith 与企业工程示例

**Files:**
- Create: `doc/langchain-ecosystem/examples/07_langsmith/trace.py`
- Create: `doc/langchain-ecosystem/examples/07_langsmith/dataset.py`
- Create: `doc/langchain-ecosystem/examples/07_langsmith/evaluation.py`
- Create: `doc/langchain-ecosystem/examples/07_langsmith/feedback.py`
- Create: `doc/langchain-ecosystem/examples/07_langsmith/monitoring_metrics.py`
- Create: `doc/langchain-ecosystem/examples/08_enterprise/access_control.py`
- Create: `doc/langchain-ecosystem/examples/08_enterprise/knowledge_updates.py`
- Create: `doc/langchain-ecosystem/examples/08_enterprise/citations.py`
- Create: `doc/langchain-ecosystem/examples/08_enterprise/cost_and_latency.py`
- Create: `doc/langchain-ecosystem/examples/08_enterprise/fallbacks.py`

- [ ] Dataset 与 Feedback 示例默认打印预览，只有 `--write` 才调用远端 API。
- [ ] Evaluation 和监控示例使用本地样本与确定性指标，默认离线执行。
- [ ] 企业示例分别展示权限前置、版本更新、引用映射、指标采集和分类兜底。

### Task 6: 更新综合示例与文档索引

**Files:**
- Modify: `doc/langchain-ecosystem/examples/01_chat_basics.py` through `08_enterprise_rag.py`
- Modify: `doc/langchain-ecosystem/examples/README.md`
- Modify: `doc/langchain-ecosystem/01-ecosystem-layers.md` through `08-enterprise-rag-engineering.md`

- [ ] 为综合脚本补中文模块说明和关键步骤注释，不改变现有入口。
- [ ] 在 README 中按章节列出脚本、概念、联网要求和远端副作用。
- [ ] 在每篇专题文档中保留综合命令并链接单概念脚本。
- [ ] 运行文档引用检查，确认所有脚本路径存在。

### Task 7: 完整验证

**Files:**
- Test: `tests/test_langchain_ecosystem_examples.py`

- [ ] 运行 `uv run pytest tests/test_langchain_ecosystem_examples.py -q`，预期全部通过。
- [ ] 运行项目现有测试，记录通过、失败或环境阻塞情况。
- [ ] 对全部示例运行 `python -m compileall doc/langchain-ecosystem/examples`。
- [ ] 运行 `git diff --check`。
- [ ] 查看 `git status --short` 和相关 diff，确认没有覆盖用户既有改动。
