"""Run the smallest LangChain request backed by OpenAI ChatGPT."""

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate

from common import get_chat_model


prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a concise enterprise knowledge assistant."),
    ("human", "Answer this question in Chinese: {question}"),
])
chain = prompt | get_chat_model() | StrOutputParser()

print(chain.invoke({"question": "什么是 RAG？"}))

