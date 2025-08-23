"""
API v1 endpoints package.

This package contains all API v1 endpoint modules for the Kanban For Agents API.
"""

# Import endpoint modules
from . import workspace, board

__all__ = ["workspace", "board"]
