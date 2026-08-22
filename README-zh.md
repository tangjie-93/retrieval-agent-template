# LangGraph 检索聊天机器人模板中文说明

本文档根据 `README.md` 整理，用于快速理解和使用 LangGraph Retrieval Chat Bot Template。

## 项目简介

这是一个用于构建检索增强问答 Agent 的入门模板。它基于 [LangGraph](https://github.com/langchain-ai/langgraph)，并可以在 [LangGraph Studio](https://github.com/langchain-ai/langgraph-studio) 中运行和调试。

模板中包含从 `src/retrieval_agent/graph.py` 导出的示例图，用来实现基于检索的问答系统。

界面示例图位于：

```text
static/studio_ui.png
```

## 核心功能

该项目包含两个主要图：

- `indexer`：索引图，用于接收文档对象或字符串，并按配置的 `user_id` 写入索引。
- `retrieval_graph`：检索问答图，用于维护聊天历史、检索上下文，并基于检索结果生成回答。

索引图可以接收如下文档输入：

```json
[{ "page_content": "I have 1 cat." }]
```

检索聊天机器人的基本流程：

1. 接收用户输入的查询问题。
2. 根据会话历史和 `user_id` 过滤条件检索相关文档。
3. 结合检索到的信息和对话上下文生成回答。

默认情况下，系统会基于用户已经索引的文档回答问题，并通过 `user_id` 实现个性化数据隔离。

## 快速开始

使用前请先安装 LangGraph Studio。安装完成后，在模板目录中进行以下配置。

### 1. 创建环境变量文件

进入 `retrieval-agent-template` 目录后执行：

```bash
cp .env.example .env
```

### 2. 选择检索器和索引后端

根据你选择的检索器、索引后端、模型提供商和嵌入模型，把对应密钥和连接信息写入 `.env`。

## 配置检索器

默认检索器配置如下：

```yaml
retriever_provider: elastic
```

支持的检索后端包括：

- Elasticsearch
- MongoDB Atlas
- Pinecone Serverless

这三个后端在当前模板中是**单选关系**。也就是说，`retriever_provider` 一次只配置一个值，例如 `elastic`、`elastic-local`、`mongodb` 或 `pinecone`。如果要同时写入或查询多个检索后端，需要额外改造检索层代码。

### 检索后端对比

| 后端 | 优点 | 缺点 | 适合场景 |
| --- | --- | --- | --- |
| Elasticsearch | 搜索能力完整，支持关键词检索、过滤、聚合和向量检索；生态成熟；既可以用云服务，也可以本地 Docker 部署；适合做混合检索。 | 部署和运维复杂度相对更高；资源占用较大；本地和云端连接方式不同，配置项较多。 | 需要关键词检索 + 向量检索结合、文档过滤复杂、后续可能扩展搜索分析能力的企业知识库。 |
| MongoDB Atlas | 如果业务数据本来就在 MongoDB 中，接入成本低；文档模型灵活；Atlas 托管服务减少数据库运维；可以在同一个数据库中保存业务数据和向量索引。 | 向量检索能力更偏 Atlas 平台能力；需要配置 Atlas Vector Search Index；如果项目不用 MongoDB，引入它可能增加技术栈复杂度。 | 已经使用 MongoDB Atlas，或希望把业务文档、元数据和向量检索放在同一套托管数据库里的应用。 |
| Pinecone Serverless | 专注向量数据库；Serverless 方式启动快、运维少；API 简洁；适合快速搭建语义检索和 RAG 原型。 | 主要面向向量检索，传统关键词检索和复杂聚合能力不如 Elasticsearch；强依赖外部云服务；需要单独管理业务数据和向量数据的关系。 | 快速验证 RAG、主要依赖语义相似度检索、不想维护搜索集群的项目。 |

简单选择建议：

- 如果你要做企业知识库，并且希望支持关键词、过滤条件、向量检索和后续搜索扩展，优先选 Elasticsearch。
- 如果你的业务数据已经在 MongoDB Atlas，优先选 MongoDB Atlas，减少数据同步和系统复杂度。
- 如果你主要想快速跑通 RAG 原型，且检索需求以向量相似度为主，优先选 Pinecone Serverless。

### Elasticsearch

Elasticsearch 是开源的分布式搜索与分析引擎，也可以作为向量数据库使用。该模板支持 Elastic Cloud、Elasticsearch Serverless 和本地 Docker 部署。

#### Elasticsearch Serverless

1. 注册 Elasticsearch Serverless 14 天免费试用。
2. 在首页的连接信息区域获取 Elasticsearch URL。
3. 在首页创建 API Key。
4. 将 URL 和 API Key 写入 `.env`：

```env
ELASTICSEARCH_URL=<ES_URL>
ELASTICSEARCH_API_KEY=<API_KEY>
```

#### Elastic Cloud

1. 注册 Elastic Cloud 14 天免费试用。
2. 在部署的 Applications 区域获取 Elasticsearch URL。
3. 创建 API Key。
4. 将 URL 和 API Key 写入 `.env`：

```env
ELASTICSEARCH_URL=<ES_URL>
ELASTICSEARCH_API_KEY=<API_KEY>
```

#### 本地 Elasticsearch Docker

可以使用 Docker 启动本地 Elasticsearch：

```bash
docker run -p 127.0.0.1:9200:9200 -d --name elasticsearch --network elastic-net -e ELASTIC_PASSWORD=changeme -e "discovery.type=single-node" -e "xpack.security.http.ssl.enabled=false" -e "xpack.license.self_generated.type=trial" docker.elastic.co/elasticsearch/elasticsearch:8.15.1
```

由于 Elasticsearch 和 LangGraph Studio 都运行在 Docker 中，`.env` 中需要使用 `host.docker.internal` 访问主机服务：

```env
ELASTICSEARCH_URL=http://host.docker.internal:9200
ELASTICSEARCH_USER=elastic
ELASTICSEARCH_PASSWORD=changeme
```

如果在本地 Docker Elasticsearch 环境下运行集成测试，则需要改用 `localhost`：

```bash
export ELASTICSEARCH_URL=http://localhost:9200
```

### MongoDB Atlas

MongoDB Atlas 是托管云数据库，并支持向量搜索能力。

配置步骤：

1. 注册 MongoDB Atlas 账号并创建免费集群。
2. 创建 Vector Search Index。
3. 默认集合为 `langgraph_retrieval_agent.default`，请在该集合上创建索引。
4. 为 `user_id` 路径添加索引过滤字段。
5. 创建索引时注意选择 Atlas Vector Search，而不是 Atlas Search。

索引配置示例：

```json
{
  "fields": [
    {
      "numDimensions": 1536,
      "path": "embedding",
      "similarity": "cosine",
      "type": "vector"
    },
    {
      "path": "user_id",
      "type": "filter"
    }
  ]
}
```

如果你更换了嵌入模型，`numDimensions` 可能需要相应调整。

随后在 Atlas 控制台点击集群的 Connect，选择 Connect your application，复制连接字符串，并写入 `.env`：

```env
MONGODB_URI="mongodb+srv://username:password@your-cluster-url.mongodb.net/?retryWrites=true&w=majority&appName=your-cluster-name"
```

请将 `username`、`password`、`your-cluster-url` 和 `your-cluster-name` 替换为实际信息。

### Pinecone Serverless

Pinecone 是托管的云原生向量数据库，可为 AI 应用提供长期记忆能力。

配置步骤：

1. 注册 Pinecone 账号。
2. 登录后在 Pinecone 控制台生成 API Key。
3. 创建 Serverless Index：
   - 设置索引名称，例如 `example-index`。
   - 根据嵌入模型设置维度，例如 OpenAI embeddings 通常为 `1536`。
   - 相似度指标选择 `cosine`。
   - 索引类型选择 `Serverless`。
   - 选择云服务商和区域，例如 AWS `us-east-1`。
4. 将 API Key 和索引名称写入 `.env`：

```env
PINECONE_API_KEY=your-api-key
PINECONE_INDEX_NAME=your-index-name
```

## 配置语言模型

默认模型配置如下：

```yaml
response_model: anthropic/claude-3-5-sonnet-20240620
query_model: anthropic/claude-3-haiku-20240307
```

其中：

- `response_model`：用于生成最终回答。
- `query_model`：用于处理和改写检索查询。

### Anthropic

如果使用 Anthropic 模型，请先获取 API Key，并写入 `.env`：

```env
ANTHROPIC_API_KEY=your-api-key
```

### OpenAI

如果使用 OpenAI 模型，请先获取 API Key，并写入 `.env`：

```env
OPENAI_API_KEY=your-api-key
```

## 配置嵌入模型

默认嵌入模型配置如下：

```yaml
embedding_model: openai/text-embedding-3-small
```

### OpenAI Embeddings

使用 OpenAI 嵌入模型时，需要在 `.env` 中配置：

```env
OPENAI_API_KEY=your-api-key
```

### Cohere Embeddings

使用 Cohere 嵌入模型时，需要在 `.env` 中配置：

```env
COHERE_API_KEY=your-api-key
```

## 使用方式

完成检索器、模型密钥和嵌入模型配置后，即可在 LangGraph Studio 中试用。

### 1. 写入索引

打开 LangGraph Studio，在左上角下拉框中选择 `indexer` 图。

在底部配置区域填写一个示例 `user_id`，然后输入要索引的内容，例如：

```json
[{ "page_content": "My cat knows python." }]
```

上传后，内容会按照当前配置的 `user_id` 写入索引。当 `indexer` 从图内存中删除该内容时，表示内容已经持久化到配置的存储提供商中。

### 2. 进行检索问答

在左上角下拉框中切换到 `retrieval_graph`。

可以询问与刚刚索引内容相关的问题，例如：

```text
What does my cat know?
```

如果更换 `user_id`，系统将无法访问之前用户 ID 下的数据。这说明图中通过 `user_id` 对内容做了简单隔离过滤。

## 自定义方式

你可以从以下方面修改该检索 Agent 模板：

1. 更换检索器：修改配置中的 `retriever_provider`，在 Elasticsearch、MongoDB、Pinecone 之间切换。
2. 修改嵌入模型：更新 `embedding_model`，切换 OpenAI 或 Cohere 的嵌入模型。
3. 调整搜索参数：修改配置中的 `search_kwargs`，例如召回文档数量或相似度阈值。
4. 自定义回答生成：修改 `response_system_prompt`，控制 Agent 的回答风格、角色或约束。
5. 更换语言模型：修改 `response_model`，切换 Anthropic Claude、OpenAI 或其他提供商模型。
6. 扩展图结构：修改 `src/retrieval_agent/graph.py`，新增节点、边或处理流程。
7. 添加工具能力：实现新的工具或 API 集成，扩展 Agent 能力。
8. 修改提示词：调整 `src/retrieval_agent/prompts.py` 中的查询生成和回答生成提示词。

修改后应结合具体业务场景进行充分测试，确认变更确实提升了检索和回答效果。

## 开发与调试

在 LangGraph Studio 中迭代图逻辑时，可以编辑历史状态，并从某个历史状态重新运行应用，用于调试特定节点。

本地代码变更会通过热重载自动生效。你可以尝试：

- 在 Agent 调用工具前添加 interrupt。
- 修改默认系统消息，让 Agent 具备特定角色或回答风格。
- 添加更多节点和边，扩展工作流。

后续请求会追加到同一个线程中。如果需要清空历史并创建新线程，可以点击右上角的 `+` 按钮。

LangGraph Studio 也可以与 LangSmith 集成，用于更深入的链路追踪、调试和团队协作。

## 关键配置摘要

### 检索器配置

```yaml
retriever_provider: elastic
```

可选值：

```text
elastic
elastic-local
mongodb
pinecone
```

### 模型配置

```yaml
response_model: anthropic/claude-3-5-sonnet-20240620
query_model: anthropic/claude-3-haiku-20240307
```

### 嵌入模型配置

```yaml
embedding_model: openai/text-embedding-3-small
```

## 相关文件

```text
retrieval-agent-template/
├── README.md
├── README-zh.md
├── langgraph.json
├── pyproject.toml
├── src/retrieval_agent/
│   ├── graph.py
│   ├── retrieval.py
│   ├── configuration.py
│   ├── prompts.py
│   ├── state.py
│   └── utils.py
└── tests/
    ├── unit_tests/
    └── integration_tests/
```

## 建议阅读顺序

1. 先阅读 `README.md` 和本文档，理解整体用途。
2. 查看 `langgraph.json`，确认图入口和运行配置。
3. 查看 `src/retrieval_agent/configuration.py`，理解可配置项。
4. 查看 `src/retrieval_agent/graph.py` 和 `src/retrieval_agent/retrieval.py`，理解检索问答流程。
5. 查看 `src/retrieval_agent/prompts.py`，根据业务需要调整提示词。
