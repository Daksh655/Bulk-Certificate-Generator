import time
from app.models import GenerationJob, Certificate

def test_create_job_success(client, db_session):
    payload = {
        "event_name": "Test Event",
        "event_date": "2026-10-10",
        "recipients": [
            {"name": "Alice", "email": "alice@example.com"},
            {"name": "Bob", "email": "bob@example.com"}
        ]
    }
    response = client.post("/api/jobs", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["event_name"] == "Test Event"
    assert data["total_count"] == 2
    assert data["success_count"] == 0
    assert data["failure_count"] == 0
    
    # Wait briefly for background processing to finish
    job_id = data["id"]
    for _ in range(30):
        status_res = client.get(f"/api/jobs/{job_id}")
        if status_res.json()["status"] in ["COMPLETED", "COMPLETED_WITH_ERRORS", "FAILED"]:
            break
        time.sleep(0.1)

    status_data = client.get(f"/api/jobs/{job_id}").json()
    assert status_data["status"] == "COMPLETED"
    assert status_data["progress"] == 100.0
    assert status_data["success_count"] == 2

    # Verify DB records directly
    job = db_session.get(GenerationJob, job_id)
    assert job is not None
    assert len(job.certificates) == 2
    for cert in job.certificates:
        assert cert.status == "SUCCESS"
        assert cert.file_path is not None


def test_get_unknown_job(client):
    response = client.get("/api/jobs/99999")
    assert response.status_code == 404

def test_list_jobs(client):
    # Ensure empty returns list
    res_empty = client.get("/api/jobs")
    assert res_empty.status_code == 200
    
    # Create two jobs
    payload1 = {
        "event_name": "Event 1",
        "event_date": "2026-10-10",
        "recipients": [{"name": "A", "email": "a@e.com"}]
    }
    res1 = client.post("/api/jobs", json=payload1).json()
    time.sleep(0.5) # ensure different creation time conceptually
    payload2 = {
        "event_name": "Event 2",
        "event_date": "2026-10-11",
        "recipients": [{"name": "B", "email": "b@e.com"}]
    }
    res2 = client.post("/api/jobs", json=payload2).json()
    
    # Fetch list
    res_list = client.get("/api/jobs")
    assert res_list.status_code == 200
    jobs = res_list.json()
    
    # Ensure they are returned
    assert len(jobs) >= 2
    
    # Verify newest first (Event 2 should come before Event 1 if order is desc id)
    # Filter the jobs in case there are others from previous tests in the isolated DB
    test_jobs = [j for j in jobs if j["event_name"] in ["Event 1", "Event 2"]]
    assert len(test_jobs) == 2
    assert test_jobs[0]["event_name"] == "Event 2"
    assert test_jobs[1]["event_name"] == "Event 1"
    
    # Check fields
    assert "created_at" in test_jobs[0]
    assert "progress" in test_jobs[0]
    assert test_jobs[0]["total_count"] == 1
