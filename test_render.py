#!/usr/bin/env python3
"""
Simple test to verify Render setup works locally.
"""
import os
os.environ["PORT"] = "8000"  # Set default port for testing

try:
    print("Testing FastAPI import...")
    from fastapi import FastAPI
    print("✅ FastAPI imported successfully")
    
    print("Testing route imports...")
    from routes import calculator, api
    print("✅ Routes imported successfully")
    
    print("Testing services imports...")
    from services.vercel_shared_results_service import vercel_shared_results_service
    print("✅ Services imported successfully")
    
    print("Creating FastAPI app...")
    app = FastAPI(title="Test App")
    print("✅ FastAPI app created successfully")
    
    print("All imports successful! Ready for Render deployment.")
    
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Please install requirements: pip install -r requirements.txt")
except Exception as e:
    print(f"❌ Error: {e}")
