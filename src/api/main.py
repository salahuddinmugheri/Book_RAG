import os
import sys
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

allowed_origins_raw = os.getenv("ALLOWED_ORIGINS", "*")
allowed_origins = [o.strip() for o in allowed_origins_raw.split(",")] if allowed_origins_raw != "*" else ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add the project root (book_RAG/) to Python's import path,
# so we can import from the sibling "scripts" folder.
sys.path.append(str(Path(__file__).resolve().parents[2]))

from scripts.rag import ask_question


@app.post("/api/ask")
@app.post("/ask")
def ask(payload: dict):
    question = payload.get("question", "").strip()

    if not question:
        return {"error": "Question is required."}

    try:
        result = ask_question(question)
        return result
    except Exception as e:
        print(f"Error in /ask handler: {e}")
        return {"error": str(e)}