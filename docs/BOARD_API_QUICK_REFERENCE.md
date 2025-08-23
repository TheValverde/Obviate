# Board API Quick Reference

## Base URL
```
http://localhost:8000/v1/boards
```

## Endpoints Summary

| Method | Endpoint | Description | Status Codes |
|--------|----------|-------------|--------------|
| `POST` | `/v1/boards/` | Create board | 201, 400, 422 |
| `GET` | `/v1/boards/{id}` | Get board | 200, 404 |
| `GET` | `/v1/boards/` | List boards | 200 |
| `PUT` | `/v1/boards/{id}` | Update board | 200, 404, 409 |
| `DELETE` | `/v1/boards/{id}` | Delete board | 200, 404 |
| `POST` | `/v1/boards/{id}/archive` | Archive/unarchive | 200, 404, 409 |

## Quick Examples

### Create Board
```bash
curl -X POST "http://localhost:8000/v1/boards/" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "My Board",
    "description": "Description",
    "workspace_id": "AGMNJ7P3MA5QBA2XG3GRBPRKB4"
  }'
```

### Get Board
```bash
curl -X GET "http://localhost:8000/v1/boards/AGMNKFUYWE2LKTT5DGINE5NLXD"
```

### List Boards
```bash
curl -X GET "http://localhost:8000/v1/boards/?limit=10&offset=0"
```

### Update Board
```bash
curl -X PUT "http://localhost:8000/v1/boards/AGMNKFUYWE2LKTT5DGINE5NLXD" \
  -H "Content-Type: application/json" \
  -H "If-Match: \"1\"" \
  -d '{"name": "Updated Name"}'
```

### Delete Board
```bash
curl -X DELETE "http://localhost:8000/v1/boards/AGMNKFUYWE2LKTT5DGINE5NLXD"
```

### Archive Board
```bash
curl -X POST "http://localhost:8000/v1/boards/AGMNKFUYWE2LKTT5DGINE5NLXD/archive" \
  -H "Content-Type: application/json" \
  -d '{"archived": true}'
```

## PowerShell Examples

### Create Board
```powershell
$body = @{
    name = "My Board"
    description = "Description"
    workspace_id = "AGMNJ7P3MA5QBA2XG3GRBPRKB4"
} | ConvertTo-Json

Invoke-WebRequest -Uri "http://localhost:8000/v1/boards/" -Method POST -Body $body -ContentType "application/json"
```

### Update Board
```powershell
$headers = @{"If-Match" = '"1"'}
$body = @{name = "Updated Name"} | ConvertTo-Json
Invoke-WebRequest -Uri "http://localhost:8000/v1/boards/AGMNKFUYWE2LKTT5DGINE5NLXD" -Method PUT -Body $body -ContentType "application/json" -Headers $headers
```

## Response Format

### Success Response
```json
{
  "success": true,
  "message": "Operation message",
  "data": { ... }
}
```

### Error Response
```json
{
  "success": false,
  "error": {
    "code": "ERROR_CODE",
    "message": "Error message",
    "details": null
  }
}
```

## Key Fields

### Board Object
- `id`: ULID format (26 chars)
- `name`: 1-255 characters
- `description`: max 1000 characters
- `workspace_id`: ULID format
- `version`: optimistic concurrency
- `created_at`, `updated_at`, `deleted_at`: ISO 8601 timestamps

### Query Parameters (List)
- `offset`: skip records (default: 0)
- `limit`: records per page (default: 100, max: 1000)
- `workspace_id`: filter by workspace
- `archived`: filter by archived status
- `include_deleted`: include soft-deleted (default: false)

## Optimistic Concurrency
- Use `If-Match` header with version number
- Format: `If-Match: "1"`
- Returns 409 Conflict on version mismatch

## Error Codes
- `BOARD_NOT_FOUND`: 404
- `OPTIMISTIC_CONCURRENCY_EXCEPTION`: 409
- `BAD_REQUEST`: 400
- `VALIDATION_ERROR`: 422
