#!/usr/bin/env python3
"""
Test frontend API calls to identify issues
"""

import os
import requests
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_api_calls():
    """Test the API calls that the frontend makes."""
    
    admin_token = os.getenv("ADMIN_TOKEN")
    if not admin_token:
        print("❌ ADMIN_TOKEN environment variable not set")
        return
    
    base_url = "http://localhost:8000/api/v1"
    headers = {"Authorization": f"Bearer {admin_token}"}
    
    print("Testing frontend API calls...")
    
    # Test 1: GET /jobs (this is what's failing)
    print("\n1. Testing GET /jobs...")
    try:
        response = requests.get(f"{base_url}/jobs", headers=headers)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            jobs = response.json()
            print(f"   Jobs returned: {len(jobs.get('jobs', []))}")
        else:
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"   Exception: {e}")
    
    # Test 2: GET /workers
    print("\n2. Testing GET /workers...")
    try:
        response = requests.get(f"{base_url}/workers", headers=headers)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            workers = response.json()
            print(f"   Workers returned: {len(workers.get('workers', []))}")
        else:
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"   Exception: {e}")
    
    # Test 3: POST /register
    print("\n3. Testing POST /register...")
    try:
        worker_data = {
            "worker_id": "test-worker-frontend",
            "hostname": "test-machine",
            "cpu_cores": 4,
            "ram_mb": 8192,
            "status": "idle"
        }
        response = requests.post(f"{base_url}/register", json=worker_data, headers=headers)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"   Result: {result}")
        else:
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"   Exception: {e}")
    
    # Test 4: POST /submit (with admin token)
    print("\n4. Testing POST /submit...")
    try:
        job_data = {
            "title": "Test Job",
            "description": "Test job from frontend API test",
            "code": "echo 'test'",
            "priority": 3,
            "required_cores": 2,
            "required_ram_mb": 4096,
            "command": "echo 'test'",
            "parameters": "{}",
            "buyer_id": "test-buyer"
        }
        response = requests.post(f"{base_url}/submit", json=job_data, headers=headers)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"   Result: {result}")
        else:
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"   Exception: {e}")

if __name__ == "__main__":
    test_api_calls() 