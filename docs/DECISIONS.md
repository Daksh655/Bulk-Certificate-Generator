# Design Decisions

## 1. FastAPI

Chosen because the assignment specifically asks for Python
backend frameworks and FastAPI provides strong REST API support
with automatic API documentation and Pydantic integration.

## 2. SQLite

Chosen because the assignment requires a relational database
but does not require a production database server.

SQLite reduces setup and development overhead while satisfying
the assignment requirement.

## 3. React + TypeScript

Chosen to provide a modern frontend while keeping the UI
simple enough for one-day implementation.

## 4. Background Processing

Chosen because bulk certificate generation may involve hundreds
or thousands of PDFs and should not block the HTTP request.

## 5. ReportLab

Chosen because it allows certificates to be generated directly
as PDFs using Python.

## 6. Local File Storage

Generated certificates will initially be stored locally.

Cloud/object storage is outside the assignment scope.

## 7. No Redis/Celery

A full distributed task queue would add significant infrastructure
for a one-day assignment.

Controlled application-level background processing is sufficient
for the assignment.

## 8. Individual Failure Isolation

Every recipient is processed independently so one failed
certificate does not stop valid recipients from being generated.