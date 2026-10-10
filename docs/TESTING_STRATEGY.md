# Testing Strategy

## Architecture & Isolation

The automated test suite (`backend/tests/`) is entirely isolated from the development environment using `pytest` fixtures.
- **Database:** Uses a temporary in-memory SQLite database (`test.db`) initialized on a per-session basis. The FastAPI dependency and background worker are monkeypatched to use this DB.
- **File Storage:** Overrides `GENERATED_DIR` to use `pytest`'s temporary `tmp_path`, preventing any interference with the real `generated/` directory.

## Implemented Tests (Backend)

The test suite contains 21 test cases encompassing:

### 1. Job Creation (`test_jobs.py`)
- **Valid Job Flow:** Validates `POST /api/jobs` returns a `201` status, creates records accurately, tracking progress, and verifying the completion of the background tasks through database reflection.

### 2. Validation (`test_validation.py`)
- Evaluates constraints on schemas.
- Rejects missing/blank event names and event dates.
- Rejects empty recipient lists.
- Rejects blank recipient names and malformed emails.
- Correctly returns `422` for malformed JSON data.

### 3. Certificate Generator (`test_certificate_generator.py`)
- Directly invokes `generate_certificate` and verifies the actual creation of a valid PDF file (`%PDF-` format).
- Tests boundaries (200-character long names/events) to assure it renders without crashing.
- Simulates PDF rendering errors and confirms cleanup of incomplete files and correct exception handling.

### 4. Background Processor & Isolation (`test_failure_isolation.py`)
- Simulates targeted rendering failures in individual certificates within a batch.
- Asserts successful isolation: valid recipients complete and save successfully, while the failed recipient evaluates to `FAILED` with an error message without breaking the overarching task.
- Tracks `COMPLETED_WITH_ERRORS` final job state.
- Tracks job `FAILED` final state when all generation attempts fail.

### 5. Retrieval, Downloads & Security (`test_downloads.py`)
- Validates listing API (`GET /api/jobs/{id}/certificates`).
- Tests individual download endpoint (`GET /api/certificates/{id}/download`), confirming `application/pdf` headers.
- Tests bulk ZIP generation (`GET /api/jobs/{id}/download`), assuring that it omits failed certificates and correctly buffers multiple PDFs into a ZIP archive without error.
- Asserts strict path traversal prevention (rejects `../../outside.txt` or absolute paths).

## Frontend Tests
No comprehensive automated frontend test framework (like Jest or Cypress) is included at this stage to keep dependencies lean. Instead, frontend reliability is enforced via strict TypeScript typing and building the production payload (`npm run build`).