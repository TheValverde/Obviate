# Obviate - Kanban For Agents

A headless, API-first Kanban store designed for LLM/agent workflows. Think “Trello, but built for tools.” The service exposes a clean HTTP API (FastAPI) and an MCP tool surface so agents can create/update/query boards as part of larger automated workflows. No human UI in this repo.

* **MVP scope:** single-tenant (but schema and code paths are multi-tenant-ready).
* **Persistence:** PostgreSQL (async via SQLAlchemy), with JSONB for extensibility and strict indexes to keep storage tight.
* **No blobs in DB:** attachments are externalized (URLs + metadata only).

## Non-Goals (for this repo)

* Human UI.
* Notification delivery, OAuth brokering, or webhooks to third parties (events are emitted internally for now).
* Full-blown RBAC UI. We expose service tokens; a minimal ACL exists for multi-tenant prep.

---

## Why Postgres (and not SQLite/Mongo/etc.)

* **Storage efficiency:** normalized tables + JSONB extensions; tight indexes; no blob storage.
* **Scalability:** straightforward path to row-level tenancy (`tenant_id`) and partitioning if needed.
* **Transactions & concurrency:** optimistic versioning for safe agent updates.


---

## High-Level Architecture

```mermaid
graph TD
    A[Agent / IDE / Service] -->|HTTP FastAPI| B[Kanban API Service]
    B -->|async SQLAlchemy| C[PostgreSQL]
    
    B1[REST JSON] --> B
    B2[MCP Tool endpoints] --> B
    B3[Domain logic] --> B
    B4[Event bus in-proc] --> B
    
    C1[normalized schema + JSONB] --> C
    C2[no blob storage] --> C
    
    style B fill:#1CA6E6FF
    style C fill:#BE16D8FF
```

---

## Data Model

All principal entities use ULIDs/UUIDv7-ish ids (`id` TEXT) for lexicographic time ordering. Soft deletes via `deleted_at`. Optimistic concurrency via `version` (BIGINT, increment on write). Timestamps are UTC.

### Tenancy

* `tenant_id` TEXT on every row. **MVP:** use a single fixed tenant id (`"default"`) issued via config. Later, enable per-token tenancy.

### Entities

**workspaces** (optional grouping; MVP can use one)

* `id`, `name`, `created_at`, `updated_at`, `deleted_at`, `tenant_id`, `version`

**boards**

* `id`, `workspace_id`, `name`, `description`, `is_archived` (bool)
* `created_at`, `updated_at`, `deleted_at`, `tenant_id`, `version`
* `metadata` JSONB (for custom fields like WIP limits at board level)
* `template` JSONB (board template: `default_columns`, `default_labels`, `default_priorities`)

**columns** (ordered lanes within a board)

* `id`, `board_id`, `name`
* `position` (INT; gaps ok, we rebalance on large diffs)
* `wip_limit` (INT NULL)
* `created_at`, `updated_at`, `deleted_at`, `tenant_id`, `version`
* `metadata` JSONB

**cards**

* `id`, `board_id`, `column_id`, `title`, `description`
* `assignees` TEXT\[] (agent/human identifiers) — optional
* `labels` TEXT\[]  (lightweight tags)
* `priority` SMALLINT (0=none,1=low,2=med,3=high,4=urgent)
* `status` TEXT (e.g., `"todo"|"doing"|"done"|"blocked"`; not enforced, column is the source of truth; status is a hint)
* `position` INT (order within column)
* `due_at` TIMESTAMP NULL
* `created_at`, `updated_at`, `deleted_at`, `tenant_id`, `version`
* `fields` JSONB (structured, agent-defined per-card fields)
* `links` JSONB (array of `{type, url, title}` pointing to PRs, docs, etc.)
* `agent_context` JSONB (agent reasoning and context: `reasoning`, `next_steps`, `dependencies`, `estimated_complexity`, `agent_notes`)
* `workflow_state` JSONB (workflow tracking: `phase`, `blockers`, `progress_percentage`, `time_spent_minutes`, `estimated_remaining_minutes`)

**comments**

* `id`, `card_id`, `author` TEXT (agent/service/user id), `body` TEXT
* `created_at`, `updated_at`, `deleted_at`, `tenant_id`, `version`
* `metadata` JSONB

**attachments** (metadata only)

* `id`, `card_id`, `name`, `content_type`, `size_bytes` BIGINT, `url` TEXT
* `created_at`, `deleted_at`, `tenant_id`, `version`
* (No `updated_at`: treat as immutable; replace to update.)

**audit\_events**

* `id`, `entity_type` TEXT (`board|column|card|comment|attachment`)
* `entity_id` TEXT, `action` TEXT (`create|update|delete|move|reorder|archive|restore`)
* `actor` TEXT (service/agent id), `payload` JSONB (diff or snapshot)
* `created_at`, `tenant_id`
* `agent_context` JSONB (agent reasoning: `reasoning`, `confidence`, `alternative_actions`, `user_approval_required`)
* Indexed for reverse-chron and entity lookups.

**service\_tokens** (for API/MCP auth)

* `id`, `name`, `token_hash`, `scopes` TEXT\[] (`read`, `write`, `admin`)
* `tenant_id`, `created_at`, `revoked_at`
* (You will only ever store a hash; present tokens once on creation.)

### Minimal ER Diagram

```mermaid
erDiagram
    WORKSPACE ||--o{ BOARD : contains
    BOARD ||--o{ COLUMN : contains
    COLUMN ||--o{ CARD : contains
    CARD ||--o{ COMMENT : has
    CARD ||--o{ ATTACHMENT : has
    CARD ||--o{ AUDIT_EVENT : "audited by entity_id"
```

### Indexing

* `(tenant_id, id)` on every table.
* `cards(board_id, column_id, position)` for column paging.
* `audit_events(entity_type, entity_id, created_at desc)`.

---

## API (FastAPI)

### Auth

* Bearer token (`Authorization: Bearer <token>`).
* Each token binds to a single `tenant_id` + scopes.
* Rate limit headers reserved: `X-RateLimit-*` (stub in MVP).

### Conventions

* `If-Match: <version>` required on mutating endpoints (optimistic concurrency). Server returns `409` if versions mismatch.
* `Idempotency-Key` header supported for POST/PUT/PATCH (dedupe window configurable).
* Pagination: `limit` (1–200, default 50), `cursor` opaque.
* Filtering uses explicit query params; no ad-hoc search in MVP.

#### Boards

* `POST /v1/boards` → create
* `GET /v1/boards?workspace_id=&limit=&cursor=` → list
* `GET /v1/boards/{board_id}`
* `PATCH /v1/boards/{board_id}` (name, description, archive toggle)
* `DELETE /v1/boards/{board_id}` → soft delete

#### Columns

* `POST /v1/boards/{board_id}/columns`
* `GET /v1/boards/{board_id}/columns`
* `PATCH /v1/columns/{column_id}` (name, wip\_limit, position)
* `POST /v1/columns/{column_id}/reorder` (accepts `{ after_id | before_id | position }`)
* `DELETE /v1/columns/{column_id}`

#### Cards

* `POST /v1/columns/{column_id}/cards`
* `GET /v1/boards/{board_id}/cards?column_id=&label=&assignee=&priority=&limit=&cursor=` → list
* `GET /v1/cards/{card_id}`
* `PATCH /v1/cards/{card_id}` (title, description, labels, assignees, priority, due\_at, fields, links, agent_context, workflow_state)
* `POST /v1/cards/{card_id}/move` (target `column_id`, optional `position`)
* `POST /v1/cards/{card_id}/reorder` (same contract as columns)
* `DELETE /v1/cards/{card_id}`

#### Search

* `GET /v1/search/cards?board_id=&q="natural language query"&limit=&cursor=` → semantic search

#### Bulk Operations

* `POST /v1/boards/{board_id}/cards/bulk` (multiple card operations in single transaction)

#### Comments

* `POST /v1/cards/{card_id}/comments`
* `GET /v1/cards/{card_id}/comments?limit=&cursor=`
* `DELETE /v1/comments/{comment_id}`

#### Attachments (metadata)

* `POST /v1/cards/{card_id}/attachments` (body: `name, content_type, size_bytes, url`)
* `GET /v1/cards/{card_id}/attachments`
* `DELETE /v1/attachments/{attachment_id}`

#### Audit

* `GET /v1/audit?entity_type=&entity_id=&limit=&cursor=`

#### Agent-Specific Endpoints

* `GET /v1/agents/{agent_id}/next_tasks?board_id=&limit=&cursor=` → prioritized tasks for agent
* `GET /v1/agents/{agent_id}/blockers?board_id=&limit=&cursor=` → what's blocking this agent
* `GET /v1/agents/{agent_id}/summary?board_id=&timeframe=` → agent performance summary

*Note: These are experimental derived queries. Consider implementing as database views for better performance. Board_id is optional - omitting it returns data across all boards.*

#### Metrics

* `GET /v1/boards/{board_id}/metrics` → board performance metrics (cycle time, throughput, bottlenecks)

*Note: Metrics are computed asynchronously in the background, not in real-time with each request.*

#### Health

* `GET /healthz` (db ping + migration status)
* `GET /readyz`

### Error Model

```json
{
  "error": {
    "code": "conflict_version",
    "message": "If-Match failed: expected 12, got 9",
    "details": {}
  }
}
```

Common codes: `invalid_input`, `not_found`, `conflict_version`, `forbidden`, `rate_limited`, `idempotency_replay`.

---

## MCP Tool Surface (for Agents)

Expose a minimal, safe subset aligned with agent actions. Tools are thin wrappers over the REST API with stricter schemas and guardrails.

**Tools (names suggestive; adjust to your MCP framework):**

* `kanban.list_boards() -> [BoardSummary]`
* `kanban.get_board(board_id) -> Board`
* `kanban.create_card(board_id, column_id, title, description?, labels?, assignees?, priority?, due_at?, fields?, links?) -> Card`
* `kanban.move_card(card_id, column_id, position?) -> Card`
* `kanban.update_card(card_id, patch: CardPatch, if_match_version) -> Card`
* `kanban.add_comment(card_id, body) -> Comment`
* `kanban.find_cards(board_id, query: FindQuery) -> [Card]`
  MVP `FindQuery`: `labels?, assignee?, priority?, status?`

**Agent Safety:**

* Enforce `If-Match` inside tool calls; require the agent to read → mutate with returned `version`.
* Deny destructive ops by default unless token has `write` and `allow_delete=true`.

---

## Events (Internal)

On every mutating operation, emit an in-process event (later can be swapped to a broker):

```
type Event = {
  id, tenant_id, occurred_at, actor,
  kind: "board.created" | "column.moved" | "card.updated" | ...,
  entity: { type, id },
  payload: { before?, after? }  // sized to keep <8KB
}
```

Store only in `audit_events` (DB). Webhooks can be added later.

---

## Concurrency & Ordering

* **Optimistic locking** via `version`. Clients must pass `If-Match`.
* **Positions:** use integers with gaps (e.g., step=1024). Rebalance when `max_gap < threshold`.
* **Moves** are transactional: change `column_id` + `position` atomically; write an audit event showing both.

---

## Storage Hygiene

* No file data in DB. `attachments.url` must be pre-signed or stable URLs to your own blob store.
* Truncate long text fields server-side with configured max lengths:

  * `title <= 256`, `description <= 16KB`, `comment.body <= 8KB`.
* `fields` JSONB is capped (e.g., 16KB). Reject oversize.

---

## Pagination & Cursors

Opaque base64 cursor of `{ last_id, last_position }` within the current sort order. Every list endpoint supports `limit`/`cursor`. Stable sort:

* Cards: `(column_id, position, id)`
* Comments: `(created_at desc, id desc)`

---

## Security

* **Service tokens:** argon2id hash at rest; rotate via admin script.
* **Scopes:** `read`, `write`, `admin`. Write implies read.
* **Tenant isolation:** mandatory `tenant_id` condition on every query path; verify in tests.

---

## Local Development

### Prereqs

* Python 3.11+
* Postgres 14+
* Poetry or uv (recommended)

### Quickstart

```bash
cp .env.example .env
# set DATABASE_DSN=postgresql+asyncpg://user:pass@localhost:5432/kanban
# set SERVICE_TOKENS_SEED="dev:devtoken123|read,write"

# install
uv pip install -r requirements.txt  # or: poetry install

# run migrations
alembic upgrade head

# start
uvicorn app.main:app --reload --port 8080
```

### Smoke

```bash
curl -H "Authorization: Bearer devtoken123" http://localhost:8080/healthz
```

---

## Migrations

* Alembic, stamped in `alembic/versions/`.
* Never destructive in-place; use additive changes + backfills; soft-delete instead of drops.

---

## Testing

* Pytest with an ephemeral test DB.
* Fixtures for seed data (one workspace, one board with 3 columns).
* Contract tests for:

  * optimistic concurrency (`409` on stale `If-Match`)
  * idempotency (replay-safe within the dedupe window)
  * tenant fencing (no cross-tenant reads)

---

## Example Seed (useful for agent demos)

* Workspace: `default`
* Board: `“Agent Backlog”`
* Columns: `Todo (pos=1024)`, `Doing (2048)`, `Done (3072)`
* Cards:

  * `"Bootstrap service"` in `Todo`, labels: `["infra"]`
  * `"Define MCP tools"` in `Doing`, labels: `["mcp","api"]`
  * `"Write README"` in `Done`, labels: `["docs"]`

* Cards with agent context:

  * `"Bootstrap service"` in `Todo`, labels: `["infra"]`, agent_context: `{"reasoning": "Foundation for all other services", "estimated_complexity": "high"}`
  * `"Define MCP tools"` in `Doing`, labels: `["mcp","api"]`, workflow_state: `{"phase": "execution", "progress_percentage": 60}`
  * `"Write README"` in `Done`, labels: `["docs"]`, workflow_state: `{"phase": "complete", "time_spent_minutes": 45}`

---

## Minimal JSON Schemas (wire format)

**Card (read):**

```json
{
  "id": "01J...ULID",
  "board_id": "01J...",
  "column_id": "01J...",
  "title": "string",
  "description": "string",
  "assignees": ["agent://build-bot"],
  "labels": ["infra","mcp"],
  "priority": 2,
  "status": "doing",
  "position": 2048,
  "due_at": "2025-08-29T12:00:00Z",
  "fields": {"story_points": 3},
  "links": [{"type":"pr","url":"https://...","title":"PR #12"}],
  "agent_context": {
    "reasoning": "This task is critical for the build pipeline",
    "next_steps": ["review code", "run tests"],
    "dependencies": ["01J...card_id"],
    "estimated_complexity": "medium",
    "agent_notes": "Waiting for dependency completion"
  },
  "workflow_state": {
    "phase": "execution",
    "blockers": ["waiting_for_review"],
    "progress_percentage": 75,
    "time_spent_minutes": 120,
    "estimated_remaining_minutes": 30
  },
  "version": 7,
  "created_at": "2025-08-22T16:40:00Z",
  "updated_at": "2025-08-22T17:02:00Z"
}
```

**CardPatch (write):**

```json
{
  "title": "string?",
  "description": "string?",
  "assignees": ["string"]?,
  "labels": ["string"]?,
  "priority": 0,
  "status": "todo|doing|done|blocked"?,
  "due_at": "RFC3339 or null",
  "fields": {"any":"json"}?,
  "links": [{"type":"string","url":"string","title":"string"}]?,
  "agent_context": {
    "reasoning": "string?",
    "next_steps": ["string"]?,
    "dependencies": ["string"]?,
    "estimated_complexity": "low|medium|high"?,
    "agent_notes": "string?"
  }?,
  "workflow_state": {
    "phase": "planning|execution|review|complete"?,
    "blockers": ["string"]?,
    "progress_percentage": 0-100?,
    "time_spent_minutes": 0?,
    "estimated_remaining_minutes": 0?
  }?
}
```

**BulkOperations (write):**

```json
{
  "operations": [
    {
      "action": "move",
      "card_ids": ["id1", "id2"],
      "column_id": "target_column_id",
      "position": 1024?
    },
    {
      "action": "update",
      "card_ids": ["id3"],
      "patch": {
        "priority": 3,
        "labels": ["urgent"]
      }
    },
    {
      "action": "add_labels",
      "card_ids": ["id1", "id4"],
      "labels": ["bug", "critical"]
    }
  ]
}
```

**BoardTemplate (read/write):**

```json
{
  "default_columns": [
    {"name": "Backlog", "position": 1024},
    {"name": "In Progress", "position": 2048},
    {"name": "Review", "position": 3072},
    {"name": "Done", "position": 4096}
  ],
  "default_labels": ["bug", "feature", "documentation", "urgent"],
  "default_priorities": {
    "urgent": 4,
    "high": 3,
    "medium": 2,
    "low": 1
  }
}
```

**BoardMetrics (read):**

```json
{
  "cycle_time_avg_hours": 24.5,
  "throughput_per_day": 8.2,
  "cards_by_agent": {
    "agent://build-bot": 15,
    "agent://test-runner": 12,
    "agent://deploy-bot": 8
  },
  "bottlenecks": [
    {
      "column_id": "01J...review_column",
      "avg_wait_time_hours": 48.0,
      "card_count": 25
    }
  ],
  "workflow_efficiency": {
    "planning_phase_avg_hours": 4.2,
    "execution_phase_avg_hours": 18.7,
    "review_phase_avg_hours": 6.1
  }
}
```

---

## Versioning & Compatibility

* API is versioned under `/v1`.
* Backward-compatible changes only within `v1` (fields additive). Breaking changes → `/v2`.

---

## Roadmap (kept short, only what's necessary)

* Webhooks for event fan-out.
* Saved queries (server-side filters).
* Row-level security in Postgres when moving to true multi-tenant with shared DB.
* Optional full-text index on `title/description/comments` (PG trigram/TS).
* **Agent Enhancements:**
  * Hybrid search implementation (pgvector embeddings + PostgreSQL trigram similarity)
  * Nested querying for efficient agent data fetching (`?include=columns.cards.comments`)
  * Template management endpoints (`/v1/templates`) for board templates
  * Trigger system for automated agent notifications (future)

---

## License

**Service Code (this repo):** Business Source License (BUSL) - restricts commercial hosting by others while allowing open source use.

**MCP Tools (separate repo):** MIT/Apache-2.0 - maximize adoption of agent tooling.

*Note: This protects the core service while encouraging widespread adoption of the agent interface.*

---

## Notes for Implementation

* Use FastAPI + Pydantic v2 + async SQLAlchemy + asyncpg.
* **Alembic migrations must run before service start** - this prevents common deployment issues.
* Middleware:

  * auth (bearer → token lookup),
  * idempotency (hash `method+path+body` → Redis/DB table),
  * concurrency (enforce `If-Match`).
* Keep handler functions thin; push business rules to services; DB in repositories. This lets you add background brokers or sharded tenancy without touching HTTP layer.
