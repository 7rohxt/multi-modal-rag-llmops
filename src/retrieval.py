import os
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from langchain_core.documents import Document
from dotenv import load_dotenv
from langchain_community.retrievers import BM25Retriever

load_dotenv()

def get_embedding_model():
    return OpenAIEmbeddings(
        model="text-embedding-3-large",
        openai_api_key=os.getenv("MY_OPENAI_API_KEY")
    )

def load_faiss_index(embedding, index_path="faiss_index"):
    vectorstore = FAISS.load_local(
        index_path,
        embeddings=embedding,
        allow_dangerous_deserialization=True
    )
    print("FAISS index loaded.")
    return vectorstore


def semantic_retrieve(query, vectorstore, k=10):
    return vectorstore.similarity_search(query, k=k)


def deduplicate_docs(docs):
    seen = set()
    unique = []

    for doc in docs:
        key = (
            doc.metadata.get("source"),
            doc.metadata.get("page"),
            doc.page_content[:50]  # stable enough signature
        )
        if key not in seen:
            unique.append(doc)
            seen.add(key)

    return unique


def get_bm25_retriever(docs, k=10):
    retriever = BM25Retriever.from_documents(docs)
    retriever.k = k
    return retriever


def retrieve_candidates(query, bm25_retriever, vectorstore, k_bm25=10, k_sem=10):
    # 1) keyword results
    bm25_retriever.k = k_bm25
    bm25_docs = bm25_retriever.invoke(query)
    
    # 2) semantic vector results
    semantic_docs = semantic_retrieve(query, vectorstore, k=k_sem)

    # 3) Combine
    combined = bm25_docs + semantic_docs

    # 4) Deduplicate
    combined = deduplicate_docs(combined)

    print(f"BM25 retrieved: {len(bm25_docs)} chunks")
    print(f"Semantic retrieved: {len(semantic_docs)} chunks")
    print(f"Combined unique: {len(combined)}")

    return combined

def show(results):
    for i, doc in enumerate(results):
        print(f"\n----- Chunk {i+1} -----")
        print("Source:", doc.metadata["source"])
        print("Page:", doc.metadata["page"])
        print(doc.page_content[:300], "...")