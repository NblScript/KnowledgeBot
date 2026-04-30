# Alembic migrations

This directory contains Alembic migration scripts for the Chat Service.

## Usage

Create a new migration:
```bash
alembic revision --autogenerate -m "description"
```

Apply migrations:
```bash
alembic upgrade head
```

Rollback one migration:
```bash
alembic downgrade -1
```
