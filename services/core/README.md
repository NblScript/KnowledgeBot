# KnowledgeBot Core Service

FastAPI-based Knowledge Base Management API with RAG capabilities.

## Quick Start

### 1. Start Infrastructure Services

```bash
docker-compose up -d postgres redis milvus minio
```

### 2. Configure Environment

```bash
cp .env.example .env
# Edit .env with your API keys
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the API

```bash
uvicorn app.main:app --reload
```

### 5. Run Celery Worker (optional, for document processing)

```bash
celery -A app.tasks.celery_app worker --loglevel=info
```

## API Documentation

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Project Structure

```
app/
├── api/            # API routes
├── models/         # SQLAlchemy models
├── schemas/        # Pydantic schemas
├── services/       # Business logic
├── tasks/          # Celery tasks
├── processors/     # Document processors
├── retrievers/     # Vector retrievers
├── llm/            # LLM abstraction
├── config.py       # Configuration
├── database.py     # Database connections
└── main.py         # FastAPI app
```
