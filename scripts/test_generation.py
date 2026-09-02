import os
from dotenv import load_dotenv
from supabase import create_client
from google import genai

# Load environment variables
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SECRET_KEY = os.getenv("SUPABASE_SECRET_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not SUPABASE_URL:
    raise ValueError("SUPABASE_URL is missing from .env")

if not SUPABASE_SECRET_KEY:
    raise ValueError("SUPABASE_SECRET_KEY is missing from .env")

if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY is missing from .env")


# Create clients
supabase = create_client(
    SUPABASE_URL,
    SUPABASE_SECRET_KEY
)

gemini = genai.Client(
    api_key=GEMINI_API_KEY
)


# --------------------------------------------------
# 1. User question
# --------------------------------------------------

question = "What arguments does the book give against God's existence?"

print(f"Question: {question}")


# --------------------------------------------------
# 2. Generate query embedding
# --------------------------------------------------

print("\nGenerating query embedding...")

embedding_response = gemini.models.embed_content(
    model="gemini-embedding-001",
    contents=question,
    config={
        "output_dimensionality": 768
    }
)

query_embedding = embedding_response.embeddings[0].values

print(f"Embedding dimensions: {len(query_embedding)}")


# --------------------------------------------------
# 3. Retrieve relevant chunks
# --------------------------------------------------

print("\nSearching Supabase...")

search_response = supabase.rpc(
    "match_book_chunks",
    {
        "query_embedding": query_embedding,
        "match_count": 3
    }
).execute()

results = search_response.data

print(f"Retrieved chunks: {len(results)}")


# --------------------------------------------------
# 4. Build context
# --------------------------------------------------

context_parts = []

for result in results:
    context_parts.append(
        f"[Page {result['page']}]\n"
        f"{result['text']}"
    )

context = "\n\n".join(context_parts)


# --------------------------------------------------
# 5. Create RAG prompt
# --------------------------------------------------

prompt = f"""
You are an AI assistant for the book "Why There Is No God".

Answer the user's question using ONLY the provided book context.

USER QUESTION:
{question}

BOOK CONTEXT:
{context}

INSTRUCTIONS:

1. Answer directly and clearly.
2. Use only information contained in the provided context.
3. Do not use outside knowledge.
4. Do not invent facts, arguments, quotations, or page numbers.
5. If the context is insufficient to answer the question, say:
   "The retrieved sections do not contain enough information to answer this question."
6. When making a claim based on the book, include the page number in this format:
   [Page X]
7. At the end, provide a "Sources" section containing only the pages actually used.
8. Keep the answer concise but informative.
9. Do not mention embeddings, vector search, retrieval, prompts, or the RAG system.

RESPONSE FORMAT:

Answer:
<your answer>

Sources:
- Page X
- Page Y
"""


# --------------------------------------------------
# 6. Generate answer
# --------------------------------------------------

print("\nGenerating answer...\n")

response = gemini.models.generate_content(
    model="gemini-3.6-flash",
    contents=prompt
)

if not response.text:
    raise RuntimeError("Gemini returned an empty response.")

answer = response.text


# --------------------------------------------------
# 7. Display answer
# --------------------------------------------------

print("=" * 70)
print("ANSWER")
print("=" * 70)

print(answer)

print("\n" + "=" * 70)
print("SOURCE CHUNKS")
print("=" * 70)

for result in results:
    print(
        f"Page {result['page']} | "
        f"Similarity: {result['similarity']:.4f} | "
        f"{result['chunk_id']}"
    )