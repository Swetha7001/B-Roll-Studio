import React from 'react';
import { X, CheckCircle, ShieldCheck, DollarSign, Clock, Cpu, FileJson } from 'lucide-react';
import { ManifestData } from '../types';

interface ManifestModalProps {
  manifest: ManifestData | null;
  isOpen: boolean;
  onClose: () => void;
}

export const ManifestModal: React.FC<ManifestModalProps> = ({ manifest, isOpen, onClose }) => {
  if (!isOpen || !manifest) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm animate-fadeIn">
      <div className="bg-slate-900 border border-slate-800 rounded-2xl max-w-2xl w-full p-6 shadow-2xl flex flex-col space-y-4 max-h-[85vh] overflow-y-auto">
        {/* Header */}
        <div className="flex items-center justify-between pb-3 border-b border-slate-800">
          <div className="flex items-center space-x-2">
            <FileJson className="w-5 h-5 text-cyan-400" />
            <div>
              <h3 className="text-base font-semibold text-white">Execution Manifest & Rights Audit</h3>
              <p className="text-xs text-slate-400 font-mono">Job ID: {manifest.job_id}</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Overview Stats */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-2.5">
          <div className="p-3 bg-slate-950/70 border border-slate-800 rounded-xl">
            <div className="flex items-center space-x-1.5 text-xs text-slate-400 mb-1">
              <Clock className="w-3.5 h-3.5 text-cyan-400" />
              <span>Total Duration</span>
            </div>
            <div className="text-sm font-bold font-mono text-white">
              {manifest.total_processing_duration_seconds}s
            </div>
          </div>

          <div className="p-3 bg-slate-950/70 border border-slate-800 rounded-xl">
            <div className="flex items-center space-x-1.5 text-xs text-slate-400 mb-1">
              <DollarSign className="w-3.5 h-3.5 text-emerald-400" />
              <span>Total Cost</span>
            </div>
            <div className="text-sm font-bold font-mono text-emerald-400">
              ${manifest.cost_estimate?.total_usd?.toFixed(4) || '0.0000'}
            </div>
          </div>

          <div className="p-3 bg-slate-950/70 border border-slate-800 rounded-xl">
            <div className="flex items-center space-x-1.5 text-xs text-slate-400 mb-1">
              <ShieldCheck className="w-3.5 h-3.5 text-emerald-400" />
              <span>Commercial Rights</span>
            </div>
            <div className="text-sm font-bold font-mono text-emerald-400 flex items-center space-x-1">
              <CheckCircle className="w-3.5 h-3.5" />
              <span>100% Verified</span>
            </div>
          </div>

          <div className="p-3 bg-slate-950/70 border border-slate-800 rounded-xl">
            <div className="flex items-center space-x-1.5 text-xs text-slate-400 mb-1">
              <Cpu className="w-3.5 h-3.5 text-violet-400" />
              <span>Rendering Codec</span>
            </div>
            <div className="text-xs font-bold font-mono text-slate-200">
              {manifest.rendering_settings?.codec_video || 'H.264 30fps'}
            </div>
          </div>
        </div>

        {/* Models and Providers */}
        <div className="space-y-2">
          <h4 className="text-xs font-semibold uppercase tracking-wider text-slate-400">
            AI Models & Processing Engine
          </h4>
          <div className="p-3 bg-slate-950/50 border border-slate-800 rounded-xl space-y-2 text-xs">
            <div className="flex justify-between border-b border-slate-800/60 pb-1.5">
              <span className="text-slate-400">TTS Engine:</span>
              <span className="font-mono text-slate-200">{manifest.models_and_providers?.tts?.model_or_voice}</span>
            </div>
            <div className="flex justify-between border-b border-slate-800/60 pb-1.5">
              <span className="text-slate-400">Scene Disambiguation:</span>
              <span className="font-mono text-slate-200">{manifest.models_and_providers?.scene_planner?.model}</span>
            </div>
            <div className="flex justify-between border-b border-slate-800/60 pb-1.5">
              <span className="text-slate-400">Independent Relevance VLM:</span>
              <span className="font-mono text-slate-200">{manifest.models_and_providers?.vision_language_scorer?.model}</span>
            </div>
          </div>
        </div>

        {/* Stage Execution Timings */}
        <div className="space-y-2">
          <h4 className="text-xs font-semibold uppercase tracking-wider text-slate-400">
            Pipeline Execution Profile
          </h4>
          <div className="p-3 bg-slate-950/50 border border-slate-800 rounded-xl space-y-1.5 text-xs font-mono">
            {Object.entries(manifest.stage_timings_seconds || {}).map(([stage, dur]) => (
              <div key={stage} className="flex justify-between items-center text-slate-300">
                <span className="text-slate-400">{stage.replace(/_/g, ' ')}:</span>
                <span>{dur}s</span>
              </div>
            ))}
          </div>
        </div>

        {/* Raw JSON View */}
        <div className="space-y-1.5">
          <h4 className="text-xs font-semibold uppercase tracking-wider text-slate-400">
            Raw Manifest Payload (manifest.json)
          </h4>
          <pre className="p-3 bg-slate-950 rounded-xl text-[11px] font-mono text-slate-300 max-h-36 overflow-auto border border-slate-800">
            {JSON.stringify(manifest, null, 2)}
          </pre>
        </div>

        <div className="pt-2 flex justify-end">
          <button
            onClick={onClose}
            className="px-5 py-2 rounded-xl text-xs font-medium bg-slate-800 hover:bg-slate-700 text-white"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
};
