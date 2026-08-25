"""对话式检索图的主入口。

本模块定义了对话式检索图的核心结构和功能，包括主图定义、
状态管理，以及处理用户输入、生成查询、检索相关文档和生成回答的关键函数。

图流程：__start__ → generate_query → retrieve → respond
"""

from datetime import datetime, timezone
from typing import cast

from langchain_core.documents import Document
from langchain_core.messages import BaseMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableConfig
from langgraph.graph import StateGraph
from pydantic import BaseModel

from retrieval_graph import retrieval
from retrieval_graph.configuration import Configuration
from retrieval_graph.state import InputState, State
from retrieval_graph.utils import format_docs, get_message_text, load_chat_model


class SearchQuery(BaseModel):
    """用于结构化输出的搜索查询模型，约束 LLM 输出格式。"""

    query: str


async def generate_query(
    # * 强制 config 为关键字参数（keyword-only），LangGraph 约定写法
    state: State, *, config: RunnableConfig
) -> dict[str, list[str]]:
    """根据当前状态和配置生成搜索查询。

    本函数分析状态中的消息并生成合适的搜索查询。
    - 第一条消息：直接使用用户输入作为查询。
    - 后续消息：使用语言模型生成精炼的查询。

    Args:
        state (State): 当前状态，包含消息和其他信息。
        config (RunnableConfig): 查询生成过程的配置。

    Returns:
        dict[str, list[str]]: 包含 'queries' 键的字典，值为生成的查询列表。
    """
    messages = state.messages
    if len(messages) == 1:
        # ── 步骤1（首条消息）：直接使用用户原始输入作为查询 ──
        human_input = get_message_text(messages[-1])
        return {"queries": [human_input]}
    else:
        # ── 步骤1（后续对话）：从 config 解析配置 ──
        configuration = Configuration.from_runnable_config(config)

        # ── 步骤2：构建提示词模板（系统提示 + 消息历史占位符）──
        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", configuration.query_system_prompt),
                ("placeholder", "{messages}"),
            ]
        )

        # ── 步骤3：加载查询模型，并绑定结构化输出（强制 LLM 返回 SearchQuery 格式）──
        model = load_chat_model(configuration.query_model).with_structured_output(
            SearchQuery
        )

        # ── 步骤4：填充模板变量（消息历史、历史查询、系统时间）──
        message_value = await prompt.ainvoke(
            {
                "messages": state.messages,
                "queries": "\n- ".join(state.queries),
                "system_time": datetime.now(tz=timezone.utc).isoformat(),
            },
            config,
        )

        # ── 步骤5：调用 LLM 生成结构化查询，cast 告诉 mypy 返回类型是 SearchQuery ──
        generated = cast(SearchQuery, await model.ainvoke(message_value, config))
        return {
            "queries": [generated.query],
        }


async def retrieve(
    state: State, *, config: RunnableConfig
) -> dict[str, list[Document]]:
    """根据状态中最新的查询检索文档。

    本函数接收当前状态和配置，使用最新查询从向量库检索相关文档。

    Args:
        state (State): 当前状态，包含查询列表。
        config (RunnableConfig): 检索过程配置。

    Returns:
        dict[str, list[Document]]: 包含 "retrieved_docs" 键的字典，值为检索到的文档列表。
    """
    # 创建检索器（根据配置自动选择 Elastic/Pinecone/MongoDB）
    # with 上下文管理器：确保检索器使用完毕后自动关闭向量库连接，防止资源泄漏
    async with retrieval.make_retriever(config) as retriever:
        # 使用最新一条查询执行向量检索（异步调用）
        response = await retriever.ainvoke(state.queries[-1], config)
        return {"retrieved_docs": response}


async def respond(
    state: State, *, config: RunnableConfig
) -> dict[str, list[BaseMessage]]:
    """调用 LLM 生成最终回答。"""
    # ── 步骤1：从 config 解析配置（响应模型、系统提示词等）──
    configuration = Configuration.from_runnable_config(config)

    # ── 步骤2：构建提示词模板（系统提示 + 消息历史占位符）──
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", configuration.response_system_prompt),
            ("placeholder", "{messages}"),
        ]
    )

    # ── 步骤3：加载响应生成模型 ──
    model = load_chat_model(configuration.response_model)

    # ── 步骤4：将检索到的文档格式化为 XML 字符串 ──
    retrieved_docs = format_docs(state.retrieved_docs)

    # ── 步骤5：填充模板变量（消息历史、检索文档、系统时间）──
    message_value = await prompt.ainvoke(
        {
            "messages": state.messages,
            "retrieved_docs": retrieved_docs,
            "system_time": datetime.now(tz=timezone.utc).isoformat(),
        },
        config,
    )

    # ── 步骤6：调用 LLM 生成最终回答 ──
    response = await model.ainvoke(message_value, config)

    # ── 步骤7：返回消息列表，会被追加到状态中的 messages（由 add_messages reducer 处理）──
    return {"messages": [response]}


# 构建检索对话图
# State 为内部完整状态，InputState 为对外输入接口，Configuration 为上下文配置
builder = StateGraph(State, input_schema=InputState, context_schema=Configuration)

# 添加三个节点
builder.add_node(generate_query)  # 节点1：生成搜索查询
builder.add_node(retrieve)  # 节点2：检索文档
builder.add_node(respond)  # 节点3：生成回答

# 定义边：线性流程 __start__ → generate_query → retrieve → respond
builder.add_edge("__start__", "generate_query")
builder.add_edge("generate_query", "retrieve")
builder.add_edge("retrieve", "respond")

# 编译图，使其可被调用和部署
# interrupt_before/after 为空表示不在任何节点前后中断
graph = builder.compile(
    interrupt_before=[],  # 如需在调用工具前更新状态，可在此指定节点名
    interrupt_after=[],
)
graph.name = "RetrievalGraph"
