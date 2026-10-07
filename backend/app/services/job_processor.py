import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import UTC, date, datetime

from sqlalchemy import select

from app.database import SessionLocal
from app.models import Certificate, GenerationJob
from app.services.certificate_generator import generate_certificate

logger = logging.getLogger(__name__)

# Upper bound on concurrent PDF generations for one job.
MAX_WORKERS = 4

MAX_ERROR_LENGTH = 1000  # certificates.error_message is String(1000)


def process_job(job_id: int) -> None:
    """Generate every pending certificate of a job.

    Runs in the background. It owns its database session; the worker threads
    only generate PDFs from plain values and never touch the database.
    """
    db = SessionLocal()
    try:
        job = db.get(GenerationJob, job_id)
        if job is None:
            logger.error("Cannot process job %s: job not found", job_id)
            return

        job.status = "PROCESSING"
        db.commit()

        event_name, event_date = job.event_name, job.event_date
        pending = db.execute(
            select(Certificate.id, Certificate.recipient_name).where(
                Certificate.job_id == job_id, Certificate.status == "PENDING"
            )
        ).all()

        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as pool:
            futures = {
                pool.submit(
                    _generate_one, job_id, cert_id, name, event_name, event_date
                ): cert_id
                for cert_id, name in pending
            }
            # Only this thread writes to the database, as results arrive.
            for future in as_completed(futures):
                _record_result(db, job, futures[future], future)

        job.status = _final_status(job)
        job.completed_at = _utc_now()
        db.commit()
    except Exception:
        logger.exception("Job %s failed unexpectedly", job_id)
        _mark_job_failed(db, job_id)
    finally:
        db.close()


def _generate_one(
    job_id: int, certificate_id: int, name: str, event_name: str, event_date: date
) -> str:
    """Worker task: PDF generation only, no database access."""
    return generate_certificate(job_id, certificate_id, name, event_name, event_date)


def _record_result(db, job: GenerationJob, certificate_id: int, future) -> None:
    certificate = db.get(Certificate, certificate_id)
    try:
        certificate.file_path = future.result()
        certificate.status = "SUCCESS"
        certificate.error_message = None
        job.success_count += 1
    except Exception as exc:  # one failed certificate must not stop the others
        certificate.file_path = None
        certificate.status = "FAILED"
        certificate.error_message = str(exc)[:MAX_ERROR_LENGTH]
        job.failure_count += 1
    db.commit()  # commit per certificate so progress is visible while running


def _final_status(job: GenerationJob) -> str:
    if job.failure_count == 0:
        return "COMPLETED"
    if job.success_count == 0:
        return "FAILED"
    return "COMPLETED_WITH_ERRORS"


def _mark_job_failed(db, job_id: int) -> None:
    try:
        db.rollback()
        job = db.get(GenerationJob, job_id)
        if job is not None:
            job.status = "FAILED"
            job.completed_at = _utc_now()
            db.commit()
    except Exception:
        logger.exception("Could not mark job %s as FAILED", job_id)
        db.rollback()


def _utc_now() -> datetime:
    # Naive UTC, consistent with created_at (SQLite CURRENT_TIMESTAMP is UTC).
    return datetime.now(UTC).replace(tzinfo=None)
