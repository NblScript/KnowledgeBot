# Knowledge Service

Knowledge Base Management Service for KnowledgeBot platform.

## Features

- Knowledge Base CRUD operations
- Document upload and management
- Chunk management
- Milvus vector database integration
- PostgreSQL database with schema isolation

## Endpoints

- `/v1/knowledge-bases/` - Knowledge Base CRUD
- `/v1/knowledge-bases/{kb_id}/documents` - Document management under KB
- `/v1/documents/{doc_id}` - Document direct operations

## Running

```bash
# Development
uvicorn app.main:app --reload --port 8002

# Production
docker build -t knowledge-service .
docker run -p 8002:8002 knowledge-service
```

## Environment Variables

See `.env.example` for required configuration.