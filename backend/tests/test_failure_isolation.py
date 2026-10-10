import time
from app.services import job_processor

def test_failure_isolation(client, monkeypatch):
    original_generate = job_processor.generate_certificate
    
    def fake_generate(job_id, certificate_id, name, event_name, event_date):
        if name == "Fail":
            raise Exception("Simulated PDF error")
        return original_generate(job_id, certificate_id, name, event_name, event_date)
    
    monkeypatch.setattr(job_processor, "generate_certificate", fake_generate)
    
    payload = {
        "event_name": "Isolation Test",
        "event_date": "2026-10-10",
        "recipients": [
            {"name": "Pass 1", "email": "pass1@example.com"},
            {"name": "Fail", "email": "fail@example.com"},
            {"name": "Pass 2", "email": "pass2@example.com"}
        ]
    }
    
    res = client.post("/api/jobs", json=payload)
    job_id = res.json()["id"]
    
    for _ in range(30):
        status_data = client.get(f"/api/jobs/{job_id}").json()
        if status_data["status"] in ["COMPLETED", "COMPLETED_WITH_ERRORS", "FAILED"]:
            break
        time.sleep(0.1)

    final_status = client.get(f"/api/jobs/{job_id}").json()
    assert final_status["status"] == "COMPLETED_WITH_ERRORS"
    assert final_status["total_count"] == 3
    assert final_status["success_count"] == 2
    assert final_status["failure_count"] == 1
    assert final_status["progress"] == 100.0
    
    certs = client.get(f"/api/jobs/{job_id}/certificates").json()
    assert len(certs) == 3
    
    fail_cert = next(c for c in certs if c["recipient_name"] == "Fail")
    assert fail_cert["status"] == "FAILED"
    assert "Simulated PDF error" in fail_cert["error_message"]
    assert fail_cert["file_path"] is None
    
    pass_certs = [c for c in certs if c["recipient_name"] != "Fail"]
    for c in pass_certs:
        assert c["status"] == "SUCCESS"
        assert c["file_path"] is not None
        assert c["error_message"] is None

def test_all_failed(client, monkeypatch):
    def fake_generate(*args, **kwargs):
        raise Exception("Fatal error")
    
    monkeypatch.setattr(job_processor, "generate_certificate", fake_generate)
    
    payload = {
        "event_name": "All Fail",
        "event_date": "2026-10-10",
        "recipients": [
            {"name": "Fail 1", "email": "fail1@example.com"}
        ]
    }
    
    res = client.post("/api/jobs", json=payload)
    job_id = res.json()["id"]
    
    for _ in range(30):
        status_data = client.get(f"/api/jobs/{job_id}").json()
        if status_data["status"] in ["COMPLETED", "COMPLETED_WITH_ERRORS", "FAILED"]:
            break
        time.sleep(0.1)

    final_status = client.get(f"/api/jobs/{job_id}").json()
    assert final_status["status"] == "FAILED"
    assert final_status["success_count"] == 0
    assert final_status["failure_count"] == 1
