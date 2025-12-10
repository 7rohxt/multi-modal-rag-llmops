from src.retrieval import get_embedding_model, load_faiss_index, get_bm25_retriever, retrieve_candidates, show
from src.rerankers import load_reranker, rerank_documents, show_reranked
from src.router import load_router_llm, route_query
from src.generation import generate_answer_rag, load_generator_llm, build_context, generate_answer_chat
from src.caching import load_redis_client, cache_get, cache_set
from src.memory import build_memory_chain, generate_answer_chat_memory, memory_set 
from src.prompts import ROUTER_PROMPT, GENERATION_PROMPT, get_chat_prompt

redis_client = load_redis_client()
router_llm = load_router_llm()
generator_llm = load_generator_llm()

embedding_model = get_embedding_model()
vectorstore = load_faiss_index(embedding_model, index_path="faiss_index")
all_docs = list(vectorstore.docstore._dict.values())
bm25_retriever   = get_bm25_retriever(all_docs)

reranker = load_reranker()

session_id = 1

def main (query: str):

    # -------------------- Router --------------------
    router_decision = route_query(query, router_llm, ROUTER_PROMPT)


    if router_decision == "direct":
        # -------------------- Memory (For Non Rag Questions) --------------------
        memory_chain = build_memory_chain(generator_llm, get_chat_prompt())
        assistant_response = generate_answer_chat_memory(query, 1, memory_chain )
        cache_set(query, assistant_response, redis_client) 
        return assistant_response
    

    # --------------------Redis Caching--------------------
    cached = cache_get(query, redis_client)
    if cached:
        print("CACHE HIT")
        memory_set(session_id, query, cached) 
        return cached
    print("CACHE MISS → Running full RAG pipeline...")


    # --------------------Retriever--------------------
    retrieved_docs = retrieve_candidates(query, bm25_retriever, vectorstore, k_bm25=10, k_sem=10)


    # --------------------Reranker--------------------
    reranked_docs = rerank_documents(query, reranker, retrieved_docs, top_k=10)


    # --------------------Generator--------------------
    context = build_context(reranked_docs)
    assistant_response = generate_answer_rag(query, context, generator_llm, GENERATION_PROMPT)
    cache_set(query, assistant_response, redis_client)

    memory_set(1, query, assistant_response)
    return assistant_response



if __name__ == "__main__":
    query = "Explain Microsoft's cloud revenue growth in 2024."
    # query = "My phone number is 95XXXXXXX8"
    asssistant_response = main(query)
    print(asssistant_response)
    query = "what was my previous message?"
    asssistant_response = main(query)
    print(asssistant_response)