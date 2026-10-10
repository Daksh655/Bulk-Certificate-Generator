import React, { useEffect, useState, useRef } from 'react';
import { useParams, Link } from 'react-router-dom';
import { getJobStatus, getJobCertificates, downloadCertificate, downloadJobZip } from '../api/jobs';
import type { JobStatusResponse, CertificateResponse } from '../types';
import { StatusBadge, ProgressBar } from '../components/Shared';
import { ArrowLeft, Download, AlertCircle } from 'lucide-react';

export const JobDetailsPage: React.FC = () => {
  const { jobId } = useParams<{ jobId: string }>();
  const id = parseInt(jobId || '0');
  
  const [job, setJob] = useState<JobStatusResponse | null>(null);
  const [certificates, setCertificates] = useState<CertificateResponse[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  
  const timerRef = useRef<number | null>(null);

  const fetchJobData = async () => {
    try {
      const currentJob = await getJobStatus(id);
      setJob(currentJob);
      
      const certs = await getJobCertificates(id);
      setCertificates(certs);
      
      setError(null);
      return currentJob;
    } catch (err: any) {
      if (err.response?.status === 404) {
        setError('Job not found.');
      } else {
        setError(err.message || 'Failed to fetch job data.');
      }
      return null;
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    let active = true;

    const poll = async () => {
      const currentJob = await fetchJobData();
      if (!active) return;
      
      if (currentJob) {
        const terminalStatuses = ['COMPLETED', 'COMPLETED_WITH_ERRORS', 'FAILED'];
        if (!terminalStatuses.includes(currentJob.status)) {
          timerRef.current = window.setTimeout(poll, 2000);
        }
      }
    };

    poll();

    return () => {
      active = false;
      if (timerRef.current !== null) {
        window.clearTimeout(timerRef.current);
      }
    };
  }, [id]);

  const handleDownloadZip = async () => {
    try {
      await downloadJobZip(id);
    } catch (err: any) {
      alert(err.response?.data?.detail || err.message || 'Failed to download ZIP.');
    }
  };

  const handleDownloadCert = async (certId: number) => {
    try {
      await downloadCertificate(certId);
    } catch (err: any) {
      alert(err.response?.data?.detail || err.message || 'Failed to download PDF.');
    }
  };

  if (isLoading) {
    return <div className="p-10 text-center text-gray-500">Loading job details...</div>;
  }

  if (error) {
    return (
      <div className="max-w-4xl mx-auto py-10 px-4 sm:px-6 lg:px-8">
        <div className="bg-red-50 border-l-4 border-red-400 p-4">
          <p className="text-red-700 flex items-center">
            <AlertCircle className="w-5 h-5 mr-2" /> {error}
          </p>
        </div>
        <Link to="/" className="mt-4 inline-flex items-center text-indigo-600 hover:text-indigo-900">
          <ArrowLeft className="w-4 h-4 mr-1" /> Back to Dashboard
        </Link>
      </div>
    );
  }

  if (!job) return null;

  const isFinished = ['COMPLETED', 'COMPLETED_WITH_ERRORS', 'FAILED'].includes(job.status);
  const canDownloadZip = isFinished && job.success_count > 0;

  return (
    <div className="max-w-6xl mx-auto py-10 px-4 sm:px-6 lg:px-8">
      <Link to="/" className="inline-flex items-center text-indigo-600 hover:text-indigo-900 mb-6">
        <ArrowLeft className="w-4 h-4 mr-1" /> Back to Dashboard
      </Link>

      <div className="bg-white shadow rounded-lg overflow-hidden mb-8">
        <div className="px-6 py-5 border-b border-gray-200 sm:flex sm:items-center sm:justify-between bg-gray-50">
          <div>
            <h2 className="text-xl font-bold text-gray-900">Job #{job.id} - {job.event_name}</h2>
            <p className="text-sm text-gray-500 mt-1">Date: {job.event_date}</p>
          </div>
          <div className="mt-4 sm:mt-0">
            {canDownloadZip && (
              <button
                onClick={handleDownloadZip}
                className="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700"
              >
                <Download className="w-4 h-4 mr-2" /> Download All (ZIP)
              </button>
            )}
          </div>
        </div>
        
        <div className="px-6 py-5">
          <dl className="grid grid-cols-2 gap-x-4 gap-y-6 sm:grid-cols-4">
            <div className="sm:col-span-1">
              <dt className="text-sm font-medium text-gray-500">Status</dt>
              <dd className="mt-1"><StatusBadge status={job.status} /></dd>
            </div>
            <div className="sm:col-span-1">
              <dt className="text-sm font-medium text-gray-500">Total Recipients</dt>
              <dd className="mt-1 text-sm text-gray-900">{job.total_count}</dd>
            </div>
            <div className="sm:col-span-1">
              <dt className="text-sm font-medium text-gray-500">Successful</dt>
              <dd className="mt-1 text-sm text-green-600 font-medium">{job.success_count}</dd>
            </div>
            <div className="sm:col-span-1">
              <dt className="text-sm font-medium text-gray-500">Failed</dt>
              <dd className="mt-1 text-sm text-red-600 font-medium">{job.failure_count}</dd>
            </div>
          </dl>

          <div className="mt-6">
            <div className="flex justify-between text-sm text-gray-500">
              <span>Progress</span>
              <span>{job.progress}%</span>
            </div>
            <ProgressBar progress={job.progress} />
          </div>
        </div>
      </div>

      <div className="bg-white shadow rounded-lg overflow-hidden">
        <div className="px-6 py-5 border-b border-gray-200">
          <h3 className="text-lg font-medium text-gray-900">Certificate Results</h3>
        </div>
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Recipient</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Message</th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">Action</th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {certificates.length === 0 ? (
                <tr>
                  <td colSpan={4} className="px-6 py-4 text-center text-sm text-gray-500">
                    No recipients found for this job.
                  </td>
                </tr>
              ) : (
                certificates.map((cert) => (
                  <tr key={cert.id}>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm font-medium text-gray-900">{cert.recipient_name}</div>
                      <div className="text-sm text-gray-500">{cert.recipient_email}</div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <StatusBadge status={cert.status} />
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-500">
                      {cert.error_message ? <span className="text-red-500">{cert.error_message}</span> : '-'}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                      {cert.status === 'SUCCESS' && (
                        <button
                          onClick={() => handleDownloadCert(cert.id)}
                          className="text-indigo-600 hover:text-indigo-900 flex items-center justify-end w-full"
                        >
                          <Download className="w-4 h-4 mr-1" /> PDF
                        </button>
                      )}
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
