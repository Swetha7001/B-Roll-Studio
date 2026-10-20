import React, { useEffect, useState } from 'react';
import {
  Download, FileJson, RefreshCw, AlertCircle,
  ArrowLeft, ShieldCheck, DollarSign, Clock, Layers
} from 'lucide-react';
import { getJobResult } from '../services/api';
import { VideoPlayer } from '../components/VideoPlayer';
import { SceneList } from '../components/SceneList';
import { ClipSwapModal } from '../components/ClipSwapModal';
import { ManifestModal } from '../components/ManifestModal';
import { ManifestData, TimelineData } from '../types';

interface JobResultProps {
  jobId: string;
  onBack: () => void;
}

export const JobResult: React.FC<JobResultProps> = ({ jobId, onBack }) => {
  const [data, setData] = useState<{
    job_id: string;
    status: string;
    aspect_ratios: string[];
    artifacts: Record<string, string>;
    manifest?: ManifestData;
    timeline?: TimelineData;
    cost_estimate_usd: number;
    processing_duration_sec: number;
  } | null>(null);

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const [selectedRatio, setSelectedRatio] = useState<string>('16:9');
  const [swapModalOpen, setSwapModalOpen] = useState(false);
  const [activeSwapIndex, setActiveSwapIndex] = useState(0);
  const [manifestModalOpen, setManifestModalOpen] = useState(false);

  const loadResult = () => {
    setLoading(true);
    getJobResult(jobId)
      .then((res) => {
        setData(res);
        if (res.aspect_ratios && res.aspect_ratios.length > 0) {
          setSelectedRatio(res.aspect_ratios[0]);
        }
      })
      .catch((err) => setError(err.message || 'Failed to load video results'))
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    loadResult();
  }, [jobId]);

  const handleOpenSwap = (sceneIndex: number) => {
    setActiveSwapIndex(sceneIndex);
    setSwapModalOpen(true);
  };

  const handleSwapSuccess = () => {
    loadResult();
  };

  if (loading) {
    return (
      <div className="max-w-7xl mx-auto px-4 py-24 text-center text-slate-400 space-y-3">
        <RefreshCw className="w-8 h-8 animate-spin mx-auto text-cyan-400" />
        <p className="text-sm">Loading finished video and scene manifests...</p>
      </div>
    );
  }

  if (error || !data) {
    return (
      <div className="max-w-xl mx-auto px-4 py-16 text-center space-y-4">
        <AlertCircle className="w-10 h-10 text-rose-500 mx-auto" />
        <h2 className="text-lg font-bold text-white">Failed to load result</h2>
        <p className="text-xs text-rose-300">{error || 'Unknown error'}</p>
        <button
          onClick={onBack}
          className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-white rounded-xl text-xs font-medium"
        >
          Return to Dashboard
        </button>
      </div>
    );
  }

  const artifacts = data.artifacts || {};
  const timelineScenes = data.timeline?.scenes || [];

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 animate-fadeIn space-y-6">
      {/* Top Header */}
      <div className="flex flex-wrap items-center justify-between gap-4 pb-4 border-b border-slate-800">
        <div className="flex items-center space-x-3">
          <button
            onClick={onBack}
            className="p-2 rounded-xl bg-slate-900 border border-slate-800 text-slate-400 hover:text-white hover:bg-slate-800 transition-colors"
          >
            <ArrowLeft className="w-4 h-4" />
          </button>
          <div>
            <div className="flex items-center space-x-2">
              <h1 className="text-xl sm:text-2xl font-bold text-white tracking-tight">
                Finished Video Production
              </h1>
              <span className="text-[10px] font-semibold px-2 py-0.5 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                SUCCEEDED
              </span>
            </div>
            <p className="text-xs text-slate-400 font-mono mt-0.5">Job: {data.job_id}</p>
          </div>
        </div>

        {/* Action Buttons */}
        <div className="flex flex-wrap items-center gap-2">
          <button
            onClick={() => setManifestModalOpen(true)}
            className="px-3.5 py-2 rounded-xl bg-slate-800 hover:bg-slate-750 text-slate-300 text-xs font-medium border border-slate-700 transition-colors flex items-center space-x-1.5"
          >
            <FileJson className="w-3.5 h-3.5 text-cyan-400" />
            <span>Manifest & Audit</span>
          </button>

          {/* Download Current Ratio MP4 */}
          {artifacts[`video_${selectedRatio.replace(':', '_')}`] && (
            <a
              href={artifacts[`video_${selectedRatio.replace(':', '_')}`]}
              download={`video_${selectedRatio.replace(':', '_')}.mp4`}
              className="px-4 py-2 rounded-xl bg-gradient-to-r from-cyan-500 to-violet-600 text-white text-xs font-semibold shadow-lg shadow-cyan-500/20 hover:opacity-95 transition-all flex items-center space-x-1.5"
            >
              <Download className="w-3.5 h-3.5" />
              <span>Download MP4 ({selectedRatio})</span>
            </a>
          )}
        </div>
      </div>

      {/* Metrics Badge Bar */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
        <div className="p-3 bg-slate-900/70 border border-slate-800 rounded-xl flex items-center space-x-3">
          <Clock className="w-4 h-4 text-cyan-400" />
          <div>
            <p className="text-[11px] text-slate-400">Render Time</p>
            <p className="text-xs font-bold font-mono text-white">{data.processing_duration_sec.toFixed(1)}s</p>
          </div>
        </div>

        <div className="p-3 bg-slate-900/70 border border-slate-800 rounded-xl flex items-center space-x-3">
          <DollarSign className="w-4 h-4 text-emerald-400" />
          <div>
            <p className="text-[11px] text-slate-400">Production Cost</p>
            <p className="text-xs font-bold font-mono text-emerald-400">${data.cost_estimate_usd.toFixed(4)}</p>
          </div>
        </div>

        <div className="p-3 bg-slate-900/70 border border-slate-800 rounded-xl flex items-center space-x-3">
          <ShieldCheck className="w-4 h-4 text-emerald-400" />
          <div>
            <p className="text-[11px] text-slate-400">Commercial Safe</p>
            <p className="text-xs font-bold font-mono text-slate-200">100% Licence Clean</p>
          </div>
        </div>

        <div className="p-3 bg-slate-900/70 border border-slate-800 rounded-xl flex items-center space-x-3">
          <Layers className="w-4 h-4 text-violet-400" />
          <div>
            <p className="text-[11px] text-slate-400">Aspect Ratios</p>
            <p className="text-xs font-bold font-mono text-slate-200">{data.aspect_ratios.join(', ')}</p>
          </div>
        </div>
      </div>

      {/* Main Grid: Video Player on Left, Scene List on Right */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
        {/* Left Column: Video Player & Download Links (7 cols) */}
        <div className="lg:col-span-7 space-y-4">
          <VideoPlayer
            artifacts={artifacts}
            selectedRatio={selectedRatio}
            setSelectedRatio={setSelectedRatio}
            availableRatios={data.aspect_ratios}
          />

          {/* Downloadable Artifacts Drawer */}
          <div className="p-4 bg-slate-900/60 border border-slate-800 rounded-2xl space-y-2.5">
            <h4 className="text-xs font-semibold uppercase tracking-wider text-slate-400">
              Downloadable Job Artifacts:
            </h4>
            <div className="grid grid-cols-2 sm:grid-cols-3 gap-2">
              {Object.entries(artifacts).map(([key, url]) => (
                <a
                  key={key}
                  href={url}
                  download
                  className="p-2.5 rounded-xl bg-slate-950/80 border border-slate-800 hover:border-slate-700 text-slate-300 hover:text-white transition-all text-xs flex items-center justify-between group"
                >
                  <span className="truncate max-w-[120px] font-mono text-[11px]">{key}</span>
                  <Download className="w-3 h-3 text-cyan-400 group-hover:translate-y-0.5 transition-transform" />
                </a>
              ))}
            </div>
          </div>
        </div>

        {/* Right Column: Interactive Scene Breakdown (5 cols) */}
        <div className="lg:col-span-5 bg-slate-900/60 border border-slate-800 rounded-2xl p-5 shadow-xl">
          <SceneList scenes={timelineScenes} onSwapClick={handleOpenSwap} />
        </div>
      </div>

      {/* Clip Swap Modal */}
      <ClipSwapModal
        jobId={data.job_id}
        sceneIndex={activeSwapIndex}
        isOpen={swapModalOpen}
        onClose={() => setSwapModalOpen(false)}
        onSwapSuccess={handleSwapSuccess}
      />

      {/* Manifest Modal */}
      <ManifestModal
        manifest={data.manifest || null}
        isOpen={manifestModalOpen}
        onClose={() => setManifestModalOpen(false)}
      />
    </div>
  );
};
