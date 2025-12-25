from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pathlib import Path
from .database import init_db
from .routes import auth, jobs, applications
# Import models so SQLAlchemy can discover all tables
from . import models

# Create FastAPI app
app = FastAPI(
    title="Recruitment API",
    description="API for recruitment platform with AI-powered resume analysis",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(jobs.router)
app.include_router(applications.router)

# Local storage directory for serving files
LOCAL_STORAGE_DIR = Path(__file__).parent.parent / "CV_documents"

@app.on_event("startup")
async def startup():
    """Initialize database on startup."""
    init_db()
    # Ensure CV_documents directory exists
    LOCAL_STORAGE_DIR.mkdir(parents=True, exist_ok=True)

@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Welcome to Recruitment API",
        "docs": "/docs",
        "version": "1.0.0"
    }

@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy"}

@app.get("/files/resumes/{filename}")
async def get_resume_file(filename: str):
    """Serve locally stored resume files."""
    file_path = LOCAL_STORAGE_DIR / filename
    
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")
    
    # Security: prevent path traversal
    if ".." in filename or "/" in filename or "\\" in filename:
        raise HTTPException(status_code=400, detail="Invalid filename")
    
    return FileResponse(
        path=str(file_path),
        filename=filename,
        media_type="application/pdf"
    )

