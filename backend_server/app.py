import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI
from pydantic import BaseModel
import uvicorn
from main import main   # Import your existing pipeline

app = FastAPI(title="Annual Report RAG API")

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