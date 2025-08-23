# Card API Documentation

## Overview

The Card API provides CRUD operations for managing cards within Kanban boards. Cards represent individual tasks, stories, or work items that can be moved between columns to track progress.

## Base URL

All endpoints are prefixed with `/v1/cards`

## Authentication

Currently using a default tenant ID. In production, this will be resolved from authentication context.

## Endpoints

### 1. Create Card

**POST** `/v1/cards/`

Creates a new card within a board and column.

#### Request Body

```json
{
  "title": "Implement user authentication",
  "description": "Add OAuth2 authentication with Google and GitHub providers",
  "board_id": "01HXYZ1234567890ABCDEF",
  "column_id": "01HXYZ1234567890ABCDEG",
  "priority": 3,
  "labels": ["backend", "security", "high-priority"],
  "assignees": ["user1@example.com", "user2@example.com"],
  "due_date": "2025-09-15T23:59:59Z",
  "estimated_hours": 8.0,
  "actual_hours": 0.0,
  "meta_data": {
    "story_points": 5,
    "epic": "user-management",
    "sprint": "sprint-3"
  }
}
```

#### Response (201 Created)

```json
{
  "success": true,
  "data": {
    "id": "01HXYZ1234567890ABCDEF",
    "title": "Implement user authentication",
    "description": "Add OAuth2 authentication with Google and GitHub providers",
    "board_id": "01HXYZ1234567890ABCDEF",
    "column_id": "01HXYZ1234567890ABCDEG",
    "position": 1,
    "priority": 3,
    "labels": ["backend", "security", "high-priority"],
    "assignees": ["user1@example.com", "user2@example.com"],
    "due_date": "2025-09-15T23:59:59Z",
    "estimated_hours": 8.0,
    "actual_hours": 0.0,
    "meta_data": {
      "story_points": 5,
      "epic": "user-management",
      "sprint": "sprint-3"
    },
    "created_at": "2025-08-23T12:00:00Z",
    "updated_at": "2025-08-23T12:00:00Z",
    "version": 1
  }
}
```

#### cURL Example

```bash
curl -X POST "http://localhost:8000/v1/cards/" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Implement user authentication",
    "description": "Add OAuth2 authentication with Google and GitHub providers",
    "board_id": "01HXYZ1234567890ABCDEF",
    "column_id": "01HXYZ1234567890ABCDEG",
    "priority": 3,
    "labels": ["backend", "security", "high-priority"]
  }'
```

#### PowerShell Example

```powershell
Invoke-RestMethod -Uri "http://localhost:8000/v1/cards/" -Method POST -ContentType "application/json" -Body '{
  "title": "Implement user authentication",
  "description": "Add OAuth2 authentication with Google and GitHub providers",
  "board_id": "01HXYZ1234567890ABCDEF",
  "column_id": "01HXYZ1234567890ABCDEG",
  "priority": 3,
  "labels": ["backend", "security", "high-priority"]
}'
```

### 2. Get Card

**GET** `/v1/cards/{card_id}`

Retrieves a specific card by ID.

#### Response (200 OK)

```json
{
  "success": true,
  "data": {
    "id": "01HXYZ1234567890ABCDEF",
    "title": "Implement user authentication",
    "description": "Add OAuth2 authentication with Google and GitHub providers",
    "board_id": "01HXYZ1234567890ABCDEF",
    "column_id": "01HXYZ1234567890ABCDEG",
    "position": 1,
    "priority": 3,
    "priority_label": "High",
    "labels": ["backend", "security", "high-priority"],
    "assignees": ["user1@example.com", "user2@example.com"],
    "due_date": "2025-09-15T23:59:59Z",
    "estimated_hours": 8.0,
    "actual_hours": 0.0,
    "meta_data": {
      "story_points": 5,
      "epic": "user-management",
      "sprint": "sprint-3"
    },
    "created_at": "2025-08-23T12:00:00Z",
    "updated_at": "2025-08-23T12:00:00Z",
    "version": 1
  }
}
```

#### cURL Example

```bash
curl -X GET "http://localhost:8000/v1/cards/01HXYZ1234567890ABCDEF"
```

#### PowerShell Example

```powershell
Invoke-RestMethod -Uri "http://localhost:8000/v1/cards/01HXYZ1234567890ABCDEF" -Method GET
```

### 3. List Cards

**GET** `/v1/cards/`

Retrieves a paginated list of cards with optional filtering.

#### Query Parameters

- `board_id` (optional): Filter cards by board ID
- `column_id` (optional): Filter cards by column ID
- `labels` (optional): Filter cards by labels (comma-separated)
- `assignees` (optional): Filter cards by assignees (comma-separated)
- `priority` (optional): Filter cards by priority (1-5)
- `limit` (optional, default: 100): Maximum number of cards to return (1-1000)
- `offset` (optional, default: 0): Number of cards to skip

#### Response (200 OK)

```json
{
  "success": true,
  "data": [
    {
      "id": "01HXYZ1234567890ABCDEF",
      "title": "Implement user authentication",
      "description": "Add OAuth2 authentication with Google and GitHub providers",
      "board_id": "01HXYZ1234567890ABCDEF",
      "column_id": "01HXYZ1234567890ABCDEG",
      "position": 1,
      "priority": 3,
      "priority_label": "High",
      "labels": ["backend", "security", "high-priority"],
      "assignees": ["user1@example.com", "user2@example.com"],
      "due_date": "2025-09-15T23:59:59Z",
      "estimated_hours": 8.0,
      "actual_hours": 0.0,
      "created_at": "2025-08-23T12:00:00Z",
      "updated_at": "2025-08-23T12:00:00Z"
    },
    {
      "id": "01HXYZ1234567890ABCDEG",
      "title": "Design user interface",
      "description": "Create wireframes and mockups for the user interface",
      "board_id": "01HXYZ1234567890ABCDEF",
      "column_id": "01HXYZ1234567890ABCDEG",
      "position": 2,
      "priority": 2,
      "priority_label": "Medium",
      "labels": ["frontend", "design"],
      "assignees": ["user3@example.com"],
      "due_date": "2025-09-10T23:59:59Z",
      "estimated_hours": 4.0,
      "actual_hours": 0.0,
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
# Get all cards
curl -X GET "http://localhost:8000/v1/cards/"

# Get cards for a specific board
curl -X GET "http://localhost:8000/v1/cards/?board_id=01HXYZ1234567890ABCDEF"

# Get cards for a specific column
curl -X GET "http://localhost:8000/v1/cards/?column_id=01HXYZ1234567890ABCDEG"

# Get high priority cards
curl -X GET "http://localhost:8000/v1/cards/?priority=3"

# Get cards with specific labels
curl -X GET "http://localhost:8000/v1/cards/?labels=backend,security"

# Get cards assigned to specific users
curl -X GET "http://localhost:8000/v1/cards/?assignees=user1@example.com,user2@example.com"

# Get cards with pagination
curl -X GET "http://localhost:8000/v1/cards/?limit=10&offset=0"
```

#### PowerShell Example

```powershell
# Get all cards
Invoke-RestMethod -Uri "http://localhost:8000/v1/cards/" -Method GET

# Get cards for a specific board
Invoke-RestMethod -Uri "http://localhost:8000/v1/cards/?board_id=01HXYZ1234567890ABCDEF" -Method GET

# Get cards for a specific column
Invoke-RestMethod -Uri "http://localhost:8000/v1/cards/?column_id=01HXYZ1234567890ABCDEG" -Method GET

# Get high priority cards
Invoke-RestMethod -Uri "http://localhost:8000/v1/cards/?priority=3" -Method GET

# Get cards with specific labels
Invoke-RestMethod -Uri "http://localhost:8000/v1/cards/?labels=backend,security" -Method GET

# Get cards assigned to specific users
Invoke-RestMethod -Uri "http://localhost:8000/v1/cards/?assignees=user1@example.com,user2@example.com" -Method GET

# Get cards with pagination
Invoke-RestMethod -Uri "http://localhost:8000/v1/cards/?limit=10&offset=0" -Method GET
```

### 4. Update Card

**PUT** `/v1/cards/{card_id}`

Updates an existing card. Requires optimistic concurrency control via `If-Match` header.

#### Headers

- `If-Match` (optional): Current version of the card for optimistic concurrency control

#### Request Body

```json
{
  "title": "Implement user authentication - Updated",
  "description": "Updated description with more details",
  "priority": 4,
  "labels": ["backend", "security", "high-priority", "critical"],
  "assignees": ["user1@example.com"],
  "due_date": "2025-09-20T23:59:59Z",
  "estimated_hours": 12.0,
  "meta_data": {
    "story_points": 8,
    "epic": "user-management",
    "sprint": "sprint-3",
    "blocked_by": ["card-123"]
  }
}
```

#### Response (200 OK)

```json
{
  "success": true,
  "data": {
    "id": "01HXYZ1234567890ABCDEF",
    "title": "Implement user authentication - Updated",
    "description": "Updated description with more details",
    "board_id": "01HXYZ1234567890ABCDEF",
    "column_id": "01HXYZ1234567890ABCDEG",
    "position": 1,
    "priority": 4,
    "priority_label": "Critical",
    "labels": ["backend", "security", "high-priority", "critical"],
    "assignees": ["user1@example.com"],
    "due_date": "2025-09-20T23:59:59Z",
    "estimated_hours": 12.0,
    "actual_hours": 0.0,
    "meta_data": {
      "story_points": 8,
      "epic": "user-management",
      "sprint": "sprint-3",
      "blocked_by": ["card-123"]
    },
    "created_at": "2025-08-23T12:00:00Z",
    "updated_at": "2025-08-23T12:30:00Z",
    "version": 2
  }
}
```

#### cURL Example

```bash
curl -X PUT "http://localhost:8000/v1/cards/01HXYZ1234567890ABCDEF" \
  -H "Content-Type: application/json" \
  -H "If-Match: 1" \
  -d '{
    "title": "Implement user authentication - Updated",
    "description": "Updated description with more details",
    "priority": 4,
    "labels": ["backend", "security", "high-priority", "critical"]
  }'
```

#### PowerShell Example

```powershell
$headers = @{
    "Content-Type" = "application/json"
    "If-Match" = "1"
}

Invoke-RestMethod -Uri "http://localhost:8000/v1/cards/01HXYZ1234567890ABCDEF" -Method PUT -Headers $headers -Body '{
  "title": "Implement user authentication - Updated",
  "description": "Updated description with more details",
  "priority": 4,
  "labels": ["backend", "security", "high-priority", "critical"]
}'
```

### 5. Delete Card

**DELETE** `/v1/cards/{card_id}`

Soft deletes a card (marks as deleted but doesn't remove from database).

#### Response (200 OK)

```json
{
  "success": true,
  "message": "Card deleted successfully"
}
```

#### cURL Example

```bash
curl -X DELETE "http://localhost:8000/v1/cards/01HXYZ1234567890ABCDEF"
```

#### PowerShell Example

```powershell
Invoke-RestMethod -Uri "http://localhost:8000/v1/cards/01HXYZ1234567890ABCDEF" -Method DELETE
```

### 6. Move Card

**POST** `/v1/cards/{card_id}/move`

Moves a card to a different column with optional positioning.

#### Request Body

```json
{
  "column_id": "01HXYZ1234567890ABCDEH",
  "position": 2
}
```

#### Response (200 OK)

```json
{
  "success": true,
  "message": "Card moved successfully"
}
```

#### cURL Example

```bash
curl -X POST "http://localhost:8000/v1/cards/01HXYZ1234567890ABCDEF/move" \
  -H "Content-Type: application/json" \
  -d '{
    "column_id": "01HXYZ1234567890ABCDEH",
    "position": 2
  }'
```

#### PowerShell Example

```powershell
Invoke-RestMethod -Uri "http://localhost:8000/v1/cards/01HXYZ1234567890ABCDEF/move" -Method POST -ContentType "application/json" -Body '{
  "column_id": "01HXYZ1234567890ABCDEH",
  "position": 2
}'
```

### 7. Reorder Card

**POST** `/v1/cards/{card_id}/reorder`

Moves a card to a new position within its current column.

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
  "message": "Card reordered successfully"
}
```

#### cURL Example

```bash
curl -X POST "http://localhost:8000/v1/cards/01HXYZ1234567890ABCDEF/reorder" \
  -H "Content-Type: application/json" \
  -d '{
    "new_position": 3
  }'
```

#### PowerShell Example

```powershell
Invoke-RestMethod -Uri "http://localhost:8000/v1/cards/01HXYZ1234567890ABCDEF/reorder" -Method POST -ContentType "application/json" -Body '{
  "new_position": 3
}'
```

### 8. Get Column Cards

**GET** `/v1/cards/column/{column_id}`

Retrieves all cards for a specific column, ordered by position.

#### Response (200 OK)

```json
[
  {
    "id": "01HXYZ1234567890ABCDEF",
    "title": "Implement user authentication",
    "description": "Add OAuth2 authentication with Google and GitHub providers",
    "board_id": "01HXYZ1234567890ABCDEF",
    "column_id": "01HXYZ1234567890ABCDEG",
    "position": 1,
    "priority": 3,
    "priority_label": "High",
    "labels": ["backend", "security", "high-priority"],
    "assignees": ["user1@example.com", "user2@example.com"],
    "due_date": "2025-09-15T23:59:59Z",
    "estimated_hours": 8.0,
    "actual_hours": 0.0,
    "created_at": "2025-08-23T12:00:00Z",
    "updated_at": "2025-08-23T12:00:00Z"
  },
  {
    "id": "01HXYZ1234567890ABCDEG",
    "title": "Design user interface",
    "description": "Create wireframes and mockups for the user interface",
    "board_id": "01HXYZ1234567890ABCDEF",
    "column_id": "01HXYZ1234567890ABCDEG",
    "position": 2,
    "priority": 2,
    "priority_label": "Medium",
    "labels": ["frontend", "design"],
    "assignees": ["user3@example.com"],
    "due_date": "2025-09-10T23:59:59Z",
    "estimated_hours": 4.0,
    "actual_hours": 0.0,
    "created_at": "2025-08-23T12:00:00Z",
    "updated_at": "2025-08-23T12:00:00Z"
  }
]
```

#### cURL Example

```bash
curl -X GET "http://localhost:8000/v1/cards/column/01HXYZ1234567890ABCDEG"
```

#### PowerShell Example

```powershell
Invoke-RestMethod -Uri "http://localhost:8000/v1/cards/column/01HXYZ1234567890ABCDEG" -Method GET
```

### 9. Get Board Cards

**GET** `/v1/cards/board/{board_id}`

Retrieves all cards for a specific board, ordered by column position and then card position.

#### Response (200 OK)

```json
[
  {
    "id": "01HXYZ1234567890ABCDEF",
    "title": "Implement user authentication",
    "description": "Add OAuth2 authentication with Google and GitHub providers",
    "board_id": "01HXYZ1234567890ABCDEF",
    "column_id": "01HXYZ1234567890ABCDEG",
    "position": 1,
    "priority": 3,
    "priority_label": "High",
    "labels": ["backend", "security", "high-priority"],
    "assignees": ["user1@example.com", "user2@example.com"],
    "due_date": "2025-09-15T23:59:59Z",
    "estimated_hours": 8.0,
    "actual_hours": 0.0,
    "created_at": "2025-08-23T12:00:00Z",
    "updated_at": "2025-08-23T12:00:00Z"
  },
  {
    "id": "01HXYZ1234567890ABCDEG",
    "title": "Design user interface",
    "description": "Create wireframes and mockups for the user interface",
    "board_id": "01HXYZ1234567890ABCDEF",
    "column_id": "01HXYZ1234567890ABCDEG",
    "position": 2,
    "priority": 2,
    "priority_label": "Medium",
    "labels": ["frontend", "design"],
    "assignees": ["user3@example.com"],
    "due_date": "2025-09-10T23:59:59Z",
    "estimated_hours": 4.0,
    "actual_hours": 0.0,
    "created_at": "2025-08-23T12:00:00Z",
    "updated_at": "2025-08-23T12:00:00Z"
  }
]
```

#### cURL Example

```bash
curl -X GET "http://localhost:8000/v1/cards/board/01HXYZ1234567890ABCDEF"
```

#### PowerShell Example

```powershell
Invoke-RestMethod -Uri "http://localhost:8000/v1/cards/board/01HXYZ1234567890ABCDEF" -Method GET
```

## Data Models

### CardCreate

```json
{
  "title": "string (required, max 255 chars)",
  "description": "string (optional, max 5000 chars)",
  "board_id": "string (required, ULID)",
  "column_id": "string (required, ULID)",
  "position": "integer (optional, default: 0)",
  "priority": "integer (optional, 1-5, default: 1)",
  "labels": "array of strings (optional)",
  "assignees": "array of strings (optional)",
  "due_date": "datetime (optional, ISO 8601)",
  "estimated_hours": "float (optional, default: 0.0)",
  "actual_hours": "float (optional, default: 0.0)",
  "meta_data": "object (optional, JSONB)"
}
```

### CardUpdate

```json
{
  "title": "string (optional, max 255 chars)",
  "description": "string (optional, max 5000 chars)",
  "column_id": "string (optional, ULID)",
  "position": "integer (optional)",
  "priority": "integer (optional, 1-5)",
  "labels": "array of strings (optional)",
  "assignees": "array of strings (optional)",
  "due_date": "datetime (optional, ISO 8601)",
  "estimated_hours": "float (optional)",
  "actual_hours": "float (optional)",
  "meta_data": "object (optional, JSONB)"
}
```

### CardResponse

```json
{
  "id": "string (ULID)",
  "title": "string",
  "description": "string",
  "board_id": "string (ULID)",
  "column_id": "string (ULID)",
  "position": "integer",
  "priority": "integer (1-5)",
  "priority_label": "string (Very Low, Low, Medium, High, Critical)",
  "labels": "array of strings",
  "assignees": "array of strings",
  "due_date": "datetime (ISO 8601)",
  "estimated_hours": "float",
  "actual_hours": "float",
  "meta_data": "object",
  "created_at": "datetime (ISO 8601)",
  "updated_at": "datetime (ISO 8601)",
  "version": "integer"
}
```

## Priority Levels

| Priority | Label | Description |
|----------|-------|-------------|
| 1 | Very Low | Minimal impact, can be deferred |
| 2 | Low | Low impact, normal priority |
| 3 | Medium | Standard priority |
| 4 | High | Important, should be addressed soon |
| 5 | Critical | Urgent, requires immediate attention |

## Error Handling

### Common Error Responses

#### 404 Not Found

```json
{
  "success": false,
  "error": "Card not found",
  "details": "Card with ID '01HXYZ1234567890ABCDEF' not found"
}
```

#### 409 Conflict (Optimistic Concurrency)

```json
{
  "success": false,
  "error": "Optimistic concurrency conflict",
  "details": "Card has been modified by another request"
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

1. **Use Optimistic Concurrency**: Always include the `If-Match` header when updating cards to prevent conflicts
2. **Pagination**: Use pagination parameters when listing cards to avoid large response payloads
3. **Filtering**: Use query parameters to filter cards by board, column, labels, assignees, or priority
4. **Position Management**: Use the move and reorder endpoints to change card positions rather than updating the position field directly
5. **Soft Deletes**: Deleted cards are soft-deleted and can be restored if needed
6. **Priority Usage**: Use priority levels consistently across your team (1-5 scale)
7. **Labels**: Use consistent label naming conventions for better filtering and organization
8. **Meta Data**: Store additional card-specific data in the meta_data field for extensibility

## Rate Limiting

Currently no rate limiting is implemented. In production, consider implementing rate limiting based on tenant and user.

## Versioning

This API is version 1. Breaking changes will be introduced in version 2 endpoints.
