import ast
import importlib.util
import os
import re
import subprocess
import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).parents[2]
EXAMPLES_DIR = PROJECT_ROOT / "doc" / "langchain-ecosystem" / "examples"
README_PATH = EXAMPLES_DIR / "README.md"
CHAPTER_DOCS = {
    "01": "01-ecosystem-layers.md",
    "02": "02-langchain-core.md",
    "03": "03-model-calling.md",
    "04": "04-rag-pipeline.md",
    "05": "05-agent-and-tools.md",
    "06": "06-langgraph-orchestration.md",
    "07": "07-langsmith-observability.md",
    "08": "08-enterprise-rag-engineering.md",
}

CONCEPT_DEMOS = [
    "01_ecosystem/ecosystem_layers.py",
    "02_core/messages.py",
    "02_core/prompts.py",
    "02_core/runnables.py",
    "02_core/tools.py",
    "02_core/output_parsers.py",
    "03_models/chat_model.py",
    "03_models/stream_and_batch.py",
    "03_models/embeddings.py",
    "03_models/model_selection.py",
    "04_rag/documents.py",
    "04_rag/loaders.py",
    "04_rag/text_splitters.py",
    "04_rag/vector_store.py",
    "04_rag/retrievers.py",
    "04_rag/context_building.py",
    "05_agents/tool_definition.py",
    "05_agents/tool_schema.py",
    "05_agents/agent_loop.py",
    "05_agents/agentic_rag.py",
    "06_langgraph/state_node_edge.py",
    "06_langgraph/conditional_edges.py",
    "06_langgraph/bounded_loop.py",
    "06_langgraph/checkpointer.py",
    "06_langgraph/human_in_the_loop.py",
    "06_langgraph/enterprise_rag_graph.py",
    "07_langsmith/trace.py",
    "07_langsmith/dataset.py",
    "07_langsmith/evaluation.py",
    "07_langsmith/feedback.py",
    "07_langsmith/monitoring_metrics.py",
    "08_enterprise/access_control.py",
    "08_enterprise/knowledge_updates.py",
    "08_enterprise/citations.py",
    "08_enterprise/cost_and_latency.py",
    "08_enterprise/fallbacks.py",
]
ONLINE_CONCEPT_DEMOS = {
    "03_models/chat_model.py",
    "03_models/stream_and_batch.py",
    "03_models/embeddings.py",
    "07_langsmith/trace.py",
}
OFFLINE_CONCEPT_DEMOS = [
    filename for filename in CONCEPT_DEMOS if filename not in ONLINE_CONCEPT_DEMOS
]
CHAPTER_DEMOS = [
    "01_chat_basics.py",
    "02_core_chain.py",
    "03_model_calling.py",
    "04_rag_pipeline.py",
    "05_agent_tools.py",
    "06_langgraph.py",
    "07_langsmith.py",
    "08_enterprise_rag.py",
]


@pytest.mark.parametrize("filename", CONCEPT_DEMOS)
def test_concept_demo_is_parseable_documented_and_runnable(filename: str) -> None:
    path = EXAMPLES_DIR / filename

    assert path.is_file(), f"缺少单概念示例：{filename}"
    source = path.read_text(encoding="utf-8")
    module = ast.parse(source, filename=filename)

    assert ast.get_docstring(module), f"{filename} 缺少模块说明"
    assert re.search(r"[\u4e00-\u9fff]", source), f"{filename} 缺少中文注释"
    assert any(
        isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
        and node.name == "main"
        for node in module.body
    ), f"{filename} 缺少 main() 入口"


def test_readme_indexes_every_concept_demo() -> None:
    readme = README_PATH.read_text(encoding="utf-8")

    for filename in CONCEPT_DEMOS:
        assert filename in readme, f"README 未索引：{filename}"


def test_concept_demos_are_not_flattened_in_examples_root() -> None:
    flattened = sorted(EXAMPLES_DIR.glob("[0-9][0-9]_[0-9][0-9]_*.py"))

    assert not flattened, f"单概念脚本仍在根目录：{flattened}"


def test_chapter_directories_contain_only_indexed_scripts() -> None:
    expected = {*CONCEPT_DEMOS, "03_models/common.py"}
    actual = {
        path.relative_to(EXAMPLES_DIR).as_posix()
        for path in EXAMPLES_DIR.glob("[0-9][0-9]_*/*.py")
    }

    assert actual == expected


def test_chapter_docs_index_every_concept_demo() -> None:
    ecosystem_dir = EXAMPLES_DIR.parent

    for filename in CONCEPT_DEMOS:
        chapter = Path(filename).parts[0][:2]
        document = ecosystem_dir / CHAPTER_DOCS[chapter]
        content = document.read_text(encoding="utf-8").replace("\\", "/")
        assert filename in content, f"{document.name} 未索引：{filename}"


@pytest.mark.parametrize("filename", CHAPTER_DEMOS)
def test_chapter_demo_has_guarded_main(filename: str) -> None:
    source = (EXAMPLES_DIR / filename).read_text(encoding="utf-8")
    module = ast.parse(source, filename=filename)

    assert any(
        isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
        and node.name == "main"
        for node in module.body
    ), f"{filename} 缺少 main() 入口"


def test_chapter_demos_import_without_api_keys() -> None:
    module_names = [Path(filename).stem for filename in CHAPTER_DEMOS]
    code = (
        "import importlib, sys; "
        f"sys.path.insert(0, {str(EXAMPLES_DIR)!r}); "
        f"[importlib.import_module(name) for name in {module_names!r}]"
    )
    env = os.environ.copy()
    env.update(
        {"OPENAI_API_KEY": "", "LANGSMITH_API_KEY": "", "LANGSMITH_TRACING": "false"}
    )
    result = subprocess.run(
        [sys.executable, "-c", code],
        cwd=PROJECT_ROOT,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr


@pytest.mark.parametrize("filename", OFFLINE_CONCEPT_DEMOS)
def test_offline_concept_demo_runs(filename: str) -> None:
    env = os.environ.copy()
    env.update(
        {"OPENAI_API_KEY": "", "LANGSMITH_API_KEY": "", "LANGSMITH_TRACING": "false"}
    )
    result = subprocess.run(
        [sys.executable, str(EXAMPLES_DIR / filename)],
        cwd=PROJECT_ROOT,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, f"{filename}\n{result.stderr}"


def test_vector_store_demo_returns_leave_policy() -> None:
    result = subprocess.run(
        [sys.executable, str(EXAMPLES_DIR / "04_rag" / "vector_store.py")],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    assert "员工每年享有 5 天年假" in result.stdout


@pytest.mark.parametrize("tracing_value", ["false", "1"])
def test_trace_demo_requires_tracing_enabled(
    monkeypatch: pytest.MonkeyPatch, tracing_value: str
) -> None:
    monkeypatch.setenv("LANGSMITH_API_KEY", "test-key")
    monkeypatch.setenv("LANGSMITH_TRACING", tracing_value)
    path = EXAMPLES_DIR / "07_langsmith" / "trace.py"
    spec = importlib.util.spec_from_file_location("langsmith_trace_demo", path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    with pytest.raises(RuntimeError, match="LANGSMITH_TRACING"):
        module.validate_langsmith_config()


@pytest.mark.parametrize(
    "filename", ["chat_model.py", "stream_and_batch.py", "embeddings.py"]
)
def test_nested_online_model_demo_finds_local_common(filename: str) -> None:
    env = os.environ.copy()
    env["OPENAI_API_KEY"] = ""
    result = subprocess.run(
        [sys.executable, str(EXAMPLES_DIR / "03_models" / filename)],
        cwd=PROJECT_ROOT,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode != 0
    assert "OPENAI_API_KEY is not configured" in result.stderr
    assert "ModuleNotFoundError" not in result.stderr
