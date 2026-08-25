# LangChain 单概念示例设计

## 目标

补齐 `doc/langchain-ecosystem/01-08` 与 `examples` 之间的示例覆盖缺口，让学习者既能按单个概念运行最小示例，也能继续使用现有的章节综合示例。

## 范围

- 保留 `examples/01_chat_basics.py` 至 `examples/08_enterprise_rag.py`，作为章节综合入口。
- 新增按 `章节目录/概念.py` 组织的单概念脚本。
- 更新 `examples/README.md`，提供概念、脚本、运行条件和副作用索引。
- 更新 `01-08` 文档的可运行示例部分，使文档能链接到对应脚本。
- `09-learning-path.md` 和 `10-self-check.md` 继续复用 `01-08` 的示例，不新增独立脚本。
- 为新增和改动的示例添加中文模块说明、函数说明与关键步骤注释。

## 文件组织

综合脚本保留在 `doc/langchain-ecosystem/examples/` 根目录；单概念脚本进入 `01_ecosystem` 至 `08_enterprise` 八个章节目录。根级 `common.py` 供综合示例使用，`03_models/common.py` 让联网单概念脚本可以从项目根目录直接运行。

### `01` 生态分层

- 生态各层如何通过 `Prompt -> Model -> OutputParser` 协作。
- 保持内容精简，避免复制后续章节的详细示例。

### `02` LangChain Core

- `Message`
- `PromptTemplate` 与 `ChatPromptTemplate`
- `Runnable` 的 `invoke`、`stream`、`batch` 与组合
- `Tool` 名称、说明、参数 Schema 和调用
- `OutputParser` 的字符串、JSON、Pydantic 解析与失败处理

### `03` 模型调用

- `Chat Model` 的同步调用与返回消息
- 流式与批量调用
- `Embedding Model` 的文档和查询向量
- 模型参数与按任务选择模型的策略

### `04` RAG 链路

- `Document` 正文与 Metadata
- 文本文件和 Markdown `Loader`
- `Text Splitter`
- `Embedding` 与内存向量库
- `Retriever`、`top_k` 与 Metadata 过滤
- Context 拼接、去重和引用标签
- 完整 RAG 链路

### `05` Agent 与工具

- Tool 定义、参数与异常返回
- 工具描述和 Schema
- 模型选择工具并消费工具结果
- 带查询改写、检索充分性判断和最大步骤限制的 `Agentic RAG`

### `06` LangGraph

- `State`、`Node`、`Edge`
- `Conditional Edge`
- 带明确结束条件的循环
- `Checkpointer` 与线程隔离
- `Human-in-the-loop` 的中断和恢复
- 企业 RAG 图的多节点串联

### `07` LangSmith

- `Trace`
- `Dataset`
- `Evaluation`
- `Feedback`
- 延迟、错误率、Token 和成本等监控指标

会创建远端 `Dataset` 或 `Feedback` 的脚本默认只展示待写入内容；只有传入明确的写入参数后才调用 LangSmith，避免无意创建远端数据。

### `08` 企业 RAG 工程化

- 检索前权限过滤
- 文档版本、Chunk ID、增量更新与旧 Chunk 删除
- 引用与溯源
- 成本和延迟采集
- 检索为空、权限不足、模型超时、工具异常和解析失败兜底

## 运行规则

- 纯数据结构、Prompt、Runnable、切分、状态图和工程规则示例默认离线运行。
- 需要生成或 Embedding 的脚本使用 `common.py` 读取 `OPENAI_API_KEY`、`OPENAI_MODEL` 和 `OPENAI_BASE_URL`。
- 缺少必要环境变量时抛出包含修复方法的错误，不输出密钥内容。
- 在线脚本每次只发起完成概念演示所需的最少调用。
- 每个脚本提供 `main()` 和 `if __name__ == "__main__"` 入口。

## 注释规范

- 文件顶部使用中文 Docstring 说明学习目标、是否联网和预期输出。
- 公共函数使用中文 Docstring 说明输入、输出和失败条件。
- 只在关键数据转换、API 边界和容易误解的地方写中文注释。
- 不使用逐行复述代码的注释。

## 文档更新

`examples/README.md` 增加完整索引，并按以下运行条件标记脚本：

- `离线`
- `需要 OpenAI`
- `需要 LangSmith`
- `显式写入远端`

每篇专题文档的“可运行 Demo”部分列出对应的单概念脚本，并保留原综合脚本命令。

## 验证

1. 对全部示例执行 Python 语法编译。
2. 运行所有标记为离线的脚本并检查退出码。
3. 在不调用付费 API 的条件下导入在线脚本。
4. 检查 `examples/README.md` 和 `01-08` 文档引用的脚本全部存在。
5. 运行 `git diff --check`，确认没有空白字符错误。
6. 检查新增 Python 文件包含中文说明或关键注释。

## 兼容性与非目标

- 不删除或重命名现有 `01-08` 综合脚本。
- 不修改生产 RAG Agent 的业务实现。
- 不自动调用会产生远端写入的 LangSmith API。
- 不把真实 API Key、用户数据或敏感文档写入示例。
