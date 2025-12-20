from langchain_openai import ChatOpenAI
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from dotenv import load_dotenv
import os
import json

load_dotenv()


# ---------------- REDIS-BACKED CHAT HISTORY ----------------

class RedisChatMessageHistory(BaseChatMessageHistory):
    """Chat message history stored in Redis."""
    
    def __init__(self, session_id: str, redis_client, ttl: int = 86400):
        self.session_id = session_id
        self.redis = redis_client
        self.ttl = ttl
        self.key = f"session:{session_id}:messages"
    
    @property
    def messages(self):
        """Retrieve messages from Redis."""
        raw_messages = self.redis.lrange(self.key, 0, -1)
        messages = []
        
        for raw in raw_messages:
            data = json.loads(raw)
            if data["type"] == "human":
                messages.append(HumanMessage(content=data["content"]))
            elif data["type"] == "ai":
                messages.append(AIMessage(content=data["content"]))
        
        return messages
    
    def add_message(self, message: BaseMessage):
        """Add a message to Redis."""
        if isinstance(message, HumanMessage):
            msg_type = "human"
        elif isinstance(message, AIMessage):
            msg_type = "ai"
        else:
            msg_type = "generic"
        
        data = {
            "type": msg_type,
            "content": message.content
        }
        
        self.redis.rpush(self.key, json.dumps(data))
        self.redis.expire(self.key, self.ttl)
    
    def clear(self):
        """Clear all messages for this session."""
        self.redis.delete(self.key)


# ---------------- MEMORY STORE ----------------

_redis_client = None  # Will be set by initialize_redis()


def initialize_redis(redis_client):
    """Initialize Redis client for session storage."""
    global _redis_client
    _redis_client = redis_client
    # print("✅ Redis initialized for session memory")


def get_history(session_id: str):
    """Return or create Redis-backed chat history for session."""
    if _redis_client is None:
        raise RuntimeError("Redis not initialized. Call initialize_redis() first.")
    
    return RedisChatMessageHistory(session_id, _redis_client)


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


# ---------------- PUBLIC FUNCTIONS ----------------

def generate_answer_chat_memory(query: str, session_id: str, memory_chain=None):
    """
    Invoke the memory-enabled chat model for the given session.
    Caller must pass a pre-built memory_chain.
    """
    if memory_chain is None:
        raise ValueError("memory_chain must be provided")

    result = memory_chain.invoke(
        {"input": query},
        config={"configurable": {"session_id": session_id}}
    )
    
    # print(f"💬 [Session {session_id}] User: {query}")
    # print(f"💬 [Session {session_id}] Assistant: {result.content[:100]}...")
    
    return result.content


def memory_set(session_id: str, human: str = None, assistant: str = None):
    """Manually add messages to session history."""
    history = get_history(session_id)

    if human is not None:
        history.add_user_message(human)
        # print(f"💬 [Session {session_id}] Saved User: {human}")

    if assistant is not None:
        history.add_ai_message(assistant)
        # print(f"💬 [Session {session_id}] Saved Assistant: {assistant[:100]}...")