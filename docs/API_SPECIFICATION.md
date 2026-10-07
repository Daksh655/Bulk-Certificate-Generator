# API Specification

## POST /api/jobs

Creates a generation job and one certificate record per recipient, then
returns immediately with `201 Created`. Certificate generation continues in
the background.

Request:

```json
{
  "event_name": "Advanced Python Workshop",
  "event_date": "2026-10-10",
  "recipients": [
    { "name": "Rahul Sharma", "email": "rahul@gmail.com" },
    { "name": "Priya Patel", "email": "priya@gmail.com" }
  ]
}
```

Response (`201`):

```json
{
  "id": 1,
  "event_name": "Advanced Python Workshop",
  "event_date": "2026-10-10",
  "status": "PENDING",
  "total_count": 2,
  "success_count": 0,
  "failure_count": 0
}
```

Invalid input (blank names, invalid emails, empty recipient list, missing
fields) returns `422`.

## GET /api/jobs/{job_id}

Returns job status and progress. Clients poll this endpoint.

```json
{
  "id": 1,
  "event_name": "Advanced Python Workshop",
  "event_date": "2026-10-10",
  "status": "PROCESSING",
  "total_count": 100,
  "success_count": 72,
  "failure_count": 1,
  "progress": 73.0
}
```

`progress = (success_count + failure_count) / total_count * 100`.
It is calculated, not stored. Unknown job IDs return `404`.

## Job statuses

| Status | Meaning |
|---|---|
| PENDING | Created, processing not started |
| PROCESSING | Certificates are being generated |
| COMPLETED | All certificates succeeded |
| COMPLETED_WITH_ERRORS | At least one succeeded and at least one failed |
| FAILED | Every certificate failed, or a fatal job-level error occurred |
