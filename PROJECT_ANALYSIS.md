# retrieval-agent-template 项目分析

## 一、项目概述

`retrieval-agent-template` 是基于 **LangGraph** 的检索增强生成（RAG）Agent 模板项目。它提供了两个核心图（Graph）：

1. **IndexGraph（索引图）**：将用户上传的文档索引到向量数据库，按 `user_id` 隔离数据。
2. **RetrievalGraph（检索图）**：接收用户提问，生成搜索查询，从向量库检索相关文档，再由 LLM 生成最终回答。

项目设计为通过 [LangGraph Studio](https://github.com/langchain-ai/langgraph-studio) 进行可视化调试和部署。

---

## 二、技术框架

| 类别 | 技术 | 说明 |
|------|------|------|
| **语言** | Python >= 3.10 | 最低版本要求 |
| **核心框架** | LangGraph >= 1.0.0 | 图编排引擎，定义节点和边的有向图 |
| **LLM 抽象层** | LangChain >= 1.3.10 | 提供模型调用、Prompt 模板、文档抽象等 |
| **LLM 提供商** | Anthropic / OpenAI / Fireworks | 通过 `provider/model-name` 格式动态加载 |
| **Embedding 模型** | OpenAI / Cohere | 向量化文档和查询 |
| **向量数据库** | Elasticsearch / Pinecone / MongoDB Atlas | 三选一，通过配置切换 |
| **包管理** | uv | 依赖管理与锁定（uv.lock） |
| **代码质量** | ruff + mypy + codespell | Lint、格式化、类型检查、拼写检查 |
| **测试框架** | pytest + anyio + langsmith | 单元测试 + 异步测试 + 集成测试 |
| **CI/CD** | GitHub Actions | 自动运行单元测试和集成测试 |
| **部署/调试** | LangGraph Studio | 可视化图调试界面 |

---

## 三、项目结构

```
retrieval-agent-template/
├── .codespellignore                          # codespell 拼写检查忽略词列表
├── .env.example                              # 环境变量模板（API Key、向量库连接信息）
├── .github/
│   └── workflows/
│       ├── unit-tests.yml                    # CI：单元测试（ruff + mypy + codespell + pytest）
│       └── integration-tests.yml             # CI：集成测试（每日定时，启动 ES 容器跑完整流程）
├── .gitignore                                # Git 忽略规则
├── LICENSE                                   # MIT 许可证
├── Makefile                                  # 构建/测试/Lint 命令快捷方式
├── README.md                                 # 英文项目文档
├── README-zh.md                             # 中文项目文档
├── langgraph.json                            # LangGraph Studio 配置（图入口、环境文件）
├── pyproject.toml                            # Python 项目配置（依赖、ruff、mypy、setuptools）
├── uv.lock                                   # uv 依赖锁定文件
│
├── src/
│   └── retrieval_graph/                      # 核心源码包
│       ├── __init__.py                       # 模块入口，导出 graph 和 index_graph
│       ├── configuration.py                  # 配置类：IndexConfiguration + Configuration
│       ├── graph.py                          # 主检索图：generate_query → retrieve → respond
│       ├── index_graph.py                    # 索引图：文档上传 → 标记 user_id → 写入向量库
│       ├── prompts.py                        # 系统提示词（RESPONSE_SYSTEM_PROMPT、QUERY_SYSTEM_PROMPT）
│       ├── retrieval.py                      # 检索器工厂：Elastic / Pinecone / MongoDB
│       ├── state.py                          # 状态定义：IndexState、InputState、State + reducer 函数
│       └── utils.py                          # 工具函数：消息文本提取、文档格式化、模型加载
│
├── static/
│   └── studio_ui.png                         # LangGraph Studio 界面截图
│
└── tests/
    ├── conftest.py                           # pytest 公共 fixture（asyncio 后端）
    ├── integration_tests/
    │   ├── __init__.py
    │   └── test_graph.py                     # 集成测试：索引文档 → 检索 → 验证用户隔离
    └── unit_tests/
        ├── __init__.py
        └── test_configuration.py             # 单元测试：Configuration 配置解析
```

---

## 四、各文件/文件夹详细说明

### 4.1 根目录文件

#### `pyproject.toml`

项目元数据与配置文件，定义：
- **项目名称**：`retrieval-graph`，版本 `0.0.1`
- **运行依赖**：langgraph、langchain、langchain-openai/anthropic/fireworks/elasticsearch/pinecone/mongodb/cohere、python-dotenv、msgspec
- **开发依赖**：mypy、ruff、pytest、langgraph-cli
- **构建系统**：setuptools，包路径映射 `src/retrieval_graph` → `retrieval_graph`
- **Ruff 配置**：启用 E/F/I/D/UP 规则，Google 风格 docstring
- **Mypy 配置**：严格模式

#### `langgraph.json`

LangGraph Studio 入口配置：
- **dependencies**：`["."]`（从当前目录安装）
- **graphs**：注册两个图
  - `indexer`：`./src/retrieval_graph/index_graph.py:graph`
  - `retrieval_graph`：`./src/retrieval_graph/graph.py:graph`
- **env**：`.env`

#### `Makefile`

提供常用命令快捷方式：
- `make test`：运行单元测试
- `make integration_tests`：运行集成测试
- `make lint`：运行 ruff + mypy 检查
- `make format`：格式化代码
- `make test_watch`：监听模式运行测试
- `make spell_check`：拼写检查

#### `.env.example`

环境变量模板，包含：
- `LANGSMITH_PROJECT`：LangSmith 追踪项目名
- LLM API Key：`ANTHROPIC_API_KEY`、`OPENAI_API_KEY`、`FIREWORKS_API_KEY`
- 向量库连接：Elasticsearch（URL + API Key / 用户名密码）、Pinecone（API Key + Index Name）、MongoDB（URI）

#### `uv.lock`

uv 包管理器的依赖锁定文件，确保依赖版本可复现。

#### `.codespellignore`

codespell 拼写检查工具的忽略词列表。

#### `.gitignore`

标准 Python 项目 Git 忽略规则，忽略 `.env`、`.venv`、`__pycache__`、`.mypy_cache` 等。

---

### 4.2 源码目录 `src/retrieval_graph/`

#### `__init__.py`

模块入口，导出两个编译好的图对象：
- `graph`：主检索对话图（RetrievalGraph）
- `index_graph`：文档索引图（IndexGraph）

#### `configuration.py`

配置类定义，使用 `@dataclass` + `Annotated` 实现可配置参数：

**`IndexConfiguration`（索引图配置）**：
| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `user_id` | str | 必填 | 用户唯一标识，用于数据隔离 |
| `embedding_model` | str | `openai/text-embedding-3-small` | Embedding 模型 |
| `retriever_provider` | Literal | `elastic` | 向量库提供商 |
| `search_kwargs` | dict | `{}` | 检索参数（如 top_k、filter） |

**`Configuration`（检索图配置，继承 IndexConfiguration）**：
| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `response_system_prompt` | str | 见 prompts.py | 响应生成系统提示词 |
| `response_model` | str | `anthropic/claude-3-5-sonnet-20240620` | 响应生成 LLM |
| `query_system_prompt` | str | 见 prompts.py | 查询生成系统提示词 |
| `query_model` | str | `anthropic/claude-3-haiku-20240307` | 查询生成 LLM |

通过 `from_runnable_config()` 方法从 `RunnableConfig` 中解析配置。

#### `graph.py` — 主检索对话图

定义了三个节点的线性流程：

```
__start__ → generate_query → retrieve → respond
```

1. **`generate_query(state, config)`**：生成搜索查询
   - 首条消息：直接使用用户输入作为查询
   - 后续消息：用 `query_model` + `query_system_prompt` 生成结构化查询（`SearchQuery` Pydantic 模型）

2. **`retrieve(state, config)`**：从向量库检索文档
   - 调用 `retrieval.make_retriever()` 创建检索器
   - 用最新查询执行向量检索

3. **`respond(state, config)`**：生成最终回答
   - 用 `response_model` + `response_system_prompt`
   - 将检索到的文档格式化为 XML 注入 Prompt
   - 返回 AI 消息

#### `index_graph.py` — 文档索引图

单节点流程：

```
__start__ → index_docs
```

- **`ensure_docs_have_user_id(docs, config)`**：为每个文档的 metadata 注入 `user_id`
- **`index_docs(state, config)`**：创建检索器 → 标记 user_id → `aadd_documents()` 写入向量库 → 返回 `{"docs": "delete"}` 清空状态

#### `retrieval.py` — 检索器工厂

根据 `retriever_provider` 配置动态创建对应向量库的检索器：

| Provider | 向量库 | 连接方式 | 过滤方式 |
|----------|--------|----------|----------|
| `elastic` | ElasticsearchStore | URL + API Key | `{"term": {"metadata.user_id": ...}}` |
| `elastic-local` | ElasticsearchStore | URL + 用户名/密码 | 同上 |
| `pinecone` | PineconeVectorStore | Index Name + API Key | `{"user_id": ...}` |
| `mongodb` | MongoDBAtlasVectorSearch | URI + namespace | `{"user_id": {"$eq": ...}}` |

还包含 `make_text_encoder(model)` 函数，根据 `provider/model` 格式创建 Embedding 模型（OpenAI / Cohere）。

所有检索器都使用 `@contextmanager` 管理资源生命周期，并自动注入 `user_id` 过滤条件确保数据隔离。

#### `state.py` — 状态管理

定义了三个状态类和对应的 reducer 函数：

**`IndexState`（索引图状态）**：
- `docs: Sequence[Document]` — 待索引文档，使用 `reduce_docs` reducer

**`InputState`（检索图输入状态）**：
- `messages: Sequence[AnyMessage]` — 对话消息列表，使用 `add_messages` reducer（LangGraph 内置，按 ID 合并/追加）

**`State`（检索图完整状态，继承 InputState）**：
- `messages` — 继承自 InputState
- `queries: list[str]` — 生成的搜索查询列表，使用 `add_queries` reducer（累加）
- `retrieved_docs: list[Document]` — 检索到的文档列表

**reducer 函数**：
- `reduce_docs` — 处理多种输入格式（Document/dict/str/"delete"），支持删除操作
- `add_queries` — 简单累加新查询到列表

#### `prompts.py` — 系统提示词

定义两个默认系统提示词：

- **`RESPONSE_SYSTEM_PROMPT`**：指示 AI 基于检索文档回答用户问题，注入 `{retrieved_docs}` 和 `{system_time}`
- **`QUERY_SYSTEM_PROMPT`**：指示 AI 生成搜索查询，注入历史查询 `{queries}` 和 `{system_time}`

#### `utils.py` — 工具函数

- **`get_message_text(msg)`**：从各种消息格式（str/dict/list）中提取纯文本
- **`format_docs(docs)`**：将文档列表格式化为 XML 字符串，注入到 Prompt 中
- **`load_chat_model(fully_specified_name)`**：按 `provider/model` 格式加载聊天模型，底层调用 `langchain.chat_models.init_chat_model()`

---

### 4.3 测试目录 `tests/`

#### `conftest.py`

pytest 公共 fixture，设置 `anyio_backend = "asyncio"`，支持异步测试。

#### `tests/unit_tests/test_configuration.py`

单元测试，验证 `Configuration.from_runnable_config()` 能正确解析 `user_id` 配置。

#### `tests/integration_tests/test_graph.py`

集成测试，完整验证索引 + 检索 + 用户隔离流程：
1. 用 `index_graph` 索引一条文档（带 `user_id`）
2. 用 `graph` 检索验证能返回正确结果
3. 换一个 `other_user_id` 检索，验证结果中不包含该文档（数据隔离）

---

### 4.4 CI/CD `.github/workflows/`

#### `unit-tests.yml`

- 触发：push 到 main / PR / 手动
- 矩阵：Python 3.11 + 3.12
- 步骤：uv 安装依赖 → ruff lint → mypy strict → codespell 拼写检查 → pytest 单元测试

#### `integration-tests.yml`

- 触发：每日定时（UTC 14:37）+ 手动
- 矩阵：Python 3.11 + 3.12
- 服务：启动 Elasticsearch 8.13.0 Docker 容器
- 步骤：安装依赖 → pytest 集成测试（注入 Anthropic/OpenAI API Key）

---

## 五、架构流程图

### 5.1 索引流程（IndexGraph）

```
用户上传文档
    │
    ▼
┌─────────────────────┐
│   index_docs 节点    │
│  1. 为文档注入       │
│     user_id metadata │
│  2. 写入向量数据库    │
│  3. 清空 state.docs  │
└─────────────────────┘
    │
    ▼
  完成（文档已持久化到向量库）
```

### 5.2 检索流程（RetrievalGraph）

```
用户提问
    │
    ▼
┌─────────────────────┐
│  generate_query 节点  │
│  首次：直接用用户输入  │
│  后续：LLM 生成查询    │
└─────────────────────┘
    │
    ▼
┌─────────────────────┐
│    retrieve 节点      │
│  用查询检索向量库     │
│  按 user_id 过滤     │
└─────────────────────┘
    │
    ▼
┌─────────────────────┐
│    respond 节点       │
│  检索文档 + 对话历史   │
│  → LLM 生成回答       │
└─────────────────────┘
    │
    ▼
  AI 回复
```

---

## 六、启动方式

### 前置条件

- Python >= 3.10
- [LangGraph Studio](https://github.com/langchain-ai/langgraph-studio) 已安装
- 至少一个 LLM API Key（Anthropic 或 OpenAI）
- 至少一个向量数据库（Elasticsearch / Pinecone / MongoDB Atlas）

### 步骤

#### 1. 安装依赖

```bash
# 使用 uv（推荐，与项目一致）
curl -LsSf https://astral.sh/uv/install.sh | sh
uv venv
uv pip install -r pyproject.toml

# 或使用 pip
pip install -e ".[dev]"
```

#### 2. 配置环境变量

```bash
cp .env.example .env
```

编辑 `.env` 文件，填入：

```bash
# LLM API Key（至少一个）
ANTHROPIC_API_KEY=your-key
OPENAI_API_KEY=your-key

# 向量库配置（任选其一）
# Elasticsearch Cloud
ELASTICSEARCH_URL=your-url
ELASTICSEARCH_API_KEY=your-key

# 或 Elasticsearch 本地 Docker
ELASTICSEARCH_URL=http://host.docker.internal:9200
ELASTICSEARCH_USER=elastic
ELASTICSEARCH_PASSWORD=changeme

# 或 Pinecone
PINECONE_API_KEY=your-key
PINECONE_INDEX_NAME=your-index

# 或 MongoDB Atlas
MONGODB_URI=your-connection-string
```

#### 3. 启动 LangGraph Studio

```bash
# 方式一：使用 langgraph CLI
langgraph dev

# 方式二：使用 uv 运行
uv run langgraph dev
```

Studio 启动后会打开 Web UI，可在界面中：
- 左上角下拉切换图：`indexer` 或 `retrieval_graph`
- 底部配置区设置 `user_id`、`retriever_provider`、`response_model` 等参数
- 上传文档进行索引，然后切换到检索图进行对话

#### 4. 使用流程

1. **选择 `indexer` 图**，在配置区设置 `user_id`
2. 在输入框上传文档：
   ```json
   [{"page_content": "My cat knows python."}]
   ```
3. 等待索引完成（文档从 state 中删除表示已完成）
4. **切换到 `retrieval_graph` 图**，设置相同 `user_id`
5. 开始对话，Agent 会基于已索引的文档回答问题
6. 更换 `user_id` 可验证数据隔离效果

#### 5. 运行测试

```bash
# 单元测试
make test
# 或
python -m pytest tests/unit_tests

# 集成测试（需要先启动 Elasticsearch）
make integration_tests
# 或
python -m pytest tests/integration_tests

# 代码检查
make lint

# 格式化
make format
```

---

## 七、核心设计特点

1. **双图架构**：索引与检索分离，职责清晰，可独立运行
2. **用户数据隔离**：所有文档和检索都按 `user_id` 过滤，天然支持多用户场景
3. **多供应商支持**：通过配置切换 LLM（Anthropic/OpenAI）、Embedding（OpenAI/Cohere）、向量库（Elastic/Pinecone/MongoDB），无需改代码
4. **状态管理**：使用 dataclass + Annotated reducer 模式，消息按 ID 合并、查询累加、文档支持删除
5. **LangGraph Studio 集成**：可视化调试，支持热重载、断点回放、LangSmith 追踪
6. **完整工程化**：ruff + mypy strict + codespell + pytest + GitHub Actions CI
