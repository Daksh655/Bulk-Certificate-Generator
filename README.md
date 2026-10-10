# Bulk Certificate Generator

## Project Overview
The Bulk Certificate Generator solves the problem of dynamically creating large batches of personalized PDF certificates. The workflow allows users to submit an event name, event date, and a bulk list of recipients (names and emails). The system validates the input, queues a generation job, and processes the certificates concurrently in the background. Users can track real-time progress via a dashboard, view individual results (including isolated failures), and download successful certificates either individually or as a bulk ZIP archive.

## Features
- **Bulk Recipient Submission & Validation:** Accepts a robust list of recipients, validating email structures and required fields.
- **PDF Creation:** Generates personalized landscape A4 certificates natively.
- **Background Processing & Concurrency:** Offloads the heavy PDF generation to a ThreadPoolExecutor without blocking the API.
- **Failure Isolation:** Errors in generating a single certificate do not crash the overarching job; successful certificates are preserved while failed ones are marked.
- **Progress Tracking:** Provides real-time percentage updates via polling.
- **Downloads:** Permits individual PDF retrieval and bulk ZIP packaging of all successful certificates.
- **File Safety:** Guards against directory traversal and exposes no internal machine paths.

## Technology Stack
- **Backend:** Python, FastAPI, Pydantic, SQLAlchemy, SQLite, ReportLab
- **Frontend:** React, TypeScript, Vite, Tailwind CSS (v4), Axios, React Router
- **Testing:** Pytest, FastAPI TestClient

## Project Structure
```
bulk-certificate-generator/
├── backend/
│   ├── app/
│   │   ├── api/             # HTTP Routers (jobs, certificates)
│   │   ├── database/        # SQLite engine & SessionLocal
│   │   ├── models/          # SQLAlchemy ORM definitions
│   │   ├── schemas/         # Pydantic validation schemas
│   │   └── services/        # Business logic, ReportLab, ThreadPoolProcessor
│   ├── tests/               # Isolated Pytest suite
│   ├── main.py              # FastAPI application entrypoint
│   └── requirements.txt     # Python dependencies
├── docs/                    # Architecture, Decisions, Testing specifications
├── frontend/                # React Vite SPA application
│   ├── src/                 # React components, pages, API clients
│   └── package.json         # Node.js dependencies
└── README.md
```

## Prerequisites
- **Python:** 3.9+
- **Node.js:** v18+ and `npm`

## Setup & Running the Application

### Backend Setup
Execute these commands in Windows PowerShell from the project root:

```powershell
# Create a virtual environment
python -m venv .venv

# Activate the virtual environment
.\.venv\Scripts\activate

# Install backend dependencies
pip install -r backend/requirements.txt

# Start the FastAPI server (runs on port 8000)
python -m uvicorn --app-dir backend app.main:app --reload
```

### Frontend Setup
Open a new terminal, navigate to the frontend folder, and start Vite:

```bash
cd frontend

# Install Node dependencies
npm install

# Start the React development server
npm run dev
```

## Application URLs
- **Frontend Dashboard:** [http://localhost:5173](http://localhost:5173)
- **Backend API:** [http://127.0.0.1:8000](http://127.0.0.1:8000)
- **Swagger UI (Interactive API Docs):** [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

## API Documentation

### 1. Create a Job
- **Endpoint:** `POST /api/jobs`
- **Description:** Submits a bulk certificate generation task.
- **Example JSON:**
  ```json
  {
    "event_name": "Python Workshop",
    "event_date": "2026-10-10",
    "recipients": [
      { "name": "Alice", "email": "alice@example.com" }
    ]
  }
  ```
- **Responses:** `201 Created` (returns job ID and initial status), `422 Unprocessable Entity` (validation error).

### 2. Get Job Status
- **Endpoint:** `GET /api/jobs/{job_id}`
- **Description:** Retrieves real-time status (`PENDING`, `PROCESSING`, `COMPLETED`, `COMPLETED_WITH_ERRORS`, `FAILED`) and progress calculations.
- **Responses:** `200 OK`, `404 Not Found` (unknown job).

### 3. List Job Certificates
- **Endpoint:** `GET /api/jobs/{job_id}/certificates`
- **Description:** Lists all individual recipient generation results.
- **Responses:** `200 OK` (returns array of certificates), `404 Not Found` (unknown job).

### 4. Download Individual Certificate
- **Endpoint:** `GET /api/certificates/{certificate_id}/download`
- **Description:** Streams the generated PDF file safely.
- **Responses:** `200 OK` (`application/pdf`), `409 Conflict` (failed status), `404 Not Found`, `403 Forbidden` (unsafe path).

### 5. Download Job ZIP
- **Endpoint:** `GET /api/jobs/{job_id}/download`
- **Description:** Packages all successful certificates for a job into a temporary ZIP archive and returns it.
- **Responses:** `200 OK` (`application/zip`), `404 Not Found`, `409 Conflict` (no successful files available).

## Testing

**Backend Tests:**
The backend utilizes an isolated automated suite. Ensure the virtual environment is activated.
```powershell
$env:PYTHONPATH="backend"; .\.venv\Scripts\python.exe -m pytest backend/tests -v
```

**Frontend Build:**
Verify the React application builds correctly for production.
```bash
cd frontend
npm run build
```

## Architecture and Design Decisions
- **Workflow:** The router receives the HTTP request and passes it to the `job_service` to transactionally insert the `GenerationJob` and its child `Certificate` records into SQLite. A FastAPI `BackgroundTask` takes the job ID and orchestrates actual PDF generation outside the HTTP cycle.
- **Background Processing & Concurrency:** To keep the design simple for this assignment, background processing is implemented natively using standard library `ThreadPoolExecutor` (max 4 workers). 
- **Failure Isolation:** Each thread generates its PDF inside a try/catch block. If one fails, its individual database record is marked `FAILED` while others continue safely. 
- **Database & Relational Structure:** SQLite was chosen per the core requirement to avoid complex infrastructure. SQLAlchemy 2.0 handles the 1-to-many relationship securely.
- **File Storage:** Certificates are saved directly to local disk in a structured `generated/{job_id}/` format. Database columns only store relative POSIX paths to remain machine-portable.

## What I Learned

Through this project, I learned how to:

- **Build REST APIs:** Use FastAPI to accept requests, validate input, and return responses.
- **Work with databases:** Store jobs and certificate details using SQLite and SQLAlchemy.
- **Generate PDF certificates:** Create personalized certificates using a fixed template and Python.
- **Process multiple requests in the background:** Generate many certificates without making the user wait for every PDF to finish.
- **Handle failures:** Allow other certificates to generate even if one recipient's certificate fails.
- **Track progress:** Show how many certificates are completed and how many failed.
- **Test an application:** Write automated tests to check API behavior, certificate generation, and downloads.

## Future Scope

The project can be improved further by:

- **Better background processing:** Use a task queue such as Celery with Redis so unfinished jobs can be recovered if the server restarts.
- **A stronger database:** Use PostgreSQL instead of SQLite for a larger application with more users.
- **Cloud file storage:** Store generated certificates in a service such as AWS S3 instead of keeping all files on the server.
- **User login:** Add authentication so only authorized users can access their jobs and certificates.
- **Deployment:** Deploy the application online and use Docker to make setup and deployment easier.
- **More testing and language support:** Add frontend tests and support names in languages such as Hindi by using suitable fonts.
