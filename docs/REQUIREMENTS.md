# Bulk Certificate Generator - Requirements

## 1. Objective

Build a backend API that accepts certificate generation requests
for a list of recipients and generates personalized certificates
using a predefined certificate template.

The system must support bulk generation, track generation progress,
handle individual failures without unnecessarily stopping the entire
job, and allow generated certificates to be retrieved.

---

## 2. Technology

### Backend
- Python
- FastAPI
- Pydantic
- SQLAlchemy
- SQLite
- ReportLab
- Uvicorn

### Frontend
- React
- TypeScript
- Vite
- Tailwind CSS
- Axios
- React Router

### Testing
- Pytest
- FastAPI TestClient

### Version Control
- Git
- GitHub

---

## 3. Core Functional Requirements

### 3.1 Create Generation Job

The client sends one API request containing:

- Event name
- Event date
- List of recipients

Each recipient contains:

- Name
- Email

The request creates one generation job.

The API must return a job ID and initial job status.

---

### 3.2 Validation

The system must validate:

- Required fields
- Recipient name
- Recipient email
- Event information
- Recipient list must not be empty

Invalid recipient data must be reported clearly.

---

### 3.3 Bulk Certificate Generation

A single generation job may contain many recipients.

The system must generate one personalized certificate
for each valid recipient.

Each certificate must be generated from one predefined template.

The certificate should contain at minimum:

- Recipient name
- Event name
- Event date
- Certificate ID

---

### 3.4 Background Processing

Certificate generation must not unnecessarily block the HTTP request.

The create-job API should create the generation job and return
a job ID while processing continues in the background.

---

### 3.5 Failure Handling

Failure of one certificate must not unnecessarily stop
the remaining certificates.

Each recipient/certificate must have an individual status:

- SUCCESS
- FAILED

Failed certificates must store an error message where appropriate.

---

### 3.6 Job Tracking

The system must track:

- Total recipients
- Successful certificates
- Failed certificates
- Job status
- Creation time
- Completion time

Supported job statuses:

- PENDING
- PROCESSING
- COMPLETED
- COMPLETED_WITH_ERRORS
- FAILED

---

## 4. API Requirements

### Create Job

POST /api/jobs

### Get Job Status

GET /api/jobs/{job_id}

### Get Certificates for Job

GET /api/jobs/{job_id}/certificates

### Download Certificate

GET /api/certificates/{certificate_id}/download

### Download All Certificates

GET /api/jobs/{job_id}/download

The last endpoint may return a ZIP containing generated certificates.

---

## 5. Frontend Requirements

The frontend must provide:

### Dashboard
- Create generation job
- Display recent jobs
- Display job status and progress

### Job Details
- Total recipients
- Successful count
- Failed count
- Progress
- Recipient-level result
- Certificate download

The UI should be clean and functional.
It does not need advanced visual design.

---

## 6. Testing Requirements

Tests must cover:

- Creating a generation job
- Input validation
- Certificate generation
- Job status/progress
- Individual certificate failure
- Certificate retrieval
- ZIP generation where implemented

---

## 7. Scope Restrictions

Do not add unnecessary infrastructure.

The initial implementation will NOT use:

- Redis
- Celery
- RabbitMQ
- Kafka
- Docker
- Cloud storage
- Authentication
- Microservices

These may be mentioned as future production improvements,
but they are outside the scope of this assignment.