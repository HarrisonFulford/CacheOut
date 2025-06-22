#!/usr/bin/env python3
"""
Integration test script for CacheOut system
Tests the backend API and verifies the frontend can connect
"""

import requests
import time
import json
import os

# Configuration
BASE_URL = "http://localhost:8000/api/v1"
ADMIN_TOKEN = os.getenv("ADMIN_TOKEN", "test_token_12345")  # Use environment variable with fallback

def print_response(response, title=""):
    """Helper function to print API responses."""
    print(f"\n{title}")
    print(f"Status Code: {response.status_code}")
    print("Response:")
    try:
        print(json.dumps(response.json(), indent=2))
    except:
        print(response.text)
    print("-" * 50)

def test_backend_health():
    """Test if backend is running."""
    print("Testing backend health...")
    try:
        response = requests.get(f"{BASE_URL}/workers")
        print_response(response, "Backend Health Check")
        return True
    except requests.exceptions.ConnectionError:
        print("❌ Backend is not running. Please start the backend server first.")
        return False

def test_worker_registration():
    """Test registering a worker."""
    print("\nTesting worker registration...")
    
    worker_data = {
        "worker_id": "test-worker-001",
        "hostname": "test-machine",
        "cpu_cores": 4,
        "ram_mb": 8192,
        "status": "idle"
    }
    
    response = requests.post(f"{BASE_URL}/register", json=worker_data)
    print_response(response, "Worker Registration")
    return worker_data["worker_id"]

def test_job_submission():
    """Test submitting a job."""
    print("\nTesting job submission...")
    
    job_data = {
        "priority": 1,
        "required_cores": 2,
        "required_ram_mb": 4096,
        "command": "echo 'Hello from test job'",
        "parameters": {
            "test": True,
            "description": "Integration test job"
        }
    }
    
    headers = {"X-Admin-Token": ADMIN_TOKEN}
    response = requests.post(f"{BASE_URL}/submit", json=job_data, headers=headers)
    print_response(response, "Job Submission")
    return response.json()

def test_get_workers():
    """Test getting the list of workers."""
    print("\nTesting get workers...")
    response = requests.get(f"{BASE_URL}/workers")
    print_response(response, "Get Workers")

def test_get_jobs():
    """Test getting the list of jobs."""
    print("\nTesting get jobs...")
    response = requests.get(f"{BASE_URL}/jobs")
    print_response(response, "Get Jobs")

def test_get_task(worker_id):
    """Test getting a task for a worker."""
    print("\nTesting get task...")
    response = requests.get(f"{BASE_URL}/task?worker_id={worker_id}")
    print_response(response, "Get Task")
    return response.json()

def test_update_status(job_id, worker_id):
    """Test updating job status."""
    print("\nTesting status update...")
    
    status_data = {
        "job_id": job_id,
        "worker_id": worker_id,
        "cpu_percent": 75.5,
        "status": "running"
    }
    
    response = requests.post(f"{BASE_URL}/status", json=status_data)
    print_response(response, "Status Update")

def test_frontend_connection():
    """Test if frontend can connect to backend."""
    print("\nTesting frontend connection...")
    try:
        # Test the same endpoints the frontend would use
        workers_response = requests.get(f"{BASE_URL}/workers")
        jobs_response = requests.get(f"{BASE_URL}/jobs")
        
        if workers_response.status_code == 200 and jobs_response.status_code == 200:
            print("✅ Frontend can connect to backend successfully!")
            return True
        else:
            print("❌ Frontend connection test failed")
            return False
    except Exception as e:
        print(f"❌ Frontend connection test failed: {e}")
        return False

def main():
    """Run all integration tests."""
    print("🚀 Starting CacheOut Integration Tests")
    print("=" * 50)
    
    # Test backend health
    if not test_backend_health():
        return
    
    # Test basic API functionality
    worker_id = test_worker_registration()
    test_get_workers()
    
    job_response = test_job_submission()
    test_get_jobs()
    
    # Wait a moment for job processing
    time.sleep(1)
    
    # Test task assignment
    task = test_get_task(worker_id)
    
    if task:
        test_update_status(task["job_id"], worker_id)
    
    # Test frontend connection
    test_frontend_connection()
    
    print("\n🎉 All integration tests completed!")
    print("\n📋 Next Steps:")
    print("1. Open http://localhost:5173 in your browser")
    print("2. Navigate to the Buyer Dashboard to submit jobs")
    print("3. Navigate to the Seller Dashboard to register as a worker")
    print("4. Test the full workflow: submit job → assign to worker → complete job")

if __name__ == "__main__":
    main() 