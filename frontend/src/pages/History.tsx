import React, { useEffect, useState } from 'react';
import { Search, CheckCircle2, Clock, AlertTriangle, ArrowRight, RefreshCw, Film } from 'lucide-react';
import { listJobs } from '../services/api';
import { JobStatusResponse } from '../types';

interface HistoryProps {
  onOpenJob: (jobId: string) => void;
}

export const History: React.FC<HistoryProps> = ({ onOpenJob }) => {
  const [jobs, setJobs] = useState<JobStatusResponse[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [statusFilter, setStatusFilter] = useState<string>('all');

  const fetchJobs = () => {
    setLoading(true);
    const filter = statusFilter === 'all' ? undefined : statusFilter;
    listJobs(filter)
      .then((res) => setJobs(res.jobs))
      .catch((err) => console.error(err))
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    fetchJobs();
  }, [statusFilter]);

  const filteredJobs = jobs.filter((j) => {
    if (!searchQuery.trim()) return true;
    return j.job_id.toLowerCase().includes(searchQuery.toLowerCase());
  });

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 animate-fadeIn space-y-6">
      {/* Header */}
      <div className="flex flex-wrap items-center justify-between gap-4 pb-4 border-b border-slate-800">
        <div>
          <h1 className="text-2xl font-bold text-white tracking-tight">Production History</h1>
          <p className="text-xs text-slate-400 mt-1">
            Searchable job repository, execution diagnostics, and downloadable artifacts.
          </p>
        </div>
        <button
          onClick={fetchJobs}
          className="px-3.5 py-2 rounded-xl bg-slate-900 border border-slate-800 text-xs font-medium text-slate-300 hover:text-white flex items-center space-x-1.5"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
          <span>Refresh</span>
        </button>
      </div>

      {/* Filter and Search Bar */}
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div className="relative flex-1 min-w-[240px]">
          <Search className="w-4 h-4 text-slate-500 absolute left-3.5 top-3" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search by Job ID..."
            className="w-full pl-10 pr-4 py-2 bg-slate-900/80 border border-slate-800 rounded-xl text-xs text-white placeholder-slate-500 focus:outline-none focus:border-cyan-500"
          />
        </div>

        <div className="flex items-center space-x-1.5 bg-slate-900/80 p-1 rounded-xl border border-slate-800 text-xs">
          {['all', 'succeeded', 'running', 'failed'].map((st) => (
            <button
              key={st}
              onClick={() => setStatusFilter(st)}
              className={`px-3 py-1 rounded-lg capitalize transition-colors ${
                statusFilter === st
                  ? 'bg-cyan-500/20 text-cyan-300 font-semibold border border-cyan-500/30'
                  : 'text-slate-400 hover:text-white'
              }`}
            >
              {st}
            </button>
          ))}
        </div>
      </div>

      {/* Jobs Table */}
      <div className="bg-slate-900/80 border border-slate-800 rounded-2xl overflow-hidden shadow-xl">
        {loading ? (
          <div className="p-12 text-center text-slate-500 text-sm">
            <RefreshCw className="w-5 h-5 animate-spin mx-auto mb-2 text-cyan-400" />
            Loading job list...
          </div>
        ) : filteredJobs.length === 0 ? (
          <div className="p-12 text-center text-slate-500 text-xs space-y-2">
            <Film className="w-8 h-8 text-slate-600 mx-auto" />
            <p>No jobs found matching criteria.</p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-slate-950/80 text-slate-400 font-semibold border-b border-slate-800 uppercase tracking-wider text-[10px]">
                <tr>
                  <th className="px-5 py-3.5">Job ID</th>
                  <th className="px-5 py-3.5">Status</th>
                  <th className="px-5 py-3.5">Progress</th>
                  <th className="px-5 py-3.5">Created At</th>
                  <th className="px-5 py-3.5 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60 font-mono">
                {filteredJobs.map((job) => {
                  const isSuccess = job.status === 'succeeded';
                  const isFailed = job.status === 'failed';
                  const isRunning = job.status === 'running' || job.status === 'queued';

                  return (
                    <tr
                      key={job.job_id}
                      onClick={() => onOpenJob(job.job_id)}
                      className="hover:bg-slate-850/50 cursor-pointer transition-colors"
                    >
                      <td className="px-5 py-4 font-semibold text-slate-200">
                        {job.job_id}
                      </td>
                      <td className="px-5 py-4 font-sans">
                        <span
                          className={`px-2 py-0.5 rounded-full text-[10px] font-semibold uppercase tracking-wider inline-flex items-center space-x-1 ${
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
                      </td>
                      <td className="px-5 py-4 text-slate-400">
                        {job.progress}% ({job.current_stage})
                      </td>
                      <td className="px-5 py-4 text-slate-400 font-sans text-[11px]">
                        {new Date(job.created_at).toLocaleString()}
                      </td>
                      <td className="px-5 py-4 text-right font-sans">
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            onOpenJob(job.job_id);
                          }}
                          className="px-3 py-1 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-medium inline-flex items-center space-x-1"
                        >
                          <span>Inspect</span>
                          <ArrowRight className="w-3 h-3 text-cyan-400" />
                        </button>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
};
