# Kanban For Agents - MVP Development Timeline

## 🎯 **CURRENT STATUS & NEXT STEPS**

### ✅ **Completed**
- Development startup script (`start_dev.py`) - Ready to use
- Git configuration (`.gitignore` with `.cursor/` exclusion)
- Project planning and timeline documentation

### 📁 **Current Project Structure**
```
KanbanForAgents/
├── app/
│   ├── __init__.py
│   ├── main.py (FastAPI app with health checks)
│   ├── api/v1/
│   │   ├── __init__.py
│   │   └── api.py (main router)
│   └── core/
│       ├── __init__.py
│       ├── config.py (Pydantic settings)
│       └── database.py (SQLAlchemy async setup)
├── alembic/
│   ├── env.py (async migration config)
│   └── script.py.mako (migration template)
├── tests/ (empty, ready for setup)
├── pyproject.toml (dependencies: FastAPI, SQLAlchemy, asyncpg, etc.)
├── docker-compose.yml (PostgreSQL + Redis + FastAPI app)
├── Dockerfile (multi-stage: dev/prod)
├── alembic.ini (migration config)
├── .env.example (environment template)
└── start_dev.py (development startup script)
```

### 🔧 **Technical Decisions Made**
- **Dependency Management**: Using `pyproject.toml` with uv for fast installs
- **Database**: PostgreSQL 15 with asyncpg driver
- **ORM**: SQLAlchemy 2.0+ with async support
- **API Framework**: FastAPI with Pydantic v2
- **Containerization**: Multi-stage Dockerfile with development/production targets
- **Migrations**: Alembic with async support
- **Logging**: Structured logging with structlog
- **Health Checks**: `/healthz` and `/readyz` endpoints implemented

### 🚀 **Immediate Next Steps**
1. ✅ **Create feature branch**: `feat/foundation-setup` - **COMPLETED**
2. ✅ **Initialize FastAPI project structure** (app/, alembic/, etc.) - **COMPLETED**
3. ✅ **Set up dependency management** (pyproject.toml with Poetry/uv) - **COMPLETED**
4. ✅ **Create environment configuration** (.env.example) - **COMPLETED**
5. ✅ **Set up Docker Compose** for PostgreSQL development database - **COMPLETED**
6. **Set up async SQLAlchemy with asyncpg** - Configure database models
7. **Set up Alembic for migrations** - Create initial migration

### 📋 **Current Implementation Status**
- **FastAPI App**: ✅ Basic app with health checks, CORS, logging middleware
- **Configuration**: ✅ Pydantic settings with environment validation
- **Database Setup**: ✅ Async SQLAlchemy engine and session factory
- **Docker**: ✅ Multi-service setup with PostgreSQL, Redis, and FastAPI app
- **Migrations**: ✅ Alembic configured but no models yet
- **Models**: ❌ **NEXT PRIORITY** - Need to create SQLAlchemy models
- **API Endpoints**: ❌ Only placeholder endpoints exist
- **Authentication**: ❌ Not implemented yet

### 📋 **Current Sprint Focus**
**Week 1: Foundation & Core Models** - Infrastructure Setup Phase

---

## Overall Timeline: **2-3 weeks**

### Week 1: Foundation & Core Models
### Week 2: API Surface & Business Logic  
### Week 3: Polish & Agent Features

---

## Week 1: Foundation & Core Models

### 🏗️ Infrastructure Setup
- [x] Create development startup script (start_dev.py) ✅ **COMPLETED**
- [x] Add .cursor folder to .gitignore ✅ **COMPLETED**
- [x] Create feat/foundation-setup branch ✅ **COMPLETED**
- [x] Initialize FastAPI project structure ✅ **COMPLETED**
- [x] Set up Poetry/uv dependency management ✅ **COMPLETED**
- [x] Create basic environment configuration (.env.example) ✅ **COMPLETED**
- [x] Create Docker Compose setup for development ✅ **COMPLETED**
- [x] Create Dockerfile for the FastAPI application ✅ **COMPLETED**
- [x] Set up Docker networking between app and database ✅ **COMPLETED**
- [ ] **NEXT: Configure async SQLAlchemy with asyncpg**
- [ ] Set up Alembic for migrations
- [ ] Set up PostgreSQL database with Docker

### 🗄️ Database Schema
- [ ] Create initial migration with core tables:
  - [ ] workspaces (optional for MVP)
  - [ ] boards (with template JSONB, metadata JSONB)
  - [ ] columns (with position INT, wip_limit, metadata JSONB)
  - [ ] cards (with agent_context JSONB, workflow_state JSONB, fields JSONB, links JSONB)
  - [ ] comments (with metadata JSONB)
  - [ ] attachments (metadata only, no blob storage)
  - [ ] audit_events (with agent_context JSONB, payload JSONB)
  - [ ] service_tokens (for API/MCP auth)
- [ ] Add required indexes:
  - [ ] `(tenant_id, id)` on every table
  - [ ] `cards(board_id, column_id, position)` for column paging
  - [ ] `audit_events(entity_type, entity_id, created_at desc)`
- [ ] Implement ULIDs/UUIDv7-ish IDs for lexicographic ordering
- [ ] Add optimistic concurrency with `version` BIGINT field
- [ ] Set up soft delete via `deleted_at` timestamp
- [ ] Create seed data for development (workspace, board, columns, sample cards)

### 🔐 Authentication & Authorization
- [ ] Implement bearer token authentication middleware
- [ ] Create service token model and validation (argon2id hash at rest)
- [ ] Add tenant isolation (single tenant for MVP, fixed tenant_id="default")
- [ ] Set up scope checking (read/write/admin, write implies read)
- [ ] Create token generation/validation utilities
- [ ] Add rate limiting headers (X-RateLimit-* stubs for MVP)

### 📊 Core Models & Repositories
- [ ] Implement SQLAlchemy models for all entities with proper JSONB fields
- [ ] Create async repository pattern for data access
- [ ] Add optimistic concurrency with version field (If-Match header validation)
- [ ] Implement soft delete functionality via deleted_at
- [ ] Create base repository with common CRUD operations
- [ ] Add tenant isolation to all queries (mandatory tenant_id filtering)
- [ ] Implement ULID/UUIDv7 ID generation for lexicographic ordering

### 🧪 Basic Testing Setup
- [ ] Set up pytest with async support
- [ ] Create test database configuration with Docker
- [ ] Add basic fixtures for test data
- [ ] Write smoke tests for database connectivity
- [ ] Set up test Docker Compose configuration

---

## Week 2: API Surface & Business Logic

### 🚀 REST API Endpoints
- [ ] **Boards API**
  - [ ] POST /v1/boards (create)
  - [ ] GET /v1/boards?workspace_id=&limit=&cursor= (list with pagination)
  - [ ] GET /v1/boards/{board_id} (get single)
  - [ ] PATCH /v1/boards/{board_id} (name, description, archive toggle)
  - [ ] DELETE /v1/boards/{board_id} (soft delete)

- [ ] **Columns API**
  - [ ] POST /v1/boards/{board_id}/columns (create)
  - [ ] GET /v1/boards/{board_id}/columns (list)
  - [ ] PATCH /v1/columns/{column_id} (name, wip_limit, position)
  - [ ] POST /v1/columns/{column_id}/reorder (accepts {after_id|before_id|position})
  - [ ] DELETE /v1/columns/{column_id} (delete)

- [ ] **Cards API**
  - [ ] POST /v1/columns/{column_id}/cards (create)
  - [ ] GET /v1/boards/{board_id}/cards?column_id=&label=&assignee=&priority=&limit=&cursor= (list with filters)
  - [ ] GET /v1/cards/{card_id} (get single)
  - [ ] PATCH /v1/cards/{card_id} (title, description, labels, assignees, priority, due_at, fields, links, agent_context, workflow_state)
  - [ ] POST /v1/cards/{card_id}/move (target column_id, optional position)
  - [ ] POST /v1/cards/{card_id}/reorder (same contract as columns)
  - [ ] DELETE /v1/cards/{card_id} (soft delete)

- [ ] **Agent-Specific Endpoints**
  - [ ] GET /v1/agents/{agent_id}/next_tasks?board_id=&limit=&cursor= (prioritized tasks)
  - [ ] GET /v1/agents/{agent_id}/blockers?board_id=&limit=&cursor= (blocking issues)
  - [ ] GET /v1/agents/{agent_id}/summary?board_id=&timeframe= (performance summary)

- [ ] **Metrics Endpoints**
  - [ ] GET /v1/boards/{board_id}/metrics (board performance metrics)

### 🔍 Search & Filtering
- [ ] Implement basic text search on cards (title/description)
- [ ] Add filtering by labels, assignees, priority, status
- [ ] Create cursor-based pagination system
- [ ] Add sorting options (position, created_at, updated_at)

### 💬 Comments System
- [ ] POST /v1/cards/{card_id}/comments (create)
- [ ] GET /v1/cards/{card_id}/comments (list)
- [ ] DELETE /v1/comments/{comment_id} (delete)
- [ ] Add comment metadata support

### 📎 Attachments (Metadata Only)
- [ ] POST /v1/cards/{card_id}/attachments (create metadata)
- [ ] GET /v1/cards/{card_id}/attachments (list)
- [ ] DELETE /v1/attachments/{attachment_id} (delete)
- [ ] Validate attachment metadata (size, content_type, url)

### 🔄 Bulk Operations
- [ ] POST /v1/boards/{board_id}/cards/bulk (bulk card operations)
- [ ] Support move, update, and add_labels operations
- [ ] Implement transaction safety for bulk operations

### 📝 Audit System
- [ ] Create audit event model and repository
- [ ] Implement audit event emission on all mutations
- [ ] GET /v1/audit (list audit events with filtering)
- [ ] Add agent context to audit events

### 🛡️ Middleware & Validation
- [ ] Implement If-Match header validation (optimistic concurrency)
- [ ] Add idempotency key support (hash method+path+body → Redis/DB)
- [ ] Create request/response validation with Pydantic
- [ ] Add rate limiting headers (X-RateLimit-* stubs)
- [ ] Implement proper error handling and responses
- [ ] Add text field truncation (title≤256, description≤16KB, comment.body≤8KB)
- [ ] Add JSONB size limits (fields≤16KB, reject oversize)

---

## Week 3: Polish & Agent Features

### 🤖 MCP Tool Surface
- [ ] Create MCP tool wrapper functions:
  - [ ] kanban.list_boards()
  - [ ] kanban.get_board(board_id)
  - [ ] kanban.create_card()
  - [ ] kanban.move_card()
  - [ ] kanban.update_card()
  - [ ] kanban.add_comment()
  - [ ] kanban.find_cards()
- [ ] Add agent safety checks (If-Match enforcement)
- [ ] Implement destructive operation guards
- [ ] Create MCP tool documentation

### 🎯 Agent-Specific Endpoints
- [ ] GET /v1/agents/{agent_id}/next_tasks (prioritized tasks)
- [ ] GET /v1/agents/{agent_id}/blockers (blocking issues)
- [ ] GET /v1/agents/{agent_id}/summary (performance summary)
- [ ] Implement task prioritization logic
- [ ] Add dependency tracking for blockers

### 📊 Metrics & Analytics
- [ ] GET /v1/boards/{board_id}/metrics (board performance)
- [ ] Calculate cycle time averages
- [ ] Track throughput metrics
- [ ] Identify bottlenecks
- [ ] Add workflow efficiency metrics
- [ ] Implement background metric calculation

### 🧪 Comprehensive Testing
- [ ] Unit tests for all models and repositories
- [ ] Integration tests for API endpoints
- [ ] Test optimistic concurrency scenarios
- [ ] Test idempotency with replay scenarios
- [ ] Test tenant isolation (no cross-tenant access)
- [ ] Performance tests for pagination and search

### 📚 Documentation & Examples
- [ ] Complete API documentation with OpenAPI/Swagger
- [ ] Create usage examples for common workflows
- [ ] Document MCP tool usage
- [ ] Add deployment and setup instructions
- [ ] Create agent integration examples
- [ ] Document Docker setup and usage
- [ ] Create Docker development workflow guide

### 🔧 Production Readiness
- [ ] Add health check endpoints (/healthz, /readyz)
- [ ] Implement proper logging
- [ ] Add configuration validation
- [ ] Create deployment scripts
- [ ] Add monitoring and observability hooks
- [ ] Performance optimization and tuning
- [ ] Create production Docker Compose setup
- [ ] Add Docker health checks for database and app
- [ ] Create Docker volume persistence for PostgreSQL data
- [ ] Set up Docker secrets for production credentials
- [ ] Create production startup script (start_prod.py)

### 🚀 Final Polish
- [ ] Code review and cleanup
- [ ] Security audit of authentication and authorization
- [ ] Performance testing and optimization
- [ ] Create demo data and examples
- [ ] Final documentation review
- [ ] Prepare for initial release

---

## Post-MVP Features (Future)

### 🔗 Webhooks & Integrations
- [ ] Webhook system for event fan-out
- [ ] Third-party integrations
- [ ] Notification delivery system

### 👥 Multi-tenancy
- [ ] True multi-tenant support
- [ ] Row-level security in PostgreSQL
- [ ] Tenant management UI

### 🔍 Advanced Search
- [ ] Full-text search with PostgreSQL trigram
- [ ] Semantic search with embeddings
- [ ] Saved queries and filters

### 📈 Advanced Analytics
- [ ] Real-time metrics
- [ ] Custom dashboards
- [ ] Advanced reporting

### 🎨 Human UI
- [ ] Web-based Kanban interface
- [ ] Real-time collaboration
- [ ] Drag-and-drop functionality
