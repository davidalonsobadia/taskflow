# TaskFlow - Full Stack Application

A modern task management application with FastAPI backend and Next.js frontend, fully containerized with Docker.

## 🏗️ Architecture

- **Backend**: FastAPI (Python) - REST API with JWT authentication
- **Frontend**: Next.js 16 (React) - Modern React framework
- **Database**: PostgreSQL 15
- **Cache/Queue**: Redis 7
- **Worker**: Celery for async tasks
- **Containerization**: Docker & Docker Compose

## 🚀 Quick Start

### Prerequisites

- Docker and Docker Compose installed
- Git

### 1. Clone the Repository

```bash
git clone <repository-url>
cd craze_dashboard
```

### 2. Set Up Environment Variables

#### Backend Environment

```bash
# Copy backend environment file
cp backend/.env.example backend/.env

# Edit backend/.env and add your configuration
# At minimum, you'll need:
# - RESEND_API_KEY (for email functionality)
# - SECRET_KEY (for JWT tokens)
```

#### Frontend Environment

```bash
# Create frontend/.env file
cat > frontend/.env << EOF
NEXT_PUBLIC_API_URL=http://api:8000
NEXT_PUBLIC_API_KEY=your-api-key-here
NODE_ENV=production
EOF
```

### 3. Start All Services

```bash
# From the root directory
docker-compose up -d
```

This will start:
- Backend API (port 8000)
- Frontend (port 3000)
- PostgreSQL database (port 5432)
- Redis (port 6379)
- Celery worker

### 4. Create an API Key

Before the frontend can communicate with the backend, you need to create an API key:

```bash
# Create an API key for the frontend
docker-compose exec api python scripts/create_api_client.py --name "frontend"
```

**Important**: Copy the API key from the output and update `frontend/.env`:

```bash
NEXT_PUBLIC_API_KEY=your-actual-api-key-here
```

Then restart the frontend:

```bash
docker-compose restart frontend
```

### 5. Access the Application

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/api/v1/health

## 📁 Project Structure

```
craze_dashboard/
├── backend/              # FastAPI backend
│   ├── app/              # Application code
│   ├── alembic/         # Database migrations
│   ├── scripts/          # Utility scripts
│   ├── Dockerfile        # Backend Docker image
│   └── docker-compose.yml # Backend-only compose (legacy)
├── frontend/             # Next.js frontend
│   ├── app/              # Next.js app directory
│   ├── components/       # React components
│   ├── features/         # Feature modules
│   ├── lib/              # Utilities and API client
│   └── Dockerfile        # Frontend Docker image
├── docker-compose.yml    # Root-level compose (all services)
└── README.md            # This file
```

## 🛠️ Development

### Development Mode

For development with hot-reload:

```bash
# Start in development mode
docker-compose up

# Or rebuild and start
docker-compose up --build
```

The frontend will automatically reload on code changes.

### Running Services Separately

You can also run frontend or backend independently:

**Frontend only:**
```bash
cd frontend
docker-compose up
```

**Backend only:**
```bash
cd backend
docker-compose up
```

See `frontend/README.md` and `backend/README.md` for more details.

### Running Commands

```bash
# View logs
docker-compose logs -f frontend
docker-compose logs -f api

# Execute commands in containers
docker-compose exec frontend pnpm install
docker-compose exec api python scripts/create_api_client.py --name "test"

# Access database
docker-compose exec db psql -U postgres -d taskflow_db

# Run migrations
docker-compose exec api alembic upgrade head
```

### Stop Services

```bash
# Stop all services
docker-compose down

# Stop and remove volumes (⚠️ deletes database data)
docker-compose down -v
```

## 🔧 Configuration

### Environment Variables

#### Backend (`backend/.env`)

See `backend/README.md` for full configuration options.

Key variables:
- `DATABASE_URL` - PostgreSQL connection string
- `REDIS_URL` - Redis connection string
- `SECRET_KEY` - JWT secret key
- `RESEND_API_KEY` - Email service API key

#### Frontend (`frontend/.env`)

- `NEXT_PUBLIC_API_URL` - Backend API URL (use `http://api:8000` in Docker)
- `NEXT_PUBLIC_API_KEY` - API key for backend authentication
- `NODE_ENV` - `production` or `development`

### Ports

Default ports (can be overridden in `.env`):
- Frontend: `3000`
- Backend API: `8000`
- PostgreSQL: `5432`
- Redis: `6379`

## 🐳 Docker Commands

```bash
# Build all services
docker-compose build

# Start services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down

# Rebuild specific service
docker-compose build frontend
docker-compose up -d frontend

# Access container shell
docker-compose exec frontend sh
docker-compose exec api bash
```

## 🔐 API Key Setup

All requests to the backend API require an API key. The frontend automatically includes this in all requests.

1. **Create API key**:
   ```bash
   docker-compose exec api python scripts/create_api_client.py --name "frontend"
   ```

2. **Update frontend/.env**:
   ```bash
   NEXT_PUBLIC_API_KEY=your-api-key-here
   ```

3. **Restart frontend**:
   ```bash
   docker-compose restart frontend
   ```

## 📚 Documentation

- **Backend**: See `backend/README.md` for detailed backend documentation
- **Docker Usage**: See `backend/DOCKER_USAGE.md` for advanced Docker operations
- **API Docs**: Visit http://localhost:8000/docs when backend is running

## 🐛 Troubleshooting

### Frontend can't connect to backend

1. Check that both services are running: `docker-compose ps`
2. Verify API key is set in `frontend/.env`
3. Check network connectivity: `docker-compose exec frontend ping api`
4. Verify backend is healthy: `curl http://localhost:8000/api/v1/health`

### Port already in use

Change ports in `.env` or `docker-compose.yml`:
```yaml
ports:
  - "3001:3000"  # Use port 3001 instead of 3000
```

### Database connection issues

1. Check database is running: `docker-compose ps db`
2. Verify connection string in `backend/.env`
3. Check database logs: `docker-compose logs db`

### Rebuild everything

```bash
docker-compose down -v
docker-compose build --no-cache
docker-compose up -d
```

## 🚀 Production Deployment

For production deployment:

1. Set `NODE_ENV=production` in `frontend/.env`
2. Use production build target: `FRONTEND_BUILD_TARGET=runner`
3. Remove volume mounts for source code
4. Use environment-specific secrets
5. Configure proper CORS origins
6. Set up SSL/TLS (consider using Caddy profile)

## 📝 License

MIT License

---

Happy coding! 🚀
