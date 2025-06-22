from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime
from enum import Enum

class JobStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"

class WorkerStatus(str, Enum):
    IDLE = "idle"
    BUSY = "busy"
    OFFLINE = "offline"

class User(SQLModel, table=True):
    """User table for storing buyer and worker information"""
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(unique=True, index=True)  # e.g., "default-buyer", "worker-node-001"
    username: str = Field(index=True)
    email: Optional[str] = None
    credits: float = Field(default=100.0)
    is_worker: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class Job(SQLModel, table=True):
    """Job table for storing compute jobs"""
    id: Optional[int] = Field(default=None, primary_key=True)
    job_id: str = Field(unique=True, index=True)
    title: str
    description: str
    code: str
    status: JobStatus = Field(default=JobStatus.PENDING)
    cost: float = Field(default=0.0)
    result: Optional[str] = None
    error_message: Optional[str] = None
    
    # Resource requirements
    required_cores: int = Field(default=1)
    required_ram_mb: int = Field(default=512)
    priority: int = Field(default=1)
    command: str = Field(default="")
    parameters: Optional[str] = None
    
    # Foreign keys
    buyer_id: Optional[int] = Field(default=None, foreign_key="user.id")
    assigned_worker: Optional[str] = None
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

class WorkerRegistration(SQLModel, table=True):
    """Worker registration table for tracking worker availability"""
    id: Optional[int] = Field(default=None, primary_key=True)
    worker_id: str = Field(unique=True, index=True)
    cpu_cores: int
    ram_mb: int
    status: WorkerStatus = Field(default=WorkerStatus.OFFLINE)
    last_heartbeat: datetime = Field(default_factory=datetime.utcnow)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

# Pydantic models for API requests/responses (non-database models)
class WorkerInfo(SQLModel):
    """Worker information for API communication"""
    worker_id: str
    cpu_cores: int
    ram_mb: int
    status: WorkerStatus = WorkerStatus.IDLE
    last_seen: Optional[datetime] = None

class JobSubmission(SQLModel):
    title: str
    description: str
    code: str
    required_cores: int = 1
    required_ram_mb: int = 512
    priority: int = 1
    command: str = ""
    parameters: Optional[str] = None
    buyer_id: str = "default-buyer"

class JobResponse(SQLModel):
    job_id: str
    title: str
    description: str
    status: JobStatus
    cost: float
    result: Optional[str] = None
    error_message: Optional[str] = None
    buyer_id: str
    worker_id: Optional[str] = None
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

class WorkerRegistrationRequest(SQLModel):
    worker_id: str

class JobStatusUpdate(SQLModel):
    job_id: str
    worker_id: str
    status: JobStatus
    cpu_percent: float
    output: Optional[str] = None

class WorkerStatusUpdate(SQLModel):
    worker_id: str
    status: WorkerStatus
    job_id: Optional[str] = None
    result: Optional[str] = None
    error_message: Optional[str] = None
    cpu_percent: float = 0.0

class WorkerUnregister(SQLModel):
    worker_id: str

class CreditResponse(SQLModel):
    user_id: str
    credits: float 