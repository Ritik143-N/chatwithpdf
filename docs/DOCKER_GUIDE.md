# Docker Deployment Options

This project provides multiple Docker deployment strategies to suit different needs.

## 🐳 Available Dockerfiles

### 1. `Dockerfile` - Full Production Setup
**Location**: Root directory
**Description**: Multi-service container with Nginx reverse proxy
**Use case**: Production deployments requiring high performance

**Features**:
- Nginx serves React frontend
- Nginx proxies API calls to FastAPI backend
- Supervisor manages both services
- Single port (80) for entire application

**Build and Run**:
```bash
# Build the image
docker build -t chatwithpdf-full .

# Run the container
docker run -p 80:80 -v $(pwd)/chroma_data:/app/chroma_db chatwithpdf-full

# Access application at http://localhost
```

### 2. `Dockerfile.simple` - Single Process Container
**Location**: Root directory  
**Description**: FastAPI serves both API and React static files
**Use case**: Simple deployments, development, or platforms with limited resources

**Features**:
- FastAPI serves React build as static files
- Single process, single port (8000)
- Lighter resource usage
- Easier to debug

**Build and Run**:
```bash
# Build the image
docker build -f Dockerfile.simple -t chatwithpdf-simple .

# Run the container
docker run -p 8000:8000 -v $(pwd)/chroma_data:/app/chroma_db chatwithpdf-simple

# Access application at http://localhost:8000
```

### 3. Individual Service Dockerfiles
**Location**: `backend/Dockerfile`, `frontend/Dockerfile`
**Description**: Separate containers for each service
**Use case**: Microservices architecture, separate scaling

**Features**:
- Independent scaling of services
- Better separation of concerns
- Use with Docker Compose or Kubernetes

**Build and Run**:
```bash
# Use docker-compose
docker-compose up --build

# Or build individually
docker build -t chatwithpdf-backend ./backend
docker build -t chatwithpdf-frontend ./frontend
```

## 🚀 Recommended Usage

### For Development
```bash
# Use docker-compose for development
docker-compose up --build
```

### For Simple Production
```bash
# Use the simple Dockerfile
docker build -f Dockerfile.simple -t chatwithpdf .
docker run -p 8000:8000 -v chatwithpdf-data:/app/chroma_db chatwithpdf
```

### For High-Performance Production
```bash
# Use the full Dockerfile with Nginx
docker build -t chatwithpdf-prod .
docker run -p 80:80 -v chatwithpdf-data:/app/chroma_db chatwithpdf-prod
```

## ⚙️ Environment Variables

All Docker setups support these environment variables:

### Backend Variables
- `PORT`: Server port (default: varies by setup)
- `HUGGING_FACE_TOKEN`: HuggingFace API token (optional)
- `USE_LOCAL_LLM`: Use Ollama instead of HuggingFace (default: false)

### Frontend Variables (for separate builds)
- `REACT_APP_BACKEND_URL`: Backend API URL

## 📁 Volume Mounts

### Required Volumes
- `./chroma_data:/app/chroma_db` - Persistent storage for ChromaDB

### Optional Volumes
- `./logs:/var/log` - Log files (full Dockerfile only)

## 🔧 Configuration Files

### docker-compose.yml
Orchestrates backend and frontend as separate services:
```yaml
version: '3.8'
services:
  backend:
    build: ./backend
    ports: ["8000:8000"]
  frontend:
    build: ./frontend
    ports: ["3000:3000"]
```

### Docker Compose Commands
```bash
# Start all services
docker-compose up

# Build and start
docker-compose up --build

# Run in background
docker-compose up -d

# Stop services
docker-compose down

# View logs
docker-compose logs -f
```

## 🧪 Testing Docker Builds

### Test Individual Services
```bash
# Test backend
cd backend && docker build -t test-backend .
docker run -p 8000:8000 test-backend

# Test frontend
cd frontend && docker build -t test-frontend .
docker run -p 3000:3000 test-frontend
```

### Test Combined Services
```bash
# Test simple setup
docker build -f Dockerfile.simple -t test-simple .
docker run -p 8000:8000 test-simple

# Test full setup
docker build -t test-full .
docker run -p 80:80 test-full
```

## 🐛 Troubleshooting

### Common Issues

1. **Port conflicts**: Make sure ports 80, 3000, 8000 are available
2. **Volume permissions**: Ensure Docker has permission to create volumes
3. **Build failures**: Check that all source files are present

### Debug Commands
```bash
# Check running containers
docker ps

# View logs
docker logs <container-name>

# Execute commands in container
docker exec -it <container-name> bash

# Check built images
docker images
```

### Build Without Cache
```bash
docker build --no-cache -t chatwithpdf .
```

## 🚀 Production Considerations

### For Render/Heroku
- Use individual Dockerfiles (`backend/Dockerfile`, `frontend/Dockerfile`)
- Set appropriate environment variables
- Configure persistent storage

### For VPS/Server
- Use `Dockerfile` with Nginx for better performance
- Set up proper logging
- Configure SSL/HTTPS
- Use Docker Compose for easier management

### For Kubernetes
- Use individual service Dockerfiles
- Create separate deployments for each service
- Configure ingress for routing

## 📊 Performance Comparison

| Setup | Memory Usage | Build Time | Complexity | Best For |
|-------|-------------|------------|-----------|----------|
| docker-compose | High | Medium | Low | Development |
| Dockerfile.simple | Medium | Fast | Low | Simple production |
| Dockerfile | Medium | Slow | High | High-performance production |

Choose the setup that best fits your deployment requirements!
