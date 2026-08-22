"""管理多种检索器的配置。

本模块提供了为不同向量库后端（Elasticsearch、Pinecone、MongoDB）
创建和管理检索器的功能。

所有检索器都支持按 user_id 过滤结果，确保用户间的数据隔离。
"""

import os
from contextlib import contextmanager
from typing import Generator

from langchain_core.embeddings import Embeddings
from langchain_core.runnables import RunnableConfig
from langchain_core.vectorstores import VectorStoreRetriever

from retrieval_graph.configuration import Configuration, IndexConfiguration

## Encoder 构造器


def make_text_encoder(model: str) -> Embeddings:
    """连接配置的文本编码器（Embedding 模型）。

    根据模型名称中的 provider 前缀，加载对应的 Embedding 模型。

    Args:
        model (str): 模型名称，格式为 'provider/model-name'。

    Returns:
        Embeddings: Embedding 模型实例。

    Raises:
        ValueError: 当 provider 不被支持时。
    """
    provider, model = model.split("/", maxsplit=1)
    match provider:
        case "openai":
            from langchain_openai import OpenAIEmbeddings

            return OpenAIEmbeddings(model=model)
        case "cohere":
            from langchain_cohere import CohereEmbeddings

            return CohereEmbeddings(model=model)  # type: ignore
        case _:
            raise ValueError(f"Unsupported embedding provider: {provider}")


## 检索器构造器


@contextmanager
def make_elastic_retriever(
    configuration: IndexConfiguration, embedding_model: Embeddings
) -> Generator[VectorStoreRetriever, None, None]:
    """配置连接到 Elasticsearch 索引的检索器。

    支持两种认证方式：
    - elastic-local: 用户名 + 密码（本地 Docker 部署）
    - elastic: API Key（Elastic Cloud / Serverless）
    """
    from langchain_elasticsearch import ElasticsearchStore

    # 根据部署方式选择认证方式
    connection_options = {}
    if configuration.retriever_provider == "elastic-local":
        # 本地部署：用户名 + 密码认证
        connection_options = {
            "es_user": os.environ["ELASTICSEARCH_USER"],
            "es_password": os.environ["ELASTICSEARCH_PASSWORD"],
        }

    else:
        # Elastic Cloud：API Key 认证
        connection_options = {"es_api_key": os.environ["ELASTICSEARCH_API_KEY"]}

    # 创建 Elasticsearch 向量存储实例
    vstore = ElasticsearchStore(
        **connection_options,  # type: ignore
        es_url=os.environ["ELASTICSEARCH_URL"],
        index_name="langchain_index",
        embedding=embedding_model,
    )

    search_kwargs = configuration.search_kwargs

    # 注入 user_id 过滤条件，确保只检索当前用户的文档
    search_filter = search_kwargs.setdefault("filter", [])
    search_filter.append({"term": {"metadata.user_id": configuration.user_id}})
    yield vstore.as_retriever(search_kwargs=search_kwargs)


@contextmanager
def make_pinecone_retriever(
    configuration: IndexConfiguration, embedding_model: Embeddings
) -> Generator[VectorStoreRetriever, None, None]:
    """配置连接到 Pinecone 索引的检索器。"""
    from langchain_pinecone import PineconeVectorStore

    search_kwargs = configuration.search_kwargs

    # 注入 user_id 过滤条件，确保只检索当前用户的文档
    search_filter = search_kwargs.setdefault("filter", {})
    search_filter.update({"user_id": configuration.user_id})
    # 从已存在的 Pinecone 索引创建向量存储
    vstore = PineconeVectorStore.from_existing_index(
        os.environ["PINECONE_INDEX_NAME"], embedding=embedding_model
    )
    yield vstore.as_retriever(search_kwargs=search_kwargs)


@contextmanager
def make_mongodb_retriever(
    configuration: IndexConfiguration, embedding_model: Embeddings
) -> Generator[VectorStoreRetriever, None, None]:
    """配置连接到 MongoDB Atlas 向量搜索索引的检索器。"""
    from langchain_mongodb.vectorstores import MongoDBAtlasVectorSearch

    # 从连接字符串创建 MongoDB 向量存储
    vstore = MongoDBAtlasVectorSearch.from_connection_string(
        os.environ["MONGODB_URI"],
        namespace="langgraph_retrieval_agent.default",
        embedding=embedding_model,
    )
    search_kwargs = configuration.search_kwargs
    # 注入 user_id 预过滤条件，确保只检索当前用户的文档
    pre_filter = search_kwargs.setdefault("pre_filter", {})
    pre_filter["user_id"] = {"$eq": configuration.user_id}
    yield vstore.as_retriever(search_kwargs=search_kwargs)


@contextmanager
def make_retriever(
    config: RunnableConfig,
) -> Generator[VectorStoreRetriever, None, None]:
    """根据当前配置创建检索器。

    这是统一的检索器入口，根据 configuration.retriever_provider
    自动选择对应的向量库后端。

    Args:
        config (RunnableConfig): 运行时配置，包含 user_id、retriever_provider 等。

    Yields:
        VectorStoreRetriever: 配置好的检索器实例。

    Raises:
        ValueError: 当 user_id 为空或 retriever_provider 不被支持时。
    """
    configuration = IndexConfiguration.from_runnable_config(config)
    # 创建 Embedding 模型
    embedding_model = make_text_encoder(configuration.embedding_model)
    user_id = configuration.user_id
    if not user_id:
        raise ValueError("Please provide a valid user_id in the configuration.")
    # 根据配置的 provider 选择对应的向量库
    match configuration.retriever_provider:
        case "elastic" | "elastic-local":
            with make_elastic_retriever(configuration, embedding_model) as retriever:
                yield retriever

        case "pinecone":
            with make_pinecone_retriever(configuration, embedding_model) as retriever:
                yield retriever

        case "mongodb":
            with make_mongodb_retriever(configuration, embedding_model) as retriever:
                yield retriever

        case _:
            raise ValueError(
                "Unrecognized retriever_provider in configuration. "
                f"Expected one of: {', '.join(Configuration.__annotations__['retriever_provider'].__args__)}\n"
                f"Got: {configuration.retriever_provider}"
            )
