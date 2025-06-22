#!/usr/bin/env python3

import requests
import time
import socket
import psutil
import subprocess
import os
import json
from typing import Optional, Dict, Any
from datetime import datetime
import logging
from config import config
from logger import logger

class Worker:
    def __init__(self, coordinator_url: str = None):
        self.coordinator_url = coordinator_url or f"http://{config.HOST}:{config.PORT}/api/v1"
        self.worker_id = None
        self.hostname = socket.gethostname()
        self.cpu_cores = psutil.cpu_count()
        self.ram_mb = psutil.virtual_memory().total // (1024 * 1024)
        self.current_job: Optional[Dict[str, Any]] = None
        self.process: Optional[subprocess.Popen] = None
        self.max_retries = 3
        self.retry_delay = 5

    def register(self) -> bool:
        """Register this worker with the coordinator."""
        for attempt in range(self.max_retries):
            try:
                worker_info = {
                    "worker_id": self.worker_id or f"worker-{self.hostname}-{os.getpid()}",
                    "hostname": self.hostname,
                    "cpu_cores": self.cpu_cores,
                    "ram_mb": self.ram_mb,
                    "status": "idle"
                }
                
                response = requests.post(
                    f"{self.coordinator_url}/register",
                    json=worker_info,
                    timeout=10
                )
                
                if response.ok:
                    self.worker_id = response.json()
                    logger.info(f"Successfully registered as worker {self.worker_id}")
                    return True
                else:
                    logger.error(f"Registration failed (attempt {attempt + 1}): {response.text}")
                    
            except requests.exceptions.RequestException as e:
                logger.error(f"Registration error (attempt {attempt + 1}): {str(e)}")
            
            if attempt < self.max_retries - 1:
                time.sleep(self.retry_delay)
        
        return False

    def poll_for_task(self) -> Optional[Dict[str, Any]]:
        """Poll the coordinator for a new task."""
        try:
            response = requests.get(
                f"{self.coordinator_url}/task",
                params={"worker_id": self.worker_id},
                timeout=10
            )
            
            if response.ok:
                task = response.json()
                if task:  # Task can be None if no work is available
                    logger.info(f"Received task {task['job_id']}")
                    return task
            return None
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error polling for task: {str(e)}")
            return None

    def update_status(self, status: str, cpu_percent: float, error_message: Optional[str] = None) -> bool:
        """Update the coordinator about the current job's status."""
        if not self.current_job:
            return False
            
        for attempt in range(self.max_retries):
            try:
                status_data = {
                    "job_id": self.current_job["job_id"],
                    "worker_id": self.worker_id,
                    "cpu_percent": cpu_percent,
                    "status": status
                }
                if error_message:
                    status_data["error_message"] = error_message
                    
                response = requests.post(
                    f"{self.coordinator_url}/status",
                    json=status_data,
                    timeout=10
                )
                
                if response.ok:
                    return True
                else:
                    logger.error(f"Status update failed (attempt {attempt + 1}): {response.text}")
                    
            except requests.exceptions.RequestException as e:
                logger.error(f"Status update error (attempt {attempt + 1}): {str(e)}")
            
            if attempt < self.max_retries - 1:
                time.sleep(self.retry_delay)
        
        return False

    def execute_task(self, task: Dict[str, Any]) -> bool:
        """Execute the given task and monitor its progress."""
        self.current_job = task
        command = task["command"]
        parameters = task.get("parameters", {})

        # Convert parameters to command line arguments
        cmd_args = []
        if parameters:
            for key, value in parameters.items():
                if isinstance(value, bool):
                    if value:
                        cmd_args.append(f"--{key}")
                else:
                    cmd_args.append(f"--{key}={value}")

        full_command = f"{command} {' '.join(cmd_args)}"
        logger.info(f"Executing command: {full_command}")
        
        try:
            # Start the process
            self.process = subprocess.Popen(
                full_command,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Update status to running
            self.update_status("running", psutil.cpu_percent())
            
            # Monitor the process
            while self.process.poll() is None:
                # Update status every 5 seconds
                self.update_status("running", psutil.cpu_percent())
                time.sleep(5)
            
            # Process completed
            if self.process.returncode == 0:
                self.update_status("completed", 0.0)
                logger.info(f"Task {task['job_id']} completed successfully")
                return True
            else:
                stderr_output = self.process.stderr.read() if self.process.stderr else "No error output"
                self.update_status("failed", 0.0, stderr_output)
                logger.error(f"Task {task['job_id']} failed: {stderr_output}")
                return False
                
        except Exception as e:
            error_msg = str(e)
            self.update_status("failed", 0.0, error_msg)
            logger.error(f"Error executing task: {error_msg}")
            return False
        finally:
            self.current_job = None
            self.process = None

    def run(self):
        """Main worker loop."""
        if not self.register():
            logger.error("Failed to register worker. Exiting.")
            return

        logger.info("Worker started successfully")
        
        while True:
            try:
                # Poll for new task
                task = self.poll_for_task()
                
                if task:
                    # Execute the task
                    self.execute_task(task)
                else:
                    # No task available, wait before polling again
                    time.sleep(5)
                    
            except KeyboardInterrupt:
                logger.info("Received shutdown signal")
                if self.process:
                    logger.info("Terminating current task")
                    self.process.terminate()
                break
            except Exception as e:
                logger.error(f"Unexpected error in worker loop: {str(e)}")
                time.sleep(5)  # Wait before retrying

def main():
    # Get coordinator URL from environment or use default
    coordinator_url = os.getenv("COORDINATOR_URL")
    
    worker = Worker(coordinator_url)
    worker.run()

if __name__ == "__main__":
    main() 