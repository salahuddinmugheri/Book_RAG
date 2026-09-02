import sys
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add the project root (book_RAG/) to Python's import path,
# so we can import from the sibling "scripts" folder.
sys.path.append(str(Path(__file__).resolve().parents[2]))

from scripts.rag import ask_question


@app.post("/ask")
def ask(payload: dict):
    question = payload.get("question", "").strip()

    if not question:
        return {"error": "Question is required."}

    result = ask_question(question)
    return result