export interface RecipientRequest {
  name: string;
  email: string;
}

export interface CreateJobRequest {
  event_name: string;
  event_date: string;
  recipients: RecipientRequest[];
}

export interface JobResponse {
  id: number;
  event_name: string;
  event_date: string;
  status: string;
  total_count: number;
  success_count: number;
  failure_count: number;
}

export interface JobStatusResponse extends JobResponse {
  progress: number;
}

export interface CertificateResponse {
  id: number;
  recipient_name: string;
  recipient_email: string;
  status: string;
  file_path: string | null;
  error_message: string | null;
}
