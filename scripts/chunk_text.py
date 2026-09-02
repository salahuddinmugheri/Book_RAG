import json
import re

INPUT_PATH = "data/pages.json"
OUTPUT_PATH = "data/chunks.json"

CHUNK_SIZE = 800
CHUNK_OVERLAP = 150


def split_text(text, chunk_size=CHUNK_SIZE, overlap=CHUNK_OVERLAP):
    chunks = []

    start = 0
    text_length = len(text)

    while start < text_length:
        end = start + chunk_size

        # Try to end the chunk at a sentence or word boundary
        if end < text_length:
            boundary = text.rfind(". ", start, end)

            if boundary == -1:
                boundary = text.rfind(" ", start, end)

            if boundary > start:
                end = boundary + 1

        chunk = text[start:end].strip()

        if chunk:
            chunks.append(chunk)

        # Move forward while keeping overlap
        next_start = end - overlap

        if next_start <= start:
            next_start = end

        start = next_start

    return chunks


def main():
    with open(INPUT_PATH, "r", encoding="utf-8") as file:
        pages = json.load(file)

    all_chunks = []

    for page in pages:
        page_number = page["page"]
        text = page["text"]

        page_chunks = split_text(text)

        for chunk_number, chunk in enumerate(page_chunks, start=1):
            all_chunks.append({
                "chunk_id": f"page_{page_number}_chunk_{chunk_number}",
                "page": page_number,
                "text": chunk
            })

    with open(OUTPUT_PATH, "w", encoding="utf-8") as file:
        json.dump(all_chunks, file, ensure_ascii=False, indent=2)

    print(f"Pages processed: {len(pages)}")
    print(f"Total chunks created: {len(all_chunks)}")
    print(f"Chunk size: {CHUNK_SIZE} characters")
    print(f"Chunk overlap: {CHUNK_OVERLAP} characters")
    print(f"Saved chunks to: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()