#!/usr/bin/env python3
"""
Kanban For Agents - Development Startup Script

This script sets up and starts the development environment for the Kanban For Agents project.
It handles virtual environment setup, Docker services, and provides easy access to common development tasks.

Usage:
    python start_dev.py [command]

Commands:
    start       - Start the development environment (default)
    stop        - Stop all development services
    restart     - Restart all development services
    logs        - Show logs from all services
    shell       - Open a shell in the FastAPI container
    db          - Open a PostgreSQL shell
    migrate     - Run database migrations
    test        - Run tests
    clean       - Clean up Docker resources
    help        - Show this help message
"""

import os
import sys
import subprocess
import argparse
import time
from pathlib import Path
from typing import List, Optional


class DevEnvironment:
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.docker_compose_file = self.project_root / "docker-compose.yml"
        self.env_file = self.project_root / ".env"
        self.venv_path = self.project_root / ".venv"
        
    def check_prerequisites(self) -> bool:
        """Check if required tools are installed."""
        print("🔍 Checking prerequisites...")
        
        # Check Docker
        try:
            subprocess.run(["docker", "--version"], check=True, capture_output=True)
            print("✅ Docker is installed")
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("❌ Docker is not installed or not in PATH")
            return False
            
        # Check Docker Compose
        try:
            subprocess.run(["docker-compose", "--version"], check=True, capture_output=True)
            print("✅ Docker Compose is installed")
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("❌ Docker Compose is not installed or not in PATH")
            return False
            
        # Check Python
        if sys.version_info < (3, 8):
            print("❌ Python 3.8+ is required")
            return False
        print("✅ Python version is compatible")
        
        return True
    
    def setup_environment(self):
        """Set up the development environment."""
        print("🔧 Setting up development environment...")
        
        # Create .env file if it doesn't exist
        if not self.env_file.exists():
            env_example = self.project_root / ".env.example"
            if env_example.exists():
                print("📝 Creating .env file from .env.example...")
                subprocess.run(["cp", str(env_example), str(self.env_file)])
            else:
                print("⚠️  No .env.example found, creating basic .env...")
                self.create_basic_env()
        
        # Create virtual environment if it doesn't exist
        if not self.venv_path.exists():
            print("🐍 Creating virtual environment...")
            subprocess.run([sys.executable, "-m", "venv", str(self.venv_path)])
        
        # Install dependencies
        print("📦 Installing dependencies...")
        pip_path = self.venv_path / "bin" / "pip" if os.name != "nt" else self.venv_path / "Scripts" / "pip.exe"
        requirements_file = self.project_root / "requirements.txt"
        
        if requirements_file.exists():
            subprocess.run([str(pip_path), "install", "-r", str(requirements_file)])
        else:
            print("⚠️  No requirements.txt found, installing basic dependencies...")
            subprocess.run([str(pip_path), "install", "fastapi", "uvicorn", "sqlalchemy", "asyncpg", "alembic", "pydantic"])
    
    def create_basic_env(self):
        """Create a basic .env file with development defaults."""
        env_content = """# Kanban For Agents - Development Environment

# Database
DATABASE_DSN=postgresql+asyncpg://kanban:kanban@localhost:5432/kanban_dev

# Service Tokens (for development)
SERVICE_TOKENS_SEED=dev:devtoken123|read,write

# Application Settings
DEBUG=true
LOG_LEVEL=DEBUG
HOST=0.0.0.0
PORT=8080

# Docker Settings
POSTGRES_USER=kanban
POSTGRES_PASSWORD=kanban
POSTGRES_DB=kanban_dev
POSTGRES_HOST=postgres
POSTGRES_PORT=5432
"""
        with open(self.env_file, 'w') as f:
            f.write(env_content)
    
    def run_docker_compose(self, command: List[str], check: bool = True) -> subprocess.CompletedProcess:
        """Run docker-compose command."""
        cmd = ["docker-compose", "-f", str(self.docker_compose_file)] + command
        return subprocess.run(cmd, cwd=self.project_root, check=check)
    
    def start_services(self):
        """Start all development services."""
        print("🚀 Starting development services...")
        
        # Build and start services
        try:
            self.run_docker_compose(["build"])
            self.run_docker_compose(["up", "-d"])
            
            # Wait for services to be ready
            print("⏳ Waiting for services to be ready...")
            time.sleep(5)
            
            # Check service health
            self.check_service_health()
            
            print("✅ Development environment is ready!")
            print("\n📋 Available endpoints:")
            print("   • FastAPI: http://localhost:8080")
            print("   • API Docs: http://localhost:8080/docs")
            print("   • Health Check: http://localhost:8080/healthz")
            print("\n🔑 Default token: devtoken123")
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to start services: {e}")
            sys.exit(1)
    
    def check_service_health(self):
        """Check if services are healthy."""
        print("🏥 Checking service health...")
        
        # Check PostgreSQL
        try:
            result = self.run_docker_compose(["exec", "-T", "postgres", "pg_isready", "-U", "kanban"], check=False)
            if result.returncode == 0:
                print("✅ PostgreSQL is ready")
            else:
                print("⚠️  PostgreSQL is not ready yet")
        except Exception:
            print("⚠️  Could not check PostgreSQL health")
        
        # Check FastAPI
        try:
            import requests
            response = requests.get("http://localhost:8080/healthz", timeout=5)
            if response.status_code == 200:
                print("✅ FastAPI is ready")
            else:
                print("⚠️  FastAPI is not ready yet")
        except Exception:
            print("⚠️  Could not check FastAPI health")
    
    def stop_services(self):
        """Stop all development services."""
        print("🛑 Stopping development services...")
        self.run_docker_compose(["down"])
        print("✅ Services stopped")
    
    def restart_services(self):
        """Restart all development services."""
        print("🔄 Restarting development services...")
        self.stop_services()
        time.sleep(2)
        self.start_services()
    
    def show_logs(self):
        """Show logs from all services."""
        print("📋 Showing service logs...")
        self.run_docker_compose(["logs", "-f"], check=False)
    
    def open_shell(self):
        """Open a shell in the FastAPI container."""
        print("🐚 Opening shell in FastAPI container...")
        self.run_docker_compose(["exec", "app", "bash"], check=False)
    
    def open_db_shell(self):
        """Open a PostgreSQL shell."""
        print("🗄️  Opening PostgreSQL shell...")
        self.run_docker_compose(["exec", "postgres", "psql", "-U", "kanban", "-d", "kanban_dev"], check=False)
    
    def run_migrations(self):
        """Run database migrations."""
        print("🔄 Running database migrations...")
        try:
            self.run_docker_compose(["exec", "app", "alembic", "upgrade", "head"])
            print("✅ Migrations completed")
        except subprocess.CalledProcessError as e:
            print(f"❌ Migration failed: {e}")
    
    def run_tests(self):
        """Run tests."""
        print("🧪 Running tests...")
        try:
            self.run_docker_compose(["exec", "app", "pytest", "-v"])
        except subprocess.CalledProcessError as e:
            print(f"❌ Tests failed: {e}")
    
    def clean_up(self):
        """Clean up Docker resources."""
        print("🧹 Cleaning up Docker resources...")
        self.run_docker_compose(["down", "-v", "--remove-orphans"])
        print("✅ Cleanup completed")


def main():
    parser = argparse.ArgumentParser(description="Kanban For Agents Development Environment")
    parser.add_argument("command", nargs="?", default="start", 
                       choices=["start", "stop", "restart", "logs", "shell", "db", "migrate", "test", "clean", "help"],
                       help="Command to run")
    
    args = parser.parse_args()
    
    if args.command == "help":
        print(__doc__)
        return
    
    dev_env = DevEnvironment()
    
    # Check prerequisites
    if not dev_env.check_prerequisites():
        sys.exit(1)
    
    # Handle commands
    if args.command == "start":
        dev_env.setup_environment()
        dev_env.start_services()
    elif args.command == "stop":
        dev_env.stop_services()
    elif args.command == "restart":
        dev_env.restart_services()
    elif args.command == "logs":
        dev_env.show_logs()
    elif args.command == "shell":
        dev_env.open_shell()
    elif args.command == "db":
        dev_env.open_db_shell()
    elif args.command == "migrate":
        dev_env.run_migrations()
    elif args.command == "test":
        dev_env.run_tests()
    elif args.command == "clean":
        dev_env.clean_up()


if __name__ == "__main__":
    main()
