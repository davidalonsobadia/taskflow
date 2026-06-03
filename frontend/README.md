# TaskFlow Frontend

Next.js frontend application for TaskFlow task management system.

## 🚀 Quick Start

### Prerequisites

- Docker and Docker Compose installed
- Backend API running (or configure to use external API)

### 1. Set Up Environment Variables

Create a `.env` file in the frontend directory:

```bash
# Backend API URL
# Use 'http://api:8000' if backend is in same Docker network (root docker-compose)
# Use 'http://host.docker.internal:8000' if backend is running on host machine
# Use 'http://localhost:8000' if backend is accessible via localhost
NEXT_PUBLIC_API_URL=http://host.docker.internal:8000

# API Key (required - get it from the backend)
# Create one with: docker-compose exec api python scripts/create_api_client.py --name "frontend"
NEXT_PUBLIC_API_KEY=your-api-key-here

# Node Environment
NODE_ENV=development
```

### 2. Start Frontend Only

```bash
# From the frontend directory
docker-compose up
```

This will start only the frontend service. Make sure your backend API is accessible at the URL specified in `NEXT_PUBLIC_API_URL`.

### 3. Access the Application

- **Frontend**: http://localhost:3000

## 🔧 Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `NEXT_PUBLIC_API_URL` | Backend API URL | `http://host.docker.internal:8000` |
| `NEXT_PUBLIC_API_KEY` | API key for backend authentication | Required |
| `NODE_ENV` | Node environment | `development` |
| `FRONTEND_PORT` | Port to expose | `3000` |
| `FRONTEND_BUILD_TARGET` | Docker build target | `development` |

### Running with External Backend

If your backend is running separately (e.g., on your host machine or another Docker network):

```bash
# In .env file
NEXT_PUBLIC_API_URL=http://host.docker.internal:8000
# or
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### Connecting to Root Docker Compose Network

If you want to connect to the backend running via the root `docker-compose.yml`:

1. Update `frontend/docker-compose.yml`:
   ```yaml
   networks:
     frontend-network:
       external: true
       name: craze_dashboard_taskflow-network
   ```

2. Or use the same network name as the root compose file.

## 🛠️ Development

### Development Mode (Default)

```bash
# Start with hot-reload
docker-compose up

# Or in background
docker-compose up -d

# View logs
docker-compose logs -f frontend
```

### Production Mode

```bash
# Build for production
FRONTEND_BUILD_TARGET=runner docker-compose build

# Start production build
FRONTEND_BUILD_TARGET=runner NODE_ENV=production docker-compose up
```

### Running Commands

```bash
# Install dependencies
docker-compose exec frontend pnpm install

# Run build
docker-compose exec frontend pnpm build

# Access container shell
docker-compose exec frontend sh
```

## 📦 Running with Backend Services

If you want to run frontend with backend services in the same compose file, uncomment the relevant services in `docker-compose.yml`:

1. Uncomment `api` service
2. Uncomment `db` service  
3. Uncomment `redis` service (if needed)
4. Uncomment `worker` service (if needed)
5. Uncomment volumes section

Then run:

```bash
docker-compose up
```

## 🔗 Integration with Root Docker Compose

The frontend can also be run as part of the root `docker-compose.yml`:

```bash
# From project root
docker-compose up frontend
```

This will use the shared network and can communicate with backend services.

## 🐛 Troubleshooting

### Frontend can't connect to backend

1. **Check backend is running**: `curl http://localhost:8000/api/v1/health`
2. **Verify API URL**: Check `NEXT_PUBLIC_API_URL` in `.env`
3. **Check network**: If using Docker, ensure services are on the same network
4. **Verify API key**: Make sure `NEXT_PUBLIC_API_KEY` is set correctly

### Port already in use

Change the port in `.env`:
```bash
FRONTEND_PORT=3001
```

### Hot-reload not working

1. Ensure volumes are mounted correctly
2. Check `NODE_ENV` is set to `development`
3. Verify `FRONTEND_BUILD_TARGET` is `development`

### Rebuild everything

```bash
docker-compose down
docker-compose build --no-cache
docker-compose up
```

## 📚 Related Documentation

- **Root README**: See `../README.md` for full stack setup
- **Backend README**: See `../backend/README.md` for backend documentation
- **API Documentation**: http://localhost:8000/docs (when backend is running)

---

Happy coding! 🚀
