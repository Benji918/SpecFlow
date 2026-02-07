# Implementation Plan: SpecFlow Application

This document outlines the step-by-step implementation plan for building SpecFlow, a modern web application for generating and executing API journey tests. This plan integrates specific branding guidelines and leverages the Vue Flow library for visualization.

## Phase 1: Project Initialization & Configuration

### 1.1. Repository & Monorepo Setup
- [ ] Initialize a git repository.
- [ ] Create a `backend` directory (Python/FastAPI).
- [ ] Create a `frontend` directory (Vue 3/Vite).


### 1.2. Backend Foundation (FastAPI)
- [ ] Initialize FastAPI project with `uv` or `poetry`.
- [ ] Install dependencies: `fastapi`, `uvicorn`, `sqlalchemy`, `alembic`, `pydantic-settings`, `asyncpg`, `python-jose`, `passlib`.
- [ ] Configure Environment Variables (`.env`).
- [ ] Set up Database connection (`app/database.py`) using `SQLAlchemy` (Async).
- [ ] Initialize Alembic for migrations.

### 1.3. Frontend Foundation (Vue 3 + Tailwind)
- [ ] Initialize Vue 3 project: `npm create vite@latest frontend -- --template vue`
- [ ] Install Core Dependencies: `vue-router`, `pinia`, `axios`, `@vueuse/core`.
- [ ] Install UI/Styling: `tailwindcss`, `postcss`, `autoprefixer`, `shadcn-vue` (or equivalent accessible components), `lucide-vue-next`.
- [ ] Configure `vite.config.js` with alias `@` pointing to `src`.

---

## Phase 2: Design System & Branding Implementation (CRITICAL)

**Reference Materials:** `branding.json`, `www.glaido.com...json`
**Theme:** Dark Mode, Premium, Modern.

### 2.1. Tailwind Configuration
- [ ] Update `tailwind.config.js` to match the **Glaido** brand palette:
    - **Primary:** `#BFF549` (Vibrant Lime/Green)
    - **Background:** `#000000` (Pure Black)
    - **Surface/Card:** `#121212` (Dark Grey for contrast)
    - **Text Primary:** `#000000` (on primary buttons) / `#FFFFFF` (on dark backgrounds)
    - **Font Family:** `Inter`, sans-serif.
- [ ] Configure `border-radius` to match brand (e.g., highly rounded buttons `9999px` or `33554400px` as seen in json).

### 2.2. Global Styles & Typography
- [ ] Create `src/assets/main.css`.
- [ ] Set body background to `#000000` and text to `#FFFFFF`.
- [ ] Import `Inter` font from Google Fonts.
- [ ] Define global reset and base styles.

### 2.3. Core UI Components
- [ ] **Button Component**:
    - **Primary**: Background `#BFF549`, Text `#000000`, Rounded Full, Shadow `rgba(191, 245, 73, 0.6) 0px 0px 60px -15px` (Glow effect).
    - **Secondary**: Background `#282828`, Text `#FFFFFF`, Rounded Full.
- [ ] **Input/Form Fields**: Dark background (`#1A1A1A`), light border (`#333`), focus ring color `#BFF549`.
- [ ] **Card Component**: Glassmorphism or solid dark grey `#121212` with subtle borders.

---

## Phase 3: Authentication Module

### 3.1. Backend Auth
- [ ] Create `User` model (`app/models/user.py`) with `id`, `email`, `password_hash`.
- [ ] Implement `AuthService`: Password hashing (`bcrypt`), JWT token generation (`create_access_token`).
- [ ] Create Endpoints (`app/api/auth.py`):
    - `POST /register`
    - `POST /login` (Returns JWT)
    - `GET /me` (Protected)

### 3.2. Frontend Auth Pages
- [ ] Set up `AuthStore` (Pinia) to handle token storage and user state.
- [ ] Build **Login Page**:
    - Centered card layout.
    - Use branded input fields and Primary Glow Button.
    - Title: "Welcome back" (Inter font).
- [ ] Build **Signup Page**: Similar layout, requesting Name, Email, Password.
- [ ] Implement Axios Interceptor to inject `Authorization: Bearer <token>` on all requests.

---

## Phase 4: Spec Management (OpenAPI Parsing)

### 4.1. Backend Spec Parsing
- [ ] Install `prance` and `openapi-spec-validator`.
- [ ] Create `Spec` model (`app/models/spec.py`).
- [ ] Implement `SpecParserService`:
    - Validate uploaded JSON/YAML.
    - Parse standard OpenAPI structure.
    - Extract paths/endpoints into a simplified internal format.
- [ ] Endpoints:
    - `POST /specs` (Upload)
    - `GET /specs` (List)
    - `GET /specs/{id}` (Detail)

### 4.2. Frontend Dashboard & Upload
- [ ] Build **Dashboard Page**:
    - Grid layout of uploaded specs.
    - "New Project" button (Primary Brand Color).
- [ ] Build **Spec Uploader**:
    - Drag & drop zone.
    - Validation feedback.
    - Progress bar (color `#BFF549`).

---

## Phase 5: Journey Generation (AI Integration)

### 5.1. Backend AI Service
- [ ] Integrate Anthropic SDK (`claude-3-5-sonnet` or similar).
- [ ] Create `JourneyGenerator` service.
- [ ] **Prompt Engineering**:
    - Input: Parsed API Endpoints.
    - Output: JSON array of "Steps" representing a user journey.
    - *Constraint*: Output must be structured for easy conversion to VueFlow nodes.
- [ ] Endpoint: `POST /specs/{id}/generate` -> Returns generated journey graph.

### 5.2. Journey Data Model
- [ ] Create `Journey` and `JourneyStep` models in DB.
- [ ] Store the graph layout (Nodes/Edges) as JSONB.

---

## Phase 6: Journey Visualization (Vue Flow Implementation)

**Reference Material:** `vueflow_documentation_reference.json`

### 6.1. Vue Flow Installation & Setup
- [ ] Install `@vue-flow/core` and `@vue-flow/background`.
- [ ] Import default styles: `@import '@vue-flow/core/dist/style.css';`.
- [ ] Create `JourneyCanvas.vue` component.

### 6.2. Customizing Nodes & Edges
- [ ] **Custom Node (`EndpointNode.vue`)**:
    - Use `useNode` composable for data access.
    - Styling: Dark card, border left colored by method (GET=Blue, POST=Green, etc.).
    - Define `<Handle>` positions (Source/Target).
- [ ] **Custom Edge**:
    - Animated edges for active execution path.
    - Use `getBezierPath` utils.

### 6.3. Vue Flow Configuration
- [ ] Use `useVueFlow` to manage graph state.
- [ ] Configure `FitView` on load.
- [ ] Implement **MiniMap** and **Controls** (styled with dark theme).
- [ ] **Branding**: Set CSS variables for graph:
    - `--vf-node-bg`: `#121212`
    - `--vf-node-text`: `#FFFFFF`
    - `--vf-handle`: `#BFF549`
    - `--vf-connection-path`: `#BFF549`

### 6.4. Interaction & Editing
- [ ] Enable Drag & Drop.
- [ ] Implement "Connect" logic (connect step A to B).
- [ ] "Properties Panel": When a node is clicked, show details (Headers, Body) in a sidebar.

---

## Phase 7: Execution Engine & Real-time Feedback

### 7.1. Backend Execution Logic
- [ ] Create `JourneyExecutor` service.
- [ ] Method `execute_step(step_data, context)`:
    - Make real HTTP request using `httpx`.
    - capture Status, Response, Time.
- [ ] Implement **WebSocket** endpoint: `ws /journeys/{id}/run`.
    - Stream execution events: `step_start`, `step_success`, `step_failed`.

### 7.2. Frontend Execution Client
- [ ] Implement WebSocket connection in `JourneyView.vue`.
- [ ] **Visual Feedback**:
    - When `step_start` received: Animate node border (Pulse Green).
    - When `step_success` received: Show Green Checkmark.
    - When `step_failed` received: Show Red Border.
- [ ] Display real-time logs in a bottom panel (Terminal style).

---

## Phase 8: Polish & Optimization

### 8.1. UI Polish
- [ ] Add smooth transitions using Vue `Transition` or `Motion`.
- [ ] Ensure all hover states use the `accent` color `#BFF549`.
- [ ] Add Loading skeletons for data fetching.

### 8.2. SEO & Meta
- [ ] Update `index.html` title and meta tags.
- [ ] Ensure semantic HTML structure (`<main>`, `<nav>`, `<h1>`).


---

## Appendix: Technical Rules

1.  **Strict Branding**: Do not deviate from the `#BFF549` (Primary) and `#000000` (Background) scheme.
2.  **No Hallucinations**: Only use documented Vue Flow features (Handles, Nodes, Edges, Composables) as explicitly found in `vueflow_documentation_reference.json`.
3.  **Code Quality**: Type-safety where possible (Pydantic in Backend, Props validation in Frontend).
4. **Backend**: Always reference the `BE.md` file for backend implementation details.
5. **Frontend**: Always reference the `FE.md` file for frontend implementation details.
6. **Branding**: Always reference the `branding.json` file for branding implementation details.

