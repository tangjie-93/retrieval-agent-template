"""检索图的工具函数。

本模块包含处理消息、文档和项目中其他常用操作的工具函数。

函数：
    get_message_text: 从各种消息格式中提取文本内容。
    format_docs: 将文档列表转换为 XML 格式字符串。
    load_chat_model: 按 provider/model 格式加载聊天模型。
"""

from langchain.chat_models import init_chat_model
from langchain_core.documents import Document
from langchain_core.language_models import BaseChatModel
from langchain_core.messages import AnyMessage


def get_message_text(msg: AnyMessage) -> str:
    """获取消息的文本内容。

    本函数从各种消息格式中提取文本内容，支持字符串、字典和列表格式。

    Args:
        msg (AnyMessage): 要提取文本的消息对象。

    Returns:
        str: 消息中提取的文本内容。

    Examples:
        >>> from langchain_core.messages import HumanMessage
        >>> get_message_text(HumanMessage(content="Hello"))
        'Hello'
        >>> get_message_text(HumanMessage(content={"text": "World"}))
        'World'
        >>> get_message_text(HumanMessage(content=[{"text": "Hello"}, " ", {"text": "World"}]))
        'Hello World'
    """
    content = msg.content
    if isinstance(content, str):
        # 纯文本消息：直接返回
        return content
    elif isinstance(content, dict):
        # 字典格式消息：提取 "text" 字段
        return content.get("text", "")
    else:
        # 列表格式消息（多模态）：逐项提取文本并拼接
        txts = [c if isinstance(c, str) else (c.get("text") or "") for c in content]
        return "".join(txts).strip()


def _format_doc(doc: Document) -> str:
    """将单个文档格式化为 XML。

    Args:
        doc (Document): 要格式化的文档。

    Returns:
        str: 格式化为 XML 字符串的文档。
    """
    metadata = doc.metadata or {}
    # 将 metadata 的键值对拼接为 XML 属性
    meta = "".join(f" {k}={v!r}" for k, v in metadata.items())
    if meta:
        meta = f" {meta}"

    return f"<document{meta}>\n{doc.page_content}\n</document>"


def format_docs(docs: list[Document] | None) -> str:
    """将文档列表格式化为 XML。

    本函数将 Document 对象列表格式化为单个 XML 字符串，
    用于注入到 LLM 的系统提示词中。

    Args:
        docs (Optional[list[Document]]): 要格式化的文档列表，或 None。

    Returns:
        str: 包含格式化文档的 XML 字符串。

    Examples:
        >>> docs = [Document(page_content="Hello"), Document(page_content="World")]
        >>> print(format_docs(docs))
        <documents>
        <document>
        Hello
        </document>
        <document>
        World
        </document>
        </documents>

        >>> print(format_docs(None))
        <documents></documents>
    """
    if not docs:
        # 空列表或 None：返回空 XML 标签
        return "<documents></documents>"
    # 逐个格式化文档并拼接
    formatted = "\n".join(_format_doc(doc) for doc in docs)
    return f"""<documents>
{formatted}
</documents>"""


def load_chat_model(fully_specified_name: str) -> BaseChatModel:
    """从完整名称加载聊天模型。

    Args:
        fully_specified_name (str): 格式为 'provider/model' 的模型名称
            （如 'anthropic/claude-3-5-sonnet-20240620'）。

    Returns:
        BaseChatModel: 初始化的聊天模型实例。
    """
    if "/" in fully_specified_name:
        # 解析 provider 和 model 名称
        provider, model = fully_specified_name.split("/", maxsplit=1)
    else:
        # 无 provider 前缀：使用默认 provider
        provider = ""
        model = fully_specified_name
    # 调用 langchain 的 init_chat_model 统一加载
    return init_chat_model(model, model_provider=provider)
