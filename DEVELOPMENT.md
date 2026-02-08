# SpecFlow Development Guide

## Project Architecture

### Backend Architecture

#### Layers
1. **API Layer** (`app/routers/`) - FastAPI route handlers
2. **Service Layer** (`app/services/`) - Business logic
3. **Data Layer** (`app/models/`) - SQLAlchemy models
4. **Schema Layer** (`app/schemas/`) - Pydantic validation

#### Key Services

**Authentication Service** (`services/auth.py`)
- JWT token generation and verification
- Password hashing with BCrypt
- User dependency injection

**Spec Parser Service** (`services/spec_parser.py`)
- Parses OpenAPI specifications using Prance
- Resolves $ref pointers
- Extracts endpoints, schemas, and security schemes

**Journey Generator Service** (`services/journey_generator.py`)
- Uses Ollama AI to analyze endpoints
- Generates logical user journey workflows
- Converts to VueFlow format (nodes + edges)

**Journey Executor Service** (`services/journey_executor.py`)
- Executes API calls in sequence
- Manages session state
- Handles data flow between steps
- Supports error injection for testing

### Frontend Architecture

#### State Management (Pinia)

**Auth Store** (`stores/auth.js`)
- User authentication state
- Token management
- Login/logout/register actions

**Spec Store** (`stores/spec.js`)
- OpenAPI spec list and current spec
- Upload, update, delete operations

**Journey Store** (`stores/journey.js`)
- Journey list and active journey
- Execution state and results
- Session data management

#### Routing

Protected routes require authentication:
- `/dashboard` - Main dashboard
- `/spec/:id` - Spec details
- `/journey/:id` - Journey editor

Public routes:
- `/login` - Login page
- `/signup` - Registration page

## Development Workflow

### Adding a New Feature

#### Backend Example: Add a new endpoint

1. **Create Pydantic schema** in `app/schemas/`
2. **Add route handler** in `app/routers/`
3. **Implement business logic** in `app/services/` (if needed)
4. **Test with Swagger** at `/docs`

Example:
```python
# app/schemas/feature.py
from pydantic import BaseModel

class FeatureCreate(BaseModel):
    name: str
    description: str

# app/routers/features.py
from fastapi import APIRouter, Depends

router = APIRouter(prefix="/api/features")

@router.post("")
async def create_feature(
    data: FeatureCreate,
    current_user: User = Depends(get_current_user),
):
    # Implementation
    pass
```

#### Frontend Example: Add a new component

1. **Create component** in `src/components/`
2. **Import and use** in a view
3. **Add to router** if it's a page

Example:
```vue
<!-- src/components/MyComponent.vue -->
<template>
  <div class="card">
    <h2>{{ title }}</h2>
  </div>
</template>

<script setup>
defineProps({
  title: String
})
</script>
```

### Database Migrations

#### Create a migration
```bash
cd backend
alembic revision --autogenerate -m "Add new table"
```

#### Review the generated file
```bash
# Check alembic/versions/XXXXX_add_new_table.py
```

#### Apply Migration
```bash
alembic upgrade head
```

#### Rollback
```bash
alembic downgrade -1
```

## Code Style Guidelines

### Backend (Python)

- Use **async/await** for all database and I/O operations
- Follow **PEP 8** style guide
- Use **type hints** for function parameters and return values
- Format with **Black** and lint with **Ruff**

```python
# Good
async def get_user(user_id: UUID, db: AsyncSession) -> User:
    result = await db.execute(select(User).where(User.id == user_id))
    return result.scalar_one_or_none()

# Bad
def get_user(user_id, db):
    return db.query(User).filter(User.id == user_id).first()
```

### Frontend (Vue)

- Use **Composition API** with `<script setup>`
- Use **reactive** and **ref** appropriately
- Follow **Vue style guide**
- Use **Tailwind classes** for styling

```vue
<!-- Good -->
<script setup>
import { ref } from 'vue'

const count = ref(0)
const increment = () => count.value++
</script>

<!-- Bad -->
<script>
export default {
  data() {
    return { count: 0 }
  }
}
</script>
```

## Testing

### Backend Tests

```bash
cd backend
pytest
```

Test structure:
```python
# tests/test_auth.py
def test_register():
    response = client.post("/api/auth/register", json={
        "email": "test@example.com",
        "password": "password123"
    })
    assert response.status_code == 201
```

### Frontend Tests

```bash
cd frontend
npm run test
```

## Debugging

### Backend Debugging

1. **Enable DEBUG in .env**
```env
DEBUG=True
```

2. **Check logs**
```bash
# Uvicorn shows all requests
uvicorn app.main:app --reload --log-level debug
```

3. **Use Swagger UI**
- Visit `http://localhost:8000/docs`
- Test endpoints interactively

### Frontend Debugging

1. **Vue Devtools**
- Install browser extension
- Inspect component state and Pinia stores

2. **Console logging**
```javascript
console.log('Debug:', value)
```

3. **Network tab**
- Check API requests/responses in browser DevTools

## Common Issues

### Backend

**Issue: SQLAlchemy async session errors**
```python
# Wrong
user = db.query(User).first()

# Correct
result = await db.execute(select(User))
user = result.scalar_one_or_none()
```

**Issue: CORS errors**
- Check `CORS_ORIGINS` in `.env`
- Ensure frontend URL is listed

### Frontend

**Issue: Pinia store not reactive**
```javascript
// Wrong
const users = userStore.users // Not reactive

// Correct
import { storeToRefs } from 'pinia'
const { users } = storeToRefs(userStore)
```

**Issue: Router navigation not working**
```javascript
// Use router.push, not window.location
import { useRouter } from 'vue-router'
const router = useRouter()
router.push('/dashboard')
```

## Performance Optimization

### Backend

1. **Use database indexes**
```python
class User(Base):
    email = Column(String, unique=True, index=True)  # Add index
```

2. **Lazy load relationships**
```python
# Only load what you need
result = await db.execute(
    select(User).where(User.id == user_id)
)
```

3. **Use Redis for caching**
```python
# Cache frequently accessed data
redis_client.set(f"user:{user_id}", user_data, ex=3600)
```

### Frontend

1. **Lazy load routes**
```javascript
const Dashboard = () => import('@/views/Dashboard.vue')
```

2. **Debounce API calls**
```javascript
import { useDebounceFn } from '@vueuse/core'
const debouncedSearch = useDebounceFn(search, 500)
```

3. **Virtual scrolling for large lists**
```vue
<template>
  <div v-for="item in visibleItems" :key="item.id">
    <!-- Only render visible items -->
  </div>
</template>
```

## Security Best Practices

### Backend

1. **Never expose secrets**
   - Use environment variables
   - Don't commit `.env` files

2. **Validate all inputs**
   - Use Pydantic schemas
   - Sanitize user data

3. **Use HTTPS in production**
   - Configure SSL certificates
   - Force HTTPS redirects

### Frontend

1. **Never store secrets in localStorage**
   - Only store non-sensitive tokens
   - Clear on logout

2. **Sanitize user input**
   - Prevent XSS attacks
   - Use Vue's built-in escaping

3. **Use CORS properly**
   - Whitelist specific origins
   - Don't use `*` in production

## Deployment Checklist

### Backend

- [ ] Set `DEBUG=False`
- [ ] Use strong `JWT_SECRET_KEY`
- [ ] Configure production database
- [ ] Set up Redis
- [ ] Run migrations
- [ ] Use Gunicorn with multiple workers
- [ ] Configure reverse proxy (Nginx)
- [ ] Set up SSL certificates
- [ ] Configure monitoring (Sentry)

### Frontend

- [ ] Build for production: `npm run build`
- [ ] Configure environment variables
- [ ] Set up static hosting
- [ ] Configure CDN
- [ ] Enable caching
- [ ] Set up error tracking

## Monitoring

### Backend
- Use Sentry for error tracking
- Monitor database performance
- Track API response times
- Set up health check endpoints

### Frontend
- Track user interactions
- Monitor bundle size
- Track Core Web Vitals
- Set up analytics

## Resources

- **FastAPI Docs**: https://fastapi.tiangolo.com
- **Vue 3 Docs**: https://vuejs.org
- **Vue Flow Docs**: https://vueflow.dev
- **Pinia Docs**: https://pinia.vuejs.org
- **TailwindCSS Docs**: https://tailwindcss.com
- **Ollama Docs**: https://ollama.ai

## Getting Help

1. Check `PROJECT_STATUS.md` for implementation status
2. Review `SpecificationDocs/` for requirements
3. Read `README.md` for setup instructions
4. Visit `http://localhost:8000/docs` for API documentation

---

**Keep building! 🚀**
