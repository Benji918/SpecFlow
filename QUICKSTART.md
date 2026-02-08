# SpecFlow - Quick Start Guide

This guide will help you get SpecFlow up and running in **under 10 minutes**.

## Step 1: Prerequisites Check

Ensure you have the following installed:

```bash
# Check Python version (need 3.11+)
python3 --version

# Check Node.js version (need 20+)
node --version

# Check PostgreSQL (need 15+)
psql --version

# Check Redis (need 7+)
redis-cli --version

# Check Ollama
ollama --version
```

If any are missing, install them first.

## Step 2: Install Ollama Model

```bash
# Pull the required model (this may take a few minutes)
ollama pull qwen3-vl:235b-cloud
```

## Step 3: Setup PostgreSQL Database

```bash
# Create database
sudo -u postgres psql -c "CREATE DATABASE specflow;"
sudo -u postgres psql -c "CREATE USER specflow WITH PASSWORD 'specflow';"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE specflow TO specflow;"
```

## Step 4: Setup Redis

```bash
# Start Redis
sudo systemctl start redis
# Or on WSL:
sudo service redis-server start
```

## Step 5: Backend Setup

```bash
cd backend

# Create .env file
cat > .env << EOF
DATABASE_URL=postgresql+asyncpg://specflow:specflow@localhost:5432/specflow
REDIS_URL=redis://localhost:6379/0
JWT_SECRET_KEY=$(openssl rand -hex 32)
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440
OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL=qwen3-vl:235b-cloud
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0
APP_NAME=SpecFlow
DEBUG=True
CORS_ORIGINS=http://localhost:5173,http://localhost:3000
EOF

# Install UV (Python package manager)
pip install uv

# Install dependencies
uv pip install -e .

# Run database migrations
alembic upgrade head

# Start the backend server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The backend should now be running at `http://localhost:8000`

You can check the API docs at: `http://localhost:8000/docs`

## Step 6: Frontend Setup (New Terminal)

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

The frontend should now be running at `http://localhost:5173`

## Step 7: First Login

1. Open your browser to `http://localhost:5173`
2. Click "Sign up"
3. Create your account
4. You'll be redirected to the dashboard

## Step 8: Upload Your First Spec

1. From the dashboard, click "New Project"
2. Upload an OpenAPI spec file (JSON or YAML)
3. Click "Generate Journeys" to let AI create test flows
4. Edit the journey graph as needed
5. Click "Run" to execute the test

## Troubleshooting

### Backend won't start
```bash
# Check if PostgreSQL is running
sudo systemctl status postgresql
# Or on WSL:
sudo service postgresql status

# Check if Redis is running
redis-cli ping
# Should return: PONG
```

### Ollama model not found
```bash
# List installed models
ollama list

# If qwen3-vl:235b-cloud is not there, pull it
ollama pull qwen3-vl:235b-cloud
```

### Database connection error
```bash
# Make sure the database exists
psql -U specflow -d specflow -c "SELECT 1;"
# Enter password: specflow
```

### Frontend can't connect to backend
- Make sure backend is running on port 8000
- Check CORS settings in backend/.env
- Verify proxy settings in frontend/vite.config.js

### Port already in use
```bash
# Backend (8000)
lsof -ti:8000 | xargs kill -9

# Frontend (5173)
lsof -ti:5173 | xargs kill -9
```

## Next Steps

Now that you have SpecFlow running:

1. **Explore the docs**: Check `SpecificationDocs/` for detailed feature info
2. **Read PROJECT_STATUS.md**: See what's built and what's next
3. **Try the API**: Visit `http://localhost:8000/docs`
4. **Build remaining views**: See PROJECT_STATUS.md for frontend todos

## Need Help?

- Check `README.md` for full documentation
- Review `PROJECT_STATUS.md` for implementation details
- See `SpecificationDocs/` for requirements

---

**Happy Testing! 🚀**
