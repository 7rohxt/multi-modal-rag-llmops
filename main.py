from src.retrieval import get_embedding_model, load_faiss_index, get_bm25_retriever, retrieve_candidates, show
from src.rerankers import load_reranker, rerank_documents, show_reranked
from src.router import load_router_llm, route_query
from src.generation import generate_answer_rag, load_generator_llm, build_context, generate_answer_chat
from src.caching import load_redis_client, cache_get, cache_set
from src.prompts import ROUTER_PROMPT, GENERATION_PROMPT

def main (query: str):

    # -------------------- Router --------------------
    redis_client = load_redis_client()
    router_llm = load_router_llm()
    generator_llm = load_generator_llm()
    router_decision = route_query(query, router_llm, ROUTER_PROMPT)
    if router_decision == "direct":
        assistant_response = generate_answer_chat(query, generator_llm)
        cache_set(query, assistant_response, redis_client)
        return assistant_response
    

    # --------------------Redis Caching--------------------
    redis_client = load_redis_client()
    cached = cache_get(query, redis_client)
    if cached:
        print("CACHE HIT")
        return cached
    print("CACHE MISS → Running full RAG pipeline...")


    # --------------------Retriever--------------------
    embedding_model = get_embedding_model()
    vectorstore = load_faiss_index(embedding_model, index_path="faiss_index")
    all_docs = list(vectorstore.docstore._dict.values())
    bm25_retriever   = get_bm25_retriever(all_docs)
    retrieved_docs = retrieve_candidates(query, bm25_retriever, vectorstore, k_bm25=10, k_sem=10)


    # --------------------Reranker--------------------
    reranker = load_reranker()
    reranked_docs = rerank_documents(query, reranker, retrieved_docs, top_k=10)


    # --------------------Generator--------------------
    context = build_context(reranked_docs)
    assistant_response = generate_answer_rag(query, context, generator_llm, GENERATION_PROMPT)
    cache_set(query, assistant_response, redis_client)
    return assistant_response



if __name__ == "__main__":
    query = "Explain Microsoft's cloud revenue growth in 2024."
    query = "hi"
    asssistant_response = main(query)
    print(asssistant_response)