from langchain_openai import ChatOpenAI
from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
import os

# src/memory.py

from langchain_openai import ChatOpenAI
from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from dotenv import load_dotenv
import os

load_dotenv()


# ---------------- MEMORY STORE ----------------
_store = {}   # Only a data structure, no logic



def get_history(session_id: str):
    """Return or create session-specific chat history."""
    return _store.setdefault(session_id, InMemoryChatMessageHistory())


def build_memory_chain(llm, chat_prompt):
    """Create and return a memory-enabled LangChain runnable."""
    
    chain = chat_prompt | llm

    with_memory = RunnableWithMessageHistory(
        chain,
        lambda session_id: get_history(session_id),
        input_messages_key="input",
        history_messages_key="history"
    )
    return with_memory


# ---------------- PUBLIC FUNCTION ----------------

def generate_answer_chat_memory(query: str, session_id: str, memory_chain=None):
    """
    Invoke the memory-enabled chat model for the given session.
    Caller must pass a pre-built memory_chain.
    """

    if memory_chain is None:
        # fallback (optional): build a temporary chain
        memory_chain = build_memory_chain()

    result = memory_chain.invoke(
        {"input": query},
        config={"configurable": {"session_id": session_id}}
    )
    return result.content

def memory_set(session_id: str, human: str = None, assistant: str = None):

    history = get_history(session_id)

    if human is not None:
        history.add_user_message(human)

    if assistant is not None:
        history.add_ai_message(assistant)