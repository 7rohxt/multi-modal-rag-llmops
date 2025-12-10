from sentence_transformers import CrossEncoder

# bge reranker
def load_reranker():
    return CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")

def rerank_documents(query, reranker, docs, top_k=10):
    if not docs:
        return []

    # build pairs (query, doc_text)
    pairs = [(query, d.page_content) for d in docs]

    # run cross encoder scoring
    scores = reranker.predict(pairs)

    # attach scores to docs
    for doc, score in zip(docs, scores):
        doc.metadata["rerank_score"] = float(score)

    # sort by score (descending)
    ranked = sorted(docs, key=lambda x: x.metadata["rerank_score"], reverse=True)

    return ranked[:top_k]

def show_reranked(docs, top_n=10):
    for i, d in enumerate(docs[:top_n]):
        print(f"--- Rank {i+1} | Score: {d.metadata['rerank_score']:.4f} ---")
        print(d.page_content[:300], "...")
        print("Metadata:", d.metadata)
        print("\n")
