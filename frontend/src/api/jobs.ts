import { apiClient } from "./client";
import type { CreateJobRequest, JobStatusResponse, CertificateResponse } from "../types";

export const createJob = async (data: CreateJobRequest) => {
  const response = await apiClient.post<JobStatusResponse>("/api/jobs", data);
  return response.data;
};

export const getJobStatus = async (jobId: number) => {
  const response = await apiClient.get<JobStatusResponse>(`/api/jobs/${jobId}`);
  return response.data;
};

export const getJobCertificates = async (jobId: number) => {
  const response = await apiClient.get<CertificateResponse[]>(`/api/jobs/${jobId}/certificates`);
  return response.data;
};

export const downloadCertificate = async (certificateId: number) => {
  const response = await apiClient.get(`/api/certificates/${certificateId}/download`, {
    responseType: "blob",
  });
  triggerDownload(response.data, `certificate_${certificateId}.pdf`);
};

export const downloadJobZip = async (jobId: number) => {
  const response = await apiClient.get(`/api/jobs/${jobId}/download`, {
    responseType: "blob",
  });
  triggerDownload(response.data, `certificates_job_${jobId}.zip`);
};

const triggerDownload = (blob: Blob, filename: string) => {
  const url = window.URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.setAttribute("download", filename);
  document.body.appendChild(link);
  link.click();
  link.parentNode?.removeChild(link);
  window.URL.revokeObjectURL(url);
};
