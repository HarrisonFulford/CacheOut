# Environment Variables Setup

## Quick Setup

1. **Copy the template**:
```bash
cp backend/env.example .env
```

2. **Edit the .env file** with your configuration

## Required Environment Variables

### Server Configuration
```bash
HOST=0.0.0.0                    # Server host (keep as 0.0.0.0 for Docker)
PORT=8000                       # Server port
DEBUG=True                      # Debug mode (set to False in production)
```

### Admin Authentication
```bash
ADMIN_TOKEN=your_secure_token_here  # Change this to a secure token
```

### Frontend Configuration
```bash
# For Vite (frontend)
VITE_ADMIN_TOKEN=your_secure_token_here  # Must match backend ADMIN_TOKEN
VITE_API_BASE_URL=http://localhost:8000/api/v1
```

### Database Configuration
```bash
# For Docker Compose (recommended)
DATABASE_URL=postgresql://cacheout_user:cacheout_password@db:5432/cacheout_db

# For local development with SQLite
# DATABASE_URL=sqlite:///./cacheout.db
```

### Job Cost Configuration
```bash
COST_PER_CORE=0.1              # Credits per CPU core
COST_PER_100MB_RAM=0.001       # Credits per 100MB RAM
DEFAULT_STARTING_CREDITS=100.0  # Starting credits for new users
```

### Worker Configuration
```bash
WORKER_TIMEOUT_SECONDS=60      # Worker timeout in seconds
MAX_WORKERS=100                # Maximum number of workers
```

### Logging
```bash
LOG_LEVEL=INFO                 # Log level (DEBUG, INFO, WARNING, ERROR)
LOG_FILE=app.log              # Log file path
```

## Security Notes

1. **Change the ADMIN_TOKEN** to a secure random string
2. **Use strong database passwords** in production
3. **Set DEBUG=False** in production environments
4. **Use HTTPS** in production
5. **Keep VITE_ADMIN_TOKEN in sync** with backend ADMIN_TOKEN

## Example .env File

```bash
# Server Configuration
HOST=0.0.0.0
PORT=8000
DEBUG=True

# Admin Authentication
ADMIN_TOKEN=my_secure_admin_token_12345

# Frontend Configuration
VITE_ADMIN_TOKEN=my_secure_admin_token_12345
VITE_API_BASE_URL=http://localhost:8000/api/v1

# Database Configuration
DATABASE_URL=postgresql://cacheout_user:cacheout_password@db:5432/cacheout_db

# Job Cost Configuration
COST_PER_CORE=0.1
COST_PER_100MB_RAM=0.001
DEFAULT_STARTING_CREDITS=100.0

# Worker Configuration
WORKER_TIMEOUT_SECONDS=60
MAX_WORKERS=100

# Logging
LOG_LEVEL=INFO
LOG_FILE=app.log
```

## Location

Place the `.env` file in the **root directory** of the CacheOut project (same level as `docker-compose.yml`).

## Validation

After setting up the `.env` file, run the setup script to validate the configuration:

```bash
./setup.sh
```

This will test the backend health and frontend connectivity to ensure everything is configured correctly.

## Frontend Environment Variables

For the React frontend, create a `.env` file in the `frontend/` directory:

```bash
# Frontend .env file (frontend/.env)
VITE_ADMIN_TOKEN=your_secure_admin_token_here
VITE_API_BASE_URL=http://localhost:8000/api/v1
```

**Note**: The frontend admin token must match the backend admin token for the application to work properly. 