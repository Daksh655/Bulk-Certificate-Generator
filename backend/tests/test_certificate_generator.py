import pytest
from datetime import date

from app.services import certificate_generator
from app.services.certificate_generator import (
    generate_certificate,
    CertificateGenerationError
)

def test_generate_certificate_success():
    relative_path = generate_certificate(
        job_id=99,
        certificate_id=999,
        recipient_name="Test Name",
        event_name="Test Event",
        event_date=date(2026, 10, 10)
    )
    
    assert relative_path.startswith("generated/99/certificate_999.pdf")
    absolute_path = certificate_generator.PROJECT_ROOT / relative_path
    
    assert absolute_path.is_file()
    content = absolute_path.read_bytes()
    assert len(content) > 0
    assert content.startswith(b"%PDF-")
    assert content.rstrip().endswith(b"%%EOF")

def test_generate_certificate_long_names():
    # Long names and event names shouldn't fail
    relative_path = generate_certificate(
        job_id=99,
        certificate_id=1000,
        recipient_name="A" * 200,
        event_name="B" * 200,
        event_date=date(2026, 10, 10)
    )
    absolute_path = certificate_generator.PROJECT_ROOT / relative_path
    assert absolute_path.is_file()

def test_generate_certificate_error_handling(monkeypatch):
    # Force a failure inside the generator to verify it cleans up
    def fake_render(*args, **kwargs):
        raise ValueError("Simulated render error")
    
    monkeypatch.setattr(certificate_generator, "_render_pdf", fake_render)
    
    with pytest.raises(CertificateGenerationError, match="Failed to generate certificate"):
        generate_certificate(
            job_id=99,
            certificate_id=1001,
            recipient_name="Fail Name",
            event_name="Fail Event",
            event_date=date(2026, 10, 10)
        )
    
    # Assert partial file is not left behind
    absolute_path = certificate_generator.PROJECT_ROOT / "generated" / "99" / "certificate_1001.pdf"
    assert not absolute_path.exists()
