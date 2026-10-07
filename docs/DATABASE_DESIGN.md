# Database Design

## 1. GenerationJob

Represents one bulk certificate generation request.

### Fields

| Field | Type | Description |
|---|---|---|
| id | Integer | Primary key |
| event_name | String | Name of event/course |
| event_date | Date | Event date |
| status | String | Current job status |
| total_count | Integer | Total recipients |
| success_count | Integer | Successfully generated |
| failure_count | Integer | Failed generations |
| created_at | DateTime | Job creation time |
| completed_at | DateTime | Completion time |

---

## 2. Certificate

Represents one certificate generated for one recipient.

### Fields

| Field | Type | Description |
|---|---|---|
| id | Integer | Primary key |
| job_id | Integer | Foreign key to GenerationJob |
| recipient_name | String | Recipient name |
| recipient_email | String | Recipient email |
| status | String | SUCCESS / FAILED |
| file_path | String | Generated certificate path |
| error_message | String | Failure reason |
| created_at | DateTime | Creation time |

---

## 3. Relationship

One GenerationJob has many Certificates.

GenerationJob
|
| 1
|
| N
v
Certificate