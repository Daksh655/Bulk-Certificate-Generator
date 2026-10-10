import React from 'react';

export const StatusBadge: React.FC<{ status: string }> = ({ status }) => {
  let color = "bg-gray-100 text-gray-800";
  if (status === "PENDING" || status === "PROCESSING") {
    color = "bg-blue-100 text-blue-800";
  } else if (status === "SUCCESS" || status === "COMPLETED") {
    color = "bg-green-100 text-green-800";
  } else if (status === "FAILED") {
    color = "bg-red-100 text-red-800";
  } else if (status === "COMPLETED_WITH_ERRORS") {
    color = "bg-yellow-100 text-yellow-800";
  }

  return (
    <span className={`px-2.5 py-0.5 inline-flex text-xs leading-5 font-semibold rounded-full ${color}`}>
      {status}
    </span>
  );
};

export const ProgressBar: React.FC<{ progress: number }> = ({ progress }) => {
  return (
    <div className="w-full bg-gray-200 rounded-full h-2.5 mt-2">
      <div 
        className="bg-indigo-600 h-2.5 rounded-full transition-all duration-300" 
        style={{ width: `${progress}%` }}
      ></div>
    </div>
  );
};
