"""Shared configuration for the LangChain ecosystem demos."""

import os

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI


def get_chat_model() -> ChatOpenAI:
    """Create the ChatGPT model used by all examples."""
    load_dotenv()
    if not os.getenv("OPENAI_API_KEY"):
        raise RuntimeError(
            "OPENAI_API_KEY is not configured. Copy .env.example to .env and set it."
        )
    return ChatOpenAI(
        model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
        temperature=0,
    )

