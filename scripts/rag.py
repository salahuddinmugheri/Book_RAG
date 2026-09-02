import os
import re
from collections import Counter

from dotenv import load_dotenv
from supabase import create_client, Client
from google import genai
from google.genai import types


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


# Initialize clients
supabase: Client = create_client(
    SUPABASE_URL,
    SUPABASE_SECRET_KEY
)

gemini = genai.Client(
    api_key=GEMINI_API_KEY
)


# Models
EMBEDDING_MODEL = "gemini-embedding-001"
GENERATION_MODEL = "gemini-3.6-flash"

# Embedding configuration
EMBEDDING_DIMENSIONS = 768

# Retrieval configuration
RETRIEVAL_K = 8
FINAL_K = 3
SIMILARITY_THRESHOLD = 0.55


# Common words that provide little lexical information
STOPWORDS = {
    "a",
    "an",
    "and",
    "are",
    "as",
    "at",
    "be",
    "by",
    "does",
    "for",
    "from",
    "how",
    "in",
    "is",
    "it",
    "of",
    "on",
    "or",
    "the",
    "their",
    "this",
    "to",
    "was",
    "what",
    "when",
    "where",
    "who",
    "why",
    "with",
}


def generate_query_embedding(question: str):
    """
    Generate a 768-dimensional embedding for the user's question.
    """

    response = gemini.models.embed_content(
        model=EMBEDDING_MODEL,
        contents=question,
        config={
            "output_dimensionality": EMBEDDING_DIMENSIONS
        }
    )

    if not response.embeddings:
        raise RuntimeError("Gemini returned no embedding.")

    embedding = response.embeddings[0].values

    if len(embedding) != EMBEDDING_DIMENSIONS:
        raise RuntimeError(
            f"Expected {EMBEDDING_DIMENSIONS} dimensions, "
            f"but received {len(embedding)}."
        )

    return embedding


def tokenize(text: str):
    """
    Convert text into normalized words.
    """

    return re.findall(
        r"\b[a-zA-Z0-9']+\b",
        text.lower()
    )


def get_query_terms(question: str):
    """
    Extract meaningful terms from the question.
    """

    words = tokenize(question)

    return [
        word
        for word in words
        if word not in STOPWORDS and len(word) > 1
    ]


def expand_retrieval_query(question: str):
    """
    Expand very short or vague questions into clearer
    retrieval queries without changing the user's question.
    """

    normalized = question.lower().strip()

    vague_author_questions = {
        "who wrote this?",
        "who wrote this",
        "who wrote it?",
        "who wrote it",
        "who is the author?",
        "who is the author",
        "what is the author's name?",
        "what is the author's name",
        "who wrote the book?",
        "who wrote the book",
        "what is the author name?",
        "what is the author name",
    }

    if normalized in vague_author_questions:
        return (
            'Who is the author of the book '
            '"Why There Is No God"?'
        )

    return question


def lexical_score(question: str, text: str):
    """
    Calculate lexical relevance between the question and a chunk.
    """

    query_terms = get_query_terms(question)

    if not query_terms:
        return 0.0

    text_words = tokenize(text)

    if not text_words:
        return 0.0

    word_counts = Counter(text_words)

    matched_terms = sum(
        1
        for term in query_terms
        if term in word_counts
    )

    term_coverage = (
        matched_terms / len(set(query_terms))
    )

    normalized_question = " ".join(
        tokenize(question)
    )

    normalized_text = " ".join(
        text_words
    )

    phrase_bonus = 0.0

    if normalized_question in normalized_text:
        phrase_bonus = 0.30

    repetition_bonus = 0.0

    for term in set(query_terms):
        if word_counts[term] >= 2:
            repetition_bonus += 0.05

    repetition_bonus = min(
        repetition_bonus,
        0.20
    )

    score = (
        term_coverage
        + phrase_bonus
        + repetition_bonus
    )

    return min(score, 1.0)


def rerank_chunks(question: str, chunks):
    """
    Rerank candidates using semantic and lexical relevance.
    """

    reranked = []

    for chunk in chunks:

        semantic_score = float(
            chunk.get("similarity", 0.0)
        )

        lexical = lexical_score(
            question,
            chunk.get("text", "")
        )

        rerank_score = (
            0.75 * semantic_score
            + 0.25 * lexical
        )

        reranked.append({
            **chunk,
            "_semantic_score": semantic_score,
            "_lexical_score": lexical,
            "_rerank_score": rerank_score
        })

    reranked.sort(
        key=lambda chunk: chunk["_rerank_score"],
        reverse=True
    )

    return reranked[:FINAL_K]


def retrieve_chunks(
    question: str,
    match_count: int = RETRIEVAL_K
):
    """
    Retrieve candidate chunks from Supabase,
    filter weak matches, and rerank them.
    """

    retrieval_query = expand_retrieval_query(
        question
    )

    query_embedding = generate_query_embedding(
        retrieval_query
    )

    response = supabase.rpc(
        "match_book_chunks",
        {
            "query_embedding": query_embedding,
            "match_count": match_count
        }
    ).execute()

    candidates = response.data or []

    candidates = [
        chunk
        for chunk in candidates
        if float(chunk.get("similarity", 0.0))
        >= SIMILARITY_THRESHOLD
    ]

    if not candidates:
        return []

    return rerank_chunks(
        retrieval_query,
        candidates
    )


def build_context(chunks):
    """
    Build the context sent to Gemini.
    """

    context_parts = []

    for index, chunk in enumerate(
        chunks,
        start=1
    ):

        context_parts.append(
            f"""Source {index}
Page: {chunk["page"]}

{chunk["text"]}"""
        )

    return "\n\n".join(
        context_parts
    )


def generate_answer(
    question: str,
    context: str
):
    """
    Generate a grounded answer using only retrieved context.
    """

    prompt = f"""
You are an AI assistant answering questions about the book
"Why There Is No God" by Armin Navabi.

Use ONLY the provided book context to answer the user's question.

Rules:

- Do not use outside knowledge.
- Do not invent facts or information.
- Do not invent page numbers.
- Only make claims that are supported by the provided context.
- If the context is genuinely insufficient to answer the question,
  say so clearly.
- For broad questions such as summaries or explanations, synthesize
  the relevant information from all provided context before deciding
  that the context is insufficient.
- Give a clear, natural, and professional answer.
- Keep the answer focused on the user's question.
- When a claim is supported by a retrieved source, cite it using
  exactly one citation format: [Source 1], [Source 2], or [Source 3].
- Never combine multiple source citations inside one pair of brackets.
- Write citations separately, for example [Source 1] [Source 3].
- Only use source numbers that actually appear in the provided context.
- Never write [Page X] citations yourself.
- Never invent or guess source numbers.
- Do not mention RAG, embeddings, vectors, Supabase, retrieval,
  similarity scores, reranking, source IDs, or other internal
  technical details.

Book context:

{context}

User question:

{question}

Answer:
"""

    response = gemini.models.generate_content(
        model=GENERATION_MODEL,
        contents=prompt,
        config=types.GenerateContentConfig(
            automatic_function_calling=types.AutomaticFunctionCallingConfig(
                disable=True
            )
        )
    )

    if not response.text:
        raise RuntimeError(
            "Gemini returned an empty response."
        )

    return response.text.strip()


def replace_source_citations(
    answer: str,
    chunks
):
    """
    Convert Gemini's [Source N] citations into verified [Page X]
    citations using the actual retrieved chunks.
    """

    def replace(match):

        source_number = int(
            match.group(1)
        )

        if 1 <= source_number <= len(chunks):

            page = chunks[
                source_number - 1
            ]["page"]

            return f"[Page {page}]"

        return match.group(0)

    return re.sub(
        r"\[Source\s+(\d+)\]",
        replace,
        answer
    )


def format_sources(chunks):
    """
    Create clean, deduplicated source metadata.

    Multiple chunks from the same page are represented
    by one page source.
    """

    sources = []
    seen_pages = set()

    for chunk in chunks:

        page = chunk["page"]

        if page in seen_pages:
            continue

        seen_pages.add(page)

        sources.append({
            "page": page
        })

    return sources


def ask_question(question: str):
    """
    Complete RAG pipeline.

    Returns:

    {
        "answer": str,
        "sources": [
            {
                "page": int
            }
        ]
    }
    """

    if not question or not question.strip():
        raise ValueError(
            "Question cannot be empty."
        )

    question = question.strip()

    # Retrieve and rerank
    chunks = retrieve_chunks(
        question
    )

    # Handle missing context
    if not chunks:

        return {
            "answer": (
                "I could not find enough relevant information "
                "in the available book content to answer this question."
            ),
            "sources": []
        }

    # Build context
    context = build_context(
        chunks
    )

    # Generate answer
    answer = generate_answer(
        question,
        context
    )

    # Convert verified source references into page citations
    answer = replace_source_citations(
        answer,
        chunks
    )

    # Format clean source metadata
    sources = format_sources(
        chunks
    )

    return {
        "answer": answer,
        "sources": sources
    }


if __name__ == "__main__":

    question = input(
        "\nAsk a question about the book: "
    ).strip()

    try:

        result = ask_question(
            question
        )

        print("\nAnswer:")
        print(result["answer"])

        print("\nSources:")

        for source in result["sources"]:
            print(
                f"- Page {source['page']}"
            )

    except Exception as error:

        print(
            f"\nRAG error: {error}"
        )