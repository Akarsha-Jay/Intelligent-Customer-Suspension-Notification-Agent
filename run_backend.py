"""
Launcher script for FastAPI Backend.
Automatically configures the working directory and Python path.
"""

import os
import sys

# Ensure this script's directory is always the working directory and in sys.path
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
os.chdir(PROJECT_ROOT)
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import uvicorn

if __name__ == "__main__":
    print("=" * 60)
    print("STARTING INTELLIGENT NOTIFICATION AGENT BACKEND")
    print(f"Working Directory: {PROJECT_ROOT}")
    print("Swagger API Docs:  http://127.0.0.1:8000/docs")
    print("=" * 60)
    uvicorn.run("backend.main:app", host="127.0.0.1", port=8000, reload=True)
