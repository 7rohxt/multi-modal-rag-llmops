import os
from langchain_openai import OpenAIEmbeddings
from langchain_core.documents import Document
from dotenv import load_dotenv
import os

from aws_infra.opensearch.client import get_opensearch_client
   

load_dotenv()


def get_embedding_model():
    return OpenAIEmbeddings(
        model="text-embedding-3-large",
        openai_api_key=os.getenv("MY_OPENAI_API_KEY")
    )




def load_opensearch():
    client = get_opensearch_client()
    print("OpenSearch client ready.")
    return client


from langchain_core.documents import Document

def semantic_retrieve_os(query, client, embedder, index_name, k=10):
    query_vector = embedder.embed_query(query)

    response = client.search(
        index=index_name,
        body={
            "size": k,
            "query": {
                "knn": {
                    "embedding": {
                        "vector": query_vector,
                        "k": k
                    }
                }
            }
        }
    )

    docs = []
    for hit in response["hits"]["hits"]:
        src = hit["_source"]
        docs.append(
            Document(
                page_content=src["content"],
                metadata={
                    "source": src.get("source"),
                    "company": src.get("company"),
                    "year": src.get("year"),
                    "doctype": src.get("doctype"),
                }
            )
        )

    return docs


def bm25_retrieve_os(query, client, index_name, k=10):
    response = client.search(
        index=index_name,
        body={
            "size": k,
            "query": {
                "match": {
                    "content": {
                        "query": query
                    }
                }
            }
        }
    )

    docs = []
    for hit in response["hits"]["hits"]:
        src = hit["_source"]
        docs.append(
            Document(
                page_content=src["content"],
                metadata={
                    "source": src.get("source"),
                    "company": src.get("company"),
                    "year": src.get("year"),
                    "doctype": src.get("doctype"),
                }
            )
        )

    return docs


def deduplicate_docs(docs):
    seen = set()
    unique = []

    for doc in docs:
        key = (
            doc.metadata.get("source"),
            doc.page_content[:50]
        )
        if key not in seen:
            unique.append(doc)
            seen.add(key)

    return unique


def retrieve_candidates_os(
    query,
    client,
    embedder,
    index_name,
    k_bm25=10,
    k_sem=10
):
    # 1) BM25
    bm25_docs = bm25_retrieve_os(query, client, index_name, k=k_bm25)

    # 2) Semantic
    semantic_docs = semantic_retrieve_os(
        query, client, embedder, index_name, k=k_sem
    )

    # 3) Combine
    combined = bm25_docs + semantic_docs

    # 4) Deduplicate
    combined = deduplicate_docs(combined)

    print(f"BM25 retrieved: {len(bm25_docs)}")
    print(f"Semantic retrieved: {len(semantic_docs)}")
    print(f"Combined unique: {len(combined)}")

    return combined


def show(results, preview_chars=300):
    for i, doc in enumerate(results):
        print(f"\n----- Chunk {i + 1} -----")
        print("Source:", doc.metadata.get("source"))
        print("Company:", doc.metadata.get("company"))
        print("Year:", doc.metadata.get("year"))
        print("Doctype:", doc.metadata.get("doctype"))
        print("\nContent Preview:")
        print(doc.page_content[:preview_chars], "...")


if __name__ == "__main__":
    embedder = get_embedding_model()
    client = load_opensearch()

    results = retrieve_candidates_os(
        query="Explain total revenue in 2024",
        client=client,
        embedder=embedder,
        index_name="rag-docs"
    )

    show(results)