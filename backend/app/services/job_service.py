import logging

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.certificate import Certificate
from app.models.job import GenerationJob
from app.schemas.job import CreateJobRequest

logger = logging.getLogger(__name__)

def create_generation_job(db: Session, request: CreateJobRequest) -> GenerationJob:
    """
    Creates a new generation job and its associated certificates.
    All operations are performed in a single transaction.
    """
    job = GenerationJob(
        event_name=request.event_name,
        event_date=request.event_date,
        status="PENDING",
        total_count=len(request.recipients),
        success_count=0,
        failure_count=0,
    )
    
    try:
        # We append certificates directly to the job's relationship.
        # SQLAlchemy will automatically set the foreign key upon flush/commit.
        for recipient in request.recipients:
            cert = Certificate(
                recipient_name=recipient.name,
                recipient_email=recipient.email.lower(),  # Normalizing email
                status="PENDING"
            )
            job.certificates.append(cert)
        
        db.add(job)
        db.commit()
        db.refresh(job)
        return job
    except Exception as e:
        db.rollback()
        logger.error(f"Transaction failed during job creation: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create generation job."
        ) from e


def get_job(db: Session, job_id: int) -> GenerationJob | None:
    return db.get(GenerationJob, job_id)
