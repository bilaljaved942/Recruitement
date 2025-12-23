from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from ..models.user import User
from ..models.job import Job, JobStatus
from ..schemas.job import JobCreate, JobUpdate, JobResponse
from ..auth.dependencies import get_current_user, require_role

router = APIRouter(prefix="/jobs", tags=["Jobs"])

@router.get("", response_model=List[JobResponse])
async def list_jobs(db: Session = Depends(get_db)):
    """List all active jobs (public endpoint)."""
    jobs = db.query(Job).filter(Job.status == JobStatus.ACTIVE).all()
    
    result = []
    for job in jobs:
        hr_user = db.query(User).filter(User.id == job.hr_id).first()
        result.append(JobResponse(
            id=job.id,
            title=job.title,
            description=job.description,
            requirements=job.requirements,
            location=job.location,
            salary_range=job.salary_range,
            status=job.status.value,
            hr_id=job.hr_id,
            created_at=job.created_at,
            hr_name=hr_user.full_name if hr_user else None
        ))
    
    return result

@router.get("/my-postings", response_model=List[JobResponse])
async def get_my_postings(
    current_user: User = Depends(require_role("hr")),
    db: Session = Depends(get_db)
):
    """Get HR's own job postings."""
    jobs = db.query(Job).filter(Job.hr_id == current_user.id).all()
    
    return [JobResponse(
        id=job.id,
        title=job.title,
        description=job.description,
        requirements=job.requirements,
        location=job.location,
        salary_range=job.salary_range,
        status=job.status.value,
        hr_id=job.hr_id,
        created_at=job.created_at,
        hr_name=current_user.full_name
    ) for job in jobs]

@router.get("/{job_id}", response_model=JobResponse)
async def get_job(job_id: int, db: Session = Depends(get_db)):
    """Get job details by ID."""
    job = db.query(Job).filter(Job.id == job_id).first()
    
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )
    
    hr_user = db.query(User).filter(User.id == job.hr_id).first()
    
    return JobResponse(
        id=job.id,
        title=job.title,
        description=job.description,
        requirements=job.requirements,
        location=job.location,
        salary_range=job.salary_range,
        status=job.status.value,
        hr_id=job.hr_id,
        created_at=job.created_at,
        hr_name=hr_user.full_name if hr_user else None
    )

@router.post("", response_model=JobResponse)
async def create_job(
    job_data: JobCreate,
    current_user: User = Depends(require_role("hr")),
    db: Session = Depends(get_db)
):
    """Create a new job posting (HR only)."""
    job = Job(
        title=job_data.title,
        description=job_data.description,
        requirements=job_data.requirements,
        location=job_data.location,
        salary_range=job_data.salary_range,
        hr_id=current_user.id
    )
    db.add(job)
    db.commit()
    db.refresh(job)
    
    return JobResponse(
        id=job.id,
        title=job.title,
        description=job.description,
        requirements=job.requirements,
        location=job.location,
        salary_range=job.salary_range,
        status=job.status.value,
        hr_id=job.hr_id,
        created_at=job.created_at,
        hr_name=current_user.full_name
    )

@router.put("/{job_id}", response_model=JobResponse)
async def update_job(
    job_id: int,
    job_data: JobUpdate,
    current_user: User = Depends(require_role("hr")),
    db: Session = Depends(get_db)
):
    """Update a job posting (HR only, own jobs)."""
    job = db.query(Job).filter(Job.id == job_id, Job.hr_id == current_user.id).first()
    
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found or access denied"
        )
    
    if job_data.title:
        job.title = job_data.title
    if job_data.description:
        job.description = job_data.description
    if job_data.requirements:
        job.requirements = job_data.requirements
    if job_data.location is not None:
        job.location = job_data.location
    if job_data.salary_range is not None:
        job.salary_range = job_data.salary_range
    if job_data.status:
        job.status = JobStatus(job_data.status)
    
    db.commit()
    db.refresh(job)
    
    return JobResponse(
        id=job.id,
        title=job.title,
        description=job.description,
        requirements=job.requirements,
        location=job.location,
        salary_range=job.salary_range,
        status=job.status.value,
        hr_id=job.hr_id,
        created_at=job.created_at,
        hr_name=current_user.full_name
    )

@router.delete("/{job_id}")
async def delete_job(
    job_id: int,
    current_user: User = Depends(require_role("hr")),
    db: Session = Depends(get_db)
):
    """Delete a job posting (HR only, own jobs)."""
    job = db.query(Job).filter(Job.id == job_id, Job.hr_id == current_user.id).first()
    
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found or access denied"
        )
    
    db.delete(job)
    db.commit()
    
    return {"message": "Job deleted successfully"}
