# SpecFlow Backend

FastAPI backend for SpecFlow - Context-aware API testing platform.

## Tech Stack

- **Framework:** FastAPI 0.104+
- **Database:** PostgreSQL 15+ (async with SQLAlchemy 2.0)
- **Cache:** Redis 7+
- **AI:** Ollama (qwen3-vl:235b-cloud model)
- **Authentication:** JWT with python-jose
- **OpenAPI Parsing:** prance
- **HTTP Client:** httpx (async)

## Setup

### Prerequisites

- Python 3.11+
- PostgreSQL 15+
- Redis 7+
- Ollama with qwen3-vl:235b-cloud model

### Installation

1. Install dependencies using UV:
```bash
pip install uv
uv pip install -e .
```

2. Copy environment file:
```bash
cp .env.example .env
```

3. Configure `.env` with your database and service URLs

4. Run database migrations:
```bash
alembic upgrade head
```

### Running the Server

Development mode:
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Production mode:
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

## API Endpoints

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login
- `GET /api/auth/me` - Get current user
- `POST /api/auth/refresh` - Refresh token

### Specs
- `POST /api/specs` - Upload OpenAPI spec
- `GET /api/specs` - List all specs
- `GET /api/specs/{id}` - Get spec details
- `PATCH /api/specs/{id}` - Update spec
- `DELETE /api/specs/{id}` - Delete spec

### Journeys
- `POST /api/specs/{id}/generate-journeys` - Generate journeys with AI
- `GET /api/journeys` - List all journeys
- `GET /api/journeys/{id}` - Get journey details
- `POST /api/journeys` - Create journey manually
- `PUT /api/journeys/{id}` - Update journey
- `DELETE /api/journeys/{id}` - Delete journey

### Execution
- `WS /api/ws/journey/{id}/execute` - Execute journey (WebSocket)
- `GET /api/executions/{id}` - Get execution details
- `GET /api/journeys/{id}/executions` - Get journey execution history

## Database Migrations

Create a new migration:
```bash
alembic revision --autogenerate -m "description"
```

Apply migrations:
```bash
alembic upgrade head
```

Rollback:
```bash
alembic downgrade -1
```

## Project Structure

```
app/
├── main.py                 # FastAPI app entry point
├── config.py              # Settings and configuration
├── database.py            # Database setup and session
├── models/                # SQLAlchemy models
│   ├── user.py
│   ├── spec.py
│   ├── journey.py
│   └── execution.py
├── schemas/               # Pydantic schemas
│   ├── user.py
│   ├── spec.py
│   ├── journey.py
│   └── execution.py
├── routers/               # API route handlers
│   ├── auth.py
│   ├── specs.py
│   ├── journeys.py
│   └── execution.py
└── services/              # Business logic
    ├── auth.py
    ├── spec_parser.py
    ├── journey_generator.py
    └── journey_executor.py
```

## Development

### Testing
```bash
pytest
```

### Code formatting
```bash
black app/
ruff check app/
```
