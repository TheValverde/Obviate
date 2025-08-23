# Column API Documentation

## Overview

The Column API provides CRUD operations for managing columns within Kanban boards. Columns represent the different stages or categories that cards can be moved between (e.g., "Todo", "In Progress", "Done").

## Base URL

All endpoints are prefixed with `/v1/columns`

## Authentication

Currently using a default tenant ID. In production, this will be resolved from authentication context.

## Endpoints

### 1. Create Column

**POST** `/v1/columns/`

Creates a new column within a board.

#### Request Body

```json
{
  "title": "In Progress",
  "description": "Tasks currently being worked on",
  "board_id": "01HXYZ1234567890ABCDEF",
  "position": 2,
  "color": "#3B82F6",
  "is_archived": false,
  "meta_data": {
    "wip_limit": 5,
    "auto_archive": true
  }
}
```

#### Response (201 Created)

```json
{
  "success": true,
  "data": {
    "id": "01HXYZ1234567890ABCDEF",
    "title": "In Progress",
    "description": "Tasks currently being worked on",
    "board_id": "01HXYZ1234567890ABCDEF",
    "position": 2,
    "color": "#3B82F6",
    "is_archived": false,
    "meta_data": {
      "wip_limit": 5,
      "auto_archive": true
    },
    "created_at": "2025-08-23T12:00:00Z",
    "updated_at": "2025-08-23T12:00:00Z",
    "version": 1
  }
}
```

#### cURL Example

```bash
curl -X POST "http://localhost:8000/v1/columns/" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "In Progress",
    "description": "Tasks currently being worked on",
    "board_id": "01HXYZ1234567890ABCDEF",
    "position": 2,
    "color": "#3B82F6"
  }'
```

#### PowerShell Example

```powershell
Invoke-RestMethod -Uri "http://localhost:8000/v1/columns/" -Method POST -ContentType "application/json" -Body '{
  "title": "In Progress",
  "description": "Tasks currently being worked on",
  "board_id": "01HXYZ1234567890ABCDEF",
  "position": 2,
  "color": "#3B82F6"
}'
```

### 2. Get Column

**GET** `/v1/columns/{column_id}`

Retrieves a specific column by ID.

#### Response (200 OK)

```json
{
  "success": true,
  "data": {
    "id": "01HXYZ1234567890ABCDEF",
    "title": "In Progress",
    "description": "Tasks currently being worked on",
    "board_id": "01HXYZ1234567890ABCDEF",
    "position": 2,
    "color": "#3B82F6",
    "is_archived": false,
    "meta_data": {
      "wip_limit": 5,
      "auto_archive": true
    },
    "created_at": "2025-08-23T12:00:00Z",
    "updated_at": "2025-08-23T12:00:00Z",
    "version": 1
  }
}
```

#### cURL Example

```bash
curl -X GET "http://localhost:8000/v1/columns/01HXYZ1234567890ABCDEF"
```

#### PowerShell Example

```powershell
Invoke-RestMethod -Uri "http://localhost:8000/v1/columns/01HXYZ1234567890ABCDEF" -Method GET
```

### 3. List Columns

**GET** `/v1/columns/`

Retrieves a paginated list of columns with optional filtering.

#### Query Parameters

- `board_id` (optional): Filter columns by board ID
- `limit` (optional, default: 100): Maximum number of columns to return (1-1000)
- `offset` (optional, default: 0): Number of columns to skip

#### Response (200 OK)

```json
{
  "success": true,
  "data": [
    {
      "id": "01HXYZ1234567890ABCDEF",
      "title": "Todo",
      "description": "Tasks to be done",
      "board_id": "01HXYZ1234567890ABCDEF",
      "position": 1,
      "color": "#6B7280",
      "is_archived": false,
      "created_at": "2025-08-23T12:00:00Z",
      "updated_at": "2025-08-23T12:00:00Z"
    },
    {
      "id": "01HXYZ1234567890ABCDEG",
      "title": "In Progress",
      "description": "Tasks currently being worked on",
      "board_id": "01HXYZ1234567890ABCDEF",
      "position": 2,
      "color": "#3B82F6",
      "is_archived": false,
      "created_at": "2025-08-23T12:00:00Z",
      "updated_at": "2025-08-23T12:00:00Z"
    }
  ],
  "pagination": {
    "page": 1,
    "limit": 100,
    "total": 2,
    "pages": 1,
    "has_next": false,
    "has_prev": false
  }
}
```

#### cURL Example

```bash
# Get all columns
curl -X GET "http://localhost:8000/v1/columns/"

# Get columns for a specific board
curl -X GET "http://localhost:8000/v1/columns/?board_id=01HXYZ1234567890ABCDEF"

# Get columns with pagination
curl -X GET "http://localhost:8000/v1/columns/?limit=10&offset=0"
```

#### PowerShell Example

```powershell
# Get all columns
Invoke-RestMethod -Uri "http://localhost:8000/v1/columns/" -Method GET

# Get columns for a specific board
Invoke-RestMethod -Uri "http://localhost:8000/v1/columns/?board_id=01HXYZ1234567890ABCDEF" -Method GET

# Get columns with pagination
Invoke-RestMethod -Uri "http://localhost:8000/v1/columns/?limit=10&offset=0" -Method GET
```

### 4. Update Column

**PUT** `/v1/columns/{column_id}`

Updates an existing column. Requires optimistic concurrency control via `If-Match` header.

#### Headers

- `If-Match` (optional): Current version of the column for optimistic concurrency control

#### Request Body

```json
{
  "title": "In Progress - Updated",
  "description": "Updated description",
  "color": "#10B981",
  "meta_data": {
    "wip_limit": 3,
    "auto_archive": false
  }
}
```

#### Response (200 OK)

```json
{
  "success": true,
  "data": {
    "id": "01HXYZ1234567890ABCDEF",
    "title": "In Progress - Updated",
    "description": "Updated description",
    "board_id": "01HXYZ1234567890ABCDEF",
    "position": 2,
    "color": "#10B981",
    "is_archived": false,
    "meta_data": {
      "wip_limit": 3,
      "auto_archive": false
    },
    "created_at": "2025-08-23T12:00:00Z",
    "updated_at": "2025-08-23T12:30:00Z",
    "version": 2
  }
}
```

#### cURL Example

```bash
curl -X PUT "http://localhost:8000/v1/columns/01HXYZ1234567890ABCDEF" \
  -H "Content-Type: application/json" \
  -H "If-Match: 1" \
  -d '{
    "title": "In Progress - Updated",
    "description": "Updated description",
    "color": "#10B981"
  }'
```

#### PowerShell Example

```powershell
$headers = @{
    "Content-Type" = "application/json"
    "If-Match" = "1"
}

Invoke-RestMethod -Uri "http://localhost:8000/v1/columns/01HXYZ1234567890ABCDEF" -Method PUT -Headers $headers -Body '{
  "title": "In Progress - Updated",
  "description": "Updated description",
  "color": "#10B981"
}'
```

### 5. Delete Column

**DELETE** `/v1/columns/{column_id}`

Soft deletes a column (marks as deleted but doesn't remove from database).

#### Response (200 OK)

```json
{
  "success": true,
  "message": "Column deleted successfully"
}
```

#### cURL Example

```bash
curl -X DELETE "http://localhost:8000/v1/columns/01HXYZ1234567890ABCDEF"
```

#### PowerShell Example

```powershell
Invoke-RestMethod -Uri "http://localhost:8000/v1/columns/01HXYZ1234567890ABCDEF" -Method DELETE
```

### 6. Reorder Column

**POST** `/v1/columns/{column_id}/reorder`

Moves a column to a new position within its board.

#### Request Body

```json
{
  "new_position": 3
}
```

#### Response (200 OK)

```json
{
  "success": true,
  "message": "Column reordered successfully"
}
```

#### cURL Example

```bash
curl -X POST "http://localhost:8000/v1/columns/01HXYZ1234567890ABCDEF/reorder" \
  -H "Content-Type: application/json" \
  -d '{
    "new_position": 3
  }'
```

#### PowerShell Example

```powershell
Invoke-RestMethod -Uri "http://localhost:8000/v1/columns/01HXYZ1234567890ABCDEF/reorder" -Method POST -ContentType "application/json" -Body '{
  "new_position": 3
}'
```

### 7. Get Board Columns

**GET** `/v1/columns/board/{board_id}`

Retrieves all columns for a specific board, ordered by position.

#### Response (200 OK)

```json
[
  {
    "id": "01HXYZ1234567890ABCDEF",
    "title": "Todo",
    "description": "Tasks to be done",
    "board_id": "01HXYZ1234567890ABCDEF",
    "position": 1,
    "color": "#6B7280",
    "is_archived": false,
    "created_at": "2025-08-23T12:00:00Z",
    "updated_at": "2025-08-23T12:00:00Z"
  },
  {
    "id": "01HXYZ1234567890ABCDEG",
    "title": "In Progress",
    "description": "Tasks currently being worked on",
    "board_id": "01HXYZ1234567890ABCDEF",
    "position": 2,
    "color": "#3B82F6",
    "is_archived": false,
    "created_at": "2025-08-23T12:00:00Z",
    "updated_at": "2025-08-23T12:00:00Z"
  },
  {
    "id": "01HXYZ1234567890ABCDEH",
    "title": "Done",
    "description": "Completed tasks",
    "board_id": "01HXYZ1234567890ABCDEF",
    "position": 3,
    "color": "#10B981",
    "is_archived": false,
    "created_at": "2025-08-23T12:00:00Z",
    "updated_at": "2025-08-23T12:00:00Z"
  }
]
```

#### cURL Example

```bash
curl -X GET "http://localhost:8000/v1/columns/board/01HXYZ1234567890ABCDEF"
```

#### PowerShell Example

```powershell
Invoke-RestMethod -Uri "http://localhost:8000/v1/columns/board/01HXYZ1234567890ABCDEF" -Method GET
```

## Data Models

### ColumnCreate

```json
{
  "title": "string (required, max 255 chars)",
  "description": "string (optional, max 1000 chars)",
  "board_id": "string (required, ULID)",
  "position": "integer (optional, default: 0)",
  "color": "string (optional, hex color code)",
  "is_archived": "boolean (optional, default: false)",
  "meta_data": "object (optional, JSONB)"
}
```

### ColumnUpdate

```json
{
  "title": "string (optional, max 255 chars)",
  "description": "string (optional, max 1000 chars)",
  "position": "integer (optional)",
  "color": "string (optional, hex color code)",
  "is_archived": "boolean (optional)",
  "meta_data": "object (optional, JSONB)"
}
```

### ColumnResponse

```json
{
  "id": "string (ULID)",
  "title": "string",
  "description": "string",
  "board_id": "string (ULID)",
  "position": "integer",
  "color": "string",
  "is_archived": "boolean",
  "meta_data": "object",
  "created_at": "datetime (ISO 8601)",
  "updated_at": "datetime (ISO 8601)",
  "version": "integer"
}
```

## Error Handling

### Common Error Responses

#### 404 Not Found

```json
{
  "success": false,
  "error": "Column not found",
  "details": "Column with ID '01HXYZ1234567890ABCDEF' not found"
}
```

#### 409 Conflict (Optimistic Concurrency)

```json
{
  "success": false,
  "error": "Optimistic concurrency conflict",
  "details": "Column has been modified by another request"
}
```

#### 400 Bad Request

```json
{
  "success": false,
  "error": "Validation error",
  "details": "Invalid board_id format"
}
```

#### 422 Unprocessable Entity

```json
{
  "success": false,
  "error": "Validation error",
  "details": [
    {
      "loc": ["body", "title"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

## Best Practices

1. **Use Optimistic Concurrency**: Always include the `If-Match` header when updating columns to prevent conflicts
2. **Pagination**: Use pagination parameters when listing columns to avoid large response payloads
3. **Filtering**: Use `board_id` parameter to get columns for specific boards
4. **Position Management**: Use the reorder endpoint to change column positions rather than updating the position field directly
5. **Soft Deletes**: Deleted columns are soft-deleted and can be restored if needed

## Rate Limiting

Currently no rate limiting is implemented. In production, consider implementing rate limiting based on tenant and user.

## Versioning

This API is version 1. Breaking changes will be introduced in version 2 endpoints.
