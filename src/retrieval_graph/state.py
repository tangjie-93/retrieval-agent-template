"""检索图的状态管理。

本模块定义了检索图中使用的状态结构和 reducer（归约）函数，
包括文档索引、检索和对话管理的状态定义。

类：
    IndexState: 文档索引操作的状态。
    InputState: 对话检索图的对外输入接口（State 的子集）。
    State: 对话检索图的完整内部状态。

函数：
    reduce_docs: 处理并将文档输入归约为 Document 序列。
    add_queries: 将新查询累加到已有查询列表。
"""

import uuid
from dataclasses import dataclass, field
from typing import Annotated, Any, Literal, Sequence, Union

from langchain_core.documents import Document
from langchain_core.messages import AnyMessage
from langgraph.graph import add_messages

############################  文档索引状态  #############################


def reduce_docs(
    existing: Sequence[Document] | None,
    new: Union[
        Sequence[Document],
        Sequence[dict[str, Any]],
        Sequence[str],
        str,
        Literal["delete"],
    ],
) -> Sequence[Document]:
    """根据输入类型处理并归约文档。

    本函数处理多种输入类型，将其转换为 Document 对象序列。
    可以删除已有文档、从字符串或字典创建新文档，或返回已有文档。

    Args:
        existing (Optional[Sequence[Document]]): 状态中已有的文档（如有）。
        new: 新输入，可以是 Document 序列、字典序列、字符串序列、
            单个字符串，或字面量 "delete"。
    """
    if new == "delete":
        # "delete" 信号：清空文档（用于索引完成后清理状态）
        return []
    if isinstance(new, str):
        # 单个字符串：包装为带随机 id 的 Document
        return [Document(page_content=new, metadata={"id": str(uuid.uuid4())})]
    if isinstance(new, list):
        # 列表：逐项转换为 Document
        coerced = []
        for item in new:
            if isinstance(item, str):
                # 字符串项：创建带随机 id 的 Document
                coerced.append(
                    Document(page_content=item, metadata={"id": str(uuid.uuid4())})
                )
            elif isinstance(item, dict):
                # 字典项：解包为 Document（需包含 page_content 等字段）
                coerced.append(Document(**item))
            else:
                # 已是 Document 对象：直接使用
                coerced.append(item)
        return coerced
    # 无新输入：返回已有文档或空列表
    return existing or []


# 索引图状态：定义单节点索引图的简单输入输出
@dataclass(kw_only=True)
class IndexState:
    """文档索引和检索操作的状态。

    本类定义了索引状态的结构，包含待索引的文档。
    """

    # 待索引的文档列表，使用 reduce_docs reducer 处理更新
    docs: Annotated[Sequence[Document], reduce_docs]
    """Agent 可索引的文档列表。"""


#############################  Agent 状态  ###################################


# InputState 是 State 的受限版本，用于定义对外部（用户）的窄接口，
# 只暴露消息输入，而内部状态 State 维护更多信息。
@dataclass(kw_only=True)
class InputState:
    """Agent 的输入状态。

    本类定义了输入状态的结构，包含用户和 Agent 之间交换的消息。
    它是完整 State 的受限版本，对外部提供比内部维护更窄的接口。
    """

    # 消息列表：追踪 Agent 的主要执行状态
    # 使用 add_messages reducer：按 ID 合并消息，默认追加，相同 ID 则替换
    messages: Annotated[Sequence[AnyMessage], add_messages]
    """消息追踪 Agent 的主要执行状态。

    通常累积 Human/AI/Human/AI 消息模式；如果
    将此模板与工具调用 ReAct 模式结合，可能如下：

    1. HumanMessage - 用户输入
    2. AIMessage with .tool_calls - Agent 选择工具收集信息
    3. ToolMessage(s) - 执行工具的响应（或错误）

        (... 重复步骤 2 和 3 ...)
    4. AIMessage without .tool_calls - Agent 以非结构化格式回应用户

    5. HumanMessage - 用户下一轮对话

        (... 重复步骤 2-5 ...)

    合并两个消息列表，按 ID 更新已有消息。

    默认确保状态"只追加"，除非新消息与已有消息有相同 ID。

    Returns:
        一个新消息列表，`right` 中的消息合并到 `left` 中。
        如果 `right` 中的消息与 `left` 中的消息有相同 ID，
        则 `right` 中的消息替换 `left` 中的消息。"""


# 这是 Agent 的主状态，可存储任意信息


def add_queries(existing: Sequence[str], new: Sequence[str]) -> Sequence[str]:
    """将已有查询与新查询合并（累加）。

    Args:
        existing (Sequence[str]): 状态中当前的查询列表。
        new (Sequence[str]): 要添加的新查询。

    Returns:
        Sequence[str]: 包含所有查询的新列表。
    """
    return list(existing) + list(new)


@dataclass(kw_only=True)
class State(InputState):
    """图 / Agent 的主状态。"""

    # 生成的搜索查询列表，使用 add_queries reducer（累加）
    queries: Annotated[list[str], add_queries] = field(default_factory=list)
    """Agent 生成的搜索查询列表。"""

    # 检索到的文档列表，由 retrieve 节点填充
    retrieved_docs: list[Document] = field(default_factory=list)
    """由检索器填充，Agent 可引用的文档列表。"""

    # 可根据需要添加额外状态属性
    # 常见示例包括：检索到的文档、提取的实体、API 连接等
