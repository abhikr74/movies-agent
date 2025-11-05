#!/usr/bin/env python3
"""
Server startup script for Movie AI Agent
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import uvicorn
from app.main import app
from app.config import API_HOST, API_PORT

if __name__ == "__main__":
    print(f"Starting Movie AI Agent server on {API_HOST}:{API_PORT}")
    uvicorn.run("app.main:app", host=API_HOST, port=API_PORT, reload=True)