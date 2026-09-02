#  Book RAG

A Retrieval-Augmented Generation (RAG) application that allows users to ask questions about a book and receive answers grounded in the book's content, with page-level source citations.

The project uses a custom RAG pipeline built from scratch rather than relying on high-level frameworks such as LangChain or LlamaIndex. It combines semantic search, lexical matching, reranking, and Gemini-based generation to produce accurate, context-aware answers from the book.

## About the Book

The current knowledge base contains:

**Book:** *Why There Is No God*
**Author:** Armin Navabi

The application processes the book's PDF, extracts its text, divides it into meaningful chunks, generates vector embeddings, stores those embeddings in Supabase using pgvector, retrieves relevant passages for a user query, and uses Google's Gemini model to generate the final answer.

##  Features

*  PDF-based knowledge base
*  Semantic vector search
*  Lexical keyword matching
*  Hybrid retrieval and reranking
*  Gemini LLM-based answer generation
*  Page-level source citations
*  FastAPI backend
*  Interactive Next.js chat interface
*  Loading and error handling
*  Responsive frontend
*  Environment-variable based API credentials
*  Retrieval evaluation
*  Custom RAG pipeline without LangChain/LlamaIndex

##  System Architecture

The overall pipeline is:

```text
                    ┌─────────────────┐
                    │    Book PDF     │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │  Text Extraction│
                    │     PyMuPDF     │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │     Chunking    │
                    │  800 chars      │
                    │  150 overlap    │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │ Gemini Embedding│
                    │ 768 dimensions  │
                    └────────┬────────┘
                             │
                             ▼
                 ┌────────────────────────┐
                 │ Supabase + pgvector    │
                 │                        │
                 │ 335 embedded chunks    │
                 └───────────┬────────────┘
                             │
                       User Question
                             │
                             ▼
                 ┌────────────────────────┐
                 │     Query Embedding    │
                 └───────────┬────────────┘
                             │
                             ▼
                 ┌────────────────────────┐
                 │    Vector Retrieval    │
                 └───────────┬────────────┘
                             │
                             ▼
                 ┌────────────────────────┐
                 │   Lexical Matching     │
                 └───────────┬────────────┘
                             │
                             ▼
                 ┌────────────────────────┐
                 │       Reranking        │
                 │ Semantic + Lexical     │
                 └───────────┬────────────┘
                             │
                             ▼
                 ┌────────────────────────┐
                 │     Gemini LLM         │
                 │   Context-grounded     │
                 │      generation        │
                 └───────────┬────────────┘
                             │
                             ▼
                 ┌────────────────────────┐
                 │ Answer + Page Sources  │
                 └───────────┬────────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │   Next.js UI    │
                    └─────────────────┘
```

##  How the RAG Pipeline Works

### 1. PDF Text Extraction

The original book PDF is processed using **PyMuPDF**.

The extraction process:

* Opens the PDF
* Iterates through all pages
* Extracts text from each page
* Preserves page numbers
* Stores the extracted content in structured JSON

The book contains approximately **101 pages**.

The extracted data is stored in:

```text
data/pages.json
```

### 2. Text Chunking

The extracted text is divided into smaller chunks so that relevant sections can be retrieved efficiently.

Current configuration:

```text
Chunk size:     800 characters
Chunk overlap:  150 characters
Total chunks:   335
```

The overlap helps preserve contextual continuity between neighboring chunks.

Chunking is implemented in:

```text
scripts/chunk_text.py
```

### 3. Embedding Generation

Each text chunk is converted into a numerical vector using Google's Gemini embedding model.

Embedding model:

```text
gemini-embedding-001
```

Embedding dimension:

```text
768
```

The generated embeddings are stored locally in:

```text
data/embeddings.json
```

The embedding process is implemented in:

```text
scripts/generate_embeddings.py
```

### 4. Vector Database

The embeddings are stored in **Supabase PostgreSQL** using the **pgvector** extension.

The main database table is:

```text
book_chunks
```

Each record contains information such as:

* Chunk text
* Page number
* Embedding vector
* Chunk metadata

The database contains:

```text
335
```

embedded book chunks.

The pgvector column uses:

```text
vector(768)
```

### 5. Query Processing

When a user asks a question, the query is also converted into a vector using the same Gemini embedding model.

For example:

```text
Who is the author of the book?
```

The system generates an embedding for the question and searches the vector database for semantically similar book passages.

### 6. Semantic Retrieval

The system performs vector similarity search against the stored book embeddings.

This allows the application to find relevant passages even when the user's wording is different from the wording used in the book.

For example:

```text
"What does the author say about God's existence?"
```

can retrieve relevant passages even if the exact phrase does not appear in the book.

### 7. Lexical Matching

Semantic similarity is supplemented with lexical matching.

This helps when an important keyword appears directly in the question or document.

The system therefore considers both:

```text
Semantic relevance
+
Lexical relevance
```

This improves retrieval robustness compared with relying only on vector similarity.

### 8. Reranking

Retrieved candidates are reranked using their relevance scores.

The system considers:

* Semantic similarity
* Lexical relevance
* Overall query-document relevance

The highest-quality passages are selected as context for the LLM.

### 9. Context Construction

The selected chunks are combined into a context that is passed to the Gemini generation model.

The model is instructed to answer using the retrieved book context rather than relying on unsupported information.

### 10. Answer Generation

The final response is generated using Google's Gemini model.

The system is designed to keep answers grounded in the retrieved content.

For example:

```text
User:
Who is the author of the book?

Answer:
The author of the book is Armin Navabi. [Page 3]
```

### 11. Page-Level Citations

Each chunk retains its original page number.

Therefore, when a retrieved chunk contributes to an answer, the frontend can display its source page.

Example:

```text
The author of the book is Armin Navabi. [Page 3]
```

This makes the generated answer more transparent and allows the user to identify where the information came from.

#  Technology Stack

## Backend

* Python
* FastAPI
* Google Gemini API
* PyMuPDF
* Supabase
* PostgreSQL
* pgvector

## Frontend

* Next.js
* React
* JavaScript/TypeScript
* CSS

## AI / Retrieval

* Gemini Embeddings
* `gemini-embedding-001`
* Gemini LLM
* Vector similarity search
* Lexical matching
* Hybrid reranking

## Development Tools

* VS Code
* Git
* GitHub
* Python virtual environment
* npm

# Project Structure

```text
Book_RAG/
│
├── data/
│   ├── pages.json
│   └── embeddings.json
│
├── frontend/
│   ├── app/
│   ├── components/
│   ├── public/
│   ├── package.json
│   └── ...
│
├── scripts/
│   ├── chunk_text.py
│   ├── extract_text.py
│   ├── generate_embeddings.py
│   ├── insert_embeddings.py
│   ├── rag.py
│   ├── test_embedding.py
│   ├── test_gemini_generation.py
│   ├── test_generation.py
│   ├── test_retrieval.py
│   └── test_supabase.py
│
├── src/
│   └── api/
│       └── main.py
│
├── .gitignore
├── package.json
└── README.md
```

> Note: The exact frontend and backend file structure may change as the project evolves.

#  Important Scripts

## PDF Extraction

```bash
python scripts/extract_text.py
```

Extracts text from the book PDF and associates it with page numbers.

## Chunking

```bash
python scripts/chunk_text.py
```

Splits extracted text into overlapping chunks.

## Generate Embeddings

```bash
python scripts/generate_embeddings.py
```

Generates Gemini embeddings for the chunks.

## Insert Embeddings

```bash
python scripts/insert_embeddings.py
```

Uploads the embeddings and associated metadata into Supabase.

> The current database already contains the processed 335 chunks, so these ingestion scripts do not need to be rerun during normal development.

## Test Supabase Connection

```bash
python scripts/test_supabase.py
```

Tests the connection to the Supabase database.

## Test Retrieval

```bash
python scripts/test_retrieval.py
```

Tests whether relevant chunks can be retrieved for a query.

## Run RAG from CLI

```bash
python scripts/rag.py
```

Runs the RAG pipeline and allows questions to be asked from the command line.

# 🚀 Running the Project Locally

## 1. Clone the Repository

```bash
git clone https://github.com/salahuddinmugheri/Book_RAG.git
cd Book_RAG
```

## 2. Create a Python Virtual Environment

Windows:

```bash
python -m venv .venv
```

Activate it:

```bash
.venv\Scripts\activate
```

## 3. Install Python Dependencies

If a `requirements.txt` file is available:

```bash
pip install -r requirements.txt
```

Otherwise, install the required packages used by the backend and scripts.

## 4. Configure Environment Variables

Create a `.env` file for your API credentials.

Example:

```env
GEMINI_API_KEY=your_gemini_api_key
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key
```

Never commit `.env` to GitHub.

The `.gitignore` file should include:

```text
.env
.venv/
__pycache__/
node_modules/
```

## 5. Start the FastAPI Backend

From the project root:

```bash
uvicorn src.api.main:app --reload
```

The backend will normally be available at:

```text
http://127.0.0.1:8000
```

FastAPI also provides interactive API documentation at:

```text
http://127.0.0.1:8000/docs
```

## 6. Start the Next.js Frontend

Open another terminal:

```bash
cd frontend
npm install
npm run dev
```

The frontend will normally be available at:

```text
http://localhost:3000
```

Open the application in your browser and start asking questions about the book.

#  API

The FastAPI backend provides an endpoint through which the frontend sends user questions to the RAG system.

Conceptually:

```text
Frontend
   │
   │ User question
   ▼
FastAPI
   │
   ▼
RAG Pipeline
   │
   ├── Query embedding
   ├── Vector retrieval
   ├── Lexical matching
   ├── Reranking
   └── Gemini generation
   │
   ▼
Answer + Sources
   │
   ▼
Frontend
```

The API returns the generated answer together with source information used to support the response.

#  Retrieval Evaluation

Retrieval quality was evaluated separately from answer generation.

The purpose of retrieval evaluation was to determine whether the system was actually finding the correct book passages before sending them to the LLM.

Evaluation focused on:

* Relevant chunk retrieval
* Semantic similarity
* Lexical relevance
* Reranking quality
* Page/source correctness

This distinction is important because a RAG system can produce a fluent answer while still retrieving poor context.

The project therefore evaluates the retrieval layer independently before optimizing the complete pipeline.

#  Design Goals

The project was designed around several goals:

### 1. Grounded Answers

Answers should be based on the book's content rather than unsupported model knowledge.

### 2. Source Transparency

Users should be able to see the page from which the information was retrieved.

### 3. Better Retrieval

Combining semantic and lexical signals helps retrieve relevant passages more reliably.

### 4. Simple Architecture

The project intentionally implements the core RAG pipeline directly instead of hiding the retrieval process behind a high-level framework.

### 5. Practical Learning

The project demonstrates how a complete production-style RAG system works from:

```text
PDF
→ Extraction
→ Chunking
→ Embeddings
→ Vector Database
→ Retrieval
→ Reranking
→ LLM
→ API
→ Frontend
```

#  Security

API keys and database credentials must be stored in environment variables.

Never commit the following to GitHub:

```text
.env
API keys
Database passwords
Private credentials
Service-role keys
```

The repository's `.gitignore` should prevent sensitive files from being tracked.

#  Limitations

The current version has several limitations:

* The knowledge base is based on a single book.
* Answers depend on the quality of retrieved chunks.
* Extremely broad or ambiguous questions may retrieve less relevant passages.
* LLM-generated answers can still contain inaccuracies.
* Retrieval quality depends on chunk size and embedding quality.
* The current system is primarily designed for this book rather than a large multi-document knowledge base.

#  Future Improvements

Possible future improvements include:

* Support for multiple books
* Multi-document RAG
* Improved chunking strategies
* Metadata filtering
* Advanced reranking models
* Retrieval confidence scores
* Conversation memory
* Streaming responses
* Authentication
* User accounts
* Document upload functionality
* Automated retrieval evaluation datasets
* Better hallucination detection
* Production deployment
* Docker containerization
* Cloud deployment
* Monitoring and logging
* Response latency optimization

#  Current Pipeline Configuration

| Component            | Configuration            |
| -------------------- | ------------------------ |
| Source               | Book PDF                 |
| Book                 | *Why There Is No God*    |
| Author               | Armin Navabi             |
| Pages                | ~101                     |
| Chunk Size           | 800 characters           |
| Chunk Overlap        | 150 characters           |
| Total Chunks         | 335                      |
| Embedding Model      | `gemini-embedding-001`   |
| Embedding Dimensions | 768                      |
| Vector Database      | Supabase PostgreSQL      |
| Vector Extension     | pgvector                 |
| Backend              | FastAPI                  |
| Frontend             | Next.js                  |
| Generation           | Gemini                   |
| Retrieval            | Semantic + Lexical       |
| Reranking            | Hybrid relevance scoring |

#  Example Questions

You can ask questions such as:

```text
Who is the author of the book?

What arguments does the book give against God's existence?

What is the author's response to the argument from design?

What does the book say about morality?

Summarize the main arguments discussed in the book.

What does the author say about religious belief?
```

The system retrieves relevant passages and generates an answer based on those passages.

#  Project Purpose

This project was developed as a practical implementation of a Retrieval-Augmented Generation system.

It demonstrates the complete workflow of building a RAG application, including:

```text
Document Processing
        ↓
Text Chunking
        ↓
Embedding Generation
        ↓
Vector Storage
        ↓
Semantic Retrieval
        ↓
Lexical Retrieval
        ↓
Reranking
        ↓
Context Construction
        ↓
LLM Generation
        ↓
Source Citation
        ↓
Web Application
```

The main objective is to understand and implement the internal components of a RAG system rather than simply using an existing RAG framework.

#  Author

**Salahuddin Mugheri**

AI / Machine Learning Student
Mehran University of Engineering and Technology, Jamshoro

# License

This project is intended for educational and research purposes.

Check the copyright status and applicable permissions for the source book before redistributing the book's contents.

---

 If you find this project useful, consider giving the repository a star.
