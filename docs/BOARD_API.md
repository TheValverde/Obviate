# Board API Documentation

## Overview

The Board API provides CRUD operations for managing boards in the Kanban For Agents system. All endpoints support tenant isolation and optimistic concurrency control.

**Base URL**: `http://localhost:8000/v1/boards`

**Authentication**: Currently uses default tenant (`tenant_id: "default"`)

---

## Endpoints

### 1. Create Board

**POST** `/v1/boards/`

Creates a new board in the specified workspace.

#### Request

```http
POST /v1/boards/
Content-Type: application/json

{
  "name": "My Project Board",
  "description": "A board for tracking project tasks",
  "workspace_id": "AGMNJ7P3MA5QBA2XG3GRBPRKB4",
  "template": {
    "columns": ["To Do", "In Progress", "Done"]
  },
  "meta_data": {
    "project_id": "proj-123",
    "owner": "john.doe@example.com"
  }
}
```

#### Request Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `name` | string | ✅ | Board name (1-255 characters) |
| `description` | string | ❌ | Board description (max 1000 characters) |
| `workspace_id` | string | ✅ | ID of the workspace this board belongs to |
| `template` | object | ❌ | Board template configuration |
| `meta_data` | object | ❌ | Additional metadata |

#### Response

**Status**: `201 Created`

```json
{
  "success": true,
  "message": "Board created successfully",
  "data": {
    "id": "AGMNKFUYWE2LKTT5DGINE5NLXD",
    "name": "My Project Board",
    "description": "A board for tracking project tasks",
    "workspace_id": "AGMNJ7P3MA5QBA2XG3GRBPRKB4",
    "tenant_id": "default",
    "version": 1,
    "template": {
      "columns": ["To Do", "In Progress", "Done"]
    },
    "meta_data": {
      "project_id": "proj-123",
      "owner": "john.doe@example.com"
    },
    "created_at": "2025-08-23T04:01:24.123456+00:00",
    "updated_at": "2025-08-23T04:01:24.123456+00:00",
    "deleted_at": null
  }
}
```

#### Example Usage

```bash
curl -X POST "http://localhost:8000/v1/boards/" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Sprint Board",
    "description": "Current sprint tasks",
    "workspace_id": "AGMNJ7P3MA5QBA2XG3GRBPRKB4"
  }'
```

```powershell
$body = @{
    name = "Sprint Board"
    description = "Current sprint tasks"
    workspace_id = "AGMNJ7P3MA5QBA2XG3GRBPRKB4"
} | ConvertTo-Json

Invoke-WebRequest -Uri "http://localhost:8000/v1/boards/" -Method POST -Body $body -ContentType "application/json"
```

---

### 2. Get Board

**GET** `/v1/boards/{board_id}`

Retrieves a specific board by ID.

#### Request

```http
GET /v1/boards/AGMNKFUYWE2LKTT5DGINE5NLXD
```

#### Path Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `board_id` | string | The unique identifier of the board |

#### Response

**Status**: `200 OK`

```json
{
  "success": true,
  "data": {
    "id": "AGMNKFUYWE2LKTT5DGINE5NLXD",
    "name": "My Project Board",
    "description": "A board for tracking project tasks",
    "workspace_id": "AGMNJ7P3MA5QBA2XG3GRBPRKB4",
    "tenant_id": "default",
    "version": 1,
    "template": {
      "columns": ["To Do", "In Progress", "Done"]
    },
    "meta_data": {
      "project_id": "proj-123",
      "owner": "john.doe@example.com"
    },
    "created_at": "2025-08-23T04:01:24.123456+00:00",
    "updated_at": "2025-08-23T04:01:24.123456+00:00",
    "deleted_at": null
  }
}
```

#### Error Responses

**Status**: `404 Not Found`

```json
{
  "success": false,
  "error": {
    "code": "BOARD_NOT_FOUND",
    "message": "Board with ID 'AGMNKFUYWE2LKTT5DGINE5NLXD' not found",
    "details": null
  }
}
```

#### Example Usage

```bash
curl -X GET "http://localhost:8000/v1/boards/AGMNKFUYWE2LKTT5DGINE5NLXD"
```

```powershell
Invoke-WebRequest -Uri "http://localhost:8000/v1/boards/AGMNKFUYWE2LKTT5DGINE5NLXD" -Method GET
```

---

### 3. List Boards

**GET** `/v1/boards/`

Retrieves a paginated list of boards with optional filtering.

#### Request

```http
GET /v1/boards/?offset=0&limit=10&workspace_id=AGMNJ7P3MA5QBA2XG3GRBPRKB4&archived=false
```

#### Query Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `offset` | integer | 0 | Number of records to skip |
| `limit` | integer | 100 | Number of records to return (max 1000) |
| `workspace_id` | string | null | Filter by workspace ID |
| `archived` | boolean | null | Filter by archived status |
| `include_deleted` | boolean | false | Include soft-deleted boards |
| `order_by` | string | "created_at" | Field to order by |
| `order_direction` | string | "desc" | Order direction ("asc" or "desc") |

#### Response

**Status**: `200 OK`

```json
{
  "success": true,
  "data": [
    {
      "id": "AGMNKFUYWE2LKTT5DGINE5NLXD",
      "name": "My Project Board",
      "description": "A board for tracking project tasks",
      "workspace_id": "AGMNJ7P3MA5QBA2XG3GRBPRKB4",
      "tenant_id": "default",
      "version": 1,
      "template": {
        "columns": ["To Do", "In Progress", "Done"]
      },
      "meta_data": {
        "project_id": "proj-123",
        "owner": "john.doe@example.com"
      },
      "created_at": "2025-08-23T04:01:24.123456+00:00",
      "updated_at": "2025-08-23T04:01:24.123456+00:00"
    }
  ],
  "pagination": {
    "page": 1,
    "limit": 10,
    "total": 1,
    "pages": 1,
    "has_next": false,
    "has_prev": false
  }
}
```

#### Example Usage

```bash
# Get all boards
curl -X GET "http://localhost:8000/v1/boards/"

# Get boards with pagination
curl -X GET "http://localhost:8000/v1/boards/?offset=0&limit=5"

# Get boards for specific workspace
curl -X GET "http://localhost:8000/v1/boards/?workspace_id=AGMNJ7P3MA5QBA2XG3GRBPRKB4"

# Get archived boards
curl -X GET "http://localhost:8000/v1/boards/?archived=true"
```

```powershell
# Get all boards
Invoke-WebRequest -Uri "http://localhost:8000/v1/boards/" -Method GET

# Get boards with pagination
Invoke-WebRequest -Uri "http://localhost:8000/v1/boards/?offset=0&limit=5" -Method GET

# Get boards for specific workspace
Invoke-WebRequest -Uri "http://localhost:8000/v1/boards/?workspace_id=AGMNJ7P3MA5QBA2XG3GRBPRKB4" -Method GET
```

---

### 4. Update Board

**PUT** `/v1/boards/{board_id}`

Updates an existing board. Supports optimistic concurrency control via `If-Match` header.

#### Request

```http
PUT /v1/boards/AGMNKFUYWE2LKTT5DGINE5NLXD
Content-Type: application/json
If-Match: "1"

{
  "name": "Updated Project Board",
  "description": "Updated description",
  "meta_data": {
    "project_id": "proj-123",
    "owner": "john.doe@example.com",
    "last_updated_by": "jane.smith@example.com"
  }
}
```

#### Path Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `board_id` | string | The unique identifier of the board |

#### Headers

| Header | Type | Required | Description |
|--------|------|----------|-------------|
| `If-Match` | string | ❌ | ETag for optimistic concurrency control |

#### Request Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `name` | string | ❌ | Board name (1-255 characters) |
| `description` | string | ❌ | Board description (max 1000 characters) |
| `template` | object | ❌ | Board template configuration |
| `meta_data` | object | ❌ | Additional metadata |

**Note**: Only include fields you want to update. Omitted fields will remain unchanged.

#### Response

**Status**: `200 OK`

```json
{
  "success": true,
  "message": "Board updated successfully",
  "data": {
    "id": "AGMNKFUYWE2LKTT5DGINE5NLXD",
    "name": "Updated Project Board",
    "description": "Updated description",
    "workspace_id": "AGMNJ7P3MA5QBA2XG3GRBPRKB4",
    "tenant_id": "default",
    "version": 2,
    "template": {
      "columns": ["To Do", "In Progress", "Done"]
    },
    "meta_data": {
      "project_id": "proj-123",
      "owner": "john.doe@example.com",
      "last_updated_by": "jane.smith@example.com"
    },
    "created_at": "2025-08-23T04:01:24.123456+00:00",
    "updated_at": "2025-08-23T04:05:30.654321+00:00",
    "deleted_at": null
  }
}
```

#### Error Responses

**Status**: `404 Not Found`

```json
{
  "success": false,
  "error": {
    "code": "BOARD_NOT_FOUND",
    "message": "Board with ID 'AGMNKFUYWE2LKTT5DGINE5NLXD' not found",
    "details": null
  }
}
```

**Status**: `409 Conflict` (Optimistic Concurrency)

```json
{
  "success": false,
  "error": {
    "code": "OPTIMISTIC_CONCURRENCY_EXCEPTION",
    "message": "Board has been modified by another request",
    "details": null
  }
}
```

#### Example Usage

```bash
# Update board name only
curl -X PUT "http://localhost:8000/v1/boards/AGMNKFUYWE2LKTT5DGINE5NLXD" \
  -H "Content-Type: application/json" \
  -d '{"name": "New Board Name"}'

# Update with optimistic concurrency
curl -X PUT "http://localhost:8000/v1/boards/AGMNKFUYWE2LKTT5DGINE5NLXD" \
  -H "Content-Type: application/json" \
  -H "If-Match: \"1\"" \
  -d '{"description": "Updated description"}'
```

```powershell
# Update board name only
$body = @{name = "New Board Name"} | ConvertTo-Json
Invoke-WebRequest -Uri "http://localhost:8000/v1/boards/AGMNKFUYWE2LKTT5DGINE5NLXD" -Method PUT -Body $body -ContentType "application/json"

# Update with optimistic concurrency
$headers = @{"If-Match" = '"1"'}
$body = @{description = "Updated description"} | ConvertTo-Json
Invoke-WebRequest -Uri "http://localhost:8000/v1/boards/AGMNKFUYWE2LKTT5DGINE5NLXD" -Method PUT -Body $body -ContentType "application/json" -Headers $headers
```

---

### 5. Delete Board

**DELETE** `/v1/boards/{board_id}`

Soft deletes a board (marks as deleted but doesn't remove from database).

#### Request

```http
DELETE /v1/boards/AGMNKFUYWE2LKTT5DGINE5NLXD
If-Match: "2"
```

#### Path Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `board_id` | string | The unique identifier of the board |

#### Headers

| Header | Type | Required | Description |
|--------|------|----------|-------------|
| `If-Match` | string | ❌ | ETag for optimistic concurrency control |

#### Response

**Status**: `200 OK`

```json
{
  "success": true,
  "message": "Board deleted successfully",
  "data": {
    "deleted": true
  }
}
```

#### Error Responses

**Status**: `404 Not Found`

```json
{
  "success": false,
  "error": {
    "code": "BOARD_NOT_FOUND",
    "message": "Board with ID 'AGMNKFUYWE2LKTT5DGINE5NLXD' not found",
    "details": null
  }
}
```

#### Example Usage

```bash
# Delete board
curl -X DELETE "http://localhost:8000/v1/boards/AGMNKFUYWE2LKTT5DGINE5NLXD"

# Delete with optimistic concurrency
curl -X DELETE "http://localhost:8000/v1/boards/AGMNKFUYWE2LKTT5DGINE5NLXD" \
  -H "If-Match: \"2\""
```

```powershell
# Delete board
Invoke-WebRequest -Uri "http://localhost:8000/v1/boards/AGMNKFUYWE2LKTT5DGINE5NLXD" -Method DELETE

# Delete with optimistic concurrency
$headers = @{"If-Match" = '"2"'}
Invoke-WebRequest -Uri "http://localhost:8000/v1/boards/AGMNKFUYWE2LKTT5DGINE5NLXD" -Method DELETE -Headers $headers
```

---

### 6. Archive/Unarchive Board

**POST** `/v1/boards/{board_id}/archive`

Archives or unarchives a board.

#### Request

```http
POST /v1/boards/AGMNKFUYWE2LKTT5DGINE5NLXD/archive
Content-Type: application/json
If-Match: "2"

{
  "archived": true
}
```

#### Path Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `board_id` | string | The unique identifier of the board |

#### Headers

| Header | Type | Required | Description |
|--------|------|----------|-------------|
| `If-Match` | string | ❌ | ETag for optimistic concurrency control |

#### Request Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `archived` | boolean | ✅ | `true` to archive, `false` to unarchive |

#### Response

**Status**: `200 OK`

```json
{
  "success": true,
  "message": "Board archived successfully",
  "data": {
    "id": "AGMNKFUYWE2LKTT5DGINE5NLXD",
    "name": "My Project Board",
    "description": "A board for tracking project tasks",
    "workspace_id": "AGMNJ7P3MA5QBA2XG3GRBPRKB4",
    "tenant_id": "default",
    "version": 3,
    "template": {
      "columns": ["To Do", "In Progress", "Done"]
    },
    "meta_data": {
      "project_id": "proj-123",
      "owner": "john.doe@example.com"
    },
    "created_at": "2025-08-23T04:01:24.123456+00:00",
    "updated_at": "2025-08-23T04:10:15.987654+00:00",
    "deleted_at": null
  }
}
```

#### Example Usage

```bash
# Archive board
curl -X POST "http://localhost:8000/v1/boards/AGMNKFUYWE2LKTT5DGINE5NLXD/archive" \
  -H "Content-Type: application/json" \
  -d '{"archived": true}'

# Unarchive board
curl -X POST "http://localhost:8000/v1/boards/AGMNKFUYWE2LKTT5DGINE5NLXD/archive" \
  -H "Content-Type: application/json" \
  -d '{"archived": false}'
```

```powershell
# Archive board
$body = @{archived = $true} | ConvertTo-Json
Invoke-WebRequest -Uri "http://localhost:8000/v1/boards/AGMNKFUYWE2LKTT5DGINE5NLXD/archive" -Method POST -Body $body -ContentType "application/json"

# Unarchive board
$body = @{archived = $false} | ConvertTo-Json
Invoke-WebRequest -Uri "http://localhost:8000/v1/boards/AGMNKFUYWE2LKTT5DGINE5NLXD/archive" -Method POST -Body $body -ContentType "application/json"
```

---

## Data Models

### Board Object

```json
{
  "id": "string (26 chars, ULID format)",
  "name": "string (1-255 chars)",
  "description": "string (max 1000 chars) | null",
  "workspace_id": "string (26 chars, ULID format)",
  "tenant_id": "string (50 chars)",
  "version": "integer (optimistic concurrency)",
  "template": "object | null",
  "meta_data": "object | null",
  "created_at": "datetime (ISO 8601 with timezone)",
  "updated_at": "datetime (ISO 8601 with timezone) | null",
  "deleted_at": "datetime (ISO 8601 with timezone) | null"
}
```

### Pagination Object

```json
{
  "page": "integer (current page number)",
  "limit": "integer (records per page)",
  "total": "integer (total records)",
  "pages": "integer (total pages)",
  "has_next": "boolean (has next page)",
  "has_prev": "boolean (has previous page)"
}
```

---

## Error Handling

All endpoints return consistent error responses:

```json
{
  "success": false,
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable error message",
    "details": "Additional error details or null"
  }
}
```

### Common Error Codes

| Code | HTTP Status | Description |
|------|-------------|-------------|
| `BOARD_NOT_FOUND` | 404 | Board with specified ID not found |
| `OPTIMISTIC_CONCURRENCY_EXCEPTION` | 409 | Version conflict during update |
| `BAD_REQUEST` | 400 | Invalid request data |
| `VALIDATION_ERROR` | 422 | Request validation failed |

---

## Optimistic Concurrency Control

The API supports optimistic concurrency control using the `If-Match` header:

1. **Get the current version**: When retrieving a board, note the `version` field
2. **Include version in updates**: Send the version in the `If-Match` header
3. **Handle conflicts**: If the version has changed, the API returns a 409 Conflict

**Example Workflow**:

```bash
# 1. Get board
GET /v1/boards/AGMNKFUYWE2LKTT5DGINE5NLXD
# Response: {"version": 1, ...}

# 2. Update with version
PUT /v1/boards/AGMNKFUYWE2LKTT5DGINE5NLXD
If-Match: "1"
# Success: {"version": 2, ...}

# 3. Another client updates the same board
# Version becomes 3

# 4. Try to update with old version
PUT /v1/boards/AGMNKFUYWE2LKTT5DGINE5NLXD
If-Match: "1"
# Error: 409 Conflict
```

---

## Best Practices

1. **Always handle errors**: Check the `success` field and handle error responses
2. **Use pagination**: For list endpoints, use `offset` and `limit` parameters
3. **Implement optimistic concurrency**: Use `If-Match` headers for updates
4. **Validate responses**: Check that required fields are present
5. **Handle timeouts**: Implement retry logic for network issues
6. **Cache wisely**: Cache board data but respect the `version` field for updates

---

## Rate Limiting

Currently, no rate limiting is implemented. In production, consider implementing appropriate rate limiting based on your requirements.

---

## Authentication & Authorization

Currently uses a default tenant (`tenant_id: "default"`). In production, implement proper authentication and tenant resolution based on your security requirements.
