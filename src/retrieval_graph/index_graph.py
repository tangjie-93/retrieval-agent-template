"""索引图 —— 提供文档上传和索引的入口端点。

图流程：__start__ → index_docs
"""

from typing import Sequence

from langchain_core.documents import Document
from langchain_core.runnables import RunnableConfig
from langgraph.graph import StateGraph

from retrieval_graph import retrieval
from retrieval_graph.configuration import IndexConfiguration
from retrieval_graph.state import IndexState


def ensure_docs_have_user_id(
    docs: Sequence[Document], config: RunnableConfig
) -> list[Document]:
    """确保所有文档的 metadata 中都包含 user_id。

    Args:
        docs (Sequence[Document]): 待处理的文档序列。
        config (RunnableConfig): 包含 user_id 的配置对象。

    Returns:
        list[Document]: 带 user_id metadata 的新文档列表。
    """
    # 从配置中获取 user_id
    # 原写法（直接取值，风格不一致，已注释保留）：
    # user_id = config["configurable"]["user_id"]
    # 统一写法（通过配置类解析，有类型推断，与 graph.py 保持一致）：
    user_id = IndexConfiguration.from_runnable_config(config).user_id
    # 为每个文档的 metadata 注入 user_id，实现用户级数据隔离
    return [
        Document(
            page_content=doc.page_content, metadata={**doc.metadata, "user_id": user_id}
        )
        for doc in docs
    ]


async def index_docs(
    state: IndexState, *, config: RunnableConfig | None = None
) -> dict[str, str]:
    """异步索引文档到向量数据库。

    本函数从状态中获取文档，确保文档带有 user_id，
    将其添加到检索器的索引中，然后发出删除信号清空状态中的文档。

    Args:
        state (IndexState): 当前状态，包含待索引文档。
        config (Optional[RunnableConfig]): 索引过程配置。

    Returns:
        dict[str, str]: 返回 {"docs": "delete"}，触发 reduce_docs 清空已索引的文档。
    """
    if not config:
        raise ValueError("Configuration required to run index_docs.")
    # 创建检索器（根据配置自动选择 Elastic/Pinecone/MongoDB）
    async with retrieval.make_retriever(config) as retriever:
        # 为文档注入 user_id metadata
        stamped_docs = ensure_docs_have_user_id(state.docs, config)

        # 将文档写入向量数据库（异步添加文档和向量）
        await retriever.aadd_documents(stamped_docs)
    # 返回 "delete" 信号，reduce_docs 会将 state.docs 清空（表示索引完成）
    return {"docs": "delete"}


# 构建索引图
# IndexState 为状态定义，IndexConfiguration 为上下文配置
builder = StateGraph(IndexState, context_schema=IndexConfiguration)
# 添加唯一节点：index_docs
builder.add_node(index_docs)
# 定义边：__start__ → index_docs
builder.add_edge("__start__", "index_docs")
# 编译图，使其可被调用和部署
graph = builder.compile()
graph.name = "IndexGraph"
