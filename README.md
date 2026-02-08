# SpecFlow

> **Context-aware API testing platform** that automatically transforms OpenAPI specifications into interactive, visual user journey workflows.

## 🚀 What is SpecFlow?

SpecFlow bridges the gap between isolated endpoint testing and real-world API usage by:
- **Parsing** OpenAPI specs to extract all endpoints and schemas
- **Generating** logical user journeys using AI (Ollama)
- **Visualizing** workflows as interactive node graphs (Vue Flow)
- **Executing** multi-step API tests with automatic data flow
- **Managing** authentication and session state automatically

## ✨ Key Features

- **AI-Powered Journey Generation:** Uses Ollama to analyze APIs and suggest realistic test workflows
- **Visual Journey Editor:** Drag-and-drop interface for creating and editing API test flows
- **Smart Execution:** Automatically passes tokens, IDs, and other data between steps
- **Mock Data Generation:** Uses Faker.js to generate realistic test data from schemas
- **Real-Time Results:** WebSocket-powered live execution feedback
- **Session Management:** Handles auth flows and maintains state across steps
- **Error Injection:** Test failure scenarios with one click

## 🛠️ Tech Stack

### Backend
- FastAPI (Python 3.11+)
- PostgreSQL + SQLAlchemy (async)
- Ollama (qwen3-vl:235b-cloud)
- Redis
- WebSockets

### Frontend
- Vue 3 + Vite
- TailwindCSS
- Vue Flow
- Pinia
- Axios

## 📋 Prerequisites

- **Python 3.11+** with UV package manager
- **Node.js 20+**
- **PostgreSQL 15+**
- **Redis 7+**
- **Ollama** with qwen3-vl:235b-cloud model

## 🚦 Quick Start

### 1. Backend Setup

```bash
cd backend

# Copy environment variables
cp .env.example .env
# Edit .env with your database credentials

# Install dependencies
pip install uv
uv pip install -e .

# Run database migrations
alembic upgrade head

# Start the server
uvicorn app.main:app --reload
```

Backend will be running at `http://localhost:8000`  
API docs available at `http://localhost:8000/docs`

### 2. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start dev server
npm run dev
```

Frontend will be running at `http://localhost:5173`

### 3. Install Ollama Model

```bash
ollama pull qwen3-vl:235b-cloud
```

## 📖 Usage

1. **Sign up** for an account
2. **Upload** your OpenAPI specification (JSON/YAML)
3. **Generate** journeys using AI or create manually
4. **Edit** the journey graph (add/remove/reorder steps)
5. **Configure** mock data for each step
6. **Execute** the journey and see real-time results
7. **View** request/response details for each step

## 🎨 Design Philosophy

SpecFlow uses a **premium dark theme** with:
- **Primary Color:** `#BFF549` (Vibrant Lime Green)
- **Background:** `#000000` (Pure Black)
- **Font:** Inter
- **Style:** Modern, high-energy, glassmorphism effects

## 📁 Project Structure

```
SpecFlow/
├── backend/          # FastAPI backend
│   ├── app/
│   │   ├── models/   # SQLAlchemy models
│   │   ├── routers/  # API endpoints
│   │   ├── services/ # Business logic
│   │   └── schemas/  # Pydantic schemas
│   └── alembic/      # Database migrations
└── frontend/         # Vue 3 frontend
    └── src/
        ├── views/    # Page components
        ├── stores/   # Pinia stores
        └── router/   # Vue Router
```

## 🔧 Configuration

### Backend Environment Variables (.env)

```env
DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5432/specflow
REDIS_URL=redis://localhost:6379/0
JWT_SECRET_KEY=your-secret-key-here
OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL=qwen3-vl:235b-cloud
```

### Frontend Environment Variables (optional)

```env
VITE_API_URL=http://localhost:8000
```

## 📚 Documentation

- **Backend API:** `http://localhost:8000/docs` (Swagger UI)
- **Project Status:** See `PROJECT_STATUS.md` for implementation details
- **Specifications:** See `SpecificationDocs/` for full requirements

## 🧪 Development

### Backend

```bash
# Run migrations
alembic revision --autogenerate -m "description"
alembic upgrade head

# Run tests
pytest

# Format code
black app/
ruff check app/
```

### Frontend

```bash
# Development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

## 🚢 Deployment

### Backend
- Use Gunicorn/Uvicorn with multiple workers
- Set up PostgreSQL and Redis instances
- Configure environment variables
- Run Alembic migrations

### Frontend
- Build: `npm run build`
- Serve `dist/` folder with any static hosting (Nginx, Vercel, Netlify)

## 🤝 Contributing

This project follows the specifications in `SpecificationDocs/`:
- `PROJECT_DEFINITION.md` - Core concepts
- `implementation.md` - Implementation plan
- `BE.md` - Backend specification
- `FE.md` - Frontend specification
- `branding.json` - Brand guidelines

## 📝 License

Private project - All rights reserved

## 🙏 Acknowledgments

- Vue Flow for the amazing graph visualization library
- Ollama for local AI capabilities
- FastAPI for the excellent Python framework
- TailwindCSS for beautiful styling utilities

---

**Built with ❤️ by Benjamin**
