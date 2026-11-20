import React, { useState, useEffect, useRef } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { createJob, getAllJobs } from '../api/jobs';
import { Users, RefreshCw, ChevronRight } from 'lucide-react';
import type { JobStatusResponse } from '../types';
import { StatusBadge, ProgressBar } from '../components/Shared';

export const DashboardPage: React.FC = () => {
  const [eventName, setEventName] = useState('');
  const [eventDate, setEventDate] = useState('');
  const [recipientsText, setRecipientsText] = useState('');
  const [searchJobId, setSearchJobId] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const navigate = useNavigate();

  // History state
  const [jobs, setJobs] = useState<JobStatusResponse[]>([]);
  const [isJobsLoading, setIsJobsLoading] = useState(true);
  const [jobsError, setJobsError] = useState<string | null>(null);
  const timerRef = useRef<number | null>(null);

  const fetchJobs = async () => {
    try {
      setJobsError(null);
      const data = await getAllJobs();
      setJobs(data);
      return data;
    } catch (err: any) {
      setJobsError(err.message || 'Failed to load existing jobs.');
      return null;
    } finally {
      setIsJobsLoading(false);
    }
  };

  useEffect(() => {
    let active = true;

    const poll = async () => {
      const currentJobs = await fetchJobs();
      if (!active) return;
      
      const hasProcessingJobs = currentJobs?.some(
        j => j.status === 'PENDING' || j.status === 'PROCESSING'
      );

      if (hasProcessingJobs) {
        timerRef.current = window.setTimeout(poll, 3000);
      }
    };

    poll();

    return () => {
      active = false;
      if (timerRef.current !== null) {
        window.clearTimeout(timerRef.current);
      }
    };
  }, []);

  const handleManualRefresh = () => {
    setIsJobsLoading(true);
    fetchJobs();
  };

  const handleCreateJob = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    if (!eventName.trim() || !eventDate) {
      setError('Event name and date are required.');
      return;
    }

    const lines = recipientsText.split('\n').map(l => l.trim()).filter(l => l);
    if (lines.length === 0) {
      setError('At least one recipient is required.');
      return;
    }

    const recipients = [];
    for (const line of lines) {
      const parts = line.split(',');
      if (parts.length !== 2) {
        setError(`Malformed recipient line: "${line}". Expected "Name,email".`);
        return;
      }
      const [name, email] = parts;
      if (!name.trim() || !email.trim()) {
        setError(`Malformed recipient line: "${line}". Name and email cannot be empty.`);
        return;
      }
      recipients.push({ name: name.trim(), email: email.trim() });
    }

    try {
      setIsSubmitting(true);
      const job = await createJob({
        event_name: eventName,
        event_date: eventDate,
        recipients,
      });
      navigate(`/jobs/${job.id}`);
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message || 'Failed to create job');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleSearchJob = (e: React.FormEvent) => {
    e.preventDefault();
    const id = parseInt(searchJobId.trim());
    if (id && !isNaN(id)) {
      navigate(`/jobs/${id}`);
    }
  };

  const recipientCount = recipientsText.split('\n').filter(l => l.trim()).length;

  return (
    <div className="max-w-5xl mx-auto py-10 px-4 sm:px-6 lg:px-8">
      <div className="text-center mb-12">
        <h1 className="text-4xl font-extrabold text-gray-900 tracking-tight">Bulk Certificate Generator</h1>
        <p className="mt-3 text-lg text-gray-500">Create, manage, and download certificates in bulk.</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mb-12">
        <div className="md:col-span-2">
          <div className="bg-white shadow rounded-lg px-6 py-8 h-full">
            <h2 className="text-xl font-bold text-gray-900 mb-6">Create New Job</h2>
            
            {error && (
              <div className="mb-4 bg-red-50 border-l-4 border-red-400 p-4">
                <p className="text-sm text-red-700">{error}</p>
              </div>
            )}

            <form onSubmit={handleCreateJob} className="space-y-6">
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Event Name</label>
                  <input
                    type="text"
                    value={eventName}
                    onChange={(e) => setEventName(e.target.value)}
                    className="w-full border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm p-2 border"
                    placeholder="E.g., Advanced Python Workshop"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Event Date</label>
                  <input
                    type="date"
                    value={eventDate}
                    onChange={(e) => setEventDate(e.target.value)}
                    className="w-full border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm p-2 border"
                  />
                </div>
              </div>

              <div>
                <div className="flex justify-between mb-1">
                  <label className="block text-sm font-medium text-gray-700">Recipients</label>
                  <span className="text-sm text-gray-500">{recipientCount} found</span>
                </div>
                <p className="text-xs text-gray-500 mb-2">Format: <code>Full Name,email@example.com</code> (one per line)</p>
                <textarea
                  rows={8}
                  value={recipientsText}
                  onChange={(e) => setRecipientsText(e.target.value)}
                  className="w-full border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm p-2 border font-mono"
                  placeholder="Rahul Sharma,rahul@gmail.com&#10;Priya Patel,priya@gmail.com"
                />
              </div>

              <div className="flex justify-end">
                <button
                  type="submit"
                  disabled={isSubmitting}
                  className="inline-flex justify-center py-2 px-4 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50"
                >
                  {isSubmitting ? 'Creating Job...' : 'Create Job'}
                </button>
              </div>
            </form>
          </div>
        </div>

        <div className="md:col-span-1 space-y-6">
          <div className="bg-white shadow rounded-lg px-6 py-8">
            <h2 className="text-lg font-bold text-gray-900 mb-4 flex items-center">
              <Users className="w-5 h-5 mr-2 text-indigo-600" /> Open Existing Job
            </h2>
            <form onSubmit={handleSearchJob}>
              <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700 mb-1">Job ID</label>
                <input
                  type="number"
                  value={searchJobId}
                  onChange={(e) => setSearchJobId(e.target.value)}
                  className="w-full border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm p-2 border"
                  placeholder="Enter numeric ID"
                />
              </div>
              <button
                type="submit"
                className="w-full justify-center py-2 px-4 border border-gray-300 shadow-sm text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
              >
                Open Job
              </button>
            </form>
          </div>
        </div>
      </div>

      <div className="bg-white shadow rounded-lg px-6 py-8">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-xl font-bold text-gray-900">Existing Jobs</h2>
          <button 
            onClick={handleManualRefresh}
            className="inline-flex items-center px-3 py-1.5 border border-gray-300 shadow-sm text-sm font-medium rounded text-gray-700 bg-white hover:bg-gray-50 focus:outline-none"
          >
            <RefreshCw className={`w-4 h-4 mr-2 ${isJobsLoading ? 'animate-spin text-indigo-600' : ''}`} />
            Refresh
          </button>
        </div>

        {jobsError ? (
          <div className="text-red-600 text-sm">{jobsError}</div>
        ) : jobs.length === 0 && !isJobsLoading ? (
          <div className="text-gray-500 text-sm text-center py-6">No jobs found.</div>
        ) : (
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Job</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Event Details</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Progress</th>
                  <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">Action</th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {jobs.map((job) => (
                  <tr key={job.id} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm font-medium text-gray-900">#{job.id}</div>
                      <div className="text-xs text-gray-500">{new Date(job.created_at).toLocaleString()}</div>
                    </td>
                    <td className="px-6 py-4">
                      <div className="text-sm text-gray-900">{job.event_name}</div>
                      <div className="text-xs text-gray-500">{job.event_date}</div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <StatusBadge status={job.status} />
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap w-48">
                      <div className="flex justify-between text-xs text-gray-500 mb-1">
                        <span>{job.progress}%</span>
                        <span>{job.success_count}/{job.total_count}</span>
                      </div>
                      <ProgressBar progress={job.progress} />
                      {job.failure_count > 0 && (
                        <div className="text-xs text-red-500 mt-1">{job.failure_count} failed</div>
                      )}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                      <Link to={`/jobs/${job.id}`} className="text-indigo-600 hover:text-indigo-900 inline-flex items-center">
                        View Job <ChevronRight className="w-4 h-4 ml-1" />
                      </Link>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
};
