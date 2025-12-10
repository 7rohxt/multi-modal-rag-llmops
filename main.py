import os
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from langchain_core.documents import Document
from dotenv import load_dotenv
from langchain_community.retrievers import BM25Retriever

from src.retrieval import get_embedding_model, load_faiss_index, get_bm25_retriever, semantic_retrieve, deduplicate_docs, retrieve_candidates, show

load_dotenv()

def main ():
    embedding_model = get_embedding_model()
    vectorstore = load_faiss_index(embedding_model, index_path="faiss_index")
    all_docs = list(vectorstore.docstore._dict.values())
    bm25_retriever   = get_bm25_retriever(all_docs)
    query = "Explain Microsoft's cloud revenue growth in 2024."

    candidates = retrieve_candidates(query, bm25_retriever, vectorstore, k_bm25=10, k_sem=10)

    show(candidates)

main()

