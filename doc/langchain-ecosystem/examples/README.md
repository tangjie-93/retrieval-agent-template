# 可运行 Demo

这些脚本对应上一级目录的 01-08 主题。它们使用 OpenAI ChatGPT：聊天生成由
ChatOpenAI 完成，RAG 示例另外使用 OpenAI Embeddings。

## 一次性准备

在 retrieval-agent-template 目录执行：

~~~powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e .
Copy-Item .env.example .env
~~~

在 .env 中填写：

~~~dotenv
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4o-mini
~~~

然后从项目根目录运行任一脚本，例如：

~~~powershell
python doc\langchain-ecosystem\examples\01_chat_basics.py
~~~

| 脚本 | 对应主题 | 验证内容 |
|---|---|---|
| 01_chat_basics.py | 生态分层 | ChatPromptTemplate -> ChatOpenAI -> StrOutputParser |
| 02_core_chain.py | langchain_core | Message、Runnable、结构化输出 |
| 03_model_calling.py | 模型调用 | invoke、stream、batch、embedding |
| 04_rag_pipeline.py | RAG | 文档、切分、Embedding、内存向量检索、回答 |
| 05_agent_tools.py | Agent | ChatGPT 选择并调用本地工具 |
| 06_langgraph.py | LangGraph | State、Node、Edge 与模型节点 |
| 07_langsmith.py | LangSmith | OpenAI 调用的 trace |
| 08_enterprise_rag.py | 企业 RAG | 权限过滤、引用和无命中兜底 |

07_langsmith.py 还需要在 .env 中配置 LANGSMITH_API_KEY 和
LANGSMITH_TRACING=true。其余脚本只需要 OpenAI 配置。

