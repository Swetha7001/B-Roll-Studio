import React from 'react';
import { TimelineScene } from '../types';
import { Clock, ShieldCheck, Sparkles, RefreshCw, ExternalLink, Star } from 'lucide-react';

interface SceneListProps {
  scenes: TimelineScene[];
  onSwapClick: (sceneIndex: number) => void;
}

export const SceneList: React.FC<SceneListProps> = ({ scenes, onSwapClick }) => {
  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between pb-2 border-b border-slate-800">
        <h3 className="text-sm font-semibold text-white tracking-wide flex items-center space-x-2">
          <span>Timeline Breakdown</span>
          <span className="text-xs font-normal text-slate-400">({scenes.length} Scenes)</span>
        </h3>
        <span className="text-[11px] text-cyan-400 font-mono">100% Commercial Usable</span>
      </div>

      <div className="space-y-2.5 max-h-[560px] overflow-y-auto pr-1">
        {scenes.map((scene) => {
          const clip = scene.selected_clip;
          const decision = scene.selection_decision;

          return (
            <div
              key={scene.scene_id}
              className="p-3.5 rounded-xl bg-slate-900/70 border border-slate-800/80 hover:border-slate-700 transition-all flex flex-col space-y-2.5 group"
            >
              {/* Scene Header: Timecode + Badges + Swap Action */}
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-2">
                  <span className="px-2 py-0.5 rounded text-[10px] font-bold font-mono bg-cyan-500/10 text-cyan-400 border border-cyan-500/20">
                    #{scene.scene_index + 1}
                  </span>
                  <div className="flex items-center space-x-1 text-[11px] font-mono text-slate-400">
                    <Clock className="w-3 h-3" />
                    <span>{scene.start_time.toFixed(1)}s - {scene.end_time.toFixed(1)}s</span>
                    <span className="text-slate-600">({scene.duration.toFixed(1)}s)</span>
                  </div>
                </div>

                <div className="flex items-center space-x-1.5">
                  {clip.is_ai_generated ? (
                    <span className="px-2 py-0.5 rounded text-[10px] font-semibold bg-violet-500/10 text-violet-300 border border-violet-500/20 flex items-center space-x-1">
                      <Sparkles className="w-2.5 h-2.5" />
                      <span>AI Synthetic</span>
                    </span>
                  ) : (
                    <span className="px-2 py-0.5 rounded text-[10px] font-semibold bg-emerald-500/10 text-emerald-300 border border-emerald-500/20 flex items-center space-x-1">
                      <ShieldCheck className="w-2.5 h-2.5" />
                      <span>Verified Stock</span>
                    </span>
                  )}

                  <button
                    onClick={() => onSwapClick(scene.scene_index)}
                    className="p-1 rounded bg-slate-800 hover:bg-cyan-500/20 hover:text-cyan-400 text-slate-400 transition-colors text-[11px] flex items-center space-x-1 px-2 border border-slate-700"
                    title="Swap clip and re-render only this scene"
                  >
                    <RefreshCw className="w-2.5 h-2.5" />
                    <span className="hidden sm:inline">Swap Clip</span>
                  </button>
                </div>
              </div>

              {/* Narration line */}
              <p className="text-xs text-slate-200 leading-relaxed font-normal bg-slate-950/40 p-2 rounded-lg border border-slate-900">
                "{scene.narration_text}"
              </p>

              {/* Clip Metadata Footer */}
              <div className="pt-1.5 border-t border-slate-800/60 flex flex-wrap items-center justify-between text-[11px] text-slate-400 gap-1.5">
                <div className="flex items-center space-x-2">
                  <span className="font-medium text-slate-300 truncate max-w-[180px]">
                    {clip.title}
                  </span>
                  <span className="text-slate-600">•</span>
                  <span className="text-slate-400 text-[10px]">{clip.provider}</span>
                </div>

                <div className="flex items-center space-x-3">
                  {/* Relevance rating */}
                  <div className="flex items-center space-x-1 text-amber-400 font-mono text-[11px]" title={`VLM Score: ${decision.vlm_score}/5.0`}>
                    <Star className="w-3 h-3 fill-amber-400 text-amber-400" />
                    <span>{decision.human_rating_estimate.toFixed(1)}/5</span>
                  </div>

                  {clip.source_url && (
                    <a
                      href={clip.source_url}
                      target="_blank"
                      rel="noreferrer"
                      className="text-cyan-400 hover:underline flex items-center space-x-0.5 text-[10px]"
                    >
                      <span>Licence</span>
                      <ExternalLink className="w-2.5 h-2.5" />
                    </a>
                  )}
                </div>
              </div>

              {/* Selection reason explanation */}
              <div className="text-[10px] text-slate-500 italic bg-slate-950/20 px-2 py-1 rounded">
                Decision: {decision.selection_reason}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
