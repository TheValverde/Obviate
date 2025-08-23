# MCP Integration Guide for Kanban For Agents

## Overview

This guide provides everything needed to create an MCP (Model Context Protocol) server that wraps around the Kanban For Agents API. This enables AI agents to interact with Kanban boards programmatically through standardized MCP tools.

## MCP Server Architecture

### Core Concepts

The MCP server acts as a bridge between AI agents and the Kanban API, providing:
- **Tool Definitions**: Standardized tools for Kanban operations
- **Authentication**: API key management for agent access
- **Error Handling**: Consistent error responses across all tools
- **Data Transformation**: Converting between MCP and API formats

### Required MCP Tools

#### 1. Workspace Management Tools
```json
{
  "name": "list_workspaces",
  "description": "List all workspaces for the authenticated user",
  "inputSchema": {
    "type": "object",
    "properties": {
      "limit": {"type": "integer", "default": 100},
      "offset": {"type": "integer", "default": 0}
    }
  }
}
```

```json
{
  "name": "create_workspace",
  "description": "Create a new workspace",
  "inputSchema": {
    "type": "object",
    "required": ["name"],
    "properties": {
      "name": {"type": "string", "maxLength": 255},
      "description": {"type": "string", "maxLength": 1000}
    }
  }
}
```

#### 2. Board Management Tools
```json
{
  "name": "list_boards",
  "description": "List boards in a workspace",
  "inputSchema": {
    "type": "object",
    "properties": {
      "workspace_id": {"type": "string"},
      "limit": {"type": "integer", "default": 100},
      "offset": {"type": "integer", "default": 0}
    }
  }
}
```

```json
{
  "name": "create_board",
  "description": "Create a new board with default columns",
  "inputSchema": {
    "type": "object",
    "required": ["title", "workspace_id"],
    "properties": {
      "title": {"type": "string", "maxLength": 255},
      "description": {"type": "string", "maxLength": 1000},
      "workspace_id": {"type": "string"},
      "create_default_columns": {"type": "boolean", "default": true}
    }
  }
}
```

#### 3. Column Management Tools
```json
{
  "name": "list_columns",
  "description": "List columns in a board",
  "inputSchema": {
    "type": "object",
    "properties": {
      "board_id": {"type": "string"},
      "limit": {"type": "integer", "default": 100},
      "offset": {"type": "integer", "default": 0}
    }
  }
}
```

```json
{
  "name": "create_column",
  "description": "Create a new column in a board",
  "inputSchema": {
    "type": "object",
    "required": ["title", "board_id"],
    "properties": {
      "title": {"type": "string", "maxLength": 255},
      "description": {"type": "string", "maxLength": 1000},
      "board_id": {"type": "string"},
      "position": {"type": "integer", "default": 0},
      "color": {"type": "string"}
    }
  }
}
```

#### 4. Card Management Tools
```json
{
  "name": "list_cards",
  "description": "List cards with optional filtering",
  "inputSchema": {
    "type": "object",
    "properties": {
      "board_id": {"type": "string"},
      "column_id": {"type": "string"},
      "labels": {"type": "array", "items": {"type": "string"}},
      "assignees": {"type": "array", "items": {"type": "string"}},
      "priority": {"type": "integer", "minimum": 1, "maximum": 5},
      "limit": {"type": "integer", "default": 100},
      "offset": {"type": "integer", "default": 0}
    }
  }
}
```

```json
{
  "name": "create_card",
  "description": "Create a new card",
  "inputSchema": {
    "type": "object",
    "required": ["title", "board_id", "column_id"],
    "properties": {
      "title": {"type": "string", "maxLength": 255},
      "description": {"type": "string", "maxLength": 5000},
      "board_id": {"type": "string"},
      "column_id": {"type": "string"},
      "priority": {"type": "integer", "minimum": 1, "maximum": 5, "default": 1},
      "labels": {"type": "array", "items": {"type": "string"}},
      "assignees": {"type": "array", "items": {"type": "string"}},
      "due_date": {"type": "string", "format": "date-time"},
      "estimated_hours": {"type": "number", "default": 0},
      "meta_data": {"type": "object"}
    }
  }
}
```

```json
{
  "name": "move_card",
  "description": "Move a card to a different column",
  "inputSchema": {
    "type": "object",
    "required": ["card_id", "column_id"],
    "properties": {
      "card_id": {"type": "string"},
      "column_id": {"type": "string"},
      "position": {"type": "integer", "minimum": 0}
    }
  }
}
```

```json
{
  "name": "update_card",
  "description": "Update an existing card",
  "inputSchema": {
    "type": "object",
    "required": ["card_id"],
    "properties": {
      "card_id": {"type": "string"},
      "title": {"type": "string", "maxLength": 255},
      "description": {"type": "string", "maxLength": 5000},
      "priority": {"type": "integer", "minimum": 1, "maximum": 5},
      "labels": {"type": "array", "items": {"type": "string"}},
      "assignees": {"type": "array", "items": {"type": "string"}},
      "due_date": {"type": "string", "format": "date-time"},
      "estimated_hours": {"type": "number"},
      "actual_hours": {"type": "number"},
      "meta_data": {"type": "object"}
    }
  }
}
```

#### 5. Workflow Tools
```json
{
  "name": "get_board_state",
  "description": "Get complete board state with columns and cards",
  "inputSchema": {
    "type": "object",
    "required": ["board_id"],
    "properties": {
      "board_id": {"type": "string"},
      "include_cards": {"type": "boolean", "default": true}
    }
  }
}
```

```json
{
  "name": "get_agent_tasks",
  "description": "Get tasks assigned to a specific agent",
  "inputSchema": {
    "type": "object",
    "required": ["agent_id"],
    "properties": {
      "agent_id": {"type": "string"},
      "board_id": {"type": "string"},
      "status": {"type": "string", "enum": ["todo", "in_progress", "done"]},
      "priority": {"type": "integer", "minimum": 1, "maximum": 5}
    }
  }
}
```

## Implementation Guide

### 1. MCP Server Setup

```python
from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server
import httpx
import json
from typing import Any, Dict, List

class KanbanMCPServer:
    def __init__(self, api_base_url: str, api_key: str):
        self.api_base_url = api_base_url
        self.api_key = api_key
        self.client = httpx.AsyncClient(
            base_url=api_base_url,
            headers={"Authorization": f"Bearer {api_key}"}
        )
    
    async def list_workspaces(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """List all workspaces"""
        params = {
            "limit": args.get("limit", 100),
            "offset": args.get("offset", 0)
        }
        
        response = await self.client.get("/v1/workspaces/", params=params)
        response.raise_for_status()
        
        return {
            "success": True,
            "data": response.json()["data"],
            "pagination": response.json().get("pagination", {})
        }
    
    async def create_board(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new board with optional default columns"""
        board_data = {
            "title": args["title"],
            "description": args.get("description", ""),
            "workspace_id": args["workspace_id"]
        }
        
        # Create board
        response = await self.client.post("/v1/boards/", json=board_data)
        response.raise_for_status()
        board = response.json()["data"]
        
        # Create default columns if requested
        if args.get("create_default_columns", True):
            default_columns = [
                {"title": "Todo", "description": "Tasks to be done", "position": 1, "color": "#6B7280"},
                {"title": "In Progress", "description": "Tasks currently being worked on", "position": 2, "color": "#3B82F6"},
                {"title": "Done", "description": "Completed tasks", "position": 3, "color": "#10B981"}
            ]
            
            for column_data in default_columns:
                column_data["board_id"] = board["id"]
                await self.client.post("/v1/columns/", json=column_data)
        
        return {
            "success": True,
            "data": board,
            "message": "Board created successfully with default columns"
        }
    
    async def get_board_state(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Get complete board state with columns and cards"""
        board_id = args["board_id"]
        
        # Get board details
        board_response = await self.client.get(f"/v1/boards/{board_id}")
        board_response.raise_for_status()
        board = board_response.json()["data"]
        
        # Get columns
        columns_response = await self.client.get(f"/v1/columns/board/{board_id}")
        columns_response.raise_for_status()
        columns = columns_response.json()
        
        # Get cards if requested
        cards = []
        if args.get("include_cards", True):
            cards_response = await self.client.get(f"/v1/cards/board/{board_id}")
            cards_response.raise_for_status()
            cards = cards_response.json()
        
        # Organize cards by column
        columns_with_cards = []
        for column in columns:
            column_cards = [card for card in cards if card["column_id"] == column["id"]]
            columns_with_cards.append({
                **column,
                "cards": sorted(column_cards, key=lambda x: x["position"])
            })
        
        return {
            "success": True,
            "data": {
                "board": board,
                "columns": sorted(columns_with_cards, key=lambda x: x["position"]),
                "total_cards": len(cards)
            }
        }
    
    async def get_agent_tasks(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Get tasks assigned to a specific agent"""
        agent_id = args["agent_id"]
        
        # Build query parameters
        params = {
            "assignees": agent_id,
            "limit": args.get("limit", 100),
            "offset": args.get("offset", 0)
        }
        
        if "board_id" in args:
            params["board_id"] = args["board_id"]
        
        if "priority" in args:
            params["priority"] = args["priority"]
        
        # Get cards
        response = await self.client.get("/v1/cards/", params=params)
        response.raise_for_status()
        
        cards = response.json()["data"]
        
        # Filter by status if specified
        if "status" in args:
            status_mapping = {
                "todo": lambda card: card.get("column_title", "").lower() == "todo",
                "in_progress": lambda card: card.get("column_title", "").lower() in ["in progress", "doing"],
                "done": lambda card: card.get("column_title", "").lower() == "done"
            }
            
            if args["status"] in status_mapping:
                cards = [card for card in cards if status_mapping[args["status"]](card)]
        
        return {
            "success": True,
            "data": {
                "agent_id": agent_id,
                "tasks": cards,
                "total_tasks": len(cards)
            }
        }

# MCP Server initialization
async def main():
    server = Server("kanban-mcp")
    
    # Initialize Kanban MCP server
    kanban_server = KanbanMCPServer(
        api_base_url="http://localhost:8000",
        api_key="your-api-key-here"
    )
    
    # Register tools
    @server.list_tools()
    async def handle_list_tools() -> List[Tool]:
        return [
            Tool(
                name="list_workspaces",
                description="List all workspaces for the authenticated user",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "limit": {"type": "integer", "default": 100},
                        "offset": {"type": "integer", "default": 0}
                    }
                }
            ),
            Tool(
                name="create_board",
                description="Create a new board with default columns",
                inputSchema={
                    "type": "object",
                    "required": ["title", "workspace_id"],
                    "properties": {
                        "title": {"type": "string", "maxLength": 255},
                        "description": {"type": "string", "maxLength": 1000},
                        "workspace_id": {"type": "string"},
                        "create_default_columns": {"type": "boolean", "default": true}
                    }
                }
            ),
            # Add other tools...
        ]
    
    @server.call_tool()
    async def handle_call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
        try:
            if name == "list_workspaces":
                result = await kanban_server.list_workspaces(arguments)
            elif name == "create_board":
                result = await kanban_server.create_board(arguments)
            elif name == "get_board_state":
                result = await kanban_server.get_board_state(arguments)
            elif name == "get_agent_tasks":
                result = await kanban_server.get_agent_tasks(arguments)
            else:
                raise ValueError(f"Unknown tool: {name}")
            
            return [TextContent(type="text", text=json.dumps(result, indent=2))]
        
        except Exception as e:
            return [TextContent(type="text", text=json.dumps({
                "success": False,
                "error": str(e)
            }, indent=2))]
    
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="kanban-mcp",
                server_version="1.0.0",
                capabilities=ServerCapabilities(
                    tools=ToolCapability()
                )
            )
        )

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
```

### 2. Configuration

Create a configuration file `mcp_config.json`:

```json
{
  "mcpServers": {
    "kanban": {
      "command": "python",
      "args": ["-m", "kanban_mcp_server"],
      "env": {
        "KANBAN_API_URL": "http://localhost:8000",
        "KANBAN_API_KEY": "your-api-key-here"
      }
    }
  }
}
```

### 3. Error Handling

```python
class KanbanMCPError(Exception):
    """Base exception for Kanban MCP operations"""
    pass

class KanbanAPIError(KanbanMCPError):
    """Exception raised when Kanban API returns an error"""
    def __init__(self, status_code: int, message: str, details: str = None):
        self.status_code = status_code
        self.message = message
        self.details = details
        super().__init__(f"API Error {status_code}: {message}")

async def handle_api_error(response: httpx.Response) -> None:
    """Handle API errors consistently"""
    if response.status_code >= 400:
        try:
            error_data = response.json()
            raise KanbanAPIError(
                status_code=response.status_code,
                message=error_data.get("error", "Unknown error"),
                details=error_data.get("details")
            )
        except json.JSONDecodeError:
            raise KanbanAPIError(
                status_code=response.status_code,
                message=response.text or "Unknown error"
            )
```

## Workflow Examples

### 1. Agent Task Management Workflow

```python
# Example: AI agent managing its tasks
async def agent_task_workflow(agent_id: str, board_id: str):
    """Complete workflow for an AI agent managing tasks"""
    
    # 1. Get current tasks
    tasks = await get_agent_tasks({
        "agent_id": agent_id,
        "board_id": board_id,
        "status": "todo"
    })
    
    # 2. Process each task
    for task in tasks["data"]["tasks"]:
        # Move task to "In Progress"
        await move_card({
            "card_id": task["id"],
            "column_id": "in_progress_column_id"
        })
        
        # Update task with progress
        await update_card({
            "card_id": task["id"],
            "description": f"Processing by agent {agent_id}",
            "meta_data": {
                "agent_processing": True,
                "started_at": datetime.now().isoformat()
            }
        })
        
        # Simulate work
        await asyncio.sleep(5)
        
        # Move to "Done"
        await move_card({
            "card_id": task["id"],
            "column_id": "done_column_id"
        })
        
        # Update with completion
        await update_card({
            "card_id": task["id"],
            "description": f"Completed by agent {agent_id}",
            "meta_data": {
                "agent_processing": False,
                "completed_at": datetime.now().isoformat()
            }
        })
```

### 2. Board Creation Workflow

```python
# Example: Creating a new project board
async def create_project_board(workspace_id: str, project_name: str):
    """Create a new project board with standard columns"""
    
    # Create board
    board = await create_board({
        "title": f"{project_name} Project",
        "description": f"Kanban board for {project_name} project",
        "workspace_id": workspace_id,
        "create_default_columns": True
    })
    
    # Add custom columns if needed
    await create_column({
        "title": "Backlog",
        "description": "Future tasks and ideas",
        "board_id": board["data"]["id"],
        "position": 0,
        "color": "#8B5CF6"
    })
    
    await create_column({
        "title": "Review",
        "description": "Tasks ready for review",
        "board_id": board["data"]["id"],
        "position": 4,
        "color": "#F59E0B"
    })
    
    return board
```

### 3. Multi-Agent Collaboration Workflow

```python
# Example: Multiple agents working on the same board
async def multi_agent_workflow(board_id: str, agent_ids: List[str]):
    """Workflow for multiple agents collaborating on tasks"""
    
    # Get board state
    board_state = await get_board_state({
        "board_id": board_id,
        "include_cards": True
    })
    
    # Distribute tasks among agents
    todo_cards = []
    for column in board_state["data"]["columns"]:
        if column["title"].lower() == "todo":
            todo_cards = column["cards"]
            break
    
    # Assign tasks to agents
    for i, card in enumerate(todo_cards):
        agent_id = agent_ids[i % len(agent_ids)]
        
        await update_card({
            "card_id": card["id"],
            "assignees": [agent_id],
            "meta_data": {
                "assigned_at": datetime.now().isoformat(),
                "assigned_agent": agent_id
            }
        })
```

## Testing the MCP Server

### 1. Unit Tests

```python
import pytest
from unittest.mock import AsyncMock, patch
from kanban_mcp_server import KanbanMCPServer

@pytest.mark.asyncio
async def test_list_workspaces():
    with patch('httpx.AsyncClient.get') as mock_get:
        mock_response = AsyncMock()
        mock_response.json.return_value = {
            "success": True,
            "data": [{"id": "1", "name": "Test Workspace"}],
            "pagination": {"total": 1}
        }
        mock_get.return_value = mock_response
        
        server = KanbanMCPServer("http://localhost:8000", "test-key")
        result = await server.list_workspaces({"limit": 10})
        
        assert result["success"] is True
        assert len(result["data"]) == 1
        assert result["data"][0]["name"] == "Test Workspace"

@pytest.mark.asyncio
async def test_create_board_with_default_columns():
    with patch('httpx.AsyncClient.post') as mock_post:
        # Mock board creation
        board_response = AsyncMock()
        board_response.json.return_value = {
            "success": True,
            "data": {"id": "board-1", "title": "Test Board"}
        }
        
        # Mock column creation
        column_response = AsyncMock()
        column_response.json.return_value = {"success": True}
        
        mock_post.side_effect = [board_response, column_response, column_response, column_response]
        
        server = KanbanMCPServer("http://localhost:8000", "test-key")
        result = await server.create_board({
            "title": "Test Board",
            "workspace_id": "workspace-1",
            "create_default_columns": True
        })
        
        assert result["success"] is True
        assert result["data"]["title"] == "Test Board"
```

### 2. Integration Tests

```python
@pytest.mark.asyncio
async def test_full_workflow():
    """Test complete workflow from board creation to task completion"""
    
    # This would test against a real or mocked API
    server = KanbanMCPServer("http://localhost:8000", "test-key")
    
    # 1. Create workspace
    workspace = await server.create_workspace({
        "name": "Test Workspace",
        "description": "Test workspace for integration tests"
    })
    
    # 2. Create board
    board = await server.create_board({
        "title": "Test Board",
        "workspace_id": workspace["data"]["id"],
        "create_default_columns": True
    })
    
    # 3. Create card
    card = await server.create_card({
        "title": "Test Task",
        "description": "Test task description",
        "board_id": board["data"]["id"],
        "column_id": "todo-column-id",  # Would need to get actual column ID
        "priority": 3
    })
    
    # 4. Move card
    await server.move_card({
        "card_id": card["data"]["id"],
        "column_id": "in-progress-column-id"
    })
    
    # 5. Verify state
    board_state = await server.get_board_state({
        "board_id": board["data"]["id"],
        "include_cards": True
    })
    
    assert len(board_state["data"]["columns"]) >= 3  # Default columns
    assert board_state["data"]["total_cards"] == 1
```

## Deployment

### 1. Docker Configuration

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY kanban_mcp_server.py .
COPY mcp_config.json .

EXPOSE 8000

CMD ["python", "kanban_mcp_server.py"]
```

### 2. Environment Variables

```bash
# .env file
KANBAN_API_URL=http://localhost:8000
KANBAN_API_KEY=your-secure-api-key
MCP_SERVER_PORT=8001
LOG_LEVEL=INFO
```

### 3. Production Considerations

- **Authentication**: Use secure API keys and rotate regularly
- **Rate Limiting**: Implement rate limiting for MCP tools
- **Logging**: Add comprehensive logging for debugging
- **Monitoring**: Add health checks and metrics
- **Security**: Validate all inputs and sanitize outputs

## Troubleshooting

### Common Issues

1. **API Connection Errors**
   - Check API URL and authentication
   - Verify network connectivity
   - Check API server status

2. **Tool Execution Errors**
   - Validate input schemas
   - Check required fields
   - Verify data types

3. **Performance Issues**
   - Implement caching for frequently accessed data
   - Use pagination for large datasets
   - Optimize API calls

### Debug Mode

Enable debug mode for detailed logging:

```python
import logging

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

This comprehensive guide provides everything needed to create a robust MCP server that wraps around the Kanban For Agents API, enabling AI agents to interact with Kanban boards programmatically.
