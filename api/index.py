import os
import sys
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Add the project root to Python sys.path
sys.path.append(str(Path(__file__).resolve().parent.parent))

from scripts.rag import ask_question

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
