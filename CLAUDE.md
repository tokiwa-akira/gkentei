# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a G検定 (G-certification) exam preparation system that provides offline AI-powered question search and practice. It combines ChromaDB vector search, sentence transformers, and local LLM capabilities to create a comprehensive study tool.

Key components:
- **Vector Search API**: ChromaDB + sentence-transformers for semantic similarity search of exam questions
- **Local LLM Integration**: llama-cpp-python for paraphrasing and explanations
- **Exam Generation**: Automated mock exam creation with difficulty balancing
- **Web Scraping**: Playwright-based content collection with copyright-aware paraphrasing
- **Progressive Web App**: React frontend with offline capabilities

## Development Commands

### Environment Setup
```bash
# Quick setup with script
./scripts/setup.sh

# Manual setup
python -m venv venv
source venv/bin/activate  # Linux/Mac
pip install -r backend/requirements.txt
cd frontend && npm install && cd ..

# Create required directories
mkdir -p data/{chroma,backups} cache models
```

### Running Services
```bash
# New structure - Backend
cd backend && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# New structure - Frontend
cd frontend && npm run dev

# Docker Compose (recommended)
docker compose -f docker-compose.new.yml up --build

# Initialize embeddings (required before first use)
cd backend && python app/scripts/init_embeddings.py --reset --batch-size 100
```

### Testing
```bash
# Backend tests
cd backend && pytest tests/ -v

# Frontend tests
cd frontend && npm test

# Legacy tests (until migrated)
cd backend && pytest tests/legacy/ -v

# Type checking
cd frontend && npm run type-check
cd backend && mypy app/
```

### API Testing
```bash
# Health check
curl http://localhost:8000/health

# Search test
curl "http://localhost:8000/search?q=ニューラルネットワーク&k=5"

# View API documentation
# http://localhost:8000/docs
```

## Architecture

### Core Services
- **search_api.py**: FastAPI application with similarity search endpoints
- **main.py**: Main application integrator with LLM router
- **router_llm.py**: Local LLM API endpoints for paraphrasing/explanations
- **ingest_embedding.py**: Embedding ingestion pipeline for ChromaDB

### Data Layer
- **models.py**: SQLAlchemy models (Problem, Choice, AnswerLog)
- **ChromaDB**: Vector storage for semantic search (`./data/chroma/`)
- **SQLite**: Relational data storage (`./data/problems.db`)

### Processing Components
- **scraper.py**: Web content extraction with Playwright
- **parser.py**: Problem text parsing and normalization
- **exam/generate.py**: Mock exam generation with difficulty balancing
- **exam/optimizer.py**: Exam optimization algorithms

### Key Classes
- **EmbeddingService** (`search_api.py:37`): Singleton service managing ChromaDB and sentence-transformers
- **EmbeddingIngestor** (`ingest_embedding.py:28`): Handles data ingestion pipeline

## Environment Variables

- `TRANSFORMERS_CACHE`: Model cache directory (default: `./cache`)
- `CHROMA_PATH`: ChromaDB data path (default: `./data/chroma`)
- `DB_PATH`: SQLite database path (default: `./data/problems.db`)
- `EMBEDDING_MODEL`: Model name (default: `sentence-transformers/all-MiniLM-L6-v2`)

## Common Tasks

### Adding New Problems
1. Ensure SQLite database has new problem data
2. Run embedding ingestion: `python ingest_embedding.py --batch-size 50`
3. Verify with search API: `curl "http://localhost:8000/search?q=test"`

### Changing Embedding Model
1. Update `EMBEDDING_MODEL` environment variable
2. Reset embeddings: `python ingest_embedding.py --reset --model <new-model-name>`
3. Restart API service

### Database Schema Changes
1. Modify `models.py`
2. Generate migration: `alembic revision --autogenerate -m "description"`
3. Apply migration: `alembic upgrade head`

## Performance Notes

- Target search response time: < 100ms
- Embedding generation: < 5 seconds per problem
- Memory usage: < 2GB including models
- Use `--batch-size` parameter to control memory usage during ingestion

## File Structure Context

- `/exam/`: Exam generation and optimization logic
- `/test/`: Comprehensive test suite for all components
- `/alembic/`: Database migration management
- `data/`: Persistent data storage (SQLite + ChromaDB)
- `cache/`: Transformer model cache