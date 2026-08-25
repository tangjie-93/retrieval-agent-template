# LangChain Example Directories Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use `superpowers:executing-plans` to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 将 `36` 个单概念示例按 `01-08` 章节放入独立目录，并保持所有示例可运行。

**Architecture:** 根目录保留 `8` 个综合入口和根级 `common.py`；单概念脚本进入章节目录并去掉重复前缀；`03_models/common.py` 专门支持该目录内在线脚本直接执行。

**Tech Stack:** Python、Pytest、Ruff、Markdown。

---

### Task 1: 锁定目录契约

- [x] 修改 `tests/unit_tests/test_langchain_ecosystem_examples.py`，使用章节相对路径定义 `36` 个脚本。
- [x] 增加根目录不允许出现 `NN_NN_*.py` 的断言。
- [x] 增加 `03_models` 在线脚本直接执行时不得出现导入错误的测试。
- [x] 运行目标测试，确认它因目录尚未迁移而失败。

### Task 2: 迁移脚本

- [x] 创建 `01_ecosystem` 至 `08_enterprise` 八个目录。
- [x] 移动 `36` 个单概念脚本并删除文件名中的章节序号。
- [x] 在 `03_models/common.py` 提供聊天模型与 Embedding 配置。
- [x] 运行目标测试，确认新目录契约通过。

### Task 3: 更新文档

- [x] 更新 `examples/README.md` 中的目录说明、表格路径和运行命令。
- [x] 更新 `01-08` 专题文档中的单概念运行命令。
- [x] 更新原始示例设计与计划中的最终路径。
- [x] 运行文档索引测试。

### Task 4: 完整验证

- [x] 运行全部单元测试。
- [x] 实际运行所有离线单概念脚本。
- [x] 验证综合入口和在线模块导入不触发 API。
- [x] 运行 Ruff 格式、静态检查、`compileall` 和 `git diff --check`。
