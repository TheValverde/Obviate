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
6. ✅ **Set up async SQLAlchemy with asyncpg** - **COMPLETED** (infrastructure ready)
7. ✅ **Set up Alembic for migrations** - **COMPLETED** (configuration ready)
8. **Create SQLAlchemy models** - Implement all core entities
9. **Create initial migration** - Generate and test database schema
10. **Set up repository pattern** - Create base repository and CRUD operations

### 📋 **Current Implementation Status**
- **FastAPI App**: ✅ Basic app with health checks, CORS, logging middleware
- **Configuration**: ✅ Pydantic settings with environment validation
- **Database Setup**: ✅ Async SQLAlchemy engine and session factory
- **Docker**: ✅ Multi-service setup with PostgreSQL, Redis, and FastAPI app
- **Migrations**: ✅ **COMPLETED** - Initial schema migration applied
- **Models**: ✅ **COMPLETED** - SQLAlchemy models created and database schema deployed
- **Repository Pattern**: ✅ **COMPLETED** - Data access layer with tenant isolation and optimistic concurrency
- **API Endpoints**: ❌ Only placeholder endpoints exist
- **Authentication**: ❌ Not implemented yet

### 📋 **Current Sprint Focus**
**Week 1: Foundation & Core Models** - ✅ **COMPLETED** 
**Week 2: Repository Pattern & Data Access** - ✅ **COMPLETED**
**Week 3: REST API Implementation** - 🔄 **NEXT SPRINT**

---

## Overall Timeline: **2-3 weeks**

### Week 1: Foundation & Core Models ✅ **COMPLETED**
### Week 2: Repository Pattern & Data Access ✅ **COMPLETED**  
### Week 3: REST API Implementation 🔄 **IN PROGRESS**
### Week 4: API Surface & Business Logic
### Week 5: Polish & Agent Features

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
- [x] Configure async SQLAlchemy with asyncpg ✅ **COMPLETED**
- [x] Set up Alembic for migrations ✅ **COMPLETED**
- [x] Set up PostgreSQL database with Docker ✅ **COMPLETED**

### 🗄️ **COMPLETED BRANCH: `feat/core-models` - Database Schema Implementation** ✅ **MERGED**
- [x] **Create base model** with common fields (id, tenant_id, version, timestamps, soft delete) ✅ **COMPLETED**
- [x] **Create SQLAlchemy models** for all core entities: ✅ **COMPLETED**
  - [x] `workspaces` (optional for MVP)
  - [x] `boards` (with template JSONB, metadata JSONB)
  - [x] `columns` (with position INT, wip_limit, metadata JSONB)
  - [x] `cards` (with agent_context JSONB, workflow_state JSONB, fields JSONB, links JSONB)
  - [x] `comments` (with metadata JSONB)
  - [x] `attachments` (metadata only, no blob storage)
  - [x] `audit_events` (with agent_context JSONB, payload JSONB)
  - [x] `service_tokens` (for API/MCP auth)
- [x] **Update alembic/env.py** to import models and set target_metadata ✅ **COMPLETED**
- [x] **Create initial migration** with all tables and required indexes: ✅ **COMPLETED**
  - [x] `(tenant_id, id)` on every table
  - [x] `cards(board_id, column_id, position)` for column paging
  - [x] `audit_events(entity_type, entity_id, created_at desc)`
- [x] **Implement ULID/UUIDv7 ID generation** for lexicographic ordering ✅ **COMPLETED**
- [x] **Add optimistic concurrency** with `version` BIGINT field ✅ **COMPLETED**
- [x] **Set up soft delete** via `deleted_at` timestamp ✅ **COMPLETED**
- [ ] **Create base repository** with common CRUD operations
- [ ] **Add tenant isolation** to all queries (mandatory tenant_id filtering)
- [x] **Test migration flow** and database connectivity ✅ **COMPLETED**
- [ ] **Create development seed data** (workspace, board, columns, sample cards)

### 🗄️ **COMPLETED BRANCH: `feat/repository-pattern` - Data Access Layer Implementation** ✅ **READY FOR PR**
- [x] **Create base repository** (`app/repositories/base.py`) with common CRUD operations ✅ **COMPLETED**
- [x] **Implement tenant isolation** - Mandatory tenant_id filtering on all queries ✅ **COMPLETED**
- [x] **Add optimistic concurrency** - Version field handling with If-Match validation ✅ **COMPLETED**
- [x] **Set up soft delete functionality** - Automatic filtering of deleted records ✅ **COMPLETED**
- [x] **Create entity repositories** for all models: ✅ **COMPLETED**
  - [x] `app/repositories/workspace.py`
  - [x] `app/repositories/board.py`
  - [x] `app/repositories/column.py`
  - [x] `app/repositories/card.py`
  - [x] `app/repositories/comment.py`
  - [x] `app/repositories/attachment.py`
  - [x] `app/repositories/audit_event.py`
  - [x] `app/repositories/service_token.py`
- [x] **Add repository exports** (`app/repositories/__init__.py`) ✅ **COMPLETED**
- [x] **Create development seed data** - Workspace, board, columns, sample cards ✅ **COMPLETED**
- [x] **Test repository operations** - CRUD, tenant isolation, optimistic concurrency ✅ **COMPLETED**
- [x] **Add repository dependency injection** - FastAPI dependency for database sessions ✅ **COMPLETED**

### 🗄️ **NEXT BRANCH: `feat/api-endpoints` - REST API Implementation**
- [ ] **Create Pydantic schemas** for request/response models
- [ ] **Implement workspace endpoints** - CRUD operations with tenant isolation
- [ ] **Implement board endpoints** - CRUD operations with workspace relationships
- [ ] **Implement column endpoints** - CRUD operations with position management
- [ ] **Implement card endpoints** - CRUD operations with complex filtering and search
- [ ] **Implement comment endpoints** - CRUD operations with card relationships
- [ ] **Implement attachment endpoints** - Metadata operations (no blob storage)
- [ ] **Add API error handling** - Consistent error responses and validation
- [ ] **Add API documentation** - OpenAPI/Swagger documentation
- [ ] **Test API endpoints** - Integration tests for all operations

### 🗄️ Database Schema
- [x] **Infrastructure setup** ✅ **COMPLETED** (async SQLAlchemy, Alembic config)
- [x] **Models implementation** ✅ **COMPLETED** (feat/core-models branch)
- [x] **Migration creation** ✅ **COMPLETED** (initial schema migration created and applied)
- [ ] **Index optimization** (after migration complete)
- [ ] **Seed data creation** (after migration complete)

### 🔐 Authentication & Authorization
- [ ] Implement bearer token authentication middleware
- [ ] Create service token model and validation (argon2id hash at rest)
- [ ] Add tenant isolation (single tenant for MVP, fixed tenant_id="default")
- [ ] Set up scope checking (read/write/admin, write implies read)
- [ ] Create token generation/validation utilities
- [ ] Add rate limiting headers (X-RateLimit-* stubs for MVP)

### 📊 Core Models & Repositories
- [x] **Base model creation** ✅ **COMPLETED** (feat/core-models branch)
- [x] **Entity models implementation** ✅ **COMPLETED** (workspaces, boards, columns, cards, comments, attachments, audit_events, service_tokens)
- [x] **Repository pattern setup** ✅ **COMPLETED** (base repository with common CRUD operations)
- [x] **Optimistic concurrency** ✅ **COMPLETED** (version field with If-Match header validation)
- [x] **Soft delete functionality** ✅ **COMPLETED** (via deleted_at timestamp)
- [x] **Tenant isolation** ✅ **COMPLETED** (mandatory tenant_id filtering on all queries)
- [x] **ULID/UUIDv7 ID generation** ✅ **COMPLETED** (lexicographic ordering)

### 🧪 Basic Testing Setup
- [ ] Set up pytest with async support
- [ ] Create test database configuration with Docker
- [ ] Add basic fixtures for test data
- [ ] Write smoke tests for database connectivity
- [ ] Set up test Docker Compose configuration

---

## 🎯 **DETAILED IMPLEMENTATION PLAN: `feat/repository-pattern` Branch**

### **Phase 1: Base Repository Infrastructure (Day 1)**
1. **Create base repository** (`app/repositories/base.py`)
   - Generic CRUD operations (create, read, update, delete)
   - Tenant isolation enforcement (mandatory tenant_id filtering)
   - Optimistic concurrency handling (version field management)
   - Soft delete support (automatic deleted_at filtering)
   - Pagination support with cursor-based pagination
   - Error handling and validation

2. **Set up repository structure**
   - Create `app/repositories/` directory
   - Add `app/repositories/__init__.py` with exports
   - Set up dependency injection for database sessions

### **Phase 2: Entity Repositories (Day 1-2)**
3. **Create entity-specific repositories**
   - `app/repositories/workspace.py` - Workspace CRUD operations
   - `app/repositories/board.py` - Board operations with workspace relationships
   - `app/repositories/column.py` - Column operations with board relationships
   - `app/repositories/card.py` - Card operations with complex filtering
   - `app/repositories/comment.py` - Comment operations with card relationships
   - `app/repositories/attachment.py` - Attachment metadata operations
   - `app/repositories/audit_event.py` - Audit event logging operations
   - `app/repositories/service_token.py` - Token validation operations

### **Phase 3: Seed Data & Testing (Day 2)**
4. **Create development seed data**
   - Default workspace: "default"
   - Sample board: "Agent Backlog"
   - Standard columns: "Todo", "Doing", "Done"
   - Sample cards with agent context examples

5. **Test repository operations**
   - CRUD operations for all entities
   - Tenant isolation verification
   - Optimistic concurrency testing
   - Soft delete functionality testing

### **Key Technical Decisions:**
- **Repository Pattern**: Clean separation between data access and business logic
- **Tenant Isolation**: Every query must include tenant_id filter
- **Optimistic Concurrency**: Version field with If-Match header validation
- **Soft Delete**: Automatic filtering of deleted records in queries
- **Dependency Injection**: FastAPI dependency for database sessions

### **Files to Create:**
```
app/repositories/
├── __init__.py (exports)
├── base.py (base repository)
├── workspace.py
├── board.py
├── column.py
├── card.py
├── comment.py
├── attachment.py
├── audit_event.py
└── service_token.py

app/core/
└── dependencies.py (database session dependency)
```

### **Success Criteria:**
- ✅ Base repository with all CRUD operations
- ✅ Tenant isolation enforced on all queries
- ✅ Optimistic concurrency working with version fields
- ✅ Soft delete functionality implemented
- ✅ All entity repositories created and tested
- ✅ Seed data loads correctly
- ✅ Ready for API endpoint implementation

---

## 🎯 **COMPLETED: `feat/core-models` Branch** ✅ **MERGED**

### **Phase 1: Base Infrastructure (Day 1)**
1. **Create base model** (`app/models/base.py`)
   - Common fields: `id`, `tenant_id`, `version`, `created_at`, `updated_at`, `deleted_at`
   - ULID/UUIDv7 ID generation utility
   - Soft delete mixin
   - Optimistic concurrency mixin

2. **Update alembic configuration** (`alembic/env.py`)
   - Import all models
   - Set `target_metadata = Base.metadata`
   - Configure async migration support

### **Phase 2: Core Models (Day 1-2)**
3. **Create entity models** (following README.md schema):
   - `app/models/workspace.py` - Workspace model (optional for MVP)
   - `app/models/board.py` - Board model with template/metadata JSONB
   - `app/models/column.py` - Column model with position/wip_limit
   - `app/models/card.py` - Card model with agent_context/workflow_state JSONB
   - `app/models/comment.py` - Comment model with metadata JSONB
   - `app/models/attachment.py` - Attachment model (metadata only)
   - `app/models/audit_event.py` - Audit event model with agent_context JSONB
   - `app/models/service_token.py` - Service token model for auth

4. **Create model exports** (`app/models/__init__.py`)
   - Export all models for Alembic discovery
   - Create model registry

### **Phase 3: Migration & Testing (Day 2)**
5. **Generate initial migration**
   - Run `alembic revision --autogenerate -m "Initial schema"`
   - Review and adjust migration file
   - Add required indexes manually if needed

6. **Test migration flow**
   - Run `alembic upgrade head`
   - Verify all tables created correctly
   - Test database connectivity

### **Phase 4: Repository Pattern (Day 2-3)**
7. **Create base repository** (`app/repositories/base.py`)
   - Common CRUD operations
   - Tenant isolation enforcement
   - Optimistic concurrency handling
   - Soft delete support

8. **Create entity repositories**
   - `app/repositories/workspace.py`
   - `app/repositories/board.py`
   - `app/repositories/column.py`
   - `app/repositories/card.py`
   - `app/repositories/comment.py`
   - `app/repositories/attachment.py`
   - `app/repositories/audit_event.py`
   - `app/repositories/service_token.py`

### **Phase 5: Seed Data & Validation (Day 3)**
9. **Create development seed data**
   - Workspace: "default"
   - Board: "Agent Backlog"
   - Columns: "Todo", "Doing", "Done"
   - Sample cards with agent context

10. **Test complete flow**
    - Database connectivity
    - Model operations
    - Repository operations
    - Migration rollback/upgrade

### **Key Technical Decisions:**
- **ID Generation**: ULID/UUIDv7 for lexicographic ordering
- **JSONB Fields**: For extensibility (agent_context, workflow_state, etc.)
- **Tenant Isolation**: Mandatory `tenant_id` filtering on all queries
- **Optimistic Concurrency**: `version` field with If-Match validation
- **Soft Delete**: `deleted_at` timestamp instead of hard deletes
- **Indexes**: `(tenant_id, id)` on every table + specific performance indexes

### **Files to Create/Modify:**
```
app/models/
├── __init__.py (exports)
├── base.py (base model)
├── workspace.py
├── board.py
├── column.py
├── card.py
├── comment.py
├── attachment.py
├── audit_event.py
└── service_token.py

app/repositories/
├── __init__.py
├── base.py (base repository)
├── workspace.py
├── board.py
├── column.py
├── card.py
├── comment.py
├── attachment.py
├── audit_event.py
└── service_token.py

alembic/
├── env.py (update imports)
└── versions/001_initial.py (generated)

alembic/versions/
└── 001_initial.py (initial migration)
```

### **Success Criteria:**
- ✅ All models created with proper SQLAlchemy relationships
- ✅ Initial migration generates and applies successfully
- ✅ All required indexes created
- ✅ Repository pattern implemented with tenant isolation
- ✅ Seed data loads correctly
- ✅ Database connectivity tested and working
- ✅ Ready for API endpoint implementation in next branch

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
