# API Testing Scripts

This directory contains comprehensive testing scripts for the Kanban For Agents API endpoints.

## Available Scripts

### 1. `test_all_api_endpoints.py`
**Direct Repository Testing**

This script tests the API endpoints by directly calling the repository methods and business logic. It bypasses the HTTP layer and tests the core functionality.

**Features:**
- Tests all CRUD operations for workspaces, boards, columns, and cards
- Tests card movement and reordering
- Tests column reordering
- Creates test data and cleans up automatically
- Provides detailed test results with pass/fail status
- Saves test results to JSON files

**Usage:**
```bash
python debug/scripts/test_all_api_endpoints.py
```

**When to use:**
- Testing business logic and repository methods
- Debugging data layer issues
- Fast testing without HTTP overhead
- Unit testing of core functionality

### 2. `test_api_endpoints_http.py`
**HTTP-based API Testing**

This script tests the complete API stack by making actual HTTP requests to the running API server. It tests the full stack including FastAPI routing, middleware, serialization, and database operations.

**Features:**
- Tests the complete API stack via HTTP requests
- Tests FastAPI routing and middleware
- Tests request/response serialization
- Tests all CRUD operations for workspaces, boards, columns, and cards
- Tests card movement and reordering
- Tests column reordering
- Creates test data and cleans up automatically
- Provides detailed test results with pass/fail status
- Saves test results to JSON files

**Usage:**
```bash
# First, start the API server
python start_dev.py

# In another terminal, run the test script
python debug/scripts/test_api_endpoints_http.py
```

**When to use:**
- Testing the complete API stack
- Integration testing
- Testing HTTP-specific features (headers, status codes, etc.)
- End-to-end testing
- Performance testing of the full stack

## Test Coverage

Both scripts test the following endpoints:

### Workspace Endpoints
- `POST /v1/workspaces/` - Create workspace
- `GET /v1/workspaces/{id}` - Get workspace by ID
- `GET /v1/workspaces/` - List workspaces
- `PUT /v1/workspaces/{id}` - Update workspace
- `DELETE /v1/workspaces/{id}` - Archive workspace

### Board Endpoints
- `POST /v1/boards/` - Create board (with default columns)
- `GET /v1/boards/{id}` - Get board by ID
- `GET /v1/boards/` - List boards
- `PUT /v1/boards/{id}` - Update board
- `GET /v1/columns/?board_id={id}` - Get board columns

### Column Endpoints
- `POST /v1/columns/` - Create column
- `GET /v1/columns/{id}` - Get column by ID
- `GET /v1/columns/` - List columns
- `PUT /v1/columns/{id}` - Update column
- `POST /v1/columns/{id}/reorder` - Reorder column

### Card Endpoints
- `POST /v1/cards/` - Create card
- `GET /v1/cards/{id}` - Get card by ID
- `GET /v1/cards/` - List cards
- `PUT /v1/cards/{id}` - Update card
- `POST /v1/cards/{id}/move` - Move card
- `POST /v1/cards/{id}/reorder` - Reorder card

## Test Workflow

Both scripts follow this workflow:

1. **Create Test Workspace** - Creates a workspace for testing
2. **Create Test Board** - Creates a board with default columns (To Do, In Progress, Done)
3. **Test Column Operations** - Creates additional columns and tests column operations
4. **Test Card Operations** - Creates cards and tests all card operations including movement
5. **Cleanup** - Deletes all test data to leave the database clean

## Output

Both scripts provide:

1. **Console Output** - Real-time test results with ✅/❌ indicators
2. **JSON Results File** - Detailed test results saved to `debug/logs/`
3. **Test Summary** - Final summary with pass/fail counts and success rate

## Prerequisites

### For Direct Repository Testing (`test_all_api_endpoints.py`):
- Database must be initialized and accessible
- All dependencies installed
- No server required

### For HTTP Testing (`test_api_endpoints_http.py`):
- API server must be running on `http://localhost:8000`
- Database must be initialized and accessible
- All dependencies installed
- `httpx` library for HTTP requests

## Troubleshooting

### Common Issues

1. **Database Connection Errors**
   - Ensure the database is running and accessible
   - Check database configuration in `.env`
   - Run database migrations if needed

2. **Import Errors**
   - Ensure you're running from the project root
   - Check that all dependencies are installed
   - Verify Python path includes the project root

3. **HTTP Connection Errors** (HTTP script only)
   - Ensure the API server is running on `http://localhost:8000`
   - Check server logs for errors
   - Verify the server is accessible

4. **Test Failures**
   - Check the detailed error messages in the console output
   - Review the JSON results file for more details
   - Ensure the database schema is up to date

### Debug Mode

To run with more verbose output, you can modify the scripts to include additional logging or run them with Python's debug mode:

```bash
python -v debug/scripts/test_all_api_endpoints.py
```

## Integration with CI/CD

These scripts can be integrated into CI/CD pipelines:

```yaml
# Example GitHub Actions step
- name: Test API Endpoints
  run: |
    python start_dev.py &
    sleep 10  # Wait for server to start
    python debug/scripts/test_api_endpoints_http.py
```

## Contributing

When adding new API endpoints, update both testing scripts to include comprehensive tests for the new functionality. Follow the existing patterns for:

- Test naming conventions
- Error handling
- Result logging
- Data cleanup
- JSON result formatting
