from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class ApplicationCreate(BaseModel):
    job_id: int

class ApplicationStatusUpdate(BaseModel):
    status: str

class ApplicationResponse(BaseModel):
    id: int
    job_id: int
    applicant_id: int
    resume_url: Optional[str]
    status: str
    ai_score: Optional[int]
    ai_summary: Optional[str]
    ai_gaps: Optional[str]
    created_at: datetime
    
    # Nested info
    job_title: Optional[str] = None
    applicant_name: Optional[str] = None
    applicant_email: Optional[str] = None
    
    class Config:
        from_attributes = True

class AIAnalysisResponse(BaseModel):
    score: int
    summary: str
    gaps: list[str]
