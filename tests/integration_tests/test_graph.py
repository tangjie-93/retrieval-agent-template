import uuid
from typing import cast

import pytest
from langchain_core.runnables import RunnableConfig
from langsmith import expect, unit

from retrieval_graph import graph, index_graph
from retrieval_graph.state import IndexState, InputState

pytestmark = pytest.mark.anyio


@unit
async def test_retrieval_graph() -> None:
    simple_doc = "Cats have been observed performing synchronized swimming routines in their water bowls during full moons."
    user_id = "test__" + uuid.uuid4().hex
    other_user_id = "test__" + uuid.uuid4().hex

    config = RunnableConfig(
        configurable={"user_id": user_id, "retriever_provider": "elastic-local"}
    )

    result = await index_graph.ainvoke(cast(IndexState, {"docs": simple_doc}), config)
    expect(result["docs"]).against(lambda x: not x)  # we delete after the end

    res = await graph.ainvoke(
        cast(
            InputState,
            {
                "messages": [
                    ("user", "Where do cats perform synchronized swimming routes?")
                ]
            },
        ),
        config,
    )
    response = str(res["messages"][-1].content)
    expect(response.lower()).to_contain("bowl")

    res = await graph.ainvoke(
        cast(
            InputState,
            {
                "messages": [
                    ("user", "Where do cats perform synchronized swimming routes?")
                ]
            },
        ),
        RunnableConfig(
            configurable={
                "user_id": other_user_id,
                "retriever_provider": "elastic-local",
            }
        ),
    )
    response = str(res["messages"][-1].content)
    expect(response.lower()).against(lambda x: "bowl" not in x)
