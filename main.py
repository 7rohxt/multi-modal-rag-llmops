from src.retrieval import get_embedding_model, retrieve_candidates_os
from src.rerankers import load_reranker, rerank_documents
from src.router import load_router_llm, route_query
from src.generation import generate_answer_rag, load_generator_llm, build_context, generate_answer_chat
from src.caching import load_redis_client, cache_get, cache_set
from src.memory import initialize_redis, build_memory_chain, generate_answer_chat_memory, memory_set 
from src.guardrails import inbound_check, outbound_check
from src.prompts import ROUTER_PROMPT, GENERATION_PROMPT, get_chat_prompt
from src.aws_infra.opensearch.client import get_opensearch_client
import os 

redis_client = load_redis_client()

initialize_redis(redis_client)  # for src/memory.py

router_llm = load_router_llm()
generator_llm = load_generator_llm()

embedding_model = get_embedding_model()
opensearch_client = get_opensearch_client()

reranker = load_reranker()

session_id = 1
opensearch_index_name="rag-docs"

def main(query: str):
    # Track metadata
    metadata = {}

    # -------------------- Inbound Check - Guardrails --------------------    
    inbound = inbound_check(query)
    if inbound["status"] == "blocked":
        blocked_message = inbound["message"]
        metadata["guardrail_blocked"] = True
        metadata["guardrail_reason"] = inbound.get("reason", "Unknown")
        memory_set(session_id, query, blocked_message) 
        return blocked_message, metadata
    
    query = inbound["cleaned_query"]

    # -------------------- Router --------------------
    router_decision = route_query(query, router_llm, ROUTER_PROMPT)
    metadata["router"] = router_decision

    if router_decision == "direct":
        # -------------------- Memory (For Non RAG Questions) --------------------
        memory_chain = build_memory_chain(generator_llm, get_chat_prompt())
        assistant_response = generate_answer_chat_memory(query, session_id, memory_chain)
        metadata["generated"] = True
        memory_set(session_id, query, assistant_response) 
        return assistant_response, metadata

    # -------------------- Redis Caching --------------------
    cached = cache_get(query, redis_client)
    if cached:
        print("CACHE HIT")
        metadata["cache"] = "hit"
        memory_set(session_id, query, cached) 
        return cached, metadata
    
    print("CACHE MISS → Running full RAG pipeline...")
    metadata["cache"] = "miss"

    len_bm25_docs, len_semantic_docs, len_combined, retrieved_docs = retrieve_candidates_os(query, opensearch_client, embedding_model, opensearch_index_name, k_bm25=10, k_sem=10)

    # Add detailed breakdown
    metadata["bm25_chunks"] = len_bm25_docs 
    metadata["semantic_chunks"] = len_semantic_docs  
    metadata["retrieved_chunks"] = len_combined

        # -------------------- Reranker --------------------
    reranked_docs = rerank_documents(query, reranker, retrieved_docs, top_k=10)
    metadata["reranked_chunks"] = len(reranked_docs)

    # -------------------- Generator --------------------
    context = build_context(reranked_docs)
    assistant_response = generate_answer_rag(query, context, generator_llm, GENERATION_PROMPT)
    metadata["generated"] = True
    
    cache_set(query, assistant_response, redis_client)

    # -------------------- Outbound Check - Guardrails --------------------
    safe_output = outbound_check(assistant_response)

    # -------------------- Save Output To Memory --------------------
    memory_set(session_id, query, safe_output)

    return safe_output, metadata


if __name__ == "__main__":
    query1 = "Explain total revenue in 2024."
    response, metadata = main(query1)
    print("Response:", response)
    print("Metadata:", metadata)
    query2 = "what was my previous question?."
    response, metadata = main(query2)
    print("Response:", response)
    print("Metadata:", metadata)