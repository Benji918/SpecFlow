# SpecFlow - Project Definition

## What is SpecFlow?

SpecFlow is a **context-aware API testing platform** that automatically transforms OpenAPI specifications into interactive, visual user journey workflows. It bridges the gap between isolated endpoint testing and real-world API usage by understanding how endpoints relate to each other and executing them in meaningful sequences.

## Core Problem Statement

Traditional API testing tools (Postman, Insomnia, Swagger UI) force developers to:
- Manually chain API requests together
- Copy/paste data between requests (tokens, IDs, etc.)
- Test endpoints in isolation without workflow context
- Spend hours setting up collections for multi-step scenarios
- Repeatedly update test collections when APIs change

**SpecFlow solves this by automatically generating and executing realistic API workflows based on OpenAPI specifications.**

---

## What SpecFlow Does

### Primary Function
**Converts OpenAPI specs → Interactive user journey tests**

### Core Workflow
```
1. User uploads OpenAPI spec (JSON/YAML)
   ↓
2. SpecFlow parses and validates the specification
   ↓
3. AI (Ollama) analyzes endpoints and generates logical user journeys
   ↓
4. User sees visual workflow graph (drag-and-drop interface)
   ↓
5. SpecFlow auto-generates mock data for each step
   ↓
6. User executes journey and sees real-time results
   ↓
7. SpecFlow handles authentication, data passing, and session management automatically
```

### Key Capabilities

1. **OpenAPI Spec Parsing**
   - Accepts Swagger 2.0 and OpenAPI 3.0+ specifications
   - Validates spec structure and schemas
   - Extracts all endpoints, parameters, request bodies, and responses
   - Resolves $ref pointers (including external files)

2. **AI-Powered Journey Generation**
   - Uses Ollama (qwen3-vl:235b-cloud) to analyze endpoint relationships
   - Identifies logical user flows (e.g., Register → Verify → Login → Browse)
   - Determines data dependencies between steps
   - Suggests multiple journey types (happy path, error handling, edge cases)

3. **Visual Workflow Builder**
   - Interactive drag-and-drop canvas using Vue Flow
   - Each node = one API endpoint
   - Each edge = data flow between endpoints
   - Real-time reorganization of journey execution order
   - Manual journey creation and editing

4. **Mock Data Generation**
   - Automatically generates realistic test data based on OpenAPI schemas
   - Uses Faker.js for context-aware mock data (emails, UUIDs, names, dates)
   - Respects schema constraints (minLength, maxLength, enum, pattern, required)
   - Allows manual editing of generated data
   - Saves common test payloads as presets

5. **Smart Journey Execution**
   - Executes API calls in the order defined by the visual workflow
   - Automatically extracts data from responses (tokens, IDs, etc.)
   - Passes extracted data to subsequent requests (via headers, path params, body)
   - Handles authentication flows (JWT, OAuth, API keys)
   - Maintains session state across all steps in a journey
   - Supports error injection for testing failure scenarios

6. **Real-Time Result Display**
   - Shows request payload, headers, and method for each step
   - Displays response body, status code, headers, and timing
   - Highlights pass/fail status with visual indicators
   - Provides request/response diff viewer
   - Exports results as JSON or generates reports

7. **Environment Management**
   - Switch between different API base URLs (dev, staging, production)
   - Stores environment-specific configurations
   - Applies different auth credentials per environment

8. **Team Collaboration**
   - Save and share journeys with team members
   - Export journeys to Postman collections
   - Generate shareable links for view-only access
   - Track journey execution history

---

## Core Features Breakdown

### Feature 1: OpenAPI Spec Upload & Validation
**What it does:**
- User uploads .json or .yaml file (or pastes spec URL)
- SpecFlow validates against OpenAPI schema using @apidevtools/swagger-parser
- Displays validation errors if spec is malformed
- Extracts and stores: paths, methods, parameters, request bodies, responses, schemas, security schemes

**Why it matters:**
Without a valid spec, nothing else works. This is the foundation.

---

### Feature 2: AI Journey Inference
**What it does:**
- Sends extracted endpoint list to Ollama API(Using qwen3-vl:235b-cloud model)
- Prompts Ollama to identify logical user workflows
- Ollama returns suggested journeys with:
  - Journey name (e.g., "Complete Order Flow")
  - Step sequence (ordered list of endpoints)
  - Data mappings (what data flows between steps)
  - Prerequisites (auth requirements)

**Example prompt to Ollama:**
```
Given these endpoints from a food delivery API:
- POST /auth/register
- POST /auth/verify-email
- POST /auth/login
- GET /restaurants
- GET /restaurants/{id}/menu
- POST /cart/add-items
- POST /orders/checkout

Identify 3-5 logical user journeys. For each journey, specify:
1. Name
2. Description
3. Steps (ordered endpoints)
4. Data mappings between steps

Return as JSON.
```

**Why it matters:**
Saves developers hours of manual journey creation. AI understands context humans miss.

---

### Feature 3: Visual Journey Workflow (Vue Flow)
**What it does:**
- Displays journey as interactive node graph
- Each node represents one API endpoint with:
  - HTTP method (GET, POST, etc.)
  - Endpoint path
  - Request body preview
  - Execution status (pending/running/success/error)
- Each edge represents data flow with labels showing what's passed
- Supports drag-to-reorder nodes
- Click to edit node details (request body, headers, etc.)
- Add/remove nodes and edges manually

**Visual representation:**
```
[POST /auth/login] → token
        ↓
[GET /restaurants] → restaurant_id
        ↓
[POST /orders] → order_id
```

**Why it matters:**
Non-technical users can understand and modify workflows visually without code.

---

### Feature 4: Mock Data Auto-Generation
**What it does:**
- Reads request body schema from OpenAPI spec
- Generates realistic mock data using Faker.js based on field types:
  - `format: "uuid"` → `faker.string.uuid()`
  - `format: "email"` → `faker.internet.email()`
  - `type: "string"` → `faker.lorem.words(3)`
  - `type: "integer"` → `faker.number.int({min: 1, max: 100})`
  - `type: "boolean"` → `faker.datatype.boolean()`
  - `enum: [...]` → random value from enum
- Respects required fields
- Allows manual editing via JSON editor
- Saves frequently used payloads as templates

**Why it matters:**
Eliminates tedious manual test data creation. Developers can test immediately.

---

### Feature 5: Journey Execution Engine
**What it does:**
- Takes journey workflow (nodes + edges)
- Executes API calls in topological order (respecting dependencies)
- For each step:
  1. Builds request URL (interpolates path parameters from session data)
  2. Adds headers (including auth tokens from previous steps)
  3. Constructs request body (merges mock data with session data)
  4. Makes HTTP request to target API
  5. Stores response in session state
  6. Extracts important data (tokens, IDs) for next steps
  7. Updates UI with real-time results
- Handles errors gracefully (stops or continues based on settings)
- Supports error injection (force timeout, fake 500 error, etc.)

**Example execution flow:**
```
Step 1: POST /auth/login
  Request: { email: "test@example.com", password: "123456" }
  Response: { token: "eyJhbGc..." }
  Session state after: { auth_token: "eyJhbGc..." }

Step 2: GET /restaurants
  Request headers: { Authorization: "Bearer eyJhbGc..." }
  Response: [{ id: "rest-123", name: "Pizza Place" }]
  Session state after: { auth_token: "...", restaurant_id: "rest-123" }

Step 3: POST /orders
  Request body: { restaurant_id: "rest-123", items: [...] }
  Response: { order_id: "order-456", status: "pending" }
  Session state after: { ..., order_id: "order-456" }
```

**Why it matters:**
This is the core value—automated multi-step API testing with intelligent data flow.

---

### Feature 6: Session State Management
**What it does:**
- Maintains an in-memory state object during journey execution
- Automatically extracts data from responses based on edge mappings
- Makes extracted data available to subsequent steps
- Handles common patterns:
  - Login response token → Authorization header for protected endpoints
  - Created resource ID → Path parameter for update/delete endpoints
  - User details → Request body fields for related requests
- Supports custom data mappings via edge configuration

**Data mapping configuration:**
```javascript
{
  from: "response.data.token",  // Extract from step N response
  to: "headers.Authorization"   // Inject into step N+1 request
}
```

**Why it matters:**
Without this, users would manually copy/paste between requests like in Postman.

---

### Feature 7: Error Injection & Testing
**What it does:**
- For any step, user can inject:
  - Network timeout (simulate slow API)
  - Specific HTTP status code (force 400, 500, etc.)
  - Modified response body (test frontend error handling)
  - Missing authentication (test unauthorized access)
- Configurable "continue on error" behavior
- Visual indicators show injected errors vs real API errors

**Why it matters:**
Testing error scenarios is crucial but tedious. This makes it one-click.

---

### Feature 8: Real-Time Result Viewer
**What it does:**
- Displays request and response for each step as journey executes
- Shows:
  - HTTP method and full URL
  - Request headers
  - Request body (formatted JSON)
  - Response status code
  - Response headers
  - Response body (formatted JSON with syntax highlighting)
  - Execution duration (milliseconds)
- Provides copy buttons for cURL commands
- Allows export of request/response as files

**Why it matters:**
Transparency and debugging. Users see exactly what's happening at each step.

---

### Feature 9: Environment Configuration
**What it does:**
- User defines multiple environments:
  - Development: `https://dev-api.example.com`
  - Staging: `https://staging-api.example.com`
  - Production: `https://api.example.com`
- Each environment can have different:
  - Base URL
  - Authentication credentials
  - Custom headers
- Dropdown selector switches active environment
- Same journey runs against any environment

**Why it matters:**
Teams need to test across multiple environments without duplicating journeys.

---

### Feature 10: Journey Sharing & Export
**What it does:**
- Save journey to database for later reuse
- Generate shareable link (view-only or editable)
- Export as Postman collection (JSON)
- Export as cURL commands
- Export as automated test scripts (future feature)
- View execution history for a journey

**Why it matters:**
Collaboration and handoff between teams (backend → QA → frontend).

---

## Technical Architecture (High-Level)

### Frontend (Vue 3)
- **Spec Upload:** File upload component + validation
- **Journey Visualization:** Vue Flow for node graph
- **Mock Data Editor:** JSON editor with Faker integration
- **Execution UI:** Real-time WebSocket updates
- **State Management:** Pinia stores for specs, journeys, execution state

### Backend (FastAPI)
- **Spec Parsing:** pydantic-openapi + prance
- **AI Integration:** Ollama SDK for Ollama
- **Journey Storage:** PostgreSQL database
- **Execution Engine:** httpx for making API calls
- **Real-Time Communication:** WebSocket for streaming results

### Data Flow
```
Frontend                Backend                 External API
   |                       |                         |
   |--Upload Spec--------->|                         |
   |<--Validated Spec------|                         |
   |                       |                         |
   |--Generate Journeys--->|                         |
   |                       |--Analyze with Ollama--->|
   |<--Journey Suggestions-|                         |
   |                       |                         |
   |--Execute Journey----->|                         |
   |                       |--POST /auth/login------>|
   |                       |<--{token: "..."}--------|
   |<--Step 1 Result-------|                         |
   |                       |                         |
   |                       |--GET /restaurants------>|
   |                       |  (Auth: Bearer token)   |
   |                       |<--[{restaurants}]-------|
   |<--Step 2 Result-------|                         |
   |                       |                         |
   |--Continue...--------->|                         |
```

---

## User Personas

### 1. Backend Developer (Primary)
**Needs:**
- Test multi-step API workflows quickly
- Validate auth flows
- Share API behavior with frontend team
- Auto-update tests when spec changes

**Pain points SpecFlow solves:**
- No more manual Postman collection setup
- No more copy/pasting tokens
- Tests update automatically when spec changes

### 2. QA Engineer
**Needs:**
- Create regression test suites without coding
- Test error scenarios
- Generate test reports

**Pain points SpecFlow solves:**
- Visual interface requires no code
- Error injection is one-click
- Execution history provides audit trail

### 3. Frontend Developer
**Needs:**
- Understand API behavior before backend is done
- See real request/response examples
- Test edge cases independently

**Pain points SpecFlow solves:**
- Mock data lets them test immediately
- Visual workflows explain API dependencies
- Can inject errors to test frontend error handling

### 4. Product Manager (Secondary)
**Needs:**
- Validate user flows match requirements
- Communicate features to stakeholders
- No technical barrier

**Pain points SpecFlow solves:**
- Visual workflows are self-explanatory
- No coding required to create/run journeys
- Shareable links for stakeholder demos

---

## Core Value Proposition

**Traditional API Testing:**
- 2 hours to set up Postman collection
- Manual token management
- Isolated endpoint testing
- Breaks when API changes

**SpecFlow:**
- 2 minutes from spec to working tests
- Automatic data flow
- Real workflow testing
- Auto-syncs with spec updates

**Time savings:** 90%+ reduction in test setup time

---

## Success Metrics

A successful SpecFlow implementation means:

1. **User can upload OpenAPI spec and get valid journeys in < 3 minutes**
2. **AI generates at least 3 relevant journeys per spec**
3. **Mock data matches schema 100% of the time**
4. **Journey execution handles auth flows without manual intervention**
5. **Users can modify and re-run journeys in < 30 seconds**
6. **Results display updates in real-time (< 100ms latency)**
7. **Exported Postman collections work without modification**

---

## What SpecFlow Is NOT

❌ **Not a mock server** - It executes real API calls, doesn't simulate responses  
❌ **Not a load testing tool** - Focus is correctness, not performance  
❌ **Not a code generator** - Doesn't generate API client SDKs  
❌ **Not a monitoring tool** - Doesn't run continuously in production  
❌ **Not a documentation generator** - Swagger UI already does this well  

SpecFlow is specifically for **testing API workflows during development and QA**.

---

## Development Priorities

### MVP (Must Have)
1. OpenAPI spec upload and validation
2. AI journey generation (basic)
3. Visual workflow display (read-only first)
4. Mock data generation
5. Journey execution with auth handling
6. Real-time result display

### Phase 2 (MUST Have)
1. Drag-and-drop workflow editing
2. Custom data mapping between steps
3. Error injection
4. Environment management
5. Journey saving and sharing
6. Postman export

---

## Key Technical Decisions

1. **Frontend generates mock data** (not backend) for instant feedback
2. **WebSocket for execution** (not polling) for real-time updates
3. **Backend is execution engine only** - doesn't store mock data
4. **AI suggestions are editable** - users have full control
5. **Session state is ephemeral** - cleared after each journey run

---

## Summary for LLM Context

**SpecFlow is an API testing platform that:**
- Parses OpenAPI specs to extract endpoints and schemas
- Uses AI to generate logical multi-step user journey workflows
- Provides a visual drag-and-drop interface for editing journeys
- Auto-generates realistic mock data based on schemas
- Executes API calls in sequence while managing authentication and data flow
- Displays real-time request/response results
- Supports error injection and environment switching
- Enables team collaboration through sharing and export

**Core technical flow:**
Upload spec → AI generates journeys → User edits visually → Mock data auto-generated → Execute with smart session management → Display results in real-time

**Primary goal:**
Transform hours of manual API testing setup into minutes of automated, visual, workflow-based testing.
