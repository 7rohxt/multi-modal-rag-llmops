ROUTER_PROMPT = """
Decide whether the user query requires retrieving information from a financial document dataset.

Return ONLY one word:
- "rag" → if the answer depends on financial reports (Amazon, Apple, Microsoft, Meta, NVIDIA annual reports)
- "direct" → if the query can be answered directly without retrieval.

User query: {query}
"""

GENERATION_PROMPT = """
You are an expert financial assistant. Answer the user's question STRICTLY based on the provided context from annual reports.

If the context does not contain the answer, say:
"I cannot find this information in the available documents."

--------------------
CONTEXT:
{context}
--------------------

QUESTION:
{query}

Final Answer:
"""