from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List
import json
import tempfile
import os
from ..database import get_db
from ..models.user import User
from ..models.job import Job
from ..models.application import Application, ApplicationStatus
from ..schemas.application import (
    ApplicationResponse, 
    ApplicationStatusUpdate,
    ShortlistRequest,
    ShortlistResponse,
    ShortlistedApplicant
)
from ..auth.dependencies import get_current_user, require_role
from ..services.storage import storage_service
from ..services.resume_analyzer import extract_text_from_bytes, analyze_resume
from ..services.email_service import email_service

router = APIRouter(prefix="/applications", tags=["Applications"])

@router.post("", response_model=ApplicationResponse)
async def apply_to_job(
    job_id: int = Form(...),
    resume: UploadFile = File(...),
    current_user: User = Depends(require_role("applicant")),
    db: Session = Depends(get_db)
):
    """Apply to a job with resume upload (Applicant only)."""
    # Check if job exists and is active
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )
    
    # Check if already applied
    existing = db.query(Application).filter(
        Application.job_id == job_id,
        Application.applicant_id == current_user.id
    ).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You have already applied to this job"
        )
    
    # Read resume file
    resume_content = await resume.read()
    
    # Upload to Supabase
    try:
        resume_url = storage_service.upload_resume(resume_content, resume.filename)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload resume: {str(e)}"
        )
    
    # Extract text and analyze with AI
    resume_text = extract_text_from_bytes(resume_content)
    job_description = f"{job.title}\n{job.description}\n{job.requirements}"
    
    analysis = analyze_resume(resume_text, job_description)
    
    # Create application
    application = Application(
        job_id=job_id,
        applicant_id=current_user.id,
        resume_url=resume_url,
        ai_score=analysis["score"],
        ai_summary=analysis["summary"],
        ai_gaps=json.dumps(analysis["gaps"])
    )
    db.add(application)
    db.commit()
    db.refresh(application)
    
    return ApplicationResponse(
        id=application.id,
        job_id=application.job_id,
        applicant_id=application.applicant_id,
        resume_url=application.resume_url,
        status=application.status.value,
        ai_score=application.ai_score,
        ai_summary=application.ai_summary,
        ai_gaps=application.ai_gaps,
        created_at=application.created_at,
        job_title=job.title,
        applicant_name=current_user.full_name,
        applicant_email=current_user.email
    )

@router.get("/my-applications", response_model=List[ApplicationResponse])
async def get_my_applications(
    current_user: User = Depends(require_role("applicant")),
    db: Session = Depends(get_db)
):
    """Get applicant's own applications."""
    applications = db.query(Application).filter(
        Application.applicant_id == current_user.id
    ).all()
    
    result = []
    for app in applications:
        job = db.query(Job).filter(Job.id == app.job_id).first()
        result.append(ApplicationResponse(
            id=app.id,
            job_id=app.job_id,
            applicant_id=app.applicant_id,
            resume_url=app.resume_url,
            status=app.status.value,
            ai_score=app.ai_score,
            ai_summary=app.ai_summary,
            ai_gaps=app.ai_gaps,
            created_at=app.created_at,
            job_title=job.title if job else None,
            applicant_name=current_user.full_name,
            applicant_email=current_user.email
        ))
    
    return result

@router.get("/job/{job_id}", response_model=List[ApplicationResponse])
async def get_applications_for_job(
    job_id: int,
    current_user: User = Depends(require_role("hr")),
    db: Session = Depends(get_db)
):
    """Get all applications for a job (HR only, own jobs)."""
    # Check if job belongs to HR
    job = db.query(Job).filter(Job.id == job_id, Job.hr_id == current_user.id).first()
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found or access denied"
        )
    
    applications = db.query(Application).filter(Application.job_id == job_id).all()
    
    result = []
    for app in applications:
        applicant = db.query(User).filter(User.id == app.applicant_id).first()
        result.append(ApplicationResponse(
            id=app.id,
            job_id=app.job_id,
            applicant_id=app.applicant_id,
            resume_url=app.resume_url,
            status=app.status.value,
            ai_score=app.ai_score,
            ai_summary=app.ai_summary,
            ai_gaps=app.ai_gaps,
            created_at=app.created_at,
            job_title=job.title,
            applicant_name=applicant.full_name if applicant else None,
            applicant_email=applicant.email if applicant else None
        ))
    
    # Sort by AI score descending
    result.sort(key=lambda x: x.ai_score or 0, reverse=True)
    
    return result

@router.put("/{application_id}/status", response_model=ApplicationResponse)
async def update_application_status(
    application_id: int,
    status_update: ApplicationStatusUpdate,
    current_user: User = Depends(require_role("hr")),
    db: Session = Depends(get_db)
):
    """Update application status (HR only)."""
    application = db.query(Application).filter(Application.id == application_id).first()
    if not application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application not found"
        )
    
    # Check if job belongs to HR
    job = db.query(Job).filter(Job.id == application.job_id, Job.hr_id == current_user.id).first()
    if not job:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    # Update status
    application.status = ApplicationStatus(status_update.status)
    db.commit()
    db.refresh(application)
    
    applicant = db.query(User).filter(User.id == application.applicant_id).first()
    
    return ApplicationResponse(
        id=application.id,
        job_id=application.job_id,
        applicant_id=application.applicant_id,
        resume_url=application.resume_url,
        status=application.status.value,
        ai_score=application.ai_score,
        ai_summary=application.ai_summary,
        ai_gaps=application.ai_gaps,
        created_at=application.created_at,
        job_title=job.title,
        applicant_name=applicant.full_name if applicant else None,
        applicant_email=applicant.email if applicant else None
    )

@router.get("/{application_id}", response_model=ApplicationResponse)
async def get_application(
    application_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get application details."""
    application = db.query(Application).filter(Application.id == application_id).first()
    if not application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application not found"
        )
    
    # Check access - applicant can see own, HR can see for own jobs
    job = db.query(Job).filter(Job.id == application.job_id).first()
    
    if current_user.role.value == "applicant" and application.applicant_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    
    if current_user.role.value == "hr" and job.hr_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    
    applicant = db.query(User).filter(User.id == application.applicant_id).first()
    
    return ApplicationResponse(
        id=application.id,
        job_id=application.job_id,
        applicant_id=application.applicant_id,
        resume_url=application.resume_url,
        status=application.status.value,
        ai_score=application.ai_score,
        ai_summary=application.ai_summary,
        ai_gaps=application.ai_gaps,
        created_at=application.created_at,
        job_title=job.title if job else None,
        applicant_name=applicant.full_name if applicant else None,
        applicant_email=applicant.email if applicant else None
    )


@router.post("/job/{job_id}/shortlist-and-notify", response_model=ShortlistResponse)
async def shortlist_and_notify(
    job_id: int,
    request: ShortlistRequest,
    current_user: User = Depends(require_role("hr")),
    db: Session = Depends(get_db)
):
    """
    Shortlist top N applicants by AI score and send interview notifications.
    
    - Selects top N applicants based on threshold
    - Updates their status to "shortlisted"
    - Sends interview invitation emails to selected applicants
    - Sends summary email to HR
    """
    # Validate threshold
    if request.threshold <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Threshold must be greater than 0"
        )
    
    # Check if job belongs to HR
    job = db.query(Job).filter(Job.id == job_id, Job.hr_id == current_user.id).first()
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found or access denied"
        )
    
    # Get all applications for this job, sorted by AI score
    applications = db.query(Application).filter(
        Application.job_id == job_id
    ).order_by(Application.ai_score.desc()).all()
    
    total_applicants = len(applications)
    
    if total_applicants == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No applications found for this job"
        )
    
    # Select top N applicants (or all if threshold > total)
    threshold = min(request.threshold, total_applicants)
    selected_applications = applications[:threshold]
    
    # Check if email is configured
    if not email_service.is_configured():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email not configured. Please set SMTP_EMAIL and SMTP_PASSWORD in .env file"
        )
    
    # Process selected applicants
    selected_applicants = []
    emails_sent = True
    
    for app in selected_applications:
        applicant = db.query(User).filter(User.id == app.applicant_id).first()
        if not applicant:
            continue
        
        # Update status to shortlisted
        app.status = ApplicationStatus.SHORTLISTED
        
        # Build applicant info
        applicant_info = ShortlistedApplicant(
            id=app.id,
            name=applicant.full_name,
            email=applicant.email,
            score=app.ai_score or 0,
            resume_url=app.resume_url
        )
        selected_applicants.append(applicant_info)
        
        # Send interview invitation email
        try:
            email_service.send_interview_invitation(
                applicant_email=applicant.email,
                applicant_name=applicant.full_name,
                job_title=job.title
            )
        except Exception as e:
            print(f"Failed to send email to {applicant.email}: {str(e)}")
            emails_sent = False
    
    # Commit status updates
    db.commit()
    
    # Send summary email to HR
    hr_email_sent = True
    try:
        email_service.send_hr_summary(
            hr_email=current_user.email,
            hr_name=current_user.full_name,
            job_title=job.title,
            selected_applicants=[
                {
                    "name": a.name,
                    "email": a.email,
                    "score": a.score,
                    "resume_url": a.resume_url
                }
                for a in selected_applicants
            ],
            total_applicants=total_applicants
        )
    except Exception as e:
        print(f"Failed to send HR summary email: {str(e)}")
        hr_email_sent = False
    
    return ShortlistResponse(
        success=True,
        message=f"Successfully shortlisted {len(selected_applicants)} applicants",
        total_applicants=total_applicants,
        shortlisted_count=len(selected_applicants),
        selected_applicants=selected_applicants,
        emails_sent=emails_sent,
        hr_email_sent=hr_email_sent
    )
