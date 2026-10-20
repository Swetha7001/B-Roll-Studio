import React, { useState } from 'react';
import { X, RefreshCw, Zap, Check, AlertCircle } from 'lucide-react';
import { swapSceneClip } from '../services/api';

interface ClipSwapModalProps {
  jobId: string;
  sceneIndex: number;
  isOpen: boolean;
  onClose: () => void;
  onSwapSuccess: (data: any) => void;
}

const CLIP_PRESETS = [
  { id: 'stock-fin-001', name: 'Currency & Investment Wealth', provider: 'Curated Stock (Pexels Verified)' },
  { id: 'stock-tech-002', name: 'Data Center Rack Lights', provider: 'Curated Stock (Pexels Verified)' },
  { id: 'stock-work-003', name: 'Collaborative Office Work', provider: 'Curated Stock (Pexels Verified)' },
  { id: 'stock-trust-004', name: 'Handshake & Blueprint Review', provider: 'Curated Stock (Pexels Verified)' },
  { id: 'stock-stat-005', name: 'Financial Metrics & Growth Chart', provider: 'Curated Stock (Pexels Verified)' },
  { id: 'stock-nat-006', name: 'Expansive Blue Sky', provider: 'Curated Stock (Pexels Verified)' },
];

export const ClipSwapModal: React.FC<ClipSwapModalProps> = ({
  jobId,
  sceneIndex,
  isOpen,
  onClose,
  onSwapSuccess,
}) => {
  const [selectedClipId, setSelectedClipId] = useState(CLIP_PRESETS[0].id);
  const [customHint, setCustomHint] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [speedupResult, setSpeedupResult] = useState<any | null>(null);

  if (!isOpen) return null;

  const handleSwap = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const res = await swapSceneClip(jobId, sceneIndex, {
        new_clip_id: selectedClipId,
        new_visual_hint: customHint || undefined,
      });
      setSpeedupResult(res);
      setTimeout(() => {
        onSwapSuccess(res);
        onClose();
      }, 2000);
    } catch (err: any) {
      setError(err.message || 'Swap operation failed');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm animate-fadeIn">
      <div className="bg-slate-900 border border-slate-800 rounded-2xl max-w-lg w-full p-6 shadow-2xl flex flex-col space-y-4">
        {/* Header */}
        <div className="flex items-center justify-between pb-3 border-b border-slate-800">
          <div>
            <h3 className="text-base font-semibold text-white flex items-center space-x-2">
              <RefreshCw className="w-4 h-4 text-cyan-400" />
              <span>Replace Scene #{sceneIndex + 1} Clip</span>
            </h3>
            <p className="text-xs text-slate-400">
              Triggers partial re-render of only this scene interval.
            </p>
          </div>
          <button
            onClick={onClose}
            className="p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Speedup Success Banner */}
        {speedupResult && (
          <div className="p-3.5 rounded-xl bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-xs flex items-center space-x-2">
            <Zap className="w-5 h-5 flex-shrink-0" />
            <div>
              <p className="font-semibold">Partial Re-render Succeeded!</p>
              <p className="text-[11px] text-emerald-300">
                Completed in {speedupResult.partial_render_duration_sec}s vs full {speedupResult.full_render_estimate_sec}s ({speedupResult.speedup_factor}x faster)!
              </p>
            </div>
          </div>
        )}

        {/* Error message */}
        {error && (
          <div className="p-3 rounded-lg bg-rose-500/10 border border-rose-500/20 text-rose-400 text-xs flex items-center space-x-2">
            <AlertCircle className="w-4 h-4 flex-shrink-0" />
            <span>{error}</span>
          </div>
        )}

        {/* Clip Selection */}
        <div className="space-y-2">
          <label className="text-xs font-semibold uppercase tracking-wider text-slate-400">
            Select Replacement Footage:
          </label>
          <div className="space-y-1.5 max-h-48 overflow-y-auto pr-1">
            {CLIP_PRESETS.map((item) => (
              <div
                key={item.id}
                onClick={() => setSelectedClipId(item.id)}
                className={`p-2.5 rounded-xl border text-xs cursor-pointer flex items-center justify-between transition-all ${
                  selectedClipId === item.id
                    ? 'bg-cyan-500/10 border-cyan-500 text-cyan-300 font-medium'
                    : 'bg-slate-950/60 border-slate-800 text-slate-300 hover:border-slate-700'
                }`}
              >
                <div>
                  <div className="text-slate-200">{item.name}</div>
                  <div className="text-[10px] text-slate-500">{item.provider}</div>
                </div>
                {selectedClipId === item.id && <Check className="w-4 h-4 text-cyan-400" />}
              </div>
            ))}
          </div>
        </div>

        {/* Custom Visual Hint */}
        <div className="space-y-1.5">
          <label className="text-xs font-semibold uppercase tracking-wider text-slate-400">
            Or Specify Custom Visual Hint:
          </label>
          <input
            type="text"
            value={customHint}
            onChange={(e) => setCustomHint(e.target.value)}
            placeholder="e.g. Modern executive conference room with cityscape"
            className="w-full px-3 py-2 bg-slate-950 border border-slate-800 rounded-xl text-xs text-white placeholder-slate-600 focus:outline-none focus:border-cyan-500"
          />
        </div>

        {/* Actions */}
        <div className="pt-3 border-t border-slate-800 flex items-center justify-end space-x-2">
          <button
            onClick={onClose}
            disabled={isLoading}
            className="px-4 py-2 rounded-xl text-xs font-medium text-slate-400 hover:text-white hover:bg-slate-800"
          >
            Cancel
          </button>
          <button
            onClick={handleSwap}
            disabled={isLoading}
            className="px-5 py-2 rounded-xl text-xs font-medium bg-gradient-to-r from-cyan-500 to-violet-600 text-white shadow-lg shadow-cyan-500/20 hover:opacity-90 transition-all flex items-center space-x-1.5"
          >
            {isLoading ? (
              <>
                <RefreshCw className="w-3.5 h-3.5 animate-spin" />
                <span>Re-rendering Scene...</span>
              </>
            ) : (
              <>
                <Zap className="w-3.5 h-3.5" />
                <span>Re-render Affected Clip</span>
              </>
            )}
          </button>
        </div>
      </div>
    </div>
  );
};
