from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
from main import main

app = FastAPI(title="Annual Report RAG API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class QueryRequest(BaseModel):
    query: str


@app.post("/query")
def ask_question(req: QueryRequest):
    response, metadata = main(req.query)  # Get both response and metadata
    return {
        "response": response,
        "metadata": metadata
    }


@app.get("/")
def health_check():
    return {"status": "ok", "message": "RAG server running"}

if __name__ == "__main__":
    uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=True)