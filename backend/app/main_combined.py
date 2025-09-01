from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
import os

# Try to import routes - handle gracefully if ML dependencies are missing
try:
    from .routes.api import router
    ML_AVAILABLE = True
except ImportError as e:
    print(f"Warning: ML dependencies not available: {e}")
    from fastapi import APIRouter
    router = APIRouter()
    ML_AVAILABLE = False
    
    # Create basic endpoints when ML is not available
    @router.get("/health")
    def health_check():
        return {"status": "healthy", "ml_available": False}
    
    @router.post("/upload")
    def upload_placeholder():
        return {"error": "ML dependencies not available", "message": "Please install sentence-transformers and chromadb"}
    
    @router.post("/ask")
    def ask_placeholder():
        return {"error": "ML dependencies not available", "message": "Please install sentence-transformers and chromadb"}

app = FastAPI(
    title="Chat with PDF API",
    description="API for uploading PDFs and chatting with their content",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files (React build) if the directory exists
static_dir = "static"
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

# Include API routes
app.include_router(router, prefix="/api/v1")

@app.get("/")
def read_root():
    return {"msg": "Chat with PDF API is running", "ml_available": ML_AVAILABLE}

# Health check endpoint
@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "chat-with-pdf", "ml_available": ML_AVAILABLE}

# Serve React app for all other routes (if static directory exists)
@app.get("/{full_path:path}")
async def serve_react_app(full_path: str):
    # Don't serve static files for API routes
    if full_path.startswith("api/"):
        return {"error": "API endpoint not found"}
    
    # Serve React app
    static_file_path = os.path.join(static_dir, "index.html")
    if os.path.exists(static_file_path):
        return FileResponse(static_file_path)
    else:
        return {"error": "Frontend not available", "path": full_path}
