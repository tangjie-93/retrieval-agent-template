# LangChain 示例目录整理设计

## 目标

把平铺在 `doc/langchain-ecosystem/examples/` 下的 `36` 个单概念脚本按章节归档，降低目录扫描成本，同时保留现有 `8` 个章节综合入口。

## 目录结构

```text
examples/
├── README.md
├── common.py
├── 01_chat_basics.py ... 08_enterprise_rag.py
├── 01_ecosystem/
├── 02_core/
├── 03_models/
├── 04_rag/
├── 05_agents/
├── 06_langgraph/
├── 07_langsmith/
└── 08_enterprise/
```

章节目录内删除重复章节前缀，例如 `02_01_messages.py` 迁移为 `02_core/messages.py`。根目录继续只放综合入口、`README.md` 和公共配置。

## 导入策略

直接执行子目录脚本时，Python 只把脚本所在目录加入 `sys.path`。因此 `03_models/` 增加目录内 `common.py`，为 `chat_model.py`、`stream_and_batch.py` 和 `embeddings.py` 提供统一配置。其他单概念脚本不依赖根目录模块，不需要路径修改。

## 文档与验证

- 更新 `examples/README.md` 和 `01-08` 专题文档中的所有命令与脚本索引。
- 更新结构测试，要求 `36` 个脚本存在于预期章节目录，根目录不再存在 `NN_NN_*.py`。
- 实际运行全部离线脚本。
- 验证在线脚本能找到目录内配置，并在缺少密钥时返回明确错误，而不是 `ModuleNotFoundError`。
- 保持 LangSmith 的 `--write` 保护和综合脚本的安全导入行为不变。
