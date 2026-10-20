import { useState } from 'react';
import { Navbar } from './components/Navbar';
import { Dashboard } from './pages/Dashboard';
import { CreateJob } from './pages/CreateJob';
import { GoogleAIStudio } from './pages/GoogleAIStudio';
import { JobProgress } from './pages/JobProgress';
import { JobResult } from './pages/JobResult';
import { History } from './pages/History';

export function App() {
  const [currentTab, setCurrentTab] = useState<'dashboard' | 'create' | 'google-studio' | 'progress' | 'result' | 'history'>('dashboard');
  const [activeJobId, setActiveJobId] = useState<string | null>(null);

  const handleJobCreated = (jobId: string) => {
    setActiveJobId(jobId);
    setCurrentTab('progress');
  };

  const handleJobCompleted = (jobId: string) => {
    setActiveJobId(jobId);
    setCurrentTab('result');
  };

  const handleOpenJob = (jobId: string) => {
    setActiveJobId(jobId);
    setCurrentTab('result');
  };

  return (
    <div className="min-h-screen bg-[#090d16] text-slate-100 flex flex-col font-sans selection:bg-cyan-500 selection:text-white">
      {/* Top Navigation */}
      <Navbar currentTab={currentTab} setCurrentTab={(tab) => setCurrentTab(tab as any)} />

      {/* Main Content Area */}
      <main className="flex-1 pb-16">
        {currentTab === 'dashboard' && (
          <Dashboard
            onNewVideo={() => setCurrentTab('create')}
            onOpenJob={handleOpenJob}
          />
        )}

        {currentTab === 'create' && (
          <CreateJob onJobCreated={handleJobCreated} />
        )}

        {currentTab === 'google-studio' && (
          <GoogleAIStudio />
        )}

        {currentTab === 'progress' && activeJobId && (
          <JobProgress
            jobId={activeJobId}
            onCompleted={handleJobCompleted}
            onBack={() => setCurrentTab('dashboard')}
          />
        )}

        {currentTab === 'result' && activeJobId && (
          <JobResult
            jobId={activeJobId}
            onBack={() => setCurrentTab('dashboard')}
          />
        )}

        {currentTab === 'history' && (
          <History onOpenJob={handleOpenJob} />
        )}
      </main>

      {/* Footer */}
      <footer className="border-t border-slate-900 bg-slate-950/60 py-6 text-center text-xs text-slate-600">
        <div className="max-w-7xl mx-auto px-4 flex flex-col sm:flex-row items-center justify-between gap-2">
          <span>IncuBrix Engineering Assessment 3 • Script to B-Roll Video Engine</span>
          <span className="font-mono text-[11px] text-slate-500">v1.0.0 • 100% Commercial-Use Clean</span>
        </div>
      </footer>
    </div>
  );
}

export default App;
