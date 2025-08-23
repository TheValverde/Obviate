# Kanban For Agents API Documentation

## Overview

This is the complete API documentation for the Kanban For Agents application. The API provides a comprehensive set of endpoints for managing workspaces, boards, columns, and cards in a Kanban-style project management system.

## Quick Start

### Base URL
```
http://localhost:8000
```

### API Version
All endpoints are prefixed with `/v1`

### Authentication
Currently using a default tenant ID. In production, this will be resolved from authentication context.

### Interactive Documentation
Visit `http://localhost:8000/docs` for interactive Swagger/OpenAPI documentation.

## API Endpoints by Entity

### 1. Workspace API
**Base Path**: `/v1/workspaces`

Workspaces are the top-level organizational units that contain boards.

- [📋 Workspace API Documentation](BOARD_API.md)
- **Endpoints**:
  - `POST /v1/workspaces/` - Create workspace
  - `GET /v1/workspaces/{workspace_id}` - Get workspace
  - `GET /v1/workspaces/` - List workspaces
  - `PUT /v1/workspaces/{workspace_id}` - Update workspace
  - `DELETE /v1/workspaces/{workspace_id}` - Delete workspace
  - `POST /v1/workspaces/{workspace_id}/archive` - Archive workspace

### 2. Board API
**Base Path**: `/v1/boards`

Boards represent Kanban boards within workspaces.

- [📋 Board API Documentation](BOARD_API.md)
- **Endpoints**:
  - `POST /v1/boards/` - Create board
  - `GET /v1/boards/{board_id}` - Get board
  - `GET /v1/boards/` - List boards
  - `PUT /v1/boards/{board_id}` - Update board
  - `DELETE /v1/boards/{board_id}` - Delete board
  - `POST /v1/boards/{board_id}/archive` - Archive board

### 3. Column API
**Base Path**: `/v1/columns`

Columns represent the different stages or categories that cards can be moved between.

- [📋 Column API Documentation](COLUMN_API.md)
- **Endpoints**:
  - `POST /v1/columns/` - Create column
  - `GET /v1/columns/{column_id}` - Get column
  - `GET /v1/columns/` - List columns
  - `PUT /v1/columns/{column_id}` - Update column
  - `DELETE /v1/columns/{column_id}` - Delete column
  - `POST /v1/columns/{column_id}/reorder` - Reorder column
  - `GET /v1/columns/board/{board_id}` - Get board columns

### 4. Card API
**Base Path**: `/v1/cards`

Cards represent individual tasks, stories, or work items that can be moved between columns.

- [📋 Card API Documentation](CARD_API.md)
- **Endpoints**:
  - `POST /v1/cards/` - Create card
  - `GET /v1/cards/{card_id}` - Get card
  - `GET /v1/cards/` - List cards
  - `PUT /v1/cards/{card_id}` - Update card
  - `DELETE /v1/cards/{card_id}` - Delete card
  - `POST /v1/cards/{card_id}/move` - Move card between columns
  - `POST /v1/cards/{card_id}/reorder` - Reorder card within column
  - `GET /v1/cards/column/{column_id}` - Get column cards
  - `GET /v1/cards/board/{board_id}` - Get board cards

## Common Features

### Response Format
All API responses follow a consistent format:

```json
{
  "success": true,
  "data": { ... },
  "pagination": { ... }  // For list endpoints
}
```

### Error Handling
All endpoints return consistent error responses:

```json
{
  "success": false,
  "error": "Error message",
  "details": "Additional error details"
}
```

### Pagination
List endpoints support pagination with the following parameters:
- `limit` (optional, default: 100): Maximum number of items to return (1-1000)
- `offset` (optional, default: 0): Number of items to skip

Pagination response includes:
```json
{
  "page": 1,
  "limit": 100,
  "total": 250,
  "pages": 3,
  "has_next": true,
  "has_prev": false
}
```

### Optimistic Concurrency Control
Update endpoints support optimistic concurrency control via the `If-Match` header:
```bash
curl -X PUT "http://localhost:8000/v1/cards/{card_id}" \
  -H "If-Match: 1" \
  -H "Content-Type: application/json" \
  -d '{ ... }'
```

### Filtering
Many list endpoints support filtering via query parameters:
- `board_id` - Filter by board
- `column_id` - Filter by column
- `labels` - Filter by labels (comma-separated)
- `assignees` - Filter by assignees (comma-separated)
- `priority` - Filter by priority (1-5)

## Data Models

### Common Fields
All entities include these common fields:
- `id` (ULID) - Unique identifier
- `created_at` (ISO 8601 datetime) - Creation timestamp
- `updated_at` (ISO 8601 datetime) - Last update timestamp
- `version` (integer) - Version for optimistic concurrency
- `meta_data` (JSONB) - Flexible metadata storage

### Priority Levels
Cards use a 5-level priority system:
| Priority | Label | Description |
|----------|-------|-------------|
| 1 | Very Low | Minimal impact, can be deferred |
| 2 | Low | Low impact, normal priority |
| 3 | Medium | Standard priority |
| 4 | High | Important, should be addressed soon |
| 5 | Critical | Urgent, requires immediate attention |

## Quick Reference

### Common HTTP Status Codes
- `200 OK` - Request successful
- `201 Created` - Resource created successfully
- `400 Bad Request` - Invalid request data
- `404 Not Found` - Resource not found
- `409 Conflict` - Optimistic concurrency conflict
- `422 Unprocessable Entity` - Validation error

### Common Headers
- `Content-Type: application/json` - For POST/PUT requests
- `If-Match: <version>` - For optimistic concurrency control
- `Accept: application/json` - For response format

## Examples

### Complete Workflow Example

1. **Create a Workspace**
```bash
curl -X POST "http://localhost:8000/v1/workspaces/" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "My Project",
    "description": "A sample project workspace"
  }'
```

2. **Create a Board**
```bash
curl -X POST "http://localhost:8000/v1/boards/" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Development Board",
    "description": "Main development tasks",
    "workspace_id": "01HXYZ1234567890ABCDEF"
  }'
```

3. **Create Columns**
```bash
# Create Todo column
curl -X POST "http://localhost:8000/v1/columns/" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Todo",
    "description": "Tasks to be done",
    "board_id": "01HXYZ1234567890ABCDEF",
    "position": 1
  }'

# Create In Progress column
curl -X POST "http://localhost:8000/v1/columns/" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "In Progress",
    "description": "Tasks currently being worked on",
    "board_id": "01HXYZ1234567890ABCDEF",
    "position": 2
  }'

# Create Done column
curl -X POST "http://localhost:8000/v1/columns/" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Done",
    "description": "Completed tasks",
    "board_id": "01HXYZ1234567890ABCDEF",
    "position": 3
  }'
```

4. **Create a Card**
```bash
curl -X POST "http://localhost:8000/v1/cards/" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Implement user authentication",
    "description": "Add OAuth2 authentication",
    "board_id": "01HXYZ1234567890ABCDEF",
    "column_id": "01HXYZ1234567890ABCDEG",
    "priority": 3,
    "labels": ["backend", "security"]
  }'
```

5. **Move a Card**
```bash
curl -X POST "http://localhost:8000/v1/cards/01HXYZ1234567890ABCDEF/move" \
  -H "Content-Type: application/json" \
  -d '{
    "column_id": "01HXYZ1234567890ABCDEH",
    "position": 1
  }'
```

## Best Practices

1. **Use Optimistic Concurrency**: Always include `If-Match` headers for updates
2. **Implement Pagination**: Use pagination for large datasets
3. **Use Filtering**: Leverage query parameters for efficient data retrieval
4. **Handle Errors Gracefully**: Check for error responses and handle them appropriately
5. **Use Consistent Naming**: Follow consistent naming conventions for labels and metadata
6. **Monitor Rate Limits**: Be aware of potential rate limiting in production

## Development

### Local Development
```bash
# Start the server
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Access interactive docs
open http://localhost:8000/docs
```

### Testing
Use the provided debug scripts in the `debug/scripts/` directory:
- `debug_api_endpoints.py` - Test all API endpoints
- `debug_column_endpoints.py` - Test column operations
- `debug_card_endpoints.py` - Test card operations

## Support

For issues, questions, or contributions:
1. Check the interactive documentation at `/docs`
2. Review the debug logs in `debug/logs/`
3. Use the debug scripts for troubleshooting
4. Check the TODO.md for current development status

## Version History

- **v1.0** - Initial release with Workspace, Board, Column, and Card APIs
  - Full CRUD operations for all entities
  - Optimistic concurrency control
  - Comprehensive filtering and pagination
  - Move and reorder functionality for cards and columns
