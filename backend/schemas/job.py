from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class JobCreate(BaseModel):
    title: str
    description: str
    requirements: str
    location: Optional[str] = None
    salary_range: Optional[str] = None

class JobUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    requirements: Optional[str] = None
    location: Optional[str] = None
    salary_range: Optional[str] = None
    status: Optional[str] = None

class JobResponse(BaseModel):
    id: int
    title: str
    description: str
    requirements: str
    location: Optional[str]
    salary_range: Optional[str]
    status: str
    hr_id: int
    created_at: datetime
    hr_name: Optional[str] = None
    
    class Config:
        from_attributes = True
