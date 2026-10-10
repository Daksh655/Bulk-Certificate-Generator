import pytest

def test_missing_event_name(client):
    payload = {
        "event_date": "2026-10-10",
        "recipients": [{"name": "Alice", "email": "alice@example.com"}]
    }
    response = client.post("/api/jobs", json=payload)
    assert response.status_code == 422

def test_blank_event_name(client):
    payload = {
        "event_name": "   ",
        "event_date": "2026-10-10",
        "recipients": [{"name": "Alice", "email": "alice@example.com"}]
    }
    response = client.post("/api/jobs", json=payload)
    assert response.status_code == 422

def test_invalid_event_date(client):
    payload = {
        "event_name": "Test",
        "event_date": "not-a-date",
        "recipients": [{"name": "Alice", "email": "alice@example.com"}]
    }
    response = client.post("/api/jobs", json=payload)
    assert response.status_code == 422

def test_missing_recipients(client):
    payload = {
        "event_name": "Test",
        "event_date": "2026-10-10"
    }
    response = client.post("/api/jobs", json=payload)
    assert response.status_code == 422

def test_empty_recipient_list(client):
    payload = {
        "event_name": "Test",
        "event_date": "2026-10-10",
        "recipients": []
    }
    response = client.post("/api/jobs", json=payload)
    assert response.status_code == 422

def test_blank_recipient_name(client):
    payload = {
        "event_name": "Test",
        "event_date": "2026-10-10",
        "recipients": [{"name": "  ", "email": "alice@example.com"}]
    }
    response = client.post("/api/jobs", json=payload)
    assert response.status_code == 422

def test_invalid_recipient_email(client):
    payload = {
        "event_name": "Test",
        "event_date": "2026-10-10",
        "recipients": [{"name": "Alice", "email": "not-an-email"}]
    }
    response = client.post("/api/jobs", json=payload)
    assert response.status_code == 422

def test_malformed_json(client):
    response = client.post("/api/jobs", data="not json")
    assert response.status_code == 422
