#!/usr/bin/env python3
"""
Script để chạy EpiMap X locally mà không cần Docker
"""
import subprocess
import sys
import os

def install_requirements():
    """Cài đặt requirements"""
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "backend/requirements.txt"])

def setup_database():
    """Tạo database tables"""
    os.chdir("backend")
    from app.db.session import create_db_and_tables
    create_db_and_tables()
    print("Database tables created successfully!")

def run_backend():
    """Chạy FastAPI backend"""
    os.chdir("backend")
    subprocess.run([sys.executable, "-m", "uvicorn", "app.main:app", "--reload", "--host", "0.0.0.0", "--port", "8000"])

if __name__ == "__main__":
    print("Setting up EpiMap X locally...")
    
    # Cài đặt requirements
    print("Installing requirements...")
    install_requirements()
    
    # Setup database (sẽ cần PostgreSQL running)
    try:
        setup_database()
    except Exception as e:
        print(f"Database setup failed: {e}")
        print("You'll need PostgreSQL, Redis, and MinIO running separately")
    
    # Chạy backend
    print("Starting FastAPI backend...")
    run_backend()