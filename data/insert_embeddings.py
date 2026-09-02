import os
import json
from dotenv import load_dotenv
from supabase import create_client

# Load environment variables
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SECRET_KEY = os.getenv("SUPABASE_SECRET_KEY")

if not SUPABASE_URL:
    raise ValueError("SUPABASE_URL is missing from .env")

if not SUPABASE_SECRET_KEY:
    raise ValueError("SUPABASE_SECRET_KEY is missing from .env")

# Create Supabase client
supabase = create_client(
    SUPABASE_URL,
    SUPABASE_SECRET_KEY
)

# Load embeddings
with open("data/embeddings.json", "r", encoding="utf-8") as f:
    embeddings = json.load(f)

print(f"Loaded {len(embeddings)} embeddings")

# Prepare records
records = []

for item in embeddings:
    records.append({
        "chunk_id": item["chunk_id"],
        "page": item["page"],
        "text": item["text"],
        "embedding": item["embedding"]
    })

# Insert in batches
BATCH_SIZE = 50

for i in range(0, len(records), BATCH_SIZE):
    batch = records[i:i + BATCH_SIZE]

    response = (
        supabase
        .table("book_chunks")
        .insert(batch)
        .execute()
    )

    print(
        f"Inserted {min(i + BATCH_SIZE, len(records))}"
        f"/{len(records)}"
    )

print("\nEmbedding insertion completed successfully!")

# Verify database count
response = (
    supabase
    .table("book_chunks")
    .select("id", count="exact")
    .execute()
)

print(f"Rows in Supabase: {response.count}")