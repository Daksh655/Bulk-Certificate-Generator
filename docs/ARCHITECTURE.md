# Architecture

## 1. High-Level Architecture

The application consists of two main components:

1. React frontend
2. FastAPI backend

Architecture:

React
|
| HTTP/JSON
v
FastAPI
|
+-- API Layer
|
+-- Service Layer
|
+-- SQLAlchemy
|
v
SQLite

Certificate generation is handled by the backend using ReportLab.

Background processing is used so that large certificate generation
jobs do not block the HTTP request.

---

## 2. Request Flow

### Create Job

Client
|
v
POST /api/jobs
|
v
Pydantic validation
|
v
Create GenerationJob
|
v
Return job ID
|
v
Background processing
|
v
Generate certificates
|
v
Update certificate and job status

---

## 3. Bulk Processing

A single job can contain many recipients.

Example:

5000 recipients
|
v
one generation job
|
v
background processing
|
+-- certificate 1
+-- certificate 2
+-- certificate 3
+-- ...
+-- certificate 5000

Controlled concurrent processing is used to improve throughput.

POST /api/jobs commits the job and certificate rows, then schedules
services/job_processor.py with FastAPI BackgroundTasks. The processor
opens its own database session and generates PDFs through a
ThreadPoolExecutor (MAX_WORKERS = 4). Worker threads only generate PDFs
from plain values and never touch the database; the processor thread
records each result (SUCCESS or FAILED) as it completes and updates the
job counts. When all certificates are done, the job becomes COMPLETED,
COMPLETED_WITH_ERRORS or FAILED and completed_at is set.

Progress is calculated from the counts, not stored:
(success_count + failure_count) / total_count * 100.
Clients poll GET /api/jobs/{job_id}.

The number of workers should remain configurable.

---

## 4. Failure Isolation

Each certificate is processed independently.

Example:

100 certificates

97 SUCCESS
3 FAILED

A failed certificate must not automatically stop the remaining
certificates.

---

## 5. Certificate Generation

One predefined certificate template is used.

Recipient-specific values are inserted into the generated PDF.

Required dynamic values:

- Recipient name
- Event name
- Event date
- Certificate ID

Generated files are stored locally in the generated/ directory
for this assignment.

PDF generation lives in services/certificate_generator.py. It is
independent of HTTP routes and the database: it receives the values
to print and returns the path of the file it wrote, or raises
CertificateGenerationError. File layout:

generated/{job_id}/certificate_{certificate_id}.pdf

---

## 6. Frontend Communication

The React frontend communicates with the FastAPI backend using Axios.

The frontend can:

- Create jobs
- Fetch job status
- Fetch certificate results
- Download certificates

---

## 7. Future Production Architecture

For a larger production system, the architecture could later use:

- PostgreSQL
- Redis
- Celery or another job queue
- Object storage such as S3
- Authentication
- Docker
- Cloud deployment

These technologies are intentionally excluded from the initial
assignment implementation to keep the system simple and reliable.