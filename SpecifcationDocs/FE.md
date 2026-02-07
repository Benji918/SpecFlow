# SpecFlow Frontend Specification (MVP)

## Overview
Vue 3 SPA for visualizing and executing API journey tests from OpenAPI specs.

## Tech Stack
- **Framework:** Vue 3 + JavaScript (Composition API)
- **Build Tool:** Vite 5+
- **State Management:** Pinia
- **Routing:** Vue Router 4
- **HTTP Client:** Axios
- **Visualization:** @vue-flow/core (for journey graph)
- **UI Components:** 
  - TailwindCSS 3+ (styling)
  - shadcn-vue (component library)
  - Headless UI (modals, dropdowns)
- **Form Handling:** VeeValidate + Zod
- **OpenAPI Parsing:** @apidevtools/swagger-parser
- **Mock Data:** @faker-js/faker
- **Code Highlighting:** Prism.js or Shiki
- **Notifications:** vue-toastification

## Core Features & Implementation

### 1. Authentication & User Management
**Pages:**
- `/login` - Email/password login
- `/signup` - User registration
- `/forgot-password` - Password reset

**State (Pinia store: `useAuthStore`):**
```javascript
{
  user: { id, email, name, plan },
  token: string,
  isAuthenticated: boolean
}
```

**Implementation:**
- JWT stored in localStorage
- Axios interceptor adds `Authorization: Bearer {token}` to requests
- Route guards protect authenticated pages

---

### 2. OpenAPI Spec Management

**Pages:**
- `/dashboard` - List of uploaded specs
- `/spec/:id` - View spec details & journeys

**Components:**
- `SpecUploader.vue` - Drag-and-drop file upload (.json, .yaml)
- `SpecValidator.vue` - Shows validation errors from swagger-parser

**Validation Flow:**
```javascript
import SwaggerParser from '@apidevtools/swagger-parser';

async function validateSpec(file) {
  try {
    const spec = await SwaggerParser.validate(file);
    // Send to backend: POST /api/specs with parsed spec
    return { valid: true, spec };
  } catch (err) {
    return { valid: false, errors: err.message };
  }
}
```

**State (Pinia: `useSpecStore`):**
```javascript
{
  specs: [
    { id, name, version, uploadedAt, endpoints }
  ],
  currentSpec: { ...fullSpecObject },
  schemas: { ...componentSchemas }
}
```

---

### 3. Journey Visualization & Editing

**Page:** `/journey/:journeyId`

**Component: `JourneyFlow.vue`** (uses @vue-flow/core)
```javascript
// Node structure
{
  id: 'step-1',
  type: 'endpoint', // custom node type
  position: { x: 100, y: 100 },
  data: {
    method: 'POST',
    path: '/auth/login',
    operationId: 'login',
    requestBody: { ... },
    responses: { ... },
    status: 'pending' | 'running' | 'success' | 'error',
    result: { statusCode, responseBody, headers, duration }
  }
}

// Edge structure (data flow between steps)
{
  id: 'e1-2',
  source: 'step-1',
  target: 'step-2',
  label: 'token → Authorization header',
  data: {
    dataMapping: {
      from: 'response.token',
      to: 'headers.Authorization'
    }
  }
}
```

**Drag-and-Drop Behavior:**
1. User drags node → updates node position
2. User connects nodes → creates edge, opens data mapping modal
3. On position change → auto-save to backend via debounced API call
4. Order changes → regenerate execution sequence from graph topology

**State (Pinia: `useJourneyStore`):**
```javascript
{
  journeys: [
    { id, name, specId, nodes, edges, createdAt }
  ],
  activeJourney: { ... },
  executionState: 'idle' | 'running' | 'paused' | 'completed',
  executionResults: [
    { stepId, statusCode, responseBody, duration, timestamp }
  ]
}
```

---

### 4. Mock Data Generation

**Component: `MockDataEditor.vue`**

**Implementation:**
```javascript
import { faker } from '@faker-js/faker';

function generateMockFromSchema(schema) {
  const properties = schema.properties || {};
  const mockData = {};
  
  for (const [key, spec] of Object.entries(properties)) {
    if (spec.format === 'uuid') {
      mockData[key] = faker.string.uuid();
    } else if (spec.format === 'email') {
      mockData[key] = faker.internet.email();
    } else if (spec.type === 'string') {
      mockData[key] = faker.lorem.words(3);
    } else if (spec.type === 'integer') {
      mockData[key] = faker.number.int({ min: 1, max: 100 });
    }
    // ... handle all types
  }
  
  return mockData;
}
```

**Features:**
- Auto-generate button → fills all fields with mock data
- Manual edit → inline JSON editor with syntax highlighting
- Save presets → store common test payloads

---

### 5. Journey Execution Engine (Frontend Orchestration)

**Component: `JourneyRunner.vue`**

**Execution Flow:**
```javascript
async function executeJourney(journeyId) {
  const journey = journeyStore.getJourney(journeyId);
  const steps = topologicalSort(journey.nodes, journey.edges);
  
  for (const step of steps) {
    journeyStore.setStepStatus(step.id, 'running');
    
    try {
      // Call backend to execute this step
      const result = await axios.post('/api/execute-step', {
        journeyId,
        stepId: step.id,
        sessionData: journeyStore.sessionData // auth tokens, prev responses
      });
      
      journeyStore.saveStepResult(step.id, result.data);
      journeyStore.setStepStatus(step.id, 'success');
      
      // Update session data with response for next steps
      journeyStore.updateSessionData(result.data);
      
    } catch (error) {
      journeyStore.setStepStatus(step.id, 'error');
      journeyStore.saveStepError(step.id, error);
      
      if (!step.data.continueOnError) break;
    }
  }
}
```

**Real-time Updates:**
- WebSocket connection: `ws://backend/journey/${journeyId}/execute`
- Backend sends step results as they complete
- Frontend updates node status in real-time

---

### 6. Request/Response Viewer

**Component: `ResponsePanel.vue`**

**Features:**
- Tabbed view: Request | Response | Headers | Timing
- JSON syntax highlighting with Prism.js
- Diff view (compare with previous runs)
- Copy cURL command
- Export response as JSON file
```vue
<template>
  <div class="response-panel">
    <Tabs>
      <Tab name="Response">
        <pre><code class="language-json">{{ formattedResponse }}</code></pre>
      </Tab>
      <Tab name="Headers">
        <KeyValueTable :data="response.headers" />
      </Tab>
      <Tab name="Timing">
        <div>Duration: {{ response.duration }}ms</div>
        <div>Status: {{ response.statusCode }}</div>
      </Tab>
    </Tabs>
  </div>
</template>
```

---

### 7. Error Injection

**Component: `ErrorInjector.vue`**

**Modal UI for each step:**
- [ ] Inject network timeout (delay: ___ ms)
- [ ] Force specific status code: [400 ▼]
- [ ] Modify response body
- [ ] Drop authentication header

**Implementation:**
```javascript
function injectError(stepId, errorType, config) {
  journeyStore.addErrorInjection(stepId, {
    type: errorType, // 'timeout' | 'status' | 'body' | 'auth'
    config
  });
}
```

Backend receives error injection config and simulates it during execution.

---

### 8. Additional Features

**Environment Management:**
- Component: `EnvironmentSelector.vue`
- Dropdown to switch between:
  - Development (https://dev-api.example.com)
  - Staging (https://staging-api.example.com)
  - Production (https://api.example.com)

**Journey Sharing:**
- Export button → generates shareable link
- `/shared/:journeyToken` page for view-only access

**History:**
- `/journey/:id/history` - List of past executions
- Compare runs side-by-side

---

## Folder Structure
```
src/
├── components/
│   ├── journey/
│   │   ├── JourneyFlow.vue
│   │   ├── JourneyRunner.vue
│   │   ├── EndpointNode.vue (custom Vue Flow node)
│   │   └── ResponsePanel.vue
│   ├── spec/
│   │   ├── SpecUploader.vue
│   │   ├── SpecValidator.vue
│   │   └── EndpointList.vue
│   ├── shared/
│   │   ├── MockDataEditor.vue
│   │   ├── ErrorInjector.vue
│   │   └── EnvironmentSelector.vue
├── stores/
│   ├── auth.js
│   ├── spec.js
│   ├── journey.js
│   └── execution.js
├── views/
│   ├── Login.vue
│   ├── Dashboard.vue
│   ├── SpecDetail.vue
│   └── JourneyView.vue
├── utils/
│   ├── specParser.js
│   ├── mockGenerator.js
│   └── graphUtils.js (topological sort, etc.)
└── api/
    └── client.js (axios instance with interceptors)
```

---

## API Integration (calls to FastAPI backend)
```javascript
// POST /api/auth/login
{ email, password } → { token, user }

// POST /api/specs
{ name, content } → { id, validated, endpoints }

// GET /api/specs/:id/journeys
→ [ { id, name, nodes, edges } ]

// POST /api/journeys/:id/generate
{ strategy: 'ai' | 'manual' } → { journey }

// POST /api/journeys/:id/execute
{ steps, sessionData, errorInjections } → WebSocket stream of results

// POST /api/execute-step
{ journeyId, stepId, sessionData } → { statusCode, body, headers, duration }
```

---

## State Management Flow
```
User uploads spec
  ↓
SpecStore.addSpec() → POST /api/specs
  ↓
Backend validates & extracts endpoints
  ↓
SpecStore updates → triggers AI journey generation
  ↓
JourneyStore.setJourneys(aiGenerated)
  ↓
User edits journey in VueFlow
  ↓
JourneyStore.updateJourney() → debounced POST /api/journeys/:id
  ↓
User clicks "Run Journey"
  ↓
ExecutionStore.execute() → WebSocket /journey/:id/execute
  ↓
Results stream in → ExecutionStore.updateStepResult()
  ↓
VueFlow nodes update in real-time
```

