import json
import os
import time

from dotenv import load_dotenv
from google import genai


# --------------------------------------------------
# Configuration
# --------------------------------------------------

CHUNKS_PATH = "data/chunks.json"
OUTPUT_PATH = "data/embeddings.json"

MODEL_NAME = "gemini-embedding-001"
OUTPUT_DIMENSIONALITY = 768

# Keep this small because the free tier has request limits.
BATCH_SIZE = 10

# Maximum number of times we retry a rate-limit error.
MAX_RETRIES = 5


# --------------------------------------------------
# Load environment variables
# --------------------------------------------------

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError("GEMINI_API_KEY not found in .env")


# --------------------------------------------------
# Create Gemini client
# --------------------------------------------------

client = genai.Client(api_key=api_key)


# --------------------------------------------------
# Load chunks
# --------------------------------------------------

with open(CHUNKS_PATH, "r", encoding="utf-8") as f:
    chunks = json.load(f)

print(f"Loaded {len(chunks)} chunks.")


# --------------------------------------------------
# Load existing progress if available
# --------------------------------------------------

if os.path.exists(OUTPUT_PATH):

    with open(OUTPUT_PATH, "r", encoding="utf-8") as f:
        embedded_chunks = json.load(f)

    completed_ids = {
        chunk["chunk_id"]
        for chunk in embedded_chunks
    }

    print(f"Found existing progress: {len(embedded_chunks)} chunks already embedded.")

else:

    embedded_chunks = []
    completed_ids = set()

    print("No existing embedding file found. Starting from the beginning.")


# --------------------------------------------------
# Process chunks
# --------------------------------------------------

remaining_chunks = [
    chunk
    for chunk in chunks
    if chunk["chunk_id"] not in completed_ids
]

print(f"Remaining chunks to embed: {len(remaining_chunks)}")


for start in range(0, len(remaining_chunks), BATCH_SIZE):

    batch = remaining_chunks[start:start + BATCH_SIZE]

    texts = [chunk["text"] for chunk in batch]

    print(
        f"\nEmbedding chunks "
        f"{start + 1}-{start + len(batch)} "
        f"of {len(remaining_chunks)}..."
    )

    # --------------------------------------------------
    # Retry handling
    # --------------------------------------------------

    for attempt in range(MAX_RETRIES):

        try:

            result = client.models.embed_content(
                model=MODEL_NAME,
                contents=texts,
                config={
                    "output_dimensionality": OUTPUT_DIMENSIONALITY
                }
            )

            embeddings = result.embeddings

            break

        except Exception as e:

            error_message = str(e)

            if "429" not in error_message and "RESOURCE_EXHAUSTED" not in error_message:
                raise

            if attempt == MAX_RETRIES - 1:
                print("Maximum retries reached.")
                raise

            # Increasing wait time between retries.
            wait_time = 30 * (attempt + 1)

            print(
                f"Rate limit reached. "
                f"Waiting {wait_time} seconds before retry..."
            )

            time.sleep(wait_time)

    # --------------------------------------------------
    # Store successful embeddings
    # --------------------------------------------------

    for chunk, embedding in zip(batch, embeddings):

        embedded_chunks.append({
            "chunk_id": chunk["chunk_id"],
            "page": chunk["page"],
            "text": chunk["text"],
            "embedding": embedding.values
        })

    # --------------------------------------------------
    # Save progress immediately
    # --------------------------------------------------

    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(
            embedded_chunks,
            f,
            ensure_ascii=False
        )

    print(
        f"Saved progress: "
        f"{len(embedded_chunks)}/{len(chunks)} chunks"
    )

    # Small delay between batches.
    time.sleep(5)


# --------------------------------------------------
# Finished
# --------------------------------------------------

print()
print("Embedding generation completed successfully!")
print(f"Total embedded chunks: {len(embedded_chunks)}")
print(
    f"Embedding dimensions: "
    f"{len(embedded_chunks[0]['embedding'])}"
)
print(f"Saved to: {OUTPUT_PATH}")