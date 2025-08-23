#!/usr/bin/env python3
"""
Kanban For Agents - Development Startup Script

This script automatically sets up and starts the complete development environment:
1. Checks if Docker is running
2. Starts PostgreSQL database if not running
3. Runs database migrations
4. Starts FastAPI server
5. Opens browser to API docs

Usage:
    python start_dev.py [command]

Commands:
    start       - Start the complete development environment (default)
    stop        - Stop all services
    restart     - Restart all services
    status      - Check status of all services
    logs        - Show logs
    db          - Open database shell
    clean       - Clean up everything
    help        - Show this help message
"""

import os
import sys
import subprocess
import argparse
import time
import requests
import webbrowser
from pathlib import Path
from typing import List, Optional, Dict, Any


class DevEnvironment:
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.docker_compose_file = self.project_root / "docker-compose.yml"
        self.env_file = self.project_root / ".env"
        self.venv_path = self.project_root / "venv"
        
        # Service URLs
        self.fastapi_url = "http://localhost:8000"
        self.api_docs_url = "http://localhost:8000/docs"
        self.db_url = "postgresql://kanban:kanban@localhost:5432/kanban_dev"
        
    def print_banner(self):
        """Print startup banner."""
        print("=" * 80)
        print("🚀 KANBAN FOR AGENTS - DEVELOPMENT ENVIRONMENT")
        print("=" * 80)
        print(f"📁 Project: {self.project_root}")
        print(f"🐍 Python: {sys.version}")
        print("=" * 80)
    
    def check_prerequisites(self) -> bool:
        """Check if required tools are installed."""
        print("🔍 Checking prerequisites...")
        
        # Check Docker
        try:
            result = subprocess.run(["docker", "--version"], 
                                  capture_output=True, text=True, check=True)
            print(f"✅ Docker: {result.stdout.strip()}")
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("❌ Docker is not installed or not in PATH")
            print("   Please install Docker Desktop: https://www.docker.com/products/docker-desktop")
            return False
            
        # Check Docker Compose
        try:
            result = subprocess.run(["docker-compose", "--version"], 
                                  capture_output=True, text=True, check=True)
            print(f"✅ Docker Compose: {result.stdout.strip()}")
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("❌ Docker Compose is not installed or not in PATH")
            return False
            
        # Check if Docker daemon is running
        try:
            subprocess.run(["docker", "info"], capture_output=True, check=True)
            print("✅ Docker daemon is running")
        except subprocess.CalledProcessError:
            print("❌ Docker daemon is not running")
            print("   Please start Docker Desktop")
            return False
        
        return True
    
    def setup_environment(self):
        """Set up the development environment."""
        print("🔧 Setting up development environment...")
        
        # Create .env file if it doesn't exist
        if not self.env_file.exists():
            print("📝 Creating .env file...")
            self.create_env_file()
        
        # Create virtual environment if it doesn't exist
        if not self.venv_path.exists():
            print("🐍 Creating virtual environment...")
            subprocess.run([sys.executable, "-m", "venv", str(self.venv_path)], check=True)
        
        # Install dependencies
        print("📦 Installing dependencies...")
        self.install_dependencies()
    
    def create_env_file(self):
        """Create a .env file with development defaults."""
        env_content = """# Kanban For Agents - Development Environment

# Database
DATABASE_URL=postgresql://kanban:kanban@localhost:5432/kanban_dev
DATABASE_DSN=postgresql+asyncpg://kanban:kanban@localhost:5432/kanban_dev

# Application Settings
DEBUG=true
LOG_LEVEL=DEBUG
HOST=0.0.0.0
PORT=8000

# Docker Settings
POSTGRES_USER=kanban
POSTGRES_PASSWORD=kanban
POSTGRES_DB=kanban_dev
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
"""
        with open(self.env_file, 'w') as f:
            f.write(env_content)
        print("✅ Created .env file")
    
    def install_dependencies(self):
        """Install Python dependencies."""
        pip_path = self.venv_path / "Scripts" / "pip.exe" if os.name == "nt" else self.venv_path / "bin" / "pip"
        
        # Check if requirements.txt exists
        requirements_file = self.project_root / "requirements.txt"
        if requirements_file.exists():
            print("📦 Installing from requirements.txt...")
            subprocess.run([str(pip_path), "install", "-r", str(requirements_file)], check=True)
        else:
            print("📦 Installing basic dependencies...")
            basic_deps = [
                "fastapi", "uvicorn[standard]", "sqlalchemy[asyncio]", 
                "asyncpg", "alembic", "pydantic", "python-dotenv",
                "httpx", "pytest", "pytest-asyncio"
            ]
            subprocess.run([str(pip_path), "install"] + basic_deps, check=True)
        
        print("✅ Dependencies installed")
    
    def run_docker_compose(self, command: List[str], check: bool = True) -> subprocess.CompletedProcess:
        """Run docker-compose command."""
        cmd = ["docker-compose", "-f", str(self.docker_compose_file)] + command
        return subprocess.run(cmd, cwd=self.project_root, check=check)
    
    def check_database_status(self) -> bool:
        """Check if PostgreSQL database is running."""
        try:
            result = subprocess.run(["docker", "ps", "--filter", "name=kanban-postgres", "--format", "{{.Status}}"], 
                                  capture_output=True, text=True, check=True)
            return "Up" in result.stdout
        except subprocess.CalledProcessError:
            return False
    
    def start_database(self):
        """Start PostgreSQL database."""
        print("🗄️  Starting PostgreSQL database...")
        
        if self.check_database_status():
            print("✅ Database is already running")
            return
        
        try:
            # Start database
            self.run_docker_compose(["up", "-d", "postgres"])
            
            # Wait for database to be ready
            print("⏳ Waiting for database to be ready...")
            for i in range(30):  # Wait up to 30 seconds
                try:
                    result = subprocess.run(
                        ["docker", "exec", "kanban-postgres", "pg_isready", "-U", "kanban"],
                        capture_output=True, text=True, check=False
                    )
                    if result.returncode == 0:
                        print("✅ Database is ready")
                        return
                except subprocess.CalledProcessError:
                    pass
                time.sleep(1)
                print(f"   Waiting... ({i+1}/30)")
            
            print("❌ Database failed to start within 30 seconds")
            raise Exception("Database startup timeout")
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to start database: {e}")
            raise
    
    def run_migrations(self):
        """Run database migrations."""
        print("🔄 Running database migrations...")
        
        try:
            # Activate virtual environment and run migrations
            python_path = self.venv_path / "Scripts" / "python.exe" if os.name == "nt" else self.venv_path / "bin" / "python"
            
            # Initialize database if needed
            subprocess.run([str(python_path), "-m", "app.core.database", "init_db"], 
                          cwd=self.project_root, check=False)
            
            # Run Alembic migrations
            subprocess.run([str(python_path), "-m", "alembic", "upgrade", "head"], 
                          cwd=self.project_root, check=True)
            
            print("✅ Migrations completed")
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Migration failed: {e}")
            raise
    
    def check_fastapi_status(self) -> bool:
        """Check if FastAPI server is running."""
        try:
            response = requests.get(f"{self.fastapi_url}/docs", timeout=2)
            return response.status_code == 200
        except requests.RequestException:
            return False
    
    def start_fastapi(self):
        """Start FastAPI server."""
        print("🚀 Starting FastAPI server...")
        
        if self.check_fastapi_status():
            print("✅ FastAPI server is already running")
            return
        
        # Start FastAPI in background
        python_path = self.venv_path / "Scripts" / "python.exe" if os.name == "nt" else self.venv_path / "bin" / "python"
        
        cmd = [
            str(python_path), "-m", "uvicorn", 
            "app.main:app", 
            "--reload", 
            "--host", "0.0.0.0", 
            "--port", "8000"
        ]
        
        # Start in background
        if os.name == "nt":  # Windows
            subprocess.Popen(cmd, cwd=self.project_root, 
                           creationflags=subprocess.CREATE_NEW_CONSOLE)
        else:  # Unix/Linux
            subprocess.Popen(cmd, cwd=self.project_root, 
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        # Wait for server to be ready
        print("⏳ Waiting for FastAPI server to be ready...")
        for i in range(30):  # Wait up to 30 seconds
            if self.check_fastapi_status():
                print("✅ FastAPI server is ready")
                return
            time.sleep(1)
            print(f"   Waiting... ({i+1}/30)")
        
        print("❌ FastAPI server failed to start within 30 seconds")
        raise Exception("FastAPI startup timeout")
    
    def open_browser(self):
        """Open browser to API documentation."""
        print("🌐 Opening API documentation in browser...")
        try:
            webbrowser.open(self.api_docs_url)
            print(f"✅ Opened: {self.api_docs_url}")
        except Exception as e:
            print(f"⚠️  Could not open browser: {e}")
            print(f"   Please manually open: {self.api_docs_url}")
    
    def show_status(self):
        """Show status of all services."""
        print("📊 Service Status:")
        print("-" * 40)
        
        # Database status
        db_status = "✅ Running" if self.check_database_status() else "❌ Stopped"
        print(f"🗄️  Database: {db_status}")
        
        # FastAPI status
        api_status = "✅ Running" if self.check_fastapi_status() else "❌ Stopped"
        print(f"🚀 FastAPI: {api_status}")
        
        # URLs
        print(f"\n🌐 URLs:")
        print(f"   API Docs: {self.api_docs_url}")
        print(f"   API Base: {self.fastapi_url}")
        print(f"   Database: {self.db_url}")
    
    def start_all(self):
        """Start the complete development environment."""
        self.print_banner()
        
        # Check prerequisites
        if not self.check_prerequisites():
            sys.exit(1)
        
        # Setup environment
        self.setup_environment()
        
        # Start database
        self.start_database()
        
        # Run migrations
        self.run_migrations()
        
        # Start FastAPI
        self.start_fastapi()
        
        # Show final status
        print("\n" + "=" * 80)
        print("🎉 DEVELOPMENT ENVIRONMENT IS READY!")
        print("=" * 80)
        self.show_status()
        print("\n🔧 Available commands:")
        print("   python start_dev.py status  - Check service status")
        print("   python start_dev.py logs    - Show logs")
        print("   python start_dev.py stop    - Stop all services")
        print("   python start_dev.py db      - Open database shell")
        print("=" * 80)
        
        # Open browser
        self.open_browser()
    
    def stop_all(self):
        """Stop all services."""
        print("🛑 Stopping all services...")
        
        # Stop FastAPI (kill any uvicorn processes)
        try:
            if os.name == "nt":  # Windows
                subprocess.run(["taskkill", "/f", "/im", "python.exe"], 
                             capture_output=True, check=False)
            else:  # Unix/Linux
                subprocess.run(["pkill", "-f", "uvicorn"], 
                             capture_output=True, check=False)
        except Exception:
            pass
        
        # Stop Docker services
        try:
            self.run_docker_compose(["down"])
        except Exception:
            pass
        
        print("✅ All services stopped")
    
    def show_logs(self):
        """Show logs from all services."""
        print("📋 Showing service logs...")
        try:
            self.run_docker_compose(["logs", "-f"], check=False)
        except KeyboardInterrupt:
            print("\n📋 Logs stopped")
    
    def open_db_shell(self):
        """Open a PostgreSQL shell."""
        print("🗄️  Opening PostgreSQL shell...")
        try:
            subprocess.run(["docker", "exec", "-it", "kanban-postgres", 
                          "psql", "-U", "kanban", "-d", "kanban_dev"], check=False)
        except Exception as e:
            print(f"❌ Failed to open database shell: {e}")
    
    def clean_up(self):
        """Clean up everything."""
        print("🧹 Cleaning up everything...")
        
        # Stop all services
        self.stop_all()
        
        # Remove Docker volumes
        try:
            self.run_docker_compose(["down", "-v", "--remove-orphans"])
        except Exception:
            pass
        
        # Remove virtual environment
        if self.venv_path.exists():
            import shutil
            shutil.rmtree(self.venv_path)
            print("✅ Removed virtual environment")
        
        # Remove .env file
        if self.env_file.exists():
            self.env_file.unlink()
            print("✅ Removed .env file")
        
        print("✅ Cleanup completed")


def main():
    parser = argparse.ArgumentParser(description="Kanban For Agents Development Environment")
    parser.add_argument("command", nargs="?", default="start", 
                       choices=["start", "stop", "restart", "status", "logs", "db", "clean", "help"],
                       help="Command to run")
    
    args = parser.parse_args()
    
    if args.command == "help":
        print(__doc__)
        return
    
    dev_env = DevEnvironment()
    
    try:
        if args.command == "start":
            dev_env.start_all()
        elif args.command == "stop":
            dev_env.stop_all()
        elif args.command == "restart":
            dev_env.stop_all()
            time.sleep(2)
            dev_env.start_all()
        elif args.command == "status":
            dev_env.show_status()
        elif args.command == "logs":
            dev_env.show_logs()
        elif args.command == "db":
            dev_env.open_db_shell()
        elif args.command == "clean":
            dev_env.clean_up()
    
    except KeyboardInterrupt:
        print("\n\n🛑 Interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
