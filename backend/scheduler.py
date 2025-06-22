from typing import Dict, List, Optional
from datetime import datetime, timedelta
import uuid
from sqlmodel import Session, select
from models import Job, WorkerInfo, JobStatus, WorkerStatus, WorkerRegistration, User
from credit_manager import CreditManager
from database import engine
from config import config
from logger import logger
import threading

class Scheduler:
    """Job scheduler for the CacheOut distributed compute marketplace."""
    
    def __init__(self):
        self.workers: Dict[str, WorkerInfo] = {}
        self.jobs: Dict[str, Job] = {}
        self.worker_loads: Dict[str, float] = {}
        self.credit_manager = CreditManager()
        self._load_state_from_db()
        logger.info("Scheduler initialized")
    
    def _load_state_from_db(self):
        """Load existing workers and jobs from database."""
        try:
            with Session(engine) as session:
                # Load workers
                workers = session.exec(select(WorkerInfo)).all()
                for worker in workers:
                    self.workers[worker.worker_id] = worker
                
                # Load jobs
                jobs = session.exec(select(Job)).all()
                for job in jobs:
                    self.jobs[job.job_id] = job
                
                logger.info(f"Loaded {len(workers)} workers and {len(jobs)} jobs from database")
        except Exception as e:
            logger.error(f"Error loading state from database: {e}")
    
    def _calculate_job_cost(self, job: Job) -> float:
        """Calculate the cost of a job based on resource requirements."""
        core_cost = job.required_cores * config.COST_PER_CORE
        ram_cost = (job.required_ram_mb / 100) * config.COST_PER_100MB_RAM
        return core_cost + ram_cost
    
    def register_worker(self, worker_info: WorkerInfo) -> str:
        """Register a new worker or update existing worker."""
        worker_id = worker_info.worker_id
        
        # Update worker info
        worker_info.last_heartbeat = datetime.now()
        self.workers[worker_id] = worker_info
        self.worker_loads[worker_id] = 0.0
        
        # Persist to database
        try:
            with Session(engine) as session:
                existing_worker = session.exec(
                    select(WorkerInfo).where(WorkerInfo.worker_id == worker_id)
                ).first()
                
                if existing_worker:
                    # Update existing worker
                    existing_worker.cpu_cores = worker_info.cpu_cores
                    existing_worker.ram_mb = worker_info.ram_mb
                    existing_worker.status = worker_info.status
                    existing_worker.last_heartbeat = worker_info.last_heartbeat
                    session.add(existing_worker)
                else:
                    # Create new worker
                    session.add(worker_info)
                
                session.commit()
                logger.info(f"Worker {worker_id} registered successfully")
        except Exception as e:
            logger.error(f"Error registering worker {worker_id}: {e}")
            raise
        
        return f"Worker {worker_id} registered successfully"
    
    def unregister_worker(self, worker_id: str) -> str:
        """Unregister a worker."""
        if worker_id in self.workers:
            del self.workers[worker_id]
            if worker_id in self.worker_loads:
                del self.worker_loads[worker_id]
            
            # Remove from database
            try:
                with Session(engine) as session:
                    worker = session.exec(
                        select(WorkerInfo).where(WorkerInfo.worker_id == worker_id)
                    ).first()
                    if worker:
                        session.delete(worker)
                        session.commit()
                        logger.info(f"Worker {worker_id} unregistered successfully")
            except Exception as e:
                logger.error(f"Error unregistering worker {worker_id}: {e}")
                raise
            
            return f"Worker {worker_id} unregistered successfully"
        else:
            raise ValueError(f"Worker {worker_id} not found")
    
    def submit_job(self, job_submission: Job, buyer_id: str) -> str:
        """Submit a new job to the queue."""
        with Session(engine) as session:
            # Look up the user ID from the buyer_id string
            user = session.exec(
                select(User).where(User.user_id == buyer_id)
            ).first()
            
            if not user:
                # Create the user if it doesn't exist
                user = User(
                    user_id=buyer_id,
                    username=buyer_id,
                    email=f"{buyer_id}@cacheout.com",
                    credits=config.DEFAULT_STARTING_CREDITS,
                    is_worker=False
                )
                session.add(user)
                session.commit()
                session.refresh(user)
                logger.info(f"Created user: {buyer_id}")
            
            # Calculate job cost
            cost = self._calculate_job_cost(job_submission)
            
            # Check if user has enough credits
            if not self.credit_manager.deduct_credits(buyer_id, cost):
                logger.warning(f"Insufficient credits for buyer {buyer_id} to submit job")
                raise ValueError(f"Insufficient credits. Required: {cost:.2f}, Available: {user.credits:.2f}")
            
            # Create job
            job_id = str(uuid.uuid4())
            job_submission.job_id = job_id
            job_submission.buyer_id = user.id
            job_submission.status = JobStatus.PENDING
            job_submission.cost = cost
            job_submission.created_at = datetime.now()
            
            # Add to database
            session.add(job_submission)
            session.commit()
            session.refresh(job_submission)
            
            # Add to in-memory cache
            self.jobs[job_id] = job_submission
            
            logger.info(f"Submitted job {job_id} for buyer {buyer_id} with cost {cost}")
            return job_id
    
    def update_job_status(self, job_id: str, worker_id: str, cpu_percent: float, status: JobStatus, output: Optional[str] = None) -> None:
        """Update the status of a job."""
        if job_id not in self.jobs:
            raise ValueError(f"Job {job_id} not found")
        
        job = self.jobs[job_id]
        job.status = status
        job.assigned_worker = worker_id
        
        if status == JobStatus.RUNNING and not job.started_at:
            job.started_at = datetime.now()
        elif status == JobStatus.COMPLETED or status == JobStatus.FAILED:
            job.completed_at = datetime.now()
        
        if output:
            job.result = output
        
        # Update worker load
        self.worker_loads[worker_id] = cpu_percent
        
        # Persist to database
        try:
            with Session(engine) as session:
                db_job = session.exec(select(Job).where(Job.job_id == job_id)).first()
                if db_job:
                    db_job.status = status
                    db_job.assigned_worker = worker_id
                    db_job.started_at = job.started_at
                    db_job.completed_at = job.completed_at
                    db_job.result = job.result
                    session.add(db_job)
                    session.commit()
        except Exception as e:
            logger.error(f"Error updating job status in database: {e}")
        
        logger.info(f"Updated job {job_id} status to {status}")
    
    def get_next_job(self, worker_id: str) -> Optional[Job]:
        """Get the next available job for a worker."""
        if worker_id not in self.workers:
            raise ValueError(f"Worker {worker_id} not registered")
        
        worker = self.workers[worker_id]
        if worker.status != "idle":
            return None
        
        # Find pending jobs that match worker capabilities
        available_jobs = [
            job for job in self.jobs.values()
            if job.status == JobStatus.PENDING
            and job.required_cores <= worker.cpu_cores
            and job.required_ram_mb <= worker.ram_mb
        ]
        
        if not available_jobs:
            return None
        
        # Score jobs based on priority and waiting time
        def score_job(job: Job) -> float:
            # Lower score is better
            priority_score = job.priority * 10  # Higher priority = lower score
            waiting_time = (datetime.now() - job.created_at).total_seconds()
            time_score = waiting_time / 60  # Convert to minutes
            return priority_score + time_score
        
        # Sort by score and return the best job
        available_jobs.sort(key=score_job)
        job_to_assign = available_jobs[0]
        
        # Update job status
        job_to_assign.status = JobStatus.RUNNING
        job_to_assign.assigned_worker = worker_id
        job_to_assign.started_at = datetime.now()
        
        # Update worker status
        worker.status = "busy"
        self.workers[worker_id] = worker
        
        # Update in-memory cache
        self.jobs[job_to_assign.job_id] = job_to_assign
        logger.info(f"Assigned job {job_to_assign.job_id} to worker {worker_id}")
        return job_to_assign
    
    def cleanup_stale_workers(self, timeout_seconds: int = None) -> None:
        """Remove workers that haven't sent a heartbeat recently."""
        if timeout_seconds is None:
            timeout_seconds = 60
        
        current_time = datetime.now()
        stale_workers = []
        
        for worker_id, worker in self.workers.items():
            if worker.last_heartbeat:
                time_since_heartbeat = (current_time - worker.last_heartbeat).total_seconds()
                if time_since_heartbeat > timeout_seconds:
                    stale_workers.append(worker_id)
        
        for worker_id in stale_workers:
            logger.warning(f"Removing stale worker: {worker_id}")
            self.unregister_worker(worker_id)
    
    def get_workers(self) -> List[WorkerInfo]:
        """Get list of all registered workers."""
        return list(self.workers.values())
    
    def get_jobs(self) -> List[Job]:
        """Get list of all jobs."""
        return list(self.jobs.values()) 