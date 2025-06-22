# CacheOut - Distributed Compute Marketplace

A production-ready distributed compute marketplace that allows users to buy and sell compute resources. The system consists of a FastAPI backend coordinator, a React frontend marketplace interface, and containerized testing environment.

## 🚀 Features

### Core Functionality
- **Worker Registration**: Machines register with CPU cores, RAM, and status
- **Job Scheduling**: Priority-based job assignment with resource matching
- **Credit System**: Database-backed credit management with transaction safety
- **Real-time Monitoring**: Health checks and system metrics
- **Security**: Input validation, command injection protection, admin authentication

### Advanced Features
- **Thread-safe Operations**: Prevents race conditions in job assignment
- **Persistent Storage**: Database-backed credit system and job tracking
- **Automatic Cleanup**: Memory leak prevention and stale worker cleanup
- **Retry Logic**: Robust error handling and recovery mechanisms
- **Comprehensive Logging**: Structured logging with configurable levels

## 🏗️ Architecture

### Backend (FastAPI Coordinator)
- **Framework**: FastAPI with SQLModel ORM
- **Database**: PostgreSQL (production) / SQLite (development)
- **Authentication**: Admin token-based authentication
- **CORS**: Configured for frontend integration
- **Logging**: Centralized logging with file and console output

### Frontend (React + TypeScript)
- **Framework**: React 18 with TypeScript
- **Build Tool**: Vite
- **Styling**: Tailwind CSS with shadcn/ui components
- **State Management**: TanStack Query for API state
- **Routing**: React Router DOM

## 🐳 Containerized Testing Environment

### Quick Start with Docker Compose

1. **Clone and navigate to the project**:
```bash
cd CacheOut
```

2. **Set up environment variables**:
```bash
cp backend/env.example .env
# Edit .env with your configuration
```

3. **Start all services**:
```bash
docker-compose up -d
```

4. **Access the application**:
- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- Database: localhost:5432

### Services Overview

- **Database**: PostgreSQL 13 with persistent storage
- **Backend**: FastAPI coordinator with auto-reload
- **Frontend**: React app served by Nginx
- **Worker**: Scalable worker nodes for job execution

### Scaling Workers

To run multiple worker instances:

```bash
# Edit docker-compose.yml and uncomment the deploy section
docker-compose up -d --scale worker=3
```

## 📋 API Endpoints

### Worker Endpoints
- `GET /api/v1/workers` - List all registered workers
- `POST /api/v1/register` - Register/update worker
- `POST /api/v1/unregister` - Unregister worker
- `GET /api/v1/task?worker_id=<id>` - Get next task for worker
- `POST /api/v1/status` - Update job status

### Admin Endpoints
- `POST /api/v1/submit` - Submit new job (requires admin token)
- `GET /api/v1/jobs` - List all jobs
- `GET /api/v1/credits/{user_id}` - Get user credit balance

### System Endpoints
- `GET /api/v1/health` - System health check and metrics

## ⚙️ Configuration

### Environment Variables

Create a `.env` file in the root directory:

```bash
# Server Configuration
HOST=0.0.0.0
PORT=8000
DEBUG=True

# Admin Authentication
ADMIN_TOKEN=your_secure_token_here

# Database Configuration
DATABASE_URL=postgresql://cacheout_user:cacheout_password@db:5432/cacheout_db

# Job Cost Configuration
COST_PER_CORE=0.1
COST_PER_100MB_RAM=0.001

# Credit System
DEFAULT_STARTING_CREDITS=100.0

# Worker Configuration
WORKER_TIMEOUT_SECONDS=60
MAX_WORKERS=100

# Logging
LOG_LEVEL=INFO
LOG_FILE=app.log
```

## 🔧 Usage

### Submitting a Job

```bash
curl -X POST "http://localhost:8000/api/v1/submit" \
  -H "Content-Type: application/json" \
  -H "X-Admin-Token: your_admin_token" \
  -d '{
    "title": "Data Processing Job",
    "description": "Process large dataset",
    "code": "print(\"Hello World\")",
    "required_cores": 2,
    "required_ram_mb": 4096,
    "priority": 1,
    "command": "python script.py",
    "parameters": {"input": "data.csv"},
    "buyer_id": "default-buyer"
  }'
```

### Registering a Worker

```bash
curl -X POST "http://localhost:8000/api/v1/register" \
  -H "Content-Type: application/json" \
  -d '{
    "worker_id": "worker-001",
    "cpu_cores": 8,
    "ram_mb": 16384,
    "status": "idle"
  }'
```

### Checking System Health

```bash
curl "http://localhost:8000/api/v1/health"
```

## 🧪 Testing

### Integration Tests

Run the integration test suite:

```bash
# From the project root
cd testing
python test_integration.py
```

### Manual Testing

1. **Start the system**:
```bash
docker-compose up -d
```

2. **Test the frontend**:
   - Open http://localhost:5173
   - Navigate to Buyer Dashboard
   - Submit a test job
   - Monitor job status updates

3. **Test the backend**:
   - Use the API endpoints directly
   - Check system health
   - Monitor logs: `docker-compose logs coordinator`

### Test Scripts

- `test_integration.py` - Full system integration tests
- `test_frontend_api.py` - Frontend API connectivity tests
- `test_cors.py` - CORS configuration tests
- `test_frontend.html` - Frontend functionality tests

## 🏛️ Database Schema

### Users Table
- `id`: Primary key
- `user_id`: Unique user identifier
- `username`: Display name
- `email`: User email
- `credits`: Current credit balance
- `is_worker`: Whether user is a worker
- `created_at`, `updated_at`: Timestamps

### Jobs Table
- `id`: Primary key
- `job_id`: Unique job identifier
- `title`, `description`, `code`: Job details
- `status`: Job status (pending, running, completed, failed)
- `cost`: Job cost in credits
- `required_cores`, `required_ram_mb`: Resource requirements
- `priority`: Job priority (1-10)
- `command`, `parameters`: Execution details
- `buyer_id`, `assigned_worker`: Foreign keys
- `created_at`, `started_at`, `completed_at`: Timestamps

### WorkerRegistration Table
- `id`: Primary key
- `worker_id`: Unique worker identifier
- `cpu_cores`, `ram_mb`: Worker capacity
- `status`: Worker status (idle, busy, offline)
- `last_heartbeat`: Last activity timestamp
- `created_at`, `updated_at`: Timestamps

## 🔒 Security Features

- **Input Validation**: Comprehensive validation for all API inputs
- **Command Injection Protection**: Blocks dangerous command patterns
- **Resource Limits**: Enforces CPU and RAM limits
- **Admin Authentication**: Token-based admin access control
- **CORS Protection**: Configured for specific origins only

## 📊 Monitoring

### Health Check Endpoint
The `/api/v1/health` endpoint provides:
- System status (healthy/unhealthy)
- Worker and job counts by status
- Total credits in system
- Active user count
- System metrics

### Logging
- Configurable log levels (DEBUG, INFO, WARNING, ERROR)
- File and console output
- Structured logging format
- Comprehensive error tracking

### Container Monitoring

```bash
# View logs for all services
docker-compose logs

# View logs for specific service
docker-compose logs coordinator
docker-compose logs frontend
docker-compose logs worker

# Monitor resource usage
docker stats
```

## 🚀 Development

### Local Development Setup

For development without containers:

1. **Backend Setup**:
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python init_db.py
python main.py
```

2. **Frontend Setup**:
```bash
cd frontend
npm install
npm run dev
```

### Code Structure

```
CacheOut/
├── backend/              # FastAPI backend
│   ├── main.py          # Application entry point
│   ├── routes.py        # API routes
│   ├── models.py        # Database models
│   ├── scheduler.py     # Job scheduling logic
│   ├── credit_manager.py # Credit management
│   ├── worker.py        # Worker agent
│   └── requirements.txt # Python dependencies
├── frontend/            # React frontend
│   ├── src/            # Source code
│   ├── public/         # Static assets
│   ├── package.json    # Node dependencies
│   └── Dockerfile      # Frontend container
├── testing/            # Test scripts
│   ├── test_integration.py
│   ├── test_frontend_api.py
│   └── test_cors.py
├── docker-compose.yml  # Container orchestration
└── README.md          # This file
```

## 🚨 Troubleshooting

### Common Issues

1. **Database Connection Errors**:
   - Ensure PostgreSQL container is running: `docker-compose ps`
   - Check database logs: `docker-compose logs db`
   - Verify environment variables in `.env`

2. **Frontend Not Loading**:
   - Check frontend logs: `docker-compose logs frontend`
   - Verify API connectivity: `curl http://localhost:8000/api/v1/health`
   - Check browser console for errors

3. **Worker Not Connecting**:
   - Check worker logs: `docker-compose logs worker`
   - Verify coordinator URL in worker environment
   - Check network connectivity between containers

### Debug Commands

```bash
# Restart all services
docker-compose restart

# Rebuild containers
docker-compose build --no-cache

# View container status
docker-compose ps

# Access container shell
docker-compose exec coordinator bash
docker-compose exec frontend sh

# Check database
docker-compose exec db psql -U cacheout_user -d cacheout_db
```

## 🔮 Future Enhancements

- [ ] Kubernetes deployment
- [ ] Prometheus metrics
- [ ] JWT authentication
- [ ] API rate limiting
- [ ] WebSocket support for real-time updates
- [ ] Advanced job scheduling algorithms
- [ ] Multi-region support
- [ ] Load balancing
- [ ] Auto-scaling workers

## 🤝 Contributing (hold your horses pal)

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 🆘 Support

For issues and questions:
1. Check the health endpoint: `http://localhost:8000/api/v1/health`
2. Review container logs: `docker-compose logs`
3. Verify configuration in `.env` file
4. Run integration tests: `python testing/test_integration.py`
