from src.retrieval import get_embedding_model, load_faiss_index, get_bm25_retriever, retrieve_candidates, show
from src.rerankers import load_reranker, rerank_documents, show_reranked
from src.router import load_router_llm, route_query
from src.generation import generate_answer_rag, load_generator_llm, build_context, generate_answer_chat
from src.prompts import ROUTER_PROMPT, GENERATION_PROMPT

def main (query: str):
     # Router 
    router_llm = load_router_llm()
    generator_llm = load_generator_llm()
    router_decision = route_query(query, router_llm, ROUTER_PROMPT)
    # print(router_response)
    if router_decision == "direct":
        return generate_answer_chat(query, generator_llm)
    
    
    # Retriever
    embedding_model = get_embedding_model()
    vectorstore = load_faiss_index(embedding_model, index_path="faiss_index")
    all_docs = list(vectorstore.docstore._dict.values())
    bm25_retriever   = get_bm25_retriever(all_docs)
    retrieved_docs = retrieve_candidates(query, bm25_retriever, vectorstore, k_bm25=10, k_sem=10)
    # show(retrieved_docs)

    # Reranker
    reranker = load_reranker()
    reranked_docs = rerank_documents(query, reranker, retrieved_docs, top_k=10)
    # show_reranked(reranked_docs)

    # Generator
    context = build_context(reranked_docs)
    assistant_response = generate_answer_rag(query, context, generator_llm, reranked_docs, GENERATION_PROMPT)
    return assistant_response

if __name__ == "__main__":
    query = "Explain Microsoft's cloud revenue growth in 2024."
    query = "hi"
    asssistant_response = main(query)
    print(asssistant_response)