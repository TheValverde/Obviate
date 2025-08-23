# Debug Scripts and Logs

This directory contains debug scripts and logs for troubleshooting the Kanban For Agents application.

## Directory Structure

```
debug/
├── README.md              # This file
├── scripts/               # Debug scripts
│   ├── debug_template.py  # Template for creating new debug scripts
│   ├── debug_column_endpoints.py  # Column endpoint debugging
│   └── debug_api_endpoints.py     # API endpoint testing
└── logs/                  # Timestamped log files
    ├── debug_column_endpoints_20250823_123456.log
    ├── debug_api_endpoints_20250823_123456.log
    └── ...
```

## Usage

### Running Debug Scripts

From the project root:

```bash
# Test column endpoints
python debug/scripts/debug_column_endpoints.py

# Test API endpoints
python debug/scripts/debug_api_endpoints.py
```

### Creating New Debug Scripts

1. Copy `debug_template.py` to create a new script
2. Modify the `debug_main()` function with your specific debugging logic
3. Use the `setup_logging()` function for consistent logging

### Log Files

- All debug scripts create timestamped log files in `debug/logs/`
- Logs include both file output and console output
- Format: `{script_name}_{YYYYMMDD_HHMMSS}.log`

### Debug Script Template Features

- Automatic database initialization
- Proper path handling for imports
- Timestamped log files
- Comprehensive error handling with stack traces
- Console and file logging

## Common Debug Scenarios

### Database Issues
- Use `debug_column_endpoints.py` to test repository operations
- Check if tables exist and are accessible
- Verify tenant isolation is working

### API Issues
- Use `debug_api_endpoints.py` to test FastAPI endpoints
- Verify response formats and status codes
- Check pagination and filtering

### Schema Issues
- Test Pydantic model validation
- Check response serialization
- Verify field mappings

## Tips

1. **Always check logs first** - Most issues are logged with detailed error messages
2. **Use the template** - Ensures consistent debugging approach
3. **Test incrementally** - Start with simple operations before complex ones
4. **Check database state** - Verify data exists and is in expected format
5. **Test with different tenants** - Ensure tenant isolation works correctly

## Cleanup

Old log files can be cleaned up periodically:

```bash
# Remove logs older than 7 days
find debug/logs -name "*.log" -mtime +7 -delete
```
