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

## GET /api/jobs/{job_id}/certificates

Lists every certificate of a job with its individual result.
Unknown job IDs return `404`; a job with no certificates returns `[]`.

```json
[
  {
    "id": 1,
    "recipient_name": "Rahul Sharma",
    "recipient_email": "rahul@gmail.com",
    "status": "SUCCESS",
    "file_path": "generated/1/certificate_1.pdf",
    "error_message": null
  },
  {
    "id": 2,
    "recipient_name": "Priya Patel",
    "recipient_email": "priya@gmail.com",
    "status": "FAILED",
    "file_path": null,
    "error_message": "Certificate generation failed"
  }
]
```

`file_path` is relative to the project root.

## GET /api/certificates/{certificate_id}/download

Returns the PDF (`200`, `application/pdf`) as an attachment named
`certificate_{certificate_id}.pdf`.

| Case | Response |
|---|---|
| Certificate not found | `404` |
| Status is not `SUCCESS` (PENDING / FAILED) | `409` |
| No file path, or file missing on disk | `404` |
| Stored path resolves outside `generated/` | `403` |

## GET /api/jobs/{job_id}/download

Returns a ZIP (`200`, `application/zip`) named `certificates_job_{job_id}.zip`
containing every successfully generated PDF of the job, flat
(`certificate_1.pdf`, `certificate_2.pdf`, ...). Failed certificates are
omitted, so a `COMPLETED_WITH_ERRORS` job still downloads its successful
PDFs. The ZIP is built in a temporary file and deleted after it is sent.

| Case | Response |
|---|---|
| Job not found | `404` |
| No successful certificate files to include | `409` |

`409 Conflict` is used (rather than `404`) when the job exists but its
current state has nothing downloadable, e.g. still processing or every
certificate failed. Error bodies use FastAPI's standard
`{"detail": "..."}` format.

## Job statuses

| Status | Meaning |
|---|---|
| PENDING | Created, processing not started |
| PROCESSING | Certificates are being generated |
| COMPLETED | All certificates succeeded |
| COMPLETED_WITH_ERRORS | At least one succeeded and at least one failed |
| FAILED | Every certificate failed, or a fatal job-level error occurred |
