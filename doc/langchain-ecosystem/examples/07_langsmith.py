"""Generate an OpenAI trace visible in LangSmith."""

import os

from dotenv import load_dotenv
from langsmith import traceable

from common import get_chat_model


load_dotenv()
if not os.getenv("LANGSMITH_API_KEY"):
    raise RuntimeError(
        "LANGSMITH_API_KEY is not configured. Add it to .env before running this demo."
    )


@traceable(name="ecosystem-demo-answer")
def answer(question: str) -> str:
    """Create a trace containing one ChatGPT call."""
    return get_chat_model().invoke(question).content


print(answer("用一句中文解释 LangSmith 的作用。"))
