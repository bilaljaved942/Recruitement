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


class ShortlistRequest(BaseModel):
    """Request to shortlist top N applicants for a job."""
    threshold: int  # Number of applicants to shortlist
    
    class Config:
        json_schema_extra = {
            "example": {
                "threshold": 10
            }
        }


class ShortlistedApplicant(BaseModel):
    """Info about a shortlisted applicant."""
    id: int
    name: str
    email: str
    score: int
    resume_url: Optional[str]


class ShortlistResponse(BaseModel):
    """Response after shortlisting applicants."""
    success: bool
    message: str
    total_applicants: int
    shortlisted_count: int
    selected_applicants: list[ShortlistedApplicant]
    emails_sent: bool
    hr_email_sent: bool
