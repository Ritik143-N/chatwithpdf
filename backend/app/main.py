from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routes.api import router

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

# Include API routes
app.include_router(router, prefix="/api/v1")

@app.get("/")
def read_root():
    return {"msg": "Chat with PDF API is running"}
