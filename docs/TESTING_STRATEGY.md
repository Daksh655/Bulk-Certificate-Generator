# Testing Strategy

## Unit Tests

Test:

- Input validation
- Certificate data construction
- Certificate generation
- Failure handling
- Progress calculation

## API Tests

Test:

- POST /api/jobs
- GET /api/jobs/{id}
- GET /api/jobs/{id}/certificates
- GET /api/certificates/{id}/download

## Required Scenarios

### Valid job
Expected:
202 response and job ID.

### Invalid email
Expected:
validation error.

### Empty recipient list
Expected:
validation error.

### Successful generation
Expected:
certificate marked SUCCESS and file exists.

### Individual failure
Expected:
failed certificate marked FAILED while other certificates
continue processing.

### Job completion
Expected:
counts match total number of recipients.