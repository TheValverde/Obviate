#!/usr/bin/env python3
"""
HTTP-based API Endpoint Testing Script

This script tests every API endpoint by making actual HTTP requests to the running API server.
It tests the complete stack including FastAPI routing, middleware, serialization, and database operations.

The script:
1. Creates a test workspace
2. Creates a test board (with default columns)
3. Creates test cards
4. Tests all CRUD operations for each entity
5. Tests card movement and reordering
6. Tests column reordering
7. Cleans up test data

Usage:
    # Start the API server first
    python start_dev.py
    
    # In another terminal, run the test script
    python debug/scripts/test_api_endpoints_http.py
"""

import asyncio
import sys
import os
import json
import httpx
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional

# Add the project root to the Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))


class HTTPAPITestRunner:
    """HTTP-based API endpoint test runner."""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.client = httpx.AsyncClient(timeout=30.0)
        self.test_data = {}
        self.results = {
            "passed": 0,
            "failed": 0,
            "tests": []
        }
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.aclose()
    
    def log_test(self, test_name: str, success: bool, details: str = "", error: str = ""):
        """Log a test result."""
        test_result = {
            "name": test_name,
            "success": success,
            "details": details,
            "error": error,
            "timestamp": datetime.now().isoformat()
        }
        self.results["tests"].append(test_result)
        
        if success:
            self.results["passed"] += 1
            print(f"✅ PASS: {test_name}")
            if details:
                print(f"   {details}")
        else:
            self.results["failed"] += 1
            print(f"❌ FAIL: {test_name}")
            if error:
                print(f"   Error: {error}")
            if details:
                print(f"   {details}")
        print()
    
    async def make_request(self, method: str, endpoint: str, data: Dict = None, expected_status: int = 200) -> Dict:
        """Make an HTTP request and return the response."""
        url = f"{self.base_url}/v1{endpoint}"
        
        try:
            if method.upper() == "GET":
                response = await self.client.get(url)
            elif method.upper() == "POST":
                response = await self.client.post(url, json=data)
            elif method.upper() == "PUT":
                response = await self.client.put(url, json=data)
            elif method.upper() == "DELETE":
                response = await self.client.delete(url)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            
            if response.status_code == expected_status:
                return response.json() if response.content else {}
            else:
                raise Exception(f"Expected status {expected_status}, got {response.status_code}: {response.text}")
                
        except Exception as e:
            raise Exception(f"Request failed: {str(e)}")
    
    async def test_api_root(self):
        """Test the API root endpoint."""
        print("=" * 60)
        print("TESTING API ROOT")
        print("=" * 60)
        
        try:
            response = await self.make_request("GET", "/")
            if response.get("message") == "Kanban For Agents API v1":
                self.log_test(
                    "API Root",
                    True,
                    f"API is running: {response.get('message')} v{response.get('version')}"
                )
            else:
                self.log_test("API Root", False, f"Unexpected response: {response}")
        except Exception as e:
            self.log_test("API Root", False, error=str(e))
    
    async def test_workspace_endpoints(self):
        """Test all workspace endpoints."""
        print("=" * 60)
        print("TESTING WORKSPACE ENDPOINTS")
        print("=" * 60)
        
        # Test 1: Create workspace
        try:
            workspace_data = {
                "name": "HTTP Test Workspace",
                "description": "Workspace for HTTP API testing"
            }
            response = await self.make_request("POST", "/workspaces/", workspace_data, 201)
            workspace = response.get("data", {})
            self.test_data["workspace_id"] = workspace.get("id")
            self.log_test(
                "Create Workspace",
                True,
                f"Created workspace '{workspace.get('name')}' with ID: {workspace.get('id')}"
            )
        except Exception as e:
            self.log_test("Create Workspace", False, error=str(e))
            return False
        
        # Test 2: Get workspace by ID
        try:
            response = await self.make_request("GET", f"/workspaces/{self.test_data['workspace_id']}")
            workspace = response.get("data", {})
            if workspace.get("id") == self.test_data["workspace_id"]:
                self.log_test(
                    "Get Workspace by ID",
                    True,
                    f"Retrieved workspace '{workspace.get('name')}'"
                )
            else:
                self.log_test("Get Workspace by ID", False, "Workspace not found or ID mismatch")
        except Exception as e:
            self.log_test("Get Workspace by ID", False, error=str(e))
        
        # Test 3: List workspaces
        try:
            response = await self.make_request("GET", "/workspaces/")
            workspaces = response.get("data", {}).get("items", [])
            if len(workspaces) > 0:
                self.log_test(
                    "List Workspaces",
                    True,
                    f"Found {len(workspaces)} workspaces"
                )
            else:
                self.log_test("List Workspaces", False, "No workspaces found")
        except Exception as e:
            self.log_test("List Workspaces", False, error=str(e))
        
        # Test 4: Update workspace
        try:
            update_data = {
                "name": "Updated HTTP Test Workspace",
                "description": "Updated description for HTTP API testing"
            }
            response = await self.make_request("PUT", f"/workspaces/{self.test_data['workspace_id']}", update_data)
            workspace = response.get("data", {})
            if workspace.get("name") == "Updated HTTP Test Workspace":
                self.log_test(
                    "Update Workspace",
                    True,
                    f"Updated workspace name to '{workspace.get('name')}'"
                )
            else:
                self.log_test("Update Workspace", False, "Workspace name not updated correctly")
        except Exception as e:
            self.log_test("Update Workspace", False, error=str(e))
        
        return True
    
    async def test_board_endpoints(self):
        """Test all board endpoints."""
        print("=" * 60)
        print("TESTING BOARD ENDPOINTS")
        print("=" * 60)
        
        # Test 1: Create board (should create default columns)
        try:
            board_data = {
                "name": "HTTP Test Board",
                "description": "Board for HTTP API testing",
                "workspace_id": self.test_data["workspace_id"]
            }
            response = await self.make_request("POST", "/boards/", board_data, 201)
            board = response.get("data", {})
            self.test_data["board_id"] = board.get("id")
            self.log_test(
                "Create Board",
                True,
                f"Created board '{board.get('name')}' with ID: {board.get('id')}"
            )
        except Exception as e:
            self.log_test("Create Board", False, error=str(e))
            return False
        
        # Test 2: Get board by ID
        try:
            response = await self.make_request("GET", f"/boards/{self.test_data['board_id']}")
            board = response.get("data", {})
            if board.get("id") == self.test_data["board_id"]:
                self.log_test(
                    "Get Board by ID",
                    True,
                    f"Retrieved board '{board.get('name')}'"
                )
            else:
                self.log_test("Get Board by ID", False, "Board not found or ID mismatch")
        except Exception as e:
            self.log_test("Get Board by ID", False, error=str(e))
        
        # Test 3: List boards
        try:
            response = await self.make_request("GET", "/boards/")
            boards = response.get("data", {}).get("items", [])
            if len(boards) > 0:
                self.log_test(
                    "List Boards",
                    True,
                    f"Found {len(boards)} boards"
                )
            else:
                self.log_test("List Boards", False, "No boards found")
        except Exception as e:
            self.log_test("List Boards", False, error=str(e))
        
        # Test 4: Update board
        try:
            update_data = {
                "name": "Updated HTTP Test Board",
                "description": "Updated description for HTTP API testing"
            }
            response = await self.make_request("PUT", f"/boards/{self.test_data['board_id']}", update_data)
            board = response.get("data", {})
            if board.get("name") == "Updated HTTP Test Board":
                self.log_test(
                    "Update Board",
                    True,
                    f"Updated board name to '{board.get('name')}'"
                )
            else:
                self.log_test("Update Board", False, "Board name not updated correctly")
        except Exception as e:
            self.log_test("Update Board", False, error=str(e))
        
        # Test 5: Get board columns
        try:
            response = await self.make_request("GET", f"/columns/?board_id={self.test_data['board_id']}")
            columns = response.get("data", {}).get("items", [])
            if len(columns) >= 3:  # Should have at least 3 default columns
                self.log_test(
                    "Get Board Columns",
                    True,
                    f"Found {len(columns)} columns: {[col.get('name') for col in columns]}"
                )
                # Store column IDs for later tests
                for col in columns:
                    if col.get("name") == "To Do":
                        self.test_data["todo_column_id"] = col.get("id")
                    elif col.get("name") == "In Progress":
                        self.test_data["in_progress_column_id"] = col.get("id")
                    elif col.get("name") == "Done":
                        self.test_data["done_column_id"] = col.get("id")
            else:
                self.log_test("Get Board Columns", False, f"Expected at least 3 columns, got {len(columns)}")
        except Exception as e:
            self.log_test("Get Board Columns", False, error=str(e))
        
        return True
    
    async def test_column_endpoints(self):
        """Test all column endpoints."""
        print("=" * 60)
        print("TESTING COLUMN ENDPOINTS")
        print("=" * 60)
        
        # Test 1: Create new column
        try:
            column_data = {
                "name": "Test Column",
                "description": "Test column for HTTP API testing",
                "board_id": self.test_data["board_id"],
                "position": 3,
                "wip_limit": 3
            }
            response = await self.make_request("POST", "/columns/", column_data, 201)
            column = response.get("data", {})
            self.test_data["test_column_id"] = column.get("id")
            self.log_test(
                "Create Column",
                True,
                f"Created column '{column.get('name')}' with ID: {column.get('id')}"
            )
        except Exception as e:
            self.log_test("Create Column", False, error=str(e))
            return False
        
        # Test 2: Get column by ID
        try:
            response = await self.make_request("GET", f"/columns/{self.test_data['test_column_id']}")
            column = response.get("data", {})
            if column.get("id") == self.test_data["test_column_id"]:
                self.log_test(
                    "Get Column by ID",
                    True,
                    f"Retrieved column '{column.get('name')}'"
                )
            else:
                self.log_test("Get Column by ID", False, "Column not found or ID mismatch")
        except Exception as e:
            self.log_test("Get Column by ID", False, error=str(e))
        
        # Test 3: List columns
        try:
            response = await self.make_request("GET", "/columns/")
            columns = response.get("data", {}).get("items", [])
            if len(columns) > 0:
                self.log_test(
                    "List Columns",
                    True,
                    f"Found {len(columns)} columns"
                )
            else:
                self.log_test("List Columns", False, "No columns found")
        except Exception as e:
            self.log_test("List Columns", False, error=str(e))
        
        # Test 4: Update column
        try:
            update_data = {
                "name": "Updated Test Column",
                "description": "Updated description for HTTP API testing",
                "wip_limit": 5
            }
            response = await self.make_request("PUT", f"/columns/{self.test_data['test_column_id']}", update_data)
            column = response.get("data", {})
            if column.get("name") == "Updated Test Column" and column.get("wip_limit") == 5:
                self.log_test(
                    "Update Column",
                    True,
                    f"Updated column name to '{column.get('name')}' and WIP limit to {column.get('wip_limit')}"
                )
            else:
                self.log_test("Update Column", False, "Column not updated correctly")
        except Exception as e:
            self.log_test("Update Column", False, error=str(e))
        
        # Test 5: Reorder column
        try:
            reorder_data = {"new_position": 1}
            response = await self.make_request("POST", f"/columns/{self.test_data['test_column_id']}/reorder", reorder_data)
            column = response.get("data", {})
            if column.get("position") == 1:
                self.log_test(
                    "Reorder Column",
                    True,
                    f"Moved column to position {column.get('position')}"
                )
            else:
                self.log_test("Reorder Column", False, f"Expected position 1, got {column.get('position')}")
        except Exception as e:
            self.log_test("Reorder Column", False, error=str(e))
        
        return True
    
    async def test_card_endpoints(self):
        """Test all card endpoints."""
        print("=" * 60)
        print("TESTING CARD ENDPOINTS")
        print("=" * 60)
        
        # Test 1: Create card
        try:
            card_data = {
                "title": "Test Card",
                "description": "Test card for HTTP API testing",
                "board_id": self.test_data["board_id"],
                "column_id": self.test_data["todo_column_id"],
                "priority": 3,
                "labels": ["test", "api"],
                "assignees": ["test@example.com"]
            }
            response = await self.make_request("POST", "/cards/", card_data, 201)
            card = response.get("data", {})
            self.test_data["test_card_id"] = card.get("id")
            self.log_test(
                "Create Card",
                True,
                f"Created card '{card.get('title')}' with ID: {card.get('id')}"
            )
        except Exception as e:
            self.log_test("Create Card", False, error=str(e))
            return False
        
        # Test 2: Get card by ID
        try:
            response = await self.make_request("GET", f"/cards/{self.test_data['test_card_id']}")
            card = response.get("data", {})
            if card.get("id") == self.test_data["test_card_id"]:
                self.log_test(
                    "Get Card by ID",
                    True,
                    f"Retrieved card '{card.get('title')}'"
                )
            else:
                self.log_test("Get Card by ID", False, "Card not found or ID mismatch")
        except Exception as e:
            self.log_test("Get Card by ID", False, error=str(e))
        
        # Test 3: List cards
        try:
            response = await self.make_request("GET", "/cards/")
            cards = response.get("data", {}).get("items", [])
            if len(cards) > 0:
                self.log_test(
                    "List Cards",
                    True,
                    f"Found {len(cards)} cards"
                )
            else:
                self.log_test("List Cards", False, "No cards found")
        except Exception as e:
            self.log_test("List Cards", False, error=str(e))
        
        # Test 4: Update card
        try:
            update_data = {
                "title": "Updated Test Card",
                "description": "Updated description for HTTP API testing",
                "priority": 4,
                "labels": ["test", "api", "updated"]
            }
            response = await self.make_request("PUT", f"/cards/{self.test_data['test_card_id']}", update_data)
            card = response.get("data", {})
            if card.get("title") == "Updated Test Card" and card.get("priority") == 4:
                self.log_test(
                    "Update Card",
                    True,
                    f"Updated card title to '{card.get('title')}' and priority to {card.get('priority')}"
                )
            else:
                self.log_test("Update Card", False, "Card not updated correctly")
        except Exception as e:
            self.log_test("Update Card", False, error=str(e))
        
        # Test 5: Move card
        try:
            move_data = {"column_id": self.test_data["in_progress_column_id"]}
            response = await self.make_request("POST", f"/cards/{self.test_data['test_card_id']}/move", move_data)
            card = response.get("data", {})
            if card.get("column_id") == self.test_data["in_progress_column_id"]:
                self.log_test(
                    "Move Card",
                    True,
                    f"Moved card to column ID: {card.get('column_id')}"
                )
            else:
                self.log_test("Move Card", False, f"Expected column ID {self.test_data['in_progress_column_id']}, got {card.get('column_id')}")
        except Exception as e:
            self.log_test("Move Card", False, error=str(e))
        
        # Test 6: Reorder card
        try:
            reorder_data = {"new_position": 0}
            response = await self.make_request("POST", f"/cards/{self.test_data['test_card_id']}/reorder", reorder_data)
            card = response.get("data", {})
            if card.get("position") == 0:
                self.log_test(
                    "Reorder Card",
                    True,
                    f"Moved card to position {card.get('position')}"
                )
            else:
                self.log_test("Reorder Card", False, f"Expected position 0, got {card.get('position')}")
        except Exception as e:
            self.log_test("Reorder Card", False, error=str(e))
        
        # Test 7: Move card to Done
        try:
            move_data = {"column_id": self.test_data["done_column_id"]}
            response = await self.make_request("POST", f"/cards/{self.test_data['test_card_id']}/move", move_data)
            card = response.get("data", {})
            if card.get("column_id") == self.test_data["done_column_id"]:
                self.log_test(
                    "Move Card to Done",
                    True,
                    f"Moved card to Done column"
                )
            else:
                self.log_test("Move Card to Done", False, f"Expected Done column, got {card.get('column_id')}")
        except Exception as e:
            self.log_test("Move Card to Done", False, error=str(e))
        
        return True
    
    async def cleanup_test_data(self):
        """Clean up test data."""
        print("=" * 60)
        print("CLEANING UP TEST DATA")
        print("=" * 60)
        
        try:
            if "workspace_id" in self.test_data:
                # This will cascade delete boards, columns, and cards
                await self.make_request("DELETE", f"/workspaces/{self.test_data['workspace_id']}")
                self.log_test(
                    "Cleanup Test Data",
                    True,
                    f"Deleted test workspace and all associated data"
                )
        except Exception as e:
            self.log_test("Cleanup Test Data", False, error=str(e))
    
    def print_summary(self):
        """Print test summary."""
        print("=" * 60)
        print("TEST SUMMARY")
        print("=" * 60)
        total_tests = self.results['passed'] + self.results['failed']
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {self.results['passed']}")
        print(f"Failed: {self.results['failed']}")
        if total_tests > 0:
            success_rate = (self.results['passed'] / total_tests * 100)
            print(f"Success Rate: {success_rate:.1f}%")
        
        if self.results['failed'] > 0:
            print("\nFailed Tests:")
            for test in self.results['tests']:
                if not test['success']:
                    print(f"  - {test['name']}: {test['error']}")
        
        # Save results to file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        results_file = f"debug/logs/http_api_test_results_{timestamp}.json"
        os.makedirs(os.path.dirname(results_file), exist_ok=True)
        
        with open(results_file, 'w') as f:
            json.dump(self.results, f, indent=2)
        
        print(f"\nDetailed results saved to: {results_file}")


async def main():
    """Main test function."""
    print("=" * 80)
    print("HTTP-BASED API ENDPOINT TESTING")
    print("=" * 80)
    print(f"Started at: {datetime.now().isoformat()}")
    print("Make sure the API server is running on http://localhost:8000")
    print()
    
    async with HTTPAPITestRunner() as test_runner:
        try:
            # Test all endpoint categories
            await test_runner.test_api_root()
            await test_runner.test_workspace_endpoints()
            await test_runner.test_board_endpoints()
            await test_runner.test_column_endpoints()
            await test_runner.test_card_endpoints()
            
            # Clean up test data
            await test_runner.cleanup_test_data()
            
        except Exception as e:
            print(f"❌ CRITICAL ERROR: {str(e)}")
            import traceback
            traceback.print_exc()
        
        finally:
            # Print summary
            test_runner.print_summary()


if __name__ == "__main__":
    asyncio.run(main())
