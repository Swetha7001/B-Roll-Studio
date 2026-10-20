import React, { useEffect, useState } from 'react';
import { PlusCircle, Film, CheckCircle2, Clock, AlertTriangle, ArrowRight, Sparkles, RefreshCw } from 'lucide-react';
import { listJobs } from '../services/api';
import { JobStatusResponse } from '../types';

interface DashboardProps {
  onNewVideo: () => void;
  onOpenJob: (jobId: string) => void;
}

export const Dashboard: React.FC<DashboardProps> = ({ onNewVideo, onOpenJob }) => {
  const [jobs, setJobs] = useState<JobStatusResponse[]>([]);
  const [loading, setLoading] = useState(true);

  const fetchJobs = () => {
    setLoading(true);
    listJobs()
      .then((data) => setJobs(data.jobs))
      .catch((err) => console.error(err))
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    fetchJobs();
  }, []);

  const succeededCount = jobs.filter((j) => j.status === 'succeeded').length;
  const runningCount = jobs.filter((j) => j.status === 'running' || j.status === 'queued').length;

  return (
    <div className="space-y-8 animate-fadeIn max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Hero Banner */}
      <div className="relative overflow-hidden rounded-3xl bg-gradient-to-r from-slate-900 via-indigo-950/40 to-slate-900 border border-slate-800 p-8 sm:p-10 shadow-2xl">
        <div className="absolute -right-12 -top-12 w-64 h-64 bg-cyan-500/10 rounded-full blur-3xl pointer-events-none" />
        <div className="absolute right-48 -bottom-12 w-64 h-64 bg-violet-500/10 rounded-full blur-3xl pointer-events-none" />

        <div className="relative z-10 max-w-2xl space-y-4">
          <div className="inline-flex items-center space-x-2 px-3 py-1 rounded-full bg-cyan-500/10 border border-cyan-500/20 text-cyan-300 text-xs font-medium">
            <Sparkles className="w-3.5 h-3.5 text-cyan-400" />
            <span>AI Script & Voiceover to B-Roll Engine</span>
          </div>

          <h1 className="text-3xl sm:text-4xl font-extrabold text-white tracking-tight leading-tight">
            Turn your voiceover into a finished, <span className="bg-gradient-to-r from-cyan-400 to-violet-400 bg-clip-text text-transparent">licence-clean</span> video.
          </h1>

          <p className="text-sm sm:text-base text-slate-300 leading-relaxed">
            Automatic semantic scene planning, multi-ratio rendering (16:9, 9:16, 1:1), 100% commercial-use footage, and broadcast-grade caption sync.
          </p>

          <div className="pt-2 flex flex-wrap items-center gap-3">
            <button
              onClick={onNewVideo}
              className="px-6 py-3 rounded-xl bg-gradient-to-r from-cyan-500 to-violet-600 text-white font-semibold text-sm shadow-xl shadow-cyan-500/25 hover:opacity-95 transition-all flex items-center space-x-2"
            >
              <PlusCircle className="w-4 h-4" />
              <span>Create New Video</span>
            </button>
            <button
              onClick={fetchJobs}
              className="px-4 py-3 rounded-xl bg-slate-800/80 hover:bg-slate-800 text-slate-300 text-sm font-medium border border-slate-700/80 transition-colors flex items-center space-x-2"
            >
              <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
              <span>Refresh Projects</span>
            </button>
          </div>
        </div>
      </div>

      {/* Metrics Row */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <div className="p-5 rounded-2xl bg-slate-900/60 border border-slate-800/80 flex items-center justify-between">
          <div>
            <p className="text-xs font-medium text-slate-400">Total Projects</p>
            <p className="text-2xl font-bold font-mono text-white mt-1">{jobs.length}</p>
          </div>
          <div className="w-12 h-12 rounded-xl bg-cyan-500/10 text-cyan-400 flex items-center justify-center border border-cyan-500/20">
            <Film className="w-6 h-6" />
          </div>
        </div>

        <div className="p-5 rounded-2xl bg-slate-900/60 border border-slate-800/80 flex items-center justify-between">
          <div>
            <p className="text-xs font-medium text-slate-400">Completed Videos</p>
            <p className="text-2xl font-bold font-mono text-emerald-400 mt-1">{succeededCount}</p>
          </div>
          <div className="w-12 h-12 rounded-xl bg-emerald-500/10 text-emerald-400 flex items-center justify-center border border-emerald-500/20">
            <CheckCircle2 className="w-6 h-6" />
          </div>
        </div>

        <div className="p-5 rounded-2xl bg-slate-900/60 border border-slate-800/80 flex items-center justify-between">
          <div>
            <p className="text-xs font-medium text-slate-400">In Progress</p>
            <p className="text-2xl font-bold font-mono text-amber-400 mt-1">{runningCount}</p>
          </div>
          <div className="w-12 h-12 rounded-xl bg-amber-500/10 text-amber-400 flex items-center justify-center border border-amber-500/20">
            <Clock className="w-6 h-6" />
          </div>
        </div>
      </div>

      {/* Recent Projects Section */}
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <h2 className="text-lg font-bold text-white tracking-wide flex items-center space-x-2">
            <span>Recent Generation Jobs</span>
            <span className="text-xs font-normal text-slate-400">({jobs.length})</span>
          </h2>
        </div>

        {loading ? (
          <div className="p-12 text-center text-slate-500 text-sm">
            <RefreshCw className="w-6 h-6 animate-spin mx-auto mb-2 text-cyan-400" />
            Loading project history...
          </div>
        ) : jobs.length === 0 ? (
          /* Empty State */
          <div className="p-12 text-center rounded-2xl border border-dashed border-slate-800 bg-slate-950/40 space-y-3">
            <Film className="w-10 h-10 text-slate-600 mx-auto" />
            <h3 className="text-base font-semibold text-slate-300">No video projects yet</h3>
            <p className="text-xs text-slate-500 max-w-sm mx-auto">
              Start by typing a voiceover script or uploading an audio file to render your first B-roll video.
            </p>
            <button
              onClick={onNewVideo}
              className="mt-2 px-4 py-2 rounded-xl bg-cyan-500/10 hover:bg-cyan-500/20 text-cyan-400 text-xs font-medium border border-cyan-500/30 inline-flex items-center space-x-1.5"
            >
              <PlusCircle className="w-3.5 h-3.5" />
              <span>Create First Video</span>
            </button>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {jobs.map((job) => {
              const isSuccess = job.status === 'succeeded';
              const isFailed = job.status === 'failed';
              const isRunning = job.status === 'running' || job.status === 'queued';

              return (
                <div
                  key={job.job_id}
                  onClick={() => onOpenJob(job.job_id)}
                  className="p-5 rounded-2xl bg-slate-900/80 border border-slate-800 hover:border-cyan-500/40 hover:bg-slate-900 transition-all cursor-pointer flex flex-col justify-between space-y-4 group shadow-lg"
                >
                  <div className="space-y-2">
                    <div className="flex items-center justify-between">
                      <span className="text-[11px] font-mono text-slate-400">
                        {new Date(job.created_at).toLocaleDateString()} {new Date(job.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                      </span>
                      <span
                        className={`text-[10px] font-semibold px-2 py-0.5 rounded-full uppercase tracking-wider flex items-center space-x-1 ${
                          isSuccess
                            ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20'
                            : isFailed
                            ? 'bg-rose-500/10 text-rose-400 border border-rose-500/20'
                            : 'bg-amber-500/10 text-amber-400 border border-amber-500/20'
                        }`}
                      >
                        {isSuccess && <CheckCircle2 className="w-2.5 h-2.5" />}
                        {isFailed && <AlertTriangle className="w-2.5 h-2.5" />}
                        {isRunning && <Clock className="w-2.5 h-2.5 animate-spin" />}
                        <span>{job.status}</span>
                      </span>
                    </div>

                    <h4 className="text-sm font-semibold text-slate-200 group-hover:text-cyan-300 transition-colors line-clamp-1 font-mono">
                      Job {job.job_id.slice(0, 8)}...
                    </h4>

                    {isRunning && (
                      <div className="space-y-1">
                        <div className="flex justify-between text-[11px] text-slate-400">
                          <span>Stage: {job.current_stage}</span>
                          <span>{job.progress}%</span>
                        </div>
                        <div className="w-full h-1.5 bg-slate-800 rounded-full overflow-hidden">
                          <div
                            className="h-full bg-gradient-to-r from-cyan-500 to-violet-500 transition-all duration-300"
                            style={{ width: `${job.progress}%` }}
                          />
                        </div>
                      </div>
                    )}
                  </div>

                  <div className="pt-2 border-t border-slate-800/80 flex items-center justify-between text-xs text-slate-400">
                    <span className="text-[11px]">Click to inspect</span>
                    <ArrowRight className="w-3.5 h-3.5 group-hover:translate-x-1 transition-transform text-cyan-400" />
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
};
