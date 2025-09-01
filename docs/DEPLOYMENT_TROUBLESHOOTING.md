# Deployment Troubleshooting Guide

## Common Render Deployment Issues & Solutions

### 1. Pip Installation Failures (Network Issues)

**Symptoms:**
- `BrokenPipeError: [Errno 32] Broken pipe`
- `ProtocolError: Connection broken`
- Timeouts during package installation

**Solutions:**

#### Option A: Use Production Dockerfile (Recommended)
```yaml
# In render.yaml, use:
dockerfilePath: Dockerfile.production
```

This Dockerfile:
- Installs packages in stages
- Has retry logic and timeouts
- Falls back gracefully if ML packages fail
- Uses minimal requirements first

#### Option B: Manual Deployment with Minimal Packages
1. **Create Web Service manually**
2. **Environment**: Docker
3. **Dockerfile**: Use `Dockerfile.production`
4. **Build Command**: Leave empty

#### Option C: Non-Docker Deployment
1. **Environment**: Python 3.11
2. **Build Command**: `pip install fastapi uvicorn pydantic requests python-dotenv pdfplumber Pillow`
3. **Start Command**: `uvicorn app.main_combined:app --host 0.0.0.0 --port $PORT`

### 2. Python 3.8 Compatibility Issues

**Symptoms:**
- `TypeError: 'type' object is not subscriptable`
- ChromaDB/PostHog import errors

**Solutions:**
- Use `requirements_py38.txt` or `requirements_minimal.txt`
- Disable telemetry with environment variables

### 3. Missing ML Dependencies

**Symptoms:**
- Import errors for sentence-transformers or chromadb
- Application starts but ML features don't work

**Solutions:**
The app now handles this gracefully:
- Runs without ML dependencies
- Shows helpful error messages
- Basic file upload still works

### 4. Memory/Resource Issues

**Symptoms:**
- Build takes too long and times out
- Out of memory errors

**Solutions:**
- Use `starter` plan instead of `free`
- Install packages separately in smaller batches
- Use lighter package versions

## Deployment Strategies (In Order of Reliability)

### Strategy 1: Production Dockerfile (Best)
```yaml
services:
  - type: web
    name: chatwithpdf-app
    env: docker
    dockerfilePath: Dockerfile.production
    dockerContext: .
    plan: starter
```

### Strategy 2: Minimal Requirements
Use `requirements_minimal.txt` with only essential packages.

### Strategy 3: Manual Service Creation
1. Go to Render Dashboard
2. New → Web Service
3. Connect repository
4. Choose Docker environment
5. Use `Dockerfile.production`

### Strategy 4: Non-Docker Deployment
If Docker keeps failing:
- Environment: Python 3.11
- Build: Install only core packages
- Start: Run uvicorn directly

## Testing Deployment Locally

### Test Docker Build
```bash
# Test production build
docker build -f Dockerfile.production -t test-prod .
docker run -p 8000:8000 test-prod

# Test minimal build
docker build -f Dockerfile.simple -t test-simple .
docker run -p 8000:8000 test-simple
```

### Test Without ML
```bash
cd backend
pip install fastapi uvicorn pydantic requests python-dotenv pdfplumber Pillow
uvicorn app.main_combined:app --reload
```

## Monitoring Deployment

### Check Build Logs
- Look for specific package failures
- Note which packages cause timeouts
- Check for memory issues

### Common Error Patterns

1. **Network Timeouts**: Use retry logic and staged installation
2. **Memory Issues**: Reduce concurrent installations
3. **Import Errors**: Make imports optional with try/except
4. **Configuration Errors**: Use separate config files

## Emergency Deployment (Minimal Functionality)

If all else fails, deploy with minimal features:

```python
# Minimal main.py
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

app = FastAPI()
app.mount("/", StaticFiles(directory="static", html=True))

@app.get("/api/v1/health")
def health():
    return {"status": "ok", "message": "Minimal version running"}
```

This gives you a working deployment that you can improve incrementally.

## Getting Help

1. **Check Render logs** for specific error messages
2. **Test locally** with Docker first
3. **Use minimal requirements** and add features incrementally
4. **Contact Render support** for persistent issues

The key is to start minimal and add complexity gradually!
