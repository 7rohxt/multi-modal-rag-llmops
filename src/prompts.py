ROUTER_PROMPT = """
Decide whether the user query requires retrieving information from a financial document dataset.

Return ONLY one word:
- "rag" → if the answer depends on financial reports (Amazon, Apple, Microsoft, Meta, NVIDIA annual reports)
- "direct" → if the query can be answered directly without retrieval.

User query: {query}
"""