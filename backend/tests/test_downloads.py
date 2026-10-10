import time
import zipfile
import io
from pathlib import Path

from app.models import GenerationJob, Certificate
from app.services.certificate_generator import PROJECT_ROOT

def create_completed_job(client):
    payload = {
        "event_name": "Download Test",
        "event_date": "2026-10-10",
        "recipients": [
            {"name": "Alice", "email": "a@example.com"}
        ]
    }
    res = client.post("/api/jobs", json=payload)
    job_id = res.json()["id"]
    for _ in range(30):
        if client.get(f"/api/jobs/{job_id}").json()["status"] == "COMPLETED":
            break
        time.sleep(0.1)
    return job_id

def test_list_certificates(client):
    job_id = create_completed_job(client)
    res = client.get(f"/api/jobs/{job_id}/certificates")
    assert res.status_code == 200
    certs = res.json()
    assert len(certs) == 1
    c = certs[0]
    assert c["recipient_name"] == "Alice"
    assert c["status"] == "SUCCESS"
    assert "error_message" in c
    assert c["file_path"].startswith("generated/")
    # Confirm internal DB fields aren't exposed
    assert "job_id" not in c 

def test_download_individual_pdf(client):
    job_id = create_completed_job(client)
    certs = client.get(f"/api/jobs/{job_id}/certificates").json()
    cert_id = certs[0]["id"]
    
    res = client.get(f"/api/certificates/{cert_id}/download")
    assert res.status_code == 200
    assert res.headers["content-type"] == "application/pdf"
    assert f"certificate_{cert_id}.pdf" in res.headers["content-disposition"]
    
    content = res.content
    assert len(content) > 0
    assert content.startswith(b"%PDF-")
    assert content.rstrip().endswith(b"%%EOF")

def test_download_unknown_certificate(client):
    res = client.get("/api/certificates/99999/download")
    assert res.status_code == 404

def test_download_job_zip(client):
    job_id = create_completed_job(client)
    res = client.get(f"/api/jobs/{job_id}/download")
    assert res.status_code == 200
    assert res.headers["content-type"] == "application/zip"
    assert f"certificates_job_{job_id}.zip" in res.headers["content-disposition"]
    
    # Verify ZIP contents
    with zipfile.ZipFile(io.BytesIO(res.content)) as zf:
        assert zf.testzip() is None
        entries = zf.namelist()
        assert len(entries) == 1
        assert entries[0].startswith("certificate_")
        assert entries[0].endswith(".pdf")
        # Ensure it's not empty
        pdf_data = zf.read(entries[0])
        assert len(pdf_data) > 0
        assert pdf_data.startswith(b"%PDF-")

def test_download_job_zip_empty(client):
    res = client.get("/api/jobs/99999/download")
    assert res.status_code == 404

def test_path_traversal_blocked(client, db_session):
    # Manually create a completed job with malicious paths
    job = GenerationJob(
        event_name="Evil",
        event_date=__import__("datetime").date(2026, 10, 10),
        status="COMPLETED",
        total_count=3,
        success_count=3,
        failure_count=0
    )
    db_session.add(job)
    db_session.commit()

    # Outside file sentinel for absolute path test
    sentinel = PROJECT_ROOT.parent / "outside_sentinel.txt"
    sentinel.write_text("secret")
    
    try:
        evil_paths = [
            "../../outside.txt",
            "generated/../backend/app/main.py",
            str(sentinel.resolve())
        ]
        
        for p in evil_paths:
            cert = Certificate(
                job_id=job.id,
                recipient_name="Evil",
                recipient_email="e@example.com",
                status="SUCCESS",
                file_path=p
            )
            db_session.add(cert)
        db_session.commit()
        
        # Test individual downloads
        for cert in job.certificates:
            res = client.get(f"/api/certificates/{cert.id}/download")
            assert res.status_code == 403
            assert "not allowed" in res.json()["detail"]
            
        # Test ZIP download
        res = client.get(f"/api/jobs/{job.id}/download")
        assert res.status_code == 409  # No safe/successful certs to download
    finally:
        sentinel.unlink(missing_ok=True)
