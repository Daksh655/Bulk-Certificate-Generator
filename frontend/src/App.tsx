import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { DashboardPage } from './pages/DashboardPage';
import { JobDetailsPage } from './pages/JobDetailsPage';

function App() {
  return (
    <BrowserRouter>
      <div className="min-h-screen bg-slate-50">
        <Routes>
          <Route path="/" element={<DashboardPage />} />
          <Route path="/jobs/:jobId" element={<JobDetailsPage />} />
        </Routes>
      </div>
    </BrowserRouter>
  );
}

export default App;
