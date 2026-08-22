"""检索图模块

本模块提供了一个对话式检索图系统，能够基于用户输入进行
智能文档检索和问答。

系统主要组件包括：

1. 状态管理系统 —— 处理对话上下文和文档检索。
2. 查询生成机制 —— 将用户输入提炼为有效的搜索查询。
3. 文档检索系统 —— 基于生成的查询获取相关信息。
4. 响应生成系统 —— 使用检索到的文档和对话历史生成回答。

图通过 Configuration 类中定义的可配置参数进行配置，
支持灵活切换模型、检索方式和系统提示词。

核心特性：
- 自适应查询生成，提升文档检索效果
- 集成多种检索提供商（如 Elastic、Pinecone、MongoDB）
- 可自定义的查询和响应生成语言模型
- 有状态的对话管理，支持上下文感知交互

用法：
    使用本系统的主要入口是从本模块导出的 `graph` 对象。
    可调用它来处理用户输入，并基于检索到的信息生成回答。

详细的配置选项和使用说明，请参阅 Configuration 类
以及 retrieval_graph 包中各组件的文档。
"""  # noqa

# 导入主检索对话图（RetrievalGraph）
from retrieval_graph.graph import graph
# 导入文档索引图（IndexGraph）
from retrieval_graph.index_graph import graph as index_graph

__all__ = ["graph", "index_graph"]
