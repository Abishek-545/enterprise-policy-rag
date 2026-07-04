# Enterprise Policy Intelligence RAG

A portfolio-grade Retrieval-Augmented Generation project for answering internal company policy questions with citation-backed responses.

## Why this is industry-relevant

This project mirrors a common enterprise GenAI use case: employees need accurate answers from internal policies, security docs, handbooks, and process documents. The implementation demonstrates document ingestion, chunking, embeddings, a persistent vector database, source-grounded generation, Streamlit UX, and retrieval evaluation.

## Architecture

```text
Documents -> Loader -> Recursive Chunking -> Embeddings -> Qdrant Vector DB
                                                           |
User Question -> Hybrid Retriever -> Top-k Evidence -> Groq LLM -> Cited Answer
```

## Features

- PDF, DOCX, TXT, and Markdown ingestion with rich sample policy PDFs
- Recursive text chunking with metadata
- SentenceTransformer embeddings
- Persistent Qdrant local vector database`n- Hybrid retrieval using dense vectors plus BM25 keyword scoring
- Groq LLM answer generation
- Citation-grounded answers
- Polished Streamlit chat UI with capability guide, suggested questions, policy library, and evidence panel
- Upload documents and rebuild index from UI
- Retrieval evaluation script
- Docker-ready project structure
- Tests and lint-ready configuration

## Setup

```bash
cd D:\gen_ai_proj\enterprise-policy-rag
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

The local `.env` file stores your Groq API key and is ignored by git.


## Generate the sample policy PDFs

```bash
python scripts/create_sample_policies.py
```

The sample corpus includes multi-page PDFs for leave and vacation, workplace safety, employee conduct, information security, and travel expenses.
## Build the index

```bash
$env:PYTHONPATH="src"
python -m rag_app.ingest
```

## Run the app

```bash
$env:PYTHONPATH="src"
streamlit run app/streamlit_app.py
```

## Run retrieval evaluation

```bash
$env:PYTHONPATH="src"
python eval/run_eval.py
```

## Run tests

```bash
pytest
```

## Resume bullets

- Built an enterprise RAG assistant using Groq, Qdrant, SentenceTransformers, and Streamlit.
- Implemented document ingestion for PDF/DOCX/Markdown/TXT with metadata-preserving chunking.
- Added citation-grounded answer generation, persistent vector search, and retrieval hit-rate evaluation.
- Packaged the project with Docker, tests, environment config, and production-style documentation.

## Next improvements

- Add hybrid BM25 + vector retrieval
- Add reranking with a cross-encoder
- Add FastAPI backend for production deployment
- Add authentication and role-based document collections
- Track feedback and failed questions for continuous evaluation

