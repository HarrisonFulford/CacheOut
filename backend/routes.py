from fastapi import APIRouter, HTTPException, Depends, Header, Request
from typing import Optional, List, Dict, Any
from models import WorkerInfo, Job, WorkerStatusUpdate, JobSubmission, WorkerUnregister, JobStatus, WorkerStatus, JobStatusUpdate
from scheduler import Scheduler
from config import config
import re
from datetime import datetime
import os
import logging
import google.generativeai as genai
from sqlalchemy.orm import Session
from sqlalchemy import select
from database import engine
from pydantic import BaseModel
import uuid

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

# Global scheduler instance (will be set by main.py)
scheduler: Optional[Scheduler] = None

def get_scheduler(request: Request) -> Scheduler:
    """Get the scheduler instance from app state."""
    if scheduler is None:
        raise HTTPException(status_code=500, detail="Scheduler not initialized")
    return scheduler

def verify_admin_token(authorization: Optional[str] = Header(None)) -> bool:
    """Verify admin token from Authorization header."""
    if not authorization:
        raise HTTPException(status_code=401, detail="Authorization header required")
    
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid authorization format")
    
    token = authorization[7:]  # Remove "Bearer " prefix
    if token != config.ADMIN_TOKEN:
        raise HTTPException(status_code=401, detail="Invalid admin token")
    
    return True

def validate_job_submission(job: JobSubmission) -> None:
    """Validate job submission data for security and integrity."""
    # Validate title
    if not job.title or len(job.title.strip()) == 0:
        raise HTTPException(status_code=400, detail="Job title is required")
    if len(job.title) > 200:
        raise HTTPException(status_code=400, detail="Job title too long (max 200 characters)")
    
    # Validate description
    if not job.description or len(job.description.strip()) == 0:
        raise HTTPException(status_code=400, detail="Job description is required")
    if len(job.description) > 1000:
        raise HTTPException(status_code=400, detail="Job description too long (max 1000 characters)")
    
    # Validate code
    if not job.code or len(job.code.strip()) == 0:
        raise HTTPException(status_code=400, detail="Job code is required")
    if len(job.code) > 10000:
        raise HTTPException(status_code=400, detail="Job code too long (max 10000 characters)")
    
    # Validate resource requirements
    if job.required_cores < 1 or job.required_cores > 64:
        raise HTTPException(status_code=400, detail="Required cores must be between 1 and 64")
    
    if job.required_ram_mb < 128 or job.required_ram_mb > 131072:  # 128MB to 128GB
        raise HTTPException(status_code=400, detail="Required RAM must be between 128MB and 128GB")
    
    # Validate priority
    if job.priority < 1 or job.priority > 10:
        raise HTTPException(status_code=400, detail="Priority must be between 1 and 10")
    
    # DEMO MODE: Allow crypto mining commands
    if job.command:
        # Only block the most dangerous commands
        dangerous_patterns = [
            r'\b(rm\s+-rf|del\s+/s|format|mkfs|dd\s+if=/dev/zero)\b',  # Very dangerous file operations
            r'\b(sudo|su|doas)\b',  # Privilege escalation
        ]
        
        for pattern in dangerous_patterns:
            if re.search(pattern, job.command, re.IGNORECASE):
                raise HTTPException(
                    status_code=400, 
                    detail=f"Command contains potentially dangerous pattern: {pattern}"
                )

class WorkerRegistrationRequest(BaseModel):
    worker_id: str
    hostname: str
    cpu_cores: int
    ram_mb: int
    status: str

class JobSubmissionRequest(BaseModel):
    title: str
    description: str
    code: str
    priority: int
    required_cores: int
    required_ram_mb: int
    command: str
    parameters: str
    buyer_id: str

class JobStatusUpdateRequest(BaseModel):
    job_id: str
    status: str
    result: Optional[str] = None
    error_message: Optional[str] = None

class NaturalLanguageRequest(BaseModel):
    prompt: str

class NaturalLanguageResponse(BaseModel):
    script: str
    explanation: str
    estimatedCores: int
    estimatedRam: int
    estimatedDuration: int

@router.get("/health")
async def health_check(scheduler: Scheduler = Depends(get_scheduler)) -> Dict[str, Any]:
    """Health check endpoint for monitoring system status."""
    try:
        # Get system metrics
        workers = scheduler.get_workers()
        jobs = scheduler.get_jobs()
        
        # Count jobs by status
        job_counts = {}
        for status in JobStatus:
            job_counts[status.value] = len([j for j in jobs if j.status == status])
        
        # Count workers by status
        worker_counts = {}
        for status in ["idle", "busy", "offline"]:
            worker_counts[status] = len([w for w in workers if w.status.value == status])
        
        # Get credit system status
        total_credits = sum(scheduler.credit_manager.get_all_balances().values())
        
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "metrics": {
                "total_workers": len(workers),
                "total_jobs": len(jobs),
                "job_counts": job_counts,
                "worker_counts": worker_counts,
                "total_credits_in_system": total_credits,
                "active_users": len(scheduler.credit_manager.get_all_balances())
            },
            "version": "1.0.0"
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "timestamp": datetime.now().isoformat(),
            "error": str(e),
            "version": "1.0.0"
        }

@router.get("/workers", response_model=List[WorkerInfo])
async def get_workers(scheduler: Scheduler = Depends(get_scheduler)):
    """Get list of all registered workers."""
    return scheduler.get_workers()

@router.post("/register", response_model=str)
async def register_worker(
    request: WorkerRegistrationRequest,
    scheduler: Scheduler = Depends(get_scheduler)
):
    """Register a new worker."""
    try:
        worker_info = WorkerInfo(
            worker_id=request.worker_id,
            hostname=request.hostname,
            cpu_cores=request.cpu_cores,
            ram_mb=request.ram_mb,
            status=request.status,
            last_heartbeat=datetime.now()
        )
        
        result = scheduler.register_worker(worker_info)
        return {"message": result, "worker_id": request.worker_id}
    except Exception as e:
        logger.error(f"Error registering worker: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to register worker: {str(e)}")

@router.post("/unregister", response_model=str)
async def unregister_worker(payload: WorkerUnregister, scheduler: Scheduler = Depends(get_scheduler)):
    """Unregister a worker."""
    if not payload.worker_id or len(payload.worker_id.strip()) == 0:
        raise HTTPException(status_code=400, detail="Worker ID is required")
    
    if payload.worker_id not in scheduler.workers:
        raise HTTPException(status_code=404, detail="Worker not found")
    scheduler.unregister_worker(payload.worker_id)
    return f"Worker {payload.worker_id} unregistered"

@router.get("/credits/{user_id}", response_model=float)
async def get_credits(user_id: str, scheduler: Scheduler = Depends(get_scheduler)):
    """Get the credit balance for a user."""
    if not user_id or len(user_id.strip()) == 0:
        raise HTTPException(status_code=400, detail="User ID is required")
    
    return scheduler.credit_manager.get_balance(user_id)

@router.get("/task", response_model=Optional[Job])
async def get_task(worker_id: str, scheduler: Scheduler = Depends(get_scheduler)):
    """Get the next task for a worker."""
    if not worker_id or len(worker_id.strip()) == 0:
        raise HTTPException(status_code=400, detail="Worker ID is required")
    
    if worker_id not in scheduler.workers:
        raise HTTPException(status_code=404, detail="Worker not found")
    
    job = scheduler.get_next_job(worker_id)
    if not job:
        return None
    return job

@router.post("/status")
async def update_status(status_update: JobStatusUpdate, scheduler: Scheduler = Depends(get_scheduler)):
    """Update job status from a worker."""
    with Session(engine) as session:
        job = session.exec(select(Job).where(Job.job_id == status_update.job_id)).first()
        if not job or not job.assigned_worker:
            raise HTTPException(status_code=404, detail="Job not found or not assigned")

    # Get current CPU usage for the worker
    cpu_percent = scheduler.worker_loads.get(job.assigned_worker, 0.0)
    
    scheduler.update_job_status(
        job_id=status_update.job_id,
        worker_id=job.assigned_worker,
        cpu_percent=cpu_percent,
        status=status_update.status,
        output=status_update.output
    )
    return {"status": "updated"}

@router.post("/submit", response_model=str)
async def submit_job(
    request: JobSubmissionRequest,
    scheduler: Scheduler = Depends(get_scheduler),
    _: bool = Depends(verify_admin_token)
):
    """Submit a new job."""
    try:
        job = Job(
            job_id=str(uuid.uuid4()),
            title=request.title,
            description=request.description,
            code=request.code,
            priority=request.priority,
            required_cores=request.required_cores,
            required_ram_mb=request.required_ram_mb,
            command=request.command,
            parameters=request.parameters,
            status=JobStatus.PENDING,
            created_at=datetime.now()
        )
        
        job_id = scheduler.submit_job(job, request.buyer_id)
        return {"message": "Job submitted successfully", "job_id": job_id}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error submitting job: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to submit job: {str(e)}")

@router.get("/jobs", response_model=List[Job])
async def get_jobs(scheduler: Scheduler = Depends(get_scheduler)):
    """Get list of all jobs."""
    return scheduler.get_jobs()

@router.post("/process-natural-language")
async def process_natural_language(
    request: NaturalLanguageRequest,
    _: bool = Depends(verify_admin_token)
) -> NaturalLanguageResponse:
    """Process natural language prompt and generate script."""
    try:
        # Basic script generation based on prompt keywords
        prompt_lower = request.prompt.lower()
        
        if any(word in prompt_lower for word in ['mine', 'crypto', 'bitcoin', 'mining']):
            script = """#!/bin/bash
echo "Starting cryptocurrency mining..."
echo "Mining operation initialized"
echo "Hashrate: 1000 H/s"
echo "Mining completed successfully"
"""
            explanation = "Generated mining script based on cryptocurrency keywords"
            estimatedCores = 6
            estimatedRam = 8192
            estimatedDuration = 30
        elif any(word in prompt_lower for word in ['process', 'data', 'dataset']):
            script = """#!/bin/bash
echo "Processing dataset..."
echo "Data processing started"
echo "Processing completed successfully"
"""
            explanation = "Generated data processing script"
            estimatedCores = 4
            estimatedRam = 4096
            estimatedDuration = 20
        elif any(word in prompt_lower for word in ['train', 'model', 'ml', 'machine learning']):
            script = """#!/bin/bash
echo "Training machine learning model..."
echo "Model training started"
echo "Training completed successfully"
"""
            explanation = "Generated ML training script"
            estimatedCores = 8
            estimatedRam = 16384
            estimatedDuration = 60
        else:
            script = """#!/bin/bash
echo "Executing custom task..."
echo "Task started"
echo "Task completed successfully"
"""
            explanation = "Generated generic compute script"
            estimatedCores = 4
            estimatedRam = 4096
            estimatedDuration = 15
        
        return NaturalLanguageResponse(
            script=script,
            explanation=explanation,
            estimatedCores=estimatedCores,
            estimatedRam=estimatedRam,
            estimatedDuration=estimatedDuration
        )
    except Exception as e:
        logger.error(f"Error processing natural language: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to process natural language: {str(e)}") 