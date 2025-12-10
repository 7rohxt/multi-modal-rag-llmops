import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

load_dotenv()

def load_generator_llm():
    return ChatOpenAI(
        model="gpt-4.1",
        temperature=0,
        openai_api_key=os.getenv("MY_OPENAI_API_KEY")  
    )

def build_context(reranked_docs, top_n=6):
    context = ""
    for doc in reranked_docs[:top_n]:
        context += doc.page_content + "\n\n"
    return context.strip()

def generate_answer_chat(query, generator_llm):
    return generator_llm.invoke(query).content

def generate_answer_rag(query, context, generator_llm, GENERATION_PROMPT):
    prompt = GENERATION_PROMPT.format(
        context=context,
        query=query
    )
    
    response = generator_llm.invoke(prompt)
    return response.content
