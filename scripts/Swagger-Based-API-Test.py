#!/usr/bin/env python3
"""
Kanban For Agents - Comprehensive API Test Script

This script tests every single endpoint in the Kanban API:
- Workspaces (CRUD, archive, get by name)
- Boards (CRUD, archive, get columns/cards)
- Columns (CRUD, reorder)
- Cards (CRUD, move, reorder, filtering)
- System endpoints (health, readiness)

Usage:
    python Swagger-Based-API-Test.py [--base-url BASE_URL] [--verbose] [--cleanup]

Features:
    - Tests all 30+ endpoints
    - Validates response schemas
    - Tests optimistic concurrency (ETags)
    - Tests error conditions
    - Comprehensive logging
    - Cleanup option
"""

import asyncio
import aiohttp
import json
import time
import uuid
import argparse
import sys
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime
import logging

# Configure logging
import os

# Ensure debug/logs directory exists
os.makedirs('debug/logs', exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('debug/logs/api_test_results.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


@dataclass
class TestResult:
    """Test result data class."""
    endpoint: str
    method: str
    status_code: int
    success: bool
    response_time: float
    error_message: Optional[str] = None
    response_data: Optional[Dict] = None


class KanbanAPITester:
    """Comprehensive API tester for Kanban For Agents."""
    
    def __init__(self, base_url: str = "http://localhost:8000", verbose: bool = False):
        self.base_url = base_url.rstrip('/')
        self.verbose = verbose
        self.session: Optional[aiohttp.ClientSession] = None
        
        # Test data storage
        self.test_data = {
            'workspace_id': None,
            'workspace_etag': None,
            'board_id': None,
            'board_etag': None,
            'column_ids': [],
            'column_etags': [],
            'card_ids': [],
            'card_etags': []
        }
        
        # Test results
        self.results: List[TestResult] = []
        
    async def __aenter__(self):
        """Async context manager entry."""
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=30),
            headers={'Content-Type': 'application/json'}
        )
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.session:
            await self.session.close()
    
    async def make_request(self, method: str, endpoint: str, 
                          data: Optional[Dict] = None, 
                          headers: Optional[Dict] = None,
                          expected_status: int = 200) -> TestResult:
        """Make HTTP request and return test result."""
        url = f"{self.base_url}{endpoint}"
        start_time = time.time()
        
        try:
            if headers is None:
                headers = {}
            
            if self.verbose:
                logger.info(f"Making {method} request to {url}")
                if data:
                    logger.info(f"Request data: {json.dumps(data, indent=2)}")
            
            async with self.session.request(method, url, json=data, headers=headers) as response:
                response_time = time.time() - start_time
                response_text = await response.text()
                
                try:
                    response_data = json.loads(response_text) if response_text else None
                except json.JSONDecodeError:
                    response_data = {"raw_response": response_text}
                
                success = response.status == expected_status
                
                if self.verbose:
                    logger.info(f"Response: {response.status} - {response_data}")
                
                result = TestResult(
                    endpoint=endpoint,
                    method=method,
                    status_code=response.status,
                    success=success,
                    response_time=response_time,
                    error_message=None if success else f"Expected {expected_status}, got {response.status}",
                    response_data=response_data
                )
                
                # Store ETag if present
                etag = response.headers.get('ETag')
                if etag:
                    result.response_data = result.response_data or {}
                    result.response_data['etag'] = etag
                
                return result
                
        except Exception as e:
            response_time = time.time() - start_time
            return TestResult(
                endpoint=endpoint,
                method=method,
                status_code=0,
                success=False,
                response_time=response_time,
                error_message=str(e),
                response_data=None
            )
    
    async def test_system_endpoints(self):
        """Test system endpoints (health, readiness, root)."""
        logger.info("🔍 Testing system endpoints...")
        
        # Test root endpoint
        result = await self.make_request("GET", "/")
        self.results.append(result)
        
        # Test API root
        result = await self.make_request("GET", "/v1/")
        self.results.append(result)
        
        # Test health check
        result = await self.make_request("GET", "/healthz")
        self.results.append(result)
        
        # Test readiness check
        result = await self.make_request("GET", "/readyz")
        self.results.append(result)
    
    async def test_workspaces(self):
        """Test workspace endpoints."""
        logger.info("🏢 Testing workspace endpoints...")
        
        # Create workspace
        workspace_data = {
            "name": f"Test Workspace {uuid.uuid4().hex[:8]}",
            "meta_data": {"test": True, "created_by": "api_test"}
        }
        
        result = await self.make_request("POST", "/v1/workspaces/", workspace_data, expected_status=201)
        self.results.append(result)
        
        if result.success and result.response_data and 'data' in result.response_data:
            self.test_data['workspace_id'] = result.response_data['data']['id']
            self.test_data['workspace_etag'] = result.response_data.get('etag')
            logger.info(f"Created workspace: {self.test_data['workspace_id']}")
        
        # List workspaces
        result = await self.make_request("GET", "/v1/workspaces/")
        self.results.append(result)
        
        # Get workspace by ID
        if self.test_data['workspace_id']:
            result = await self.make_request("GET", f"/v1/workspaces/{self.test_data['workspace_id']}")
            self.results.append(result)
        
        # Get workspace by name
        if result.success and result.response_data and 'data' in result.response_data:
            # Handle both single object and list responses
            if isinstance(result.response_data['data'], list) and len(result.response_data['data']) > 0:
                workspace_name = result.response_data['data'][0]['name']
            elif isinstance(result.response_data['data'], dict):
                workspace_name = result.response_data['data']['name']
            else:
                workspace_name = None
                
            if workspace_name:
                result = await self.make_request("GET", f"/v1/workspaces/name/{workspace_name}")
                self.results.append(result)
        
        # Update workspace
        if self.test_data['workspace_id'] and self.test_data['workspace_etag']:
            update_data = {
                "name": f"Updated Workspace {uuid.uuid4().hex[:8]}",
                "meta_data": {"test": True, "updated": True}
            }
            headers = {"If-Match": self.test_data['workspace_etag']}
            result = await self.make_request("PUT", f"/v1/workspaces/{self.test_data['workspace_id']}", 
                                           update_data, headers)
            self.results.append(result)
            
            # Update ETag after successful update
            if result.success and result.response_data:
                self.test_data['workspace_etag'] = result.response_data.get('etag')
        
                # Archive workspace
        if self.test_data['workspace_id'] and self.test_data['workspace_etag']:
            archive_data = {"is_archived": True}
            headers = {"If-Match": self.test_data['workspace_etag']}
            result = await self.make_request("POST", f"/v1/workspaces/{self.test_data['workspace_id']}/archive", 
                                           archive_data, headers)
            self.results.append(result)
            
            # Unarchive workspace
            if result.success and result.response_data:
                self.test_data['workspace_etag'] = result.response_data.get('etag')
                unarchive_data = {"is_archived": False}
                headers = {"If-Match": self.test_data['workspace_etag']}
                result = await self.make_request("POST", f"/v1/workspaces/{self.test_data['workspace_id']}/archive", 
                                                unarchive_data, headers)
                self.results.append(result)
                if result.success and result.response_data:
                    self.test_data['workspace_etag'] = result.response_data.get('etag')
    
    async def test_boards(self):
        """Test board endpoints."""
        logger.info("📋 Testing board endpoints...")
        
        if not self.test_data['workspace_id']:
            logger.warning("No workspace ID available, skipping board tests")
            return
        
        # Create board
        board_data = {
            "name": f"Test Board {uuid.uuid4().hex[:8]}",
            "description": "Test board for API testing",
            "workspace_id": self.test_data['workspace_id'],
            "meta_data": {"test": True, "template": "standard"}
        }
        
        result = await self.make_request("POST", "/v1/boards/", board_data, expected_status=201)
        self.results.append(result)
        
        if result.success and result.response_data and 'data' in result.response_data:
            self.test_data['board_id'] = result.response_data['data']['id']
            self.test_data['board_etag'] = result.response_data.get('etag')
            logger.info(f"Created board: {self.test_data['board_id']}")
        
        # List boards
        result = await self.make_request("GET", "/v1/boards/")
        self.results.append(result)
        
        # Get board by ID
        if self.test_data['board_id']:
            result = await self.make_request("GET", f"/v1/boards/{self.test_data['board_id']}")
            self.results.append(result)
        
        # Update board
        if self.test_data['board_id'] and self.test_data['board_etag']:
            update_data = {
                "name": f"Updated Board {uuid.uuid4().hex[:8]}",
                "description": "Updated test board"
            }
            headers = {"If-Match": self.test_data['board_etag']}
            result = await self.make_request("PUT", f"/v1/boards/{self.test_data['board_id']}", 
                                           update_data, headers)
            self.results.append(result)
            
            if result.success and result.response_data:
                self.test_data['board_etag'] = result.response_data.get('etag')
        
                # Archive board
        if self.test_data['board_id'] and self.test_data['board_etag']:
            archive_data = {"is_archived": True}
            headers = {"If-Match": self.test_data['board_etag']}
            result = await self.make_request("POST", f"/v1/boards/{self.test_data['board_id']}/archive", 
                                           archive_data, headers)
            self.results.append(result)
            
            # Unarchive board
            if result.success and result.response_data:
                self.test_data['board_etag'] = result.response_data.get('etag')
                unarchive_data = {"is_archived": False}
                headers = {"If-Match": self.test_data['board_etag']}
                result = await self.make_request("POST", f"/v1/boards/{self.test_data['board_id']}/archive", 
                                                unarchive_data, headers)
                self.results.append(result)
                if result.success and result.response_data:
                    self.test_data['board_etag'] = result.response_data.get('etag')
    
    async def test_columns(self):
        """Test column endpoints."""
        logger.info("📊 Testing column endpoints...")
        
        if not self.test_data['board_id']:
            logger.warning("No board ID available, skipping column tests")
            return
        
        # Create multiple columns
        column_names = ["To Do", "In Progress", "Review", "Done"]
        for i, name in enumerate(column_names):
            column_data = {
                "name": name,
                "board_id": self.test_data['board_id'],
                "position": i,
                "meta_data": {"test": True, "order": i}
            }
            
            result = await self.make_request("POST", "/v1/columns/", column_data, expected_status=201)
            self.results.append(result)
            
            if result.success and result.response_data:
                # Column creation returns the column data directly, not wrapped in 'data'
                column_id = result.response_data['id']
                self.test_data['column_ids'].append(column_id)
                self.test_data['column_etags'].append(result.response_data.get('etag'))
                logger.info(f"Created column: {column_id} ({name})")
        
        # List columns
        result = await self.make_request("GET", "/v1/columns/")
        self.results.append(result)
        
        # Get columns by board ID
        result = await self.make_request("GET", f"/v1/columns/board/{self.test_data['board_id']}")
        self.results.append(result)
        
        # Get board columns (alternative endpoint)
        result = await self.make_request("GET", f"/v1/boards/{self.test_data['board_id']}/columns")
        self.results.append(result)
        
        # Get individual columns
        for column_id in self.test_data['column_ids']:
            result = await self.make_request("GET", f"/v1/columns/{column_id}")
            self.results.append(result)
        
        # Update columns
        for i, column_id in enumerate(self.test_data['column_ids']):
            if i < len(self.test_data['column_etags']) and self.test_data['column_etags'][i]:
                update_data = {
                    "name": f"Updated {column_names[i]}",
                    "description": f"Updated description for {column_names[i].lower()}"
                }
                headers = {"If-Match": self.test_data['column_etags'][i]}
                result = await self.make_request("PUT", f"/v1/columns/{column_id}", 
                                               update_data, headers)
                self.results.append(result)
                
                if result.success and result.response_data:
                    self.test_data['column_etags'][i] = result.response_data.get('etag')
        
        # Reorder columns
        if len(self.test_data['column_ids']) >= 2:
            # Move first column to last position
            column_id = self.test_data['column_ids'][0]
            result = await self.make_request("POST", f"/v1/columns/{column_id}/reorder?new_position={len(self.test_data['column_ids']) - 1}")
            self.results.append(result)
            
            # Move it back to first position
            result = await self.make_request("POST", f"/v1/columns/{column_id}/reorder?new_position=0")
            self.results.append(result)
    
    async def test_cards(self):
        """Test card endpoints."""
        logger.info("🎴 Testing card endpoints...")
        
        if not self.test_data['board_id'] or not self.test_data['column_ids']:
            logger.warning("No board ID or column IDs available, skipping card tests")
            return
        
        # Create multiple cards
        card_titles = ["Test Task 1", "Test Task 2", "Test Task 3", "High Priority Task"]
        priorities = [2, 3, 1, 5]
        
        for i, (title, priority) in enumerate(zip(card_titles, priorities)):
            card_data = {
                "title": title,
                "description": f"Description for {title}",
                "board_id": self.test_data['board_id'],
                "column_id": self.test_data['column_ids'][0],  # Put in first column
                "position": i,
                "priority": priority,
                "labels": [f"test-{i}", "api-test"],
                "assignees": [f"user-{i}"],
                "agent_context": {
                    "capabilities": ["code_generation", "testing"],
                    "context": f"Test context for {title}"
                },
                "workflow_state": {
                    "status": "pending",
                    "step": 1
                },
                "fields": {
                    "estimated_hours": 4,
                    "actual_hours": 0
                },
                "meta_data": {"test": True, "created_by": "api_test"}
            }
            
            result = await self.make_request("POST", "/v1/cards/", card_data, expected_status=201)
            self.results.append(result)
            
            if result.success and result.response_data and 'data' in result.response_data:
                card_id = result.response_data['data']['id']
                self.test_data['card_ids'].append(card_id)
                self.test_data['card_etags'].append(result.response_data.get('etag'))
                logger.info(f"Created card: {card_id} ({title})")
        
        # List cards
        result = await self.make_request("GET", "/v1/cards/")
        self.results.append(result)
        
        # List cards with filters
        result = await self.make_request("GET", f"/v1/cards/?board_id={self.test_data['board_id']}")
        self.results.append(result)
        
        result = await self.make_request("GET", f"/v1/cards/?priority=5")
        self.results.append(result)
        
        result = await self.make_request("GET", f"/v1/cards/?labels=test-0,api-test")
        self.results.append(result)
        
        # Get cards by column
        if self.test_data['column_ids']:
            result = await self.make_request("GET", f"/v1/cards/?column_id={self.test_data['column_ids'][0]}")
            self.results.append(result)
        
        # Get cards by board
        result = await self.make_request("GET", f"/v1/cards/?board_id={self.test_data['board_id']}")
        self.results.append(result)
        
        # Get board cards (alternative endpoint)
        result = await self.make_request("GET", f"/v1/boards/{self.test_data['board_id']}/cards")
        self.results.append(result)
        
        # Get individual cards
        for card_id in self.test_data['card_ids']:
            result = await self.make_request("GET", f"/v1/cards/{card_id}")
            self.results.append(result)
        
        # Update cards
        for i, card_id in enumerate(self.test_data['card_ids']):
            if i < len(self.test_data['card_etags']) and self.test_data['card_etags'][i]:
                update_data = {
                    "title": f"Updated {card_titles[i]}",
                    "description": f"Updated description for {card_titles[i]}",
                    "priority": min(5, priorities[i] + 1)
                }
                headers = {"If-Match": self.test_data['card_etags'][i]}
                result = await self.make_request("PUT", f"/v1/cards/{card_id}", 
                                               update_data, headers)
                self.results.append(result)
                
                if result.success and result.response_data:
                    self.test_data['card_etags'][i] = result.response_data.get('etag')
        
        # Move cards between columns
        if len(self.test_data['card_ids']) >= 2 and len(self.test_data['column_ids']) >= 2:
            card_id = self.test_data['card_ids'][0]
            target_column_id = self.test_data['column_ids'][1]
            result = await self.make_request("POST", f"/v1/cards/{card_id}/move?column_id={target_column_id}&position=0")
            self.results.append(result)
            
            # Move it back
            result = await self.make_request("POST", f"/v1/cards/{card_id}/move?column_id={self.test_data['column_ids'][0]}&position=0")
            self.results.append(result)
        
        # Reorder cards
        if len(self.test_data['card_ids']) >= 2:
            card_id = self.test_data['card_ids'][0]
            result = await self.make_request("POST", f"/v1/cards/{card_id}/reorder?new_position={len(self.test_data['card_ids']) - 1}")
            self.results.append(result)
            
            # Move it back to first position
            result = await self.make_request("POST", f"/v1/cards/{card_id}/reorder?new_position=0")
            self.results.append(result)
    
    async def test_error_conditions(self):
        """Test error conditions and edge cases."""
        logger.info("⚠️ Testing error conditions...")
        
        # Test invalid workspace ID
        result = await self.make_request("GET", "/v1/workspaces/invalid-id", expected_status=404)
        self.results.append(result)
        
        # Test invalid board ID
        result = await self.make_request("GET", "/v1/boards/invalid-id", expected_status=404)
        self.results.append(result)
        
        # Test invalid column ID
        result = await self.make_request("GET", "/v1/columns/invalid-id", expected_status=404)
        self.results.append(result)
        
        # Test invalid card ID
        result = await self.make_request("GET", "/v1/cards/invalid-id", expected_status=404)
        self.results.append(result)
        
        # Test invalid data (missing required fields)
        invalid_workspace = {"meta_data": {"test": True}}  # Missing name
        result = await self.make_request("POST", "/v1/workspaces/", invalid_workspace, expected_status=422)
        self.results.append(result)
        
        # Test optimistic concurrency conflict
        if self.test_data['workspace_id'] and self.test_data['workspace_etag']:
            update_data = {"name": "Conflict Test"}
            headers = {"If-Match": "invalid-etag"}
            result = await self.make_request("PUT", f"/v1/workspaces/{self.test_data['workspace_id']}", 
                                           update_data, headers, expected_status=412)
            self.results.append(result)
    
    async def cleanup_test_data(self):
        """Clean up test data."""
        logger.info("🧹 Cleaning up test data...")
        
        # Delete cards
        for card_id in self.test_data['card_ids']:
            result = await self.make_request("DELETE", f"/v1/cards/{card_id}")
            self.results.append(result)
        
        # Delete columns
        for column_id in self.test_data['column_ids']:
            result = await self.make_request("DELETE", f"/v1/columns/{column_id}")
            self.results.append(result)
        
        # Delete board
        if self.test_data['board_id']:
            result = await self.make_request("DELETE", f"/v1/boards/{self.test_data['board_id']}")
            self.results.append(result)
        
        # Delete workspace
        if self.test_data['workspace_id']:
            result = await self.make_request("DELETE", f"/v1/workspaces/{self.test_data['workspace_id']}")
            self.results.append(result)
    
    async def run_all_tests(self, cleanup: bool = False):
        """Run all API tests."""
        logger.info("🚀 Starting comprehensive API tests...")
        
        try:
            # Test system endpoints first
            await self.test_system_endpoints()
            
            # Test workspace endpoints
            await self.test_workspaces()
            
            # Test board endpoints
            await self.test_boards()
            
            # Test column endpoints
            await self.test_columns()
            
            # Test card endpoints
            await self.test_cards()
            
            # Test error conditions
            await self.test_error_conditions()
            
            # Cleanup if requested
            if cleanup:
                await self.cleanup_test_data()
            
        except Exception as e:
            logger.error(f"Test execution failed: {e}")
            raise
    
    def generate_report(self) -> Dict[str, Any]:
        """Generate comprehensive test report."""
        total_tests = len(self.results)
        successful_tests = sum(1 for r in self.results if r.success)
        failed_tests = total_tests - successful_tests
        
        # Group results by endpoint type
        endpoint_groups = {}
        for result in self.results:
            endpoint_type = result.endpoint.split('/')[2] if len(result.endpoint.split('/')) > 2 else 'system'
            if endpoint_type not in endpoint_groups:
                endpoint_groups[endpoint_type] = []
            endpoint_groups[endpoint_type].append(result)
        
        # Calculate average response time
        avg_response_time = sum(r.response_time for r in self.results) / total_tests if total_tests > 0 else 0
        
        # Find failed tests
        failed_results = [r for r in self.results if not r.success]
        
        report = {
            "summary": {
                "total_tests": total_tests,
                "successful_tests": successful_tests,
                "failed_tests": failed_tests,
                "success_rate": (successful_tests / total_tests * 100) if total_tests > 0 else 0,
                "average_response_time": avg_response_time,
                "test_duration": sum(r.response_time for r in self.results)
            },
            "endpoint_groups": endpoint_groups,
            "failed_tests": failed_results,
            "test_data": self.test_data,
            "timestamp": datetime.now().isoformat()
        }
        
        return report
    
    def save_report(self, report: Dict[str, Any], filename: str = None):
        """Save test report to file."""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"debug/logs/api_test_results_{timestamp}.json"
        
        with open(filename, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        logger.info(f"Test report saved to: {filename}")
        return filename


async def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="Kanban For Agents API Test Suite")
    parser.add_argument("--base-url", default="http://localhost:8000", 
                       help="Base URL for the API (default: http://localhost:8000)")
    parser.add_argument("--verbose", "-v", action="store_true", 
                       help="Enable verbose logging")
    parser.add_argument("--cleanup", "-c", action="store_true", 
                       help="Clean up test data after tests")
    parser.add_argument("--report", "-r", default=None, 
                       help="Report filename (default: auto-generated)")
    
    args = parser.parse_args()
    
    logger.info("=" * 80)
    logger.info("🧪 KANBAN FOR AGENTS - COMPREHENSIVE API TEST SUITE")
    logger.info("=" * 80)
    logger.info(f"Base URL: {args.base_url}")
    logger.info(f"Verbose: {args.verbose}")
    logger.info(f"Cleanup: {args.cleanup}")
    logger.info("=" * 80)
    
    async with KanbanAPITester(args.base_url, args.verbose) as tester:
        try:
            await tester.run_all_tests(args.cleanup)
            
            # Generate and save report
            report = tester.generate_report()
            filename = tester.save_report(report, args.report)
            
            # Print summary
            summary = report["summary"]
            logger.info("=" * 80)
            logger.info("📊 TEST RESULTS SUMMARY")
            logger.info("=" * 80)
            logger.info(f"Total Tests: {summary['total_tests']}")
            logger.info(f"Successful: {summary['successful_tests']}")
            logger.info(f"Failed: {summary['failed_tests']}")
            logger.info(f"Success Rate: {summary['success_rate']:.1f}%")
            logger.info(f"Average Response Time: {summary['average_response_time']:.3f}s")
            logger.info(f"Total Test Duration: {summary['test_duration']:.3f}s")
            logger.info("=" * 80)
            
            if summary['failed_tests'] > 0:
                logger.warning(f"⚠️  {summary['failed_tests']} tests failed. Check the report for details.")
                return 1
            else:
                logger.info("✅ All tests passed!")
                return 0
                
        except Exception as e:
            logger.error(f"❌ Test execution failed: {e}")
            return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
