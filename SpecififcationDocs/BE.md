# SpecFlow Backend Specification (MVP)

## Overview
FastAPI backend for parsing OpenAPI specs, generating journeys via AI, executing API tests, and managing user data.

## Tech Stack
- **Framework:** FastAPI 0.104+ (Python 3.11+)
- **Database:** PostgreSQL 15+ (via SQLAlchemy 2.0)
- **Cache:** Redis 7+ (journey execution state, rate limiting)
- **Task Queue:** Celery 5+ with Redis broker
- **ORM:** SQLAlchemy 2.0 (async mode)
- **Migrations:** Alembic
- **Validation:** Pydantic 2.0
- **OpenAPI Parsing:** pydantic-openapi, prance
- **AI:** Anthropic Python SDK (Claude)
- **Mock Data:** Faker
- **Auth:** python-jose (JWT), passlib (password hashing)
- **HTTP Client:** httpx (async)
- **WebSockets:** FastAPI native WebSocket support

## Database Schema
```python
# models/user.py
class User(Base):
    __tablename__ = "users"
    
    id = Column(UUID, primary_key=True, default=uuid.uuid4)
    email = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)
    name = Column(String)
    plan = Column(Enum('free', 'starter', 'team', 'pro'), default='free')
    created_at = Column(DateTime, default=datetime.utcnow)
    
    specs = relationship("Spec", back_populates="user")
    journeys = relationship("Journey", back_populates="user")

# models/spec.py
class Spec(Base):
    __tablename__ = "specs"
    
    id = Column(UUID, primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID, ForeignKey("users.id"))
    name = Column(String, nullable=False)
    version = Column(String)
    content = Column(JSON, nullable=False)  # Full OpenAPI spec
    endpoints = Column(JSON)  # Parsed endpoint list
    schemas = Column(JSON)  # Component schemas
    uploaded_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="specs")
    journeys = relationship("Journey", back_populates="spec")

# models/journey.py
class Journey(Base):
    __tablename__ = "journeys"
    
    id = Column(UUID, primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID, ForeignKey("users.id"))
    spec_id = Column(UUID, ForeignKey("specs.id"))
    name = Column(String, nullable=False)
    nodes = Column(JSON, nullable=False)  # VueFlow nodes
    edges = Column(JSON, nullable=False)  # VueFlow edges
    generation_method = Column(Enum('ai', 'manual'), default='ai')
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)
    
    user = relationship("User", back_populates="journeys")
    spec = relationship("Spec", back_populates="journeys")
    executions = relationship("Execution", back_populates="journey")

# models/execution.py
class Execution(Base):
    __tablename__ = "executions"
    
    id = Column(UUID, primary_key=True, default=uuid.uuid4)
    journey_id = Column(UUID, ForeignKey("journeys.id"))
    status = Column(Enum('running', 'completed', 'failed'), default='running')
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime)
    results = Column(JSON)  # Array of step results
    
    journey = relationship("Journey", back_populates="executions")
```

---

## Core Modules

### 1. Authentication & Authorization

**File:** `app/auth.py`
```python
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
SECRET_KEY = os.getenv("JWT_SECRET_KEY")
ALGORITHM = "HS256"

def create_access_token(data: dict, expires_delta: timedelta = timedelta(hours=24)):
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def verify_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

async def get_current_user(token: str = Depends(oauth2_scheme)):
    payload = verify_token(token)
    user_id = payload.get("sub")
    user = await db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user
```

**Endpoints:**
```python
POST /api/auth/register
  Body: { email, password, name }
  Returns: { user, token }

POST /api/auth/login
  Body: { email, password }
  Returns: { user, token }

POST /api/auth/refresh
  Headers: { Authorization: Bearer <token> }
  Returns: { token }
```

---

### 2. OpenAPI Spec Parsing

**File:** `app/services/spec_parser.py`
```python
import prance
from typing import Dict, List
from pydantic import BaseModel

class EndpointInfo(BaseModel):
    path: str
    method: str
    operation_id: str
    summary: str
    description: str
    parameters: List[Dict]
    request_body: Dict | None
    responses: Dict
    security: List[Dict]
    tags: List[str]

class SpecParser:
    def __init__(self, spec_content: Dict):
        # Resolve all $ref pointers
        parser = prance.ResolvingParser(spec_dict=spec_content)
        self.spec = parser.specification
    
    def extract_endpoints(self) -> List[EndpointInfo]:
        endpoints = []
        
        for path, methods in self.spec['paths'].items():
            for method, details in methods.items():
                if method in ['get', 'post', 'put', 'patch', 'delete']:
                    endpoints.append(EndpointInfo(
                        path=path,
                        method=method.upper(),
                        operation_id=details.get('operationId', f"{method}_{path}"),
                        summary=details.get('summary', ''),
                        description=details.get('description', ''),
                        parameters=details.get('parameters', []),
                        request_body=details.get('requestBody'),
                        responses=details.get('responses', {}),
                        security=details.get('security', []),
                        tags=details.get('tags', [])
                    ))
        
        return endpoints
    
    def get_schemas(self) -> Dict:
        return self.spec.get('components', {}).get('schemas', {})
    
    def get_security_schemes(self) -> Dict:
        return self.spec.get('components', {}).get('securitySchemes', {})
```

**Endpoints:**
```python
POST /api/specs
  Body: { name, content: <OpenAPI spec JSON> }
  Process:
    1. Validate spec with prance
    2. Extract endpoints
    3. Extract schemas
    4. Save to database
  Returns: { id, endpoints, schemas }

GET /api/specs/:id
  Returns: { id, name, version, endpoints, schemas }

DELETE /api/specs/:id
  Deletes spec and all associated journeys
```

---

### 3. AI Journey Generation

**File:** `app/services/journey_generator.py`
```python
from anthropic import Anthropic
import json

class JourneyGenerator:
    def __init__(self):
        self.client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
    
    async def generate_journeys(self, endpoints: List[EndpointInfo]) -> List[Dict]:
        """
        Use Claude to infer logical user journeys from endpoints
        """
        
        endpoint_summary = self._format_endpoints(endpoints)
        
        prompt = f"""
You are an API testing expert. Given these API endpoints, identify 3-5 logical user journeys.

Endpoints:
{endpoint_summary}

For each journey, return JSON with:
- name: Short descriptive name
- description: What this journey tests
- steps: Array of {{
    operationId: string,
    name: string,
    data_mappings: [{{ from: "response.field", to: "request.field" }}]
  }}

Rules:
1. Auth endpoints (login/register) should be first steps
2. Map data between steps (e.g., login token → auth header)
3. Follow logical workflows (e.g., create resource → update → delete)
4. Include error testing journeys (e.g., "Test unauthorized access")

Return ONLY a JSON array, no explanation.
"""

        response = self.client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=4000,
            messages=[{"role": "user", "content": prompt}]
        )
        
        # Parse Claude's response
        journeys_json = response.content[0].text
        journeys = json.loads(journeys_json)
        
        # Convert to VueFlow format
        return self._convert_to_vueflow_format(journeys, endpoints)
    
    def _format_endpoints(self, endpoints: List[EndpointInfo]) -> str:
        return "\n".join([
            f"{e.method} {e.path} - {e.operation_id} ({e.summary})"
            for e in endpoints
        ])
    
    def _convert_to_vueflow_format(self, journeys: List[Dict], endpoints: List[EndpointInfo]) -> List[Dict]:
        """
        Convert AI-generated journey steps into VueFlow nodes and edges
        """
        result = []
        
        for journey in journeys:
            nodes = []
            edges = []
            
            for idx, step in enumerate(journey['steps']):
                # Find endpoint details
                endpoint = next(
                    (e for e in endpoints if e.operation_id == step['operationId']),
                    None
                )
                
                if not endpoint:
                    continue
                
                # Create node
                nodes.append({
                    "id": f"step-{idx}",
                    "type": "endpoint",
                    "position": {"x": 100, "y": idx * 150},
                    "data": {
                        "method": endpoint.method,
                        "path": endpoint.path,
                        "operationId": endpoint.operation_id,
                        "requestBody": endpoint.request_body,
                        "responses": endpoint.responses,
                        "status": "pending"
                    }
                })
                
                # Create edge to previous step
                if idx > 0:
                    edges.append({
                        "id": f"e{idx-1}-{idx}",
                        "source": f"step-{idx-1}",
                        "target": f"step-{idx}",
                        "label": f"{step['data_mappings'][0]['from']} → {step['data_mappings'][0]['to']}" if step.get('data_mappings') else "",
                        "data": {
                            "dataMapping": step.get('data_mappings', [])
                        }
                    })
            
            result.append({
                "name": journey['name'],
                "description": journey['description'],
                "nodes": nodes,
                "edges": edges
            })
        
        return result
```

**Endpoints:**
```python
POST /api/specs/:id/generate-journeys
  Body: { strategy: 'ai' | 'manual' }
  Process:
    1. Fetch spec endpoints
    2. Call Claude API to generate journeys
    3. Save journeys to database
  Returns: [ { id, name, nodes, edges } ]
```

### 5. Journey Execution Engine

**File:** `app/services/journey_executor.py`
```python
import httpx
from typing import Dict, List
import asyncio

class JourneyExecutor:
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.session = httpx.AsyncClient(timeout=30.0)
    
    async def execute_journey(
        self,
        journey: Dict,
        session_data: Dict = {},
        error_injections: Dict = {}
    ) -> List[Dict]:
        """
        Execute all steps in a journey and return results
        """
        results = []
        
        for node in journey['nodes']:
            step_id = node['id']
            
            # Check for error injection
            if step_id in error_injections:
                result = self._inject_error(node, error_injections[step_id])
            else:
                result = await self._execute_step(node, session_data)
            
            results.append(result)
            
            # Update session data for next steps
            self._update_session_data(session_data, result, journey['edges'])
            
            # Stop if step failed and continueOnError is false
            if result['statusCode'] >= 400 and not node['data'].get('continueOnError'):
                break
        
        return results
    
    async def _execute_step(self, node: Dict, session_data: Dict) -> Dict:
        """
        Execute a single API call
        """
        data = node['data']
        
        # Build URL
        url = self.base_url + data['path']
        url = self._interpolate_path_params(url, session_data)
        
        # Build headers
        headers = self._build_headers(data, session_data)
        
        # Build request body
        body = self._build_body(data, session_data)
        
        # Execute request
        try:
            start_time = datetime.utcnow()
            
            response = await self.session.request(
                method=data['method'],
                url=url,
                headers=headers,
                json=body if data['method'] in ['POST', 'PUT', 'PATCH'] else None
            )
            
            duration = (datetime.utcnow() - start_time).total_seconds() * 1000
            
            return {
                "stepId": node['id'],
                "statusCode": response.status_code,
                "responseBody": response.json() if response.content else None,
                "headers": dict(response.headers),
                "duration": duration,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            return {
                "stepId": node['id'],
                "statusCode": 0,
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    def _update_session_data(self, session_data: Dict, result: Dict, edges: List[Dict]):
        """
        Extract data from response and make available for next steps
        """
        if not result.get('responseBody'):
            return
        
        # Find edges originating from this step
        relevant_edges = [e for e in edges if e['source'] == result['stepId']]
        
        for edge in relevant_edges:
            mappings = edge.get('data', {}).get('dataMapping', [])
            
            for mapping in mappings:
                # Extract value from response
                from_path = mapping['from'].replace('response.', '')
                value = self._get_nested_value(result['responseBody'], from_path)
                
                # Store for use in next step
                to_path = mapping['to']
                session_data[to_path] = value
    
    def _interpolate_path_params(self, url: str, session_data: Dict) -> str:
        """
        Replace {param} in URL with values from session_data
        """
        import re
        
        def replacer(match):
            param_name = match.group(1)
            return str(session_data.get(f'pathParams.{param_name}', match.group(0)))
        
        return re.sub(r'\{(\w+)\}', replacer, url)
    
    def _build_headers(self, step_data: Dict, session_data: Dict) -> Dict:
        """
        Build headers, including auth from session
        """
        headers = {}
        
        # Add Authorization if token exists in session
        if 'auth_token' in session_data:
            headers['Authorization'] = f"Bearer {session_data['auth_token']}"
        
        return headers
    
    def _build_body(self, step_data: Dict, session_data: Dict) -> Dict:
        """
        Build request body, interpolating values from session
        """
        if not step_data.get('requestBody'):
            return None
        
        body_template = step_data['requestBody']
        
        # Replace placeholders with session data
        return self._interpolate_dict(body_template, session_data)
    
    def _get_nested_value(self, obj: Dict, path: str) -> Any:
        """
        Get nested value from dict using dot notation (e.g., 'user.id')
        """
        keys = path.split('.')
        value = obj
        
        for key in keys:
            if isinstance(value, dict):
                value = value.get(key)
            else:
                return None
        
        return value
```

**WebSocket Endpoint:**
```python
@app.websocket("/ws/journey/{journey_id}/execute")
async def execute_journey_ws(
    websocket: WebSocket,
    journey_id: str,
    current_user: User = Depends(get_current_user)
):
    await websocket.accept()
    
    # Fetch journey
    journey = await db.query(Journey).filter(Journey.id == journey_id).first()
    
    # Create execution record
    execution = Execution(journey_id=journey_id, status='running')
    db.add(execution)
    await db.commit()
    
    # Get base URL from frontend
    data = await websocket.receive_json()
    base_url = data['baseUrl']
    session_data = data.get('sessionData', {})
    error_injections = data.get('errorInjections', {})
    
    # Execute journey
    executor = JourneyExecutor(base_url)
    
    for node in journey.nodes:
        # Send status update
        await websocket.send_json({
            "type": "step_start",
            "stepId": node['id']
        })
        
        # Execute step
        if node['id'] in error_injections:
            result = executor._inject_error(node, error_injections[node['id']])
        else:
            result = await executor._execute_step(node, session_data)
        
        # Send result
        await websocket.send_json({
            "type": "step_result",
            "result": result
        })
        
        # Update session for next steps
        executor._update_session_data(session_data, result, journey.edges)
        
        # Store result
        if not execution.results:
            execution.results = []
        execution.results.append(result)
        await db.commit()
        
        # Stop on error if needed
        if result['statusCode'] >= 400 and not node['data'].get('continueOnError'):
            break
    
    # Mark execution complete
    execution.status = 'completed'
    execution.completed_at = datetime.utcnow()
    await db.commit()
    
    await websocket.send_json({"type": "execution_complete"})
    await websocket.close()
```

---

### 6. Celery Background Tasks

**File:** `app/tasks.py`
```python
from celery import Celery

celery_app = Celery(
    "specflow",
    broker=os.getenv("REDIS_URL"),
    backend=os.getenv("REDIS_URL")
)

@celery_app.task
def generate_journeys_async(spec_id: str):
    """
    Background task to generate journeys using AI
    """
    spec = db.query(Spec).filter(Spec.id == spec_id).first()
    
    parser = SpecParser(spec.content)
    endpoints = parser.extract_endpoints()
    
    generator = JourneyGenerator()
    journeys = await generator.generate_journeys(endpoints)
    
    # Save journeys to database
    for journey_data in journeys:
        journey = Journey(
            user_id=spec.user_id,
            spec_id=spec_id,
            name=journey_data['name'],
            nodes=journey_data['nodes'],
            edges=journey_data['edges'],
            generation_method='ai'
        )
        db.add(journey)
    
    db.commit()
    
    return {"status": "completed", "count": len(journeys)}
```

---

### 7. Rate Limiting & Caching

**File:** `app/middleware/rate_limit.py`
```python
import redis
from fastapi import Request, HTTPException
from datetime import datetime, timedelta

redis_client = redis.from_url(os.getenv("REDIS_URL"))

async def rate_limit_middleware(request: Request, call_next):
    """
    Rate limit: 100 requests per minute per user
    """
    user_id = request.state.user.id if hasattr(request.state, 'user') else 'anonymous'
    
    key = f"rate_limit:{user_id}:{datetime.utcnow().strftime('%Y-%m-%d-%H-%M')}"
    
    current = redis_client.get(key)
    
    if current and int(current) >= 100:
        raise HTTPException(status_code=429, detail="Rate limit exceeded")
    
    redis_client.incr(key)
    redis_client.expire(key, 60)
    
    response = await call_next(request)
    return response
```

---

## API Endpoints Summary
```
Auth:
POST   /api/auth/register
POST   /api/auth/login
POST   /api/auth/refresh

Specs:
POST   /api/specs
GET    /api/specs
GET    /api/specs/:id
DELETE /api/specs/:id

Journeys:
POST   /api/specs/:id/generate-journeys
GET    /api/journeys
GET    /api/journeys/:id
PUT    /api/journeys/:id
DELETE /api/journeys/:id

Execution:
WS     /ws/journey/:id/execute
GET    /api/executions/:id
GET    /api/journeys/:id/executions (history)

Utils:
GET    /api/health
```

---

## Folder Structure
```
app/
├── main.py (FastAPI app initialization)
├── config.py (env vars, settings)
├── database.py (SQLAlchemy async DB setup)
├── models/
│   ├── user.py
│   ├── spec.py
│   ├── journey.py
│   └── execution.py
├── schemas/
│   ├── user.py (Pydantic schemas)
│   ├── spec.py
│   └── journey.py
├── routers/
│   ├── auth.py
│   ├── specs.py
│   ├── journeys.py
│   └── execution.py
├── services/
│   ├── spec_parser.py
│   ├── journey_generator.py
│   └── journey_executor.py
├── middleware/
│   ├── auth.py
│   └── rate_limit.py
├── tasks.py (Celery tasks)
└── utils/
    ├── security.py
    └── helpers.py
```

Backend's job is simply to:

Receive journey definition + mock data from frontend
Execute the API calls using that exact mock data
Return results


# Backend receives this from frontend:

```
{
  "journey": { nodes, edges },
  "mockData": {
    "step-1": { "email": "test@example.com", "password": "123" },
    "step-2": { "restaurant_id": "uuid-here" }
  }
}

```
