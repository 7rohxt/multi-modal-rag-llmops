import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware  # Add this
from pydantic import BaseModel
import uvicorn
from main import main

app = FastAPI(title="Annual Report RAG API")

# Add CORS middleware - IMPORTANT!
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins (for development)
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods (GET, POST, etc.)
    allow_headers=["*"],  # Allows all headers
)

class QueryRequest(BaseModel):
    query: str


@app.post("/query")
def ask_question(req: QueryRequest):
    response = main(req.query)
    return {"response": response}


@app.get("/")
def health_check():
    return {"status": "ok", "message": "RAG server running"}

if __name__ == "__main__":
    uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=True)