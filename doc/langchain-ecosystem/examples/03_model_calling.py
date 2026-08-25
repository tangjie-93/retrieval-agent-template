"""Use OpenAI ChatGPT for invocation, streaming, batching, and embeddings."""

from langchain_openai import OpenAIEmbeddings

from common import get_chat_model


llm = get_chat_model()

print("=== invoke ===")
print(llm.invoke("用一句中文解释什么是向量检索。").content)

print("\n=== stream ===")
for chunk in llm.stream("用一句中文解释什么是 PromptTemplate。"):
    print(chunk.content, end="", flush=True)
print()

print("\n=== batch ===")
answers = llm.batch(["RAG 中的检索负责什么？", "RAG 中的生成负责什么？"])
for answer in answers:
    print(answer.content)

print("\n=== embedding ===")
embedding = OpenAIEmbeddings().embed_query("员工年假制度")
print(f"dimension={len(embedding)}")

