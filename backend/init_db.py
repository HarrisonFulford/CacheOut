#!/usr/bin/env python3
"""
Database initialization script for CacheOut
Creates tables and initializes with sample data
"""

import os
import sys
from sqlmodel import SQLModel, Session, create_engine, select
from backend.models import User, Job, JobStatus
from backend.config import config
from backend.logger import logger

def init_database():
    """Initialize the database with tables and sample data."""
    try:
        # Create engine
        engine = create_engine(config.DATABASE_URL, echo=config.DEBUG)
        
        # Create all tables
        SQLModel.metadata.create_all(engine)
        logger.info("Database tables created successfully")
        
        # Initialize with sample data
        with Session(engine) as session:
            # Check if we already have users
            existing_users = session.exec(select(User)).all()
            
            if not existing_users:
                # Create sample users
                sample_users = [
                    User(
                        user_id="sample-buyer",
                        username="Sample Buyer",
                        email="buyer@cacheout.com",
                        credits=100.0,
                        is_worker=False
                    ),
                    User(
                        user_id="sample-worker",
                        username="Sample Worker",
                        email="worker@cacheout.com",
                        credits=50.0,
                        is_worker=True
                    )
                ]
                
                for user in sample_users:
                    session.add(user)
                
                session.commit()
                logger.info("Sample users created successfully")
            else:
                logger.info("Users already exist, skipping sample data creation")
        
        logger.info("Database initialization completed successfully")
        return True
        
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        return False

def reset_database():
    """Reset the database (drop all tables and recreate)."""
    try:
        # Create engine
        engine = create_engine(config.DATABASE_URL, echo=config.DEBUG)
        
        # Drop all tables
        SQLModel.metadata.drop_all(engine)
        logger.info("Database tables dropped successfully")
        
        # Recreate tables
        SQLModel.metadata.create_all(engine)
        logger.info("Database tables recreated successfully")
        
        # Initialize with sample data
        init_database()
        
        logger.info("Database reset completed successfully")
        return True
        
    except Exception as e:
        logger.error(f"Database reset failed: {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--reset":
        success = reset_database()
    else:
        success = init_database()
    
    if success:
        print("✅ Database initialization completed successfully")
        sys.exit(0)
    else:
        print("❌ Database initialization failed")
        sys.exit(1) 