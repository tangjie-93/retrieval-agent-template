"""定义 Agent 的可配置参数。"""

from __future__ import annotations

from dataclasses import dataclass, field, fields
from typing import Annotated, Any, Literal, Type, TypeVar

from langchain_core.runnables import RunnableConfig, ensure_config

from retrieval_graph import prompts
'''
  @dataclass(kw_only=True) 是“这个类里所有字段都只能关键字传参”。                                                                                                                                                                             
  field(kw_only=True) 是“某一个字段只能关键字传参”。  
  from dataclasses import dataclass, field                                                                               
                                                                                                                         
  @dataclass                                                                                                             
  class A:                                                                                                               
      x: int                                                                                                             
      y: int = field(kw_only=True)                                                                                       
                                                                                                                         
  创建时：                                                                                                               
                                                                                                                         
  A(1, y=2)   # 可以                                                                                                     
  A(1, 2)     # 不行                                                                                                     
                                                                                                                     
  而如果是：                                                                                                                                                                                                                                  
  @dataclass(kw_only=True)                                                                                               
  class B:                                                                                                               
      x: int                                                                                                             
      y: int                                                                                                             
                                                                                                                         
  那就必须这样：                                                                                                                                                                                                                               
  B(x=1, y=2)                                                                                                                                                                                                                              
  不能写成位置参数。
'''

@dataclass(kw_only=True)
class IndexConfiguration:
    """索引和检索操作的配置类。

    本类定义了配置索引和检索流程所需的参数，
    包括用户标识、Embedding 模型选择、检索提供商选择和搜索参数。
    """

    # 用户唯一标识，用于数据隔离，确保不同用户只能访问自己的文档
    user_id: str = field(metadata={"description": "Unique identifier for the user."})

    # Embedding 模型名称，格式为 provider/model-name（如 openai/text-embedding-3-small）
    embedding_model: Annotated[
        str,
        {"__template_metadata__": {"kind": "embeddings"}},
    ] = field(
        default="openai/text-embedding-3-small",
        metadata={
            "description": "Name of the embedding model to use. Must be a valid embedding model name."
        },
    )

    # 向量库提供商，可选值：elastic / elastic-local / pinecone / mongodb
    retriever_provider: Annotated[
        Literal["elastic", "elastic-local", "pinecone", "mongodb"],
        {"__template_metadata__": {"kind": "retriever"}},
    ] = field(
        default="elastic",
        metadata={
            "description": "The vector store provider to use for retrieval. Options are 'elastic', 'pinecone', or 'mongodb'."
        },
    )

    # 传递给检索器 search 方法的额外参数（如 top_k、相似度阈值等）
    search_kwargs: dict[str, Any] = field(
        default_factory=dict,
        metadata={
            "description": "Additional keyword arguments to pass to the search function of the retriever."
        },
    )

    @classmethod
    def from_runnable_config(cls: Type[T], config: RunnableConfig | None = None) -> T:
        """从 RunnableConfig 对象创建 IndexConfiguration 实例。

        Args:
            cls (Type[T]): 类本身。
            config (Optional[RunnableConfig]): 要使用的配置对象。

        Returns:
            T: 带有指定配置的 IndexConfiguration 实例。
        """
        config = ensure_config(config)
        # 从 config 中提取 configurable 字典
        configurable = config.get("configurable") or {}
        # 获取当前类的所有可初始化字段名集合
        _fields = {f.name for f in fields(cls) if f.init}
        # 只将 configurable 中与字段名匹配的参数传入构造函数
        return cls(**{k: v for k, v in configurable.items() if k in _fields})


# 泛型类型变量，绑定到 IndexConfiguration，用于 from_runnable_config 的返回类型
T = TypeVar("T", bound=IndexConfiguration)


@dataclass(kw_only=True)
class Configuration(IndexConfiguration):
    """检索对话图（RetrievalGraph）的完整配置，继承自 IndexConfiguration。"""

    # 响应生成的系统提示词，默认使用 prompts.py 中的 RESPONSE_SYSTEM_PROMPT
    response_system_prompt: str = field(
        default=prompts.RESPONSE_SYSTEM_PROMPT,
        metadata={"description": "The system prompt used for generating responses."},
    )

    # 响应生成的语言模型，格式为 provider/model-name
    response_model: Annotated[str, {"__template_metadata__": {"kind": "llm"}}] = field(
        default="anthropic/claude-3-5-sonnet-20240620",
        metadata={
            "description": "The language model used for generating responses. Should be in the form: provider/model-name."
        },
    )

    # 查询生成的系统提示词，默认使用 prompts.py 中的 QUERY_SYSTEM_PROMPT
    query_system_prompt: str = field(
        default=prompts.QUERY_SYSTEM_PROMPT,
        metadata={
            "description": "The system prompt used for processing and refining queries."
        },
    )

    # 查询生成的语言模型（通常用更轻量的模型以降低成本），格式为 provider/model-name
    query_model: Annotated[str, {"__template_metadata__": {"kind": "llm"}}] = field(
        default="anthropic/claude-3-haiku-20240307",
        metadata={
            "description": "The language model used for processing and refining queries. Should be in the form: provider/model-name."
        },
    )
