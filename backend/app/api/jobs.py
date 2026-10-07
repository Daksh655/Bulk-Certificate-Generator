from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.job import CreateJobRequest, JobResponse, JobStatusResponse
from app.services import job_service
from app.services.job_processor import process_job

router = APIRouter(prefix="/api/jobs", tags=["Jobs"])


@router.post("", response_model=JobResponse, status_code=status.HTTP_201_CREATED)
def create_job(
    request: CreateJobRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    """
    Create a new bulk certificate generation job.

    The job is committed first; certificate generation then runs in the background.
    """
    job = job_service.create_generation_job(db, request)
    background_tasks.add_task(process_job, job.id)
    return job


@router.get("/{job_id}", response_model=JobStatusResponse)
def get_job_status(job_id: int, db: Session = Depends(get_db)):
    """
    Get the status and progress of a generation job.
    """
    job = job_service.get_job(db, job_id)
    if job is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Job not found."
        )
    return job
