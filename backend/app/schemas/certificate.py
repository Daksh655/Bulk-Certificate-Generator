from pydantic import BaseModel, ConfigDict


class CertificateResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    recipient_name: str
    recipient_email: str
    status: str
    file_path: str | None
    error_message: str | None
