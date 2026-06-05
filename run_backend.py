#!/usr/bin/env python
"""
Simple script to run the FastAPI backend without reload
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

import uvicorn
from backend.main import app

if __name__ == '__main__':
    print("Starting FastAPI backend on 127.0.0.1:8000...")
    uvicorn.run(
        app,
        host='127.0.0.1',
        port=8000,
        log_level='info',
        access_log=True,
    )
