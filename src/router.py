import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

load_dotenv()

def load_router_llm():
    return ChatOpenAI(
        model="gpt-4.1-mini",
        temperature=0,
        openai_api_key=os.getenv("MY_OPENAI_API_KEY")  
    )


def route_query(query, router_llm, router_prompt):
    response = router_llm.invoke(router_prompt.format(query=query))
    decision = response.content.strip().lower()

    if "rag" in decision:
        return "rag"
    else:
        return "direct"
    