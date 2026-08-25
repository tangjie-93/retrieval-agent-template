"""Apply access filtering, source citations, and a no-answer fallback to RAG."""

from langchain_core.documents import Document
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_openai import OpenAIEmbeddings

from common import get_chat_model


documents = [
    Document(
        page_content="员工工作满一年后，每年享有 5 天年假。",
        metadata={"source": "leave-policy.md", "roles": ["employee", "hr"]},
    ),
    Document(
        page_content="高管差旅标准为商务舱，报销时需附行程单。",
        metadata={"source": "executive-travel.md", "roles": ["executive"]},
    ),
]
user_role = "employee"
permitted_documents = [
    document for document in documents if user_role in document.metadata["roles"]
]
vector_store = InMemoryVectorStore(OpenAIEmbeddings())
vector_store.add_documents(permitted_documents)

question = "员工工作满一年有几天年假？"
retrieved = vector_store.similarity_search(question, k=2)
if not retrieved:
    print("未找到你有权限访问的制度，无法回答。")
else:
    context = "\n".join(
        f"[{document.metadata['source']}] {document.page_content}"
        for document in retrieved
    )
    prompt = ChatPromptTemplate.from_messages([
        ("system", "Only use the context. Answer in Chinese and retain every source tag."),
        ("human", "Question: {question}\nContext:\n{context}"),
    ])
    chain = prompt | get_chat_model() | StrOutputParser()
    print(chain.invoke({"question": question, "context": context}))

