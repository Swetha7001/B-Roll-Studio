import React, { useEffect, useState } from 'react';
import {
  CheckCircle2, AlertTriangle,
  FileSearch, Mic, Scissors, Film, PackageCheck, RefreshCw
} from 'lucide-react';
import { getJobStatus } from '../services/api';
import { JobStatusResponse } from '../types';

interface JobProgressProps {
  jobId: string;
  onCompleted: (jobId: string) => void;
  onBack: () => void;
}

const STAGES = [
  { key: 'ingesting', label: '1. Ingestion', desc: 'Validating audio format & limits', icon: FileSearch },
  { key: 'narrating', label: '2. Narration', desc: 'Synthesizing voice & acoustic cues', icon: Mic },
  { key: 'planning', label: '3. Scene Planning', desc: 'Semantic disambiguation & timing', icon: Scissors },
  { key: 'selecting_footage', label: '4. Footage Match', desc: 'Dual-source commercial selection', icon: Film },
  { key: 'rendering', label: '5. FFmpeg Render', desc: 'Multi-aspect video & audio normalisation', icon: Film },
  { key: 'packaging', label: '6. Packaging', desc: 'Manifest & timeline generation', icon: PackageCheck },
];

export const JobProgress: React.FC<JobProgressProps> = ({ jobId, onCompleted, onBack }) => {
  const [job, setJob] = useState<JobStatusResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let timer: any;

    const poll = async () => {
      try {
        const data = await getJobStatus(jobId);
        setJob(data);

        if (data.status === 'succeeded') {
          setTimeout(() => onCompleted(jobId), 1200);
        } else if (data.status === 'failed') {
          setError(data.error?.message || 'Processing failed');
        } else {
          timer = setTimeout(poll, 1500);
        }
      } catch (err: any) {
        setError(err.message || 'Error fetching status');
        timer = setTimeout(poll, 3000);
      }
    };

    poll();
    return () => clearTimeout(timer);
  }, [jobId, onCompleted]);

  const currentStageIndex = STAGES.findIndex((s) => s.key === job?.current_stage);
  const progressPercent = job?.progress || 0;

  return (
    <div className="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8 py-12 animate-fadeIn space-y-8">
      {/* Header */}
      <div className="text-center space-y-2">
        <div className="inline-flex items-center space-x-2 px-3 py-1 rounded-full bg-cyan-500/10 border border-cyan-500/20 text-cyan-300 text-xs font-mono">
          <span>Job ID: {jobId}</span>
        </div>
        <h1 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight">
          Rendering Your Video
        </h1>
        <p className="text-xs sm:text-sm text-slate-400">
          The background engine is processing your voiceover and matching licence-clean B-roll.
        </p>
      </div>

      {/* Progress Card */}
      <div className="p-8 rounded-3xl bg-slate-900/90 border border-slate-800 shadow-2xl space-y-6">
        {/* Progress bar */}
        <div className="space-y-2">
          <div className="flex justify-between items-center text-xs font-mono">
            <span className="text-slate-400 uppercase tracking-wider">
              {job?.status === 'succeeded' ? 'Rendering Complete' : `Stage: ${job?.current_stage || 'Initializing'}`}
            </span>
            <span className="text-cyan-400 font-bold text-sm">{progressPercent}%</span>
          </div>

          <div className="w-full h-3 bg-slate-950 rounded-full overflow-hidden p-0.5 border border-slate-800">
            <div
              className="h-full bg-gradient-to-r from-cyan-500 via-indigo-500 to-violet-600 rounded-full transition-all duration-500"
              style={{ width: `${progressPercent}%` }}
            />
          </div>
        </div>

        {/* Stage List */}
        <div className="space-y-3 pt-2">
          {STAGES.map((st, idx) => {
            const isCompleted = currentStageIndex > idx || job?.status === 'succeeded';
            const isCurrent = currentStageIndex === idx && job?.status !== 'succeeded';
            const Icon = st.icon;

            return (
              <div
                key={st.key}
                className={`p-3.5 rounded-2xl border transition-all flex items-center justify-between ${
                  isCompleted
                    ? 'bg-emerald-500/5 border-emerald-500/20 text-slate-200'
                    : isCurrent
                    ? 'bg-cyan-500/10 border-cyan-500/40 text-white shadow-lg'
                    : 'bg-slate-950/40 border-slate-900 text-slate-500'
                }`}
              >
                <div className="flex items-center space-x-3.5">
                  <div
                    className={`w-9 h-9 rounded-xl flex items-center justify-center border ${
                      isCompleted
                        ? 'bg-emerald-500/10 border-emerald-500/30 text-emerald-400'
                        : isCurrent
                        ? 'bg-cyan-500/20 border-cyan-500 text-cyan-300 animate-pulse'
                        : 'bg-slate-900 border-slate-800 text-slate-600'
                    }`}
                  >
                    <Icon className="w-4 h-4" />
                  </div>
                  <div>
                    <p className="text-xs sm:text-sm font-semibold">{st.label}</p>
                    <p className="text-[11px] text-slate-400 hidden sm:block">{st.desc}</p>
                  </div>
                </div>

                <div>
                  {isCompleted && <CheckCircle2 className="w-5 h-5 text-emerald-400" />}
                  {isCurrent && <RefreshCw className="w-4 h-4 text-cyan-400 animate-spin" />}
                  {!isCompleted && !isCurrent && <span className="w-2 h-2 rounded-full bg-slate-800 inline-block" />}
                </div>
              </div>
            );
          })}
        </div>

        {/* Error Details */}
        {error && (
          <div className="p-4 rounded-xl bg-rose-500/10 border border-rose-500/20 text-rose-400 text-xs flex items-start space-x-3">
            <AlertTriangle className="w-5 h-5 flex-shrink-0 mt-0.5" />
            <div className="space-y-1">
              <p className="font-semibold">Generation Failed</p>
              <p className="text-xs text-rose-300">{error}</p>
              <button
                onClick={onBack}
                className="mt-2 text-xs font-semibold underline hover:text-white"
              >
                Return to Editor
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
