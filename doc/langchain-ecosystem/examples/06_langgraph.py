"""Build and execute a minimal LangGraph with an OpenAI model node."""

from typing import TypedDict

from langgraph.graph import END, START, StateGraph

from common import get_chat_model


class GraphState(TypedDict):
    question: str
    answer: str


def answer_question(state: GraphState) -> dict[str, str]:
    """Call ChatGPT from a graph node."""
    response = get_chat_model().invoke(
        f"用一句中文回答下面的问题：{state['question']}"
    )
    return {"answer": response.content}


builder = StateGraph(GraphState)
builder.add_node("answer_question", answer_question)
builder.add_edge(START, "answer_question")
builder.add_edge("answer_question", END)
graph = builder.compile()

result = graph.invoke({"question": "LangGraph 适合解决什么问题？"})
print(result["answer"])

