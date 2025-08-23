#!/usr/bin/env python3
"""
Debug script for testing FastAPI endpoints.

Tests API endpoints directly using FastAPI TestClient.
"""

import asyncio
import logging
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from fastapi.testclient import TestClient

from app.main import app
from app.core.database import init_db

# Set up logging
def setup_logging(script_name: str) -> logging.Logger:
    """Set up logging with file and console output."""
    
    # Create logs directory if it doesn't exist
    logs_dir = project_root / "debug" / "logs"
    logs_dir.mkdir(parents=True, exist_ok=True)
    
    # Create timestamped log file
    from datetime import datetime
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = logs_dir / f"{script_name}_{timestamp}.log"
    
    # Configure logging
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    logger = logging.getLogger(script_name)
    logger.info(f"Debug script started: {script_name}")
    logger.info(f"Log file: {log_file}")
    
    return logger

async def debug_api_endpoints():
    """Debug API endpoints step by step."""
    
    logger = setup_logging("debug_api_endpoints")
    
    try:
        # Initialize database
        logger.info("Initializing database...")
        await init_db()
        logger.info("Database initialized successfully")
        
        # Create test client
        client = TestClient(app)
        logger.info("FastAPI TestClient created successfully")
        
        # Test 1: Health check endpoint
        logger.info("Test 1: Testing health check endpoint...")
        try:
            response = client.get("/health")
            logger.info(f"Health check status: {response.status_code}")
            if response.status_code == 200:
                logger.info("SUCCESS: Health check endpoint working!")
            else:
                logger.error(f"FAILED: Health check failed: {response.text}")
        except Exception as e:
            logger.error(f"Health check test failed: {e}")
        
        # Test 2: Column list endpoint
        logger.info("Test 2: Testing column list endpoint...")
        try:
            response = client.get("/v1/columns/")
            logger.info(f"Column list status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                logger.info("SUCCESS: Column list endpoint working!")
                logger.info(f"Found {len(data.get('data', []))} columns")
                logger.info(f"Pagination: {data.get('pagination', {})}")
            else:
                logger.error(f"FAILED: Column list failed: {response.text}")
        except Exception as e:
            logger.error(f"Column list test failed: {e}")
            import traceback
            logger.error(traceback.format_exc())
        
        # Test 3: Board list endpoint
        logger.info("Test 3: Testing board list endpoint...")
        try:
            response = client.get("/v1/boards/")
            logger.info(f"Board list status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                logger.info("SUCCESS: Board list endpoint working!")
                logger.info(f"Found {len(data.get('data', []))} boards")
            else:
                logger.error(f"FAILED: Board list failed: {response.text}")
        except Exception as e:
            logger.error(f"Board list test failed: {e}")
        
        # Test 4: Workspace list endpoint
        logger.info("Test 4: Testing workspace list endpoint...")
        try:
            response = client.get("/v1/workspaces/")
            logger.info(f"Workspace list status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                logger.info("SUCCESS: Workspace list endpoint working!")
                logger.info(f"Found {len(data.get('data', []))} workspaces")
            else:
                logger.error(f"FAILED: Workspace list failed: {response.text}")
        except Exception as e:
            logger.error(f"Workspace list test failed: {e}")
        
        # Test 5: API documentation
        logger.info("Test 5: Testing API documentation...")
        try:
            response = client.get("/docs")
            logger.info(f"API docs status: {response.status_code}")
            
            if response.status_code == 200:
                logger.info("SUCCESS: API documentation accessible!")
            else:
                logger.error(f"FAILED: API docs failed: {response.text}")
        except Exception as e:
            logger.error(f"API docs test failed: {e}")
            
        logger.info("SUCCESS: All API endpoint tests completed!")
            
    except Exception as e:
        logger.error(f"Debug failed: {e}")
        import traceback
        logger.error(traceback.format_exc())

if __name__ == "__main__":
    asyncio.run(debug_api_endpoints())
