import logging
import tempfile
import zipfile
from pathlib import Path

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Certificate, GenerationJob
from app.services.certificate_generator import (
    UnsafeCertificatePathError,
    resolve_certificate_path,
)

logger = logging.getLogger(__name__)


def list_certificates(db: Session, job_id: int) -> list[Certificate]:
    _get_job_or_404(db, job_id)
    return list(
        db.scalars(
            select(Certificate)
            .where(Certificate.job_id == job_id)
            .order_by(Certificate.id)
        )
    )


def get_certificate_file(db: Session, certificate_id: int) -> Path:
    """Return the absolute path of a successfully generated certificate PDF."""
    certificate = db.get(Certificate, certificate_id)
    if certificate is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Certificate not found.")
    if certificate.status != "SUCCESS":
        raise HTTPException(
            status.HTTP_409_CONFLICT,
            f"Certificate is not available for download (status: {certificate.status}).",
        )
    if not certificate.file_path:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Certificate has no file.")
    return _safe_existing_file(certificate.file_path)


def build_job_zip(db: Session, job_id: int) -> Path:
    """Write all successful certificates of a job into a temporary ZIP file.

    The caller is responsible for deleting the returned file.
    """
    _get_job_or_404(db, job_id)
    certificates = db.scalars(
        select(Certificate)
        .where(Certificate.job_id == job_id, Certificate.status == "SUCCESS")
        .order_by(Certificate.id)
    ).all()

    files: list[Path] = []
    for certificate in certificates:
        try:
            files.append(_safe_existing_file(certificate.file_path or ""))
        except HTTPException:
            # A missing/unsafe file must not block downloading the others.
            logger.warning("Skipping certificate %s in ZIP", certificate.id)

    if not files:
        raise HTTPException(
            status.HTTP_409_CONFLICT,
            "Job has no successfully generated certificates to download.",
        )

    with tempfile.NamedTemporaryFile(suffix=".zip", delete=False) as tmp:
        zip_path = Path(tmp.name)
    try:
        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as archive:
            for file in files:
                archive.write(file, arcname=file.name)  # flat: certificate_{id}.pdf
    except Exception:
        zip_path.unlink(missing_ok=True)
        raise
    return zip_path


def _get_job_or_404(db: Session, job_id: int) -> GenerationJob:
    job = db.get(GenerationJob, job_id)
    if job is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Job not found.")
    return job


def _safe_existing_file(relative_path: str) -> Path:
    try:
        path = resolve_certificate_path(relative_path)
    except UnsafeCertificatePathError:
        logger.warning("Rejected unsafe certificate path: %r", relative_path)
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Certificate file path is not allowed.")
    if not path.is_file():
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Certificate file is missing.")
    return path
