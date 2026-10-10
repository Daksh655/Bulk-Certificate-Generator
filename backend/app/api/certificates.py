from fastapi import APIRouter, Depends
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.services import certificate_service

router = APIRouter(prefix="/api/certificates", tags=["Certificates"])


@router.get("/{certificate_id}/download", response_class=FileResponse)
def download_certificate(certificate_id: int, db: Session = Depends(get_db)):
    """
    Download one successfully generated certificate as a PDF.
    """
    path = certificate_service.get_certificate_file(db, certificate_id)
    return FileResponse(
        path,
        media_type="application/pdf",
        filename=f"certificate_{certificate_id}.pdf",
    )
