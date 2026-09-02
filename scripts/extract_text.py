import pymupdf
import json
import re

PDF_PATH = "data/Why There Is No God.pdf"
OUTPUT_PATH = "data/pages.json"


def clean_text(text):
    # Remove standalone page numbers
    text = re.sub(r"(?m)^\s*\d+\s*$", "", text)

    # Join words broken by a hyphen at the end of a line
    text = re.sub(r"-\s*\n\s*", "", text)

    # Replace remaining line breaks with spaces
    text = re.sub(r"\s*\n\s*", " ", text)

    # Remove repeated whitespace
    text = re.sub(r"\s+", " ", text)

    return text.strip()


def main():
    doc = pymupdf.open(PDF_PATH)

    total_pages = len(doc)
    pages = []

    for page_number, page in enumerate(doc, start=1):
        raw_text = page.get_text()

        cleaned_text = clean_text(raw_text)

        if cleaned_text:
            pages.append({
                "page": page_number,
                "text": cleaned_text
            })

    doc.close()

    with open(OUTPUT_PATH, "w", encoding="utf-8") as file:
        json.dump(pages, file, ensure_ascii=False, indent=2)

    print(f"PDF pages: {total_pages}")
    print(f"Pages with text: {len(pages)}")
    print(f"Saved cleaned data to: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()