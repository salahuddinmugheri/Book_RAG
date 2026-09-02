import os
from dotenv import load_dotenv
from google import genai

# Load environment variables from .env
load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError("GEMINI_API_KEY not found in .env")

# Create Gemini client
client = genai.Client(api_key=api_key)

# Test text
text = "God's existence is sometimes argued from the apparent design and order of the universe."

# Generate embedding
result = client.models.embed_content(
    model="gemini-embedding-001",
    contents=text,
    config={
        "output_dimensionality": 768
    }
)

embedding = result.embeddings[0].values

print("Embedding generated successfully!")
print("Vector dimensions:", len(embedding))
print("First 10 values:", embedding[:10])