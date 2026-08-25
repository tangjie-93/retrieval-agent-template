"""Exercise Message, Prompt, Runnable, and structured output with ChatGPT."""

from typing import Literal

from pydantic import BaseModel, Field

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate

from common import get_chat_model


class PolicyAnswer(BaseModel):
    """The fields required by the application."""

    answer: str = Field(description="A concise answer in Chinese.")
    confidence: Literal["high", "medium", "low"]


llm = get_chat_model()
messages = [
    SystemMessage(content="You answer enterprise policy questions in Chinese."),
    HumanMessage(content="年假制度通常应包含哪些信息？"),
]
print("=== Message ===")
print(llm.invoke(messages).content)

prompt = ChatPromptTemplate.from_messages([
    ("system", "Only use the supplied context. Return the requested schema."),
    ("human", "Question: {question}\nContext: {context}"),
])
chain = prompt | llm.with_structured_output(PolicyAnswer)
result = chain.invoke({
    "question": "工作满一年有几天年假？",
    "context": "员工工作满一年后，每年享有 5 天年假。",
})
print("\n=== Runnable + structured output ===")
print(result.model_dump_json(indent=2))

