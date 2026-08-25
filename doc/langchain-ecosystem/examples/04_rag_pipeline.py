"""Run a complete local RAG pipeline using OpenAI embeddings and ChatGPT."""

from langchain_core.documents import Document
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

from common import get_chat_model


documents = [
    Document(
        page_content="员工工作满一年后，每年享有 5 天年假。年假应在当年使用。",
        metadata={"source": "leave-policy.md"},
    ),
    Document(
        page_content="单笔超过 5000 元的报销，必须经部门负责人审批后提交财务。",
        metadata={"source": "expense-policy.md"},
    ),
]
splits = RecursiveCharacterTextSplitter(chunk_size=100, chunk_overlap=20).split_documents(
    documents
)
vector_store = InMemoryVectorStore(OpenAIEmbeddings())
vector_store.add_documents(splits)

question = "工作满一年有几天年假？"
retrieved = vector_store.similarity_search(question, k=2)
context = "\n\n".join(
    f"[{document.metadata['source']}] {document.page_content}" for document in retrieved
)
prompt = ChatPromptTemplate.from_messages([
    ("system", "Use only the supplied context. Answer in Chinese and cite [source]."),
    ("human", "Question: {question}\n\nContext:\n{context}"),
])
chain = prompt | get_chat_model() | StrOutputParser()

print("=== Retrieved context ===")
print(context)
print("\n=== Answer ===")
print(chain.invoke({"question": question, "context": context}))

