import { useState, useEffect } from 'react';
import { Sparkles, Film, Key, Play, Download, CheckCircle2, Clock, RefreshCw, AlertCircle } from 'lucide-react';

interface TimestampedScene {
  scene_index: number;
  timestamp_start: string;
  timestamp_end: string;
  start_seconds: number;
  end_seconds: number;
  duration_seconds: number;
  narration: string;
  character_action: string;
  camera_movement: string;
  visual_prompt: string;
  animation_style: string;
}

interface StoryboardResult {
  title: string;
  total_duration_seconds: number;
  animation_style: string;
  model_used: string;
  scenes: TimestampedScene[];
}

export function GoogleAIStudio() {
  const [script, setScript] = useState('A small boy in village got a chance to study abroad but due to financial issue he decided to stay at village and cook');
  const [animationStyle, setAnimationStyle] = useState('3d_animation');
  const [apiKey, setApiKey] = useState('');
  const [isKeyConnected, setIsKeyConnected] = useState(false);
  const [keyMessage, setKeyMessage] = useState('');

  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [storyboard, setStoryboard] = useState<StoryboardResult | null>(null);

  const [isRendering, setIsRendering] = useState(false);
  const [renderProgress, setRenderProgress] = useState(0);
  const [renderStage, setRenderStage] = useState('');
  const [renderedResult, setRenderedResult] = useState<any | null>(null);
  const [errorMessage, setErrorMessage] = useState('');

  useEffect(() => {
    fetch('/api/v1/google-studio/config')
      .then((res) => res.json())
      .then((data) => {
        setIsKeyConnected(data.configured_with_user_key);
      })
      .catch(() => {});
  }, []);

  const handleSaveApiKey = async () => {
    if (!apiKey.trim()) return;
    try {
      const res = await fetch('/api/v1/google-studio/config', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ api_key: apiKey }),
      });
      const data = await res.json();
      if (res.ok) {
        setIsKeyConnected(true);
        setKeyMessage('Google AI Studio Key activated successfully!');
        setApiKey('');
      } else {
        setKeyMessage(data.detail || 'Failed to activate key');
      }
    } catch {
      setKeyMessage('Network error connecting to API');
    }
  };

  const handleGenerateStoryboard = async () => {
    if (!script.trim()) return;
    setIsAnalyzing(true);
    setErrorMessage('');
    setStoryboard(null);
    setRenderedResult(null);

    try {
      const res = await fetch('/api/v1/google-studio/storyboard', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          script,
          animation_style: animationStyle,
          api_key: apiKey || undefined,
        }),
      });

      if (!res.ok) {
        const err = await res.json();
        throw new Error(err.detail || 'Failed to analyze script');
      }

      const data: StoryboardResult = await res.json();
      setStoryboard(data);
    } catch (err: any) {
      setErrorMessage(err.message || 'Error communicating with Google Gemini Pro');
    } finally {
      setIsAnalyzing(false);
    }
  };

  const handleRenderVideo = async () => {
    if (!storyboard) return;
    setIsRendering(true);
    setRenderProgress(15);
    setRenderStage('Synthesizing animated scenes with Google Veo...');
    setErrorMessage('');
    setRenderedResult(null);

    try {
      const res = await fetch('/api/v1/google-studio/generate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          storyboard,
          voice: 'en-IN-female',
          aspect_ratio: '16:9',
          burn_captions: true,
          api_key: apiKey.trim() || undefined,
        }),
      });

      if (!res.ok) {
        const err = await res.json();
        throw new Error(err.detail || 'Failed to start video rendering');
      }

      const jobData = await res.json();
      const jobId = jobData.job_id;

      // Poll until finished
      const pollInterval = setInterval(async () => {
        try {
          const pollRes = await fetch(`/api/v1/google-studio/jobs/${jobId}`);
          const pollData = await pollRes.json();

          setRenderProgress(pollData.progress || 50);
          setRenderStage(pollData.stage || 'Rendering animated frames...');

          if (pollData.status === 'succeeded') {
            clearInterval(pollInterval);
            setIsRendering(false);
            setRenderedResult(pollData.result);
          } else if (pollData.status === 'failed') {
            clearInterval(pollInterval);
            setIsRendering(false);
            setErrorMessage(pollData.error || 'Video rendering failed');
          }
        } catch {
          // ignore transient poll error
        }
      }, 2500);
    } catch (err: any) {
      setIsRendering(false);
      setErrorMessage(err.message || 'Failed to render animated video');
    }
  };

  return (
    <div className="max-w-6xl mx-auto px-4 py-8 space-y-8">
      {/* Hero Header */}
      <div className="relative overflow-hidden rounded-2xl bg-gradient-to-r from-violet-950/80 via-slate-900 to-cyan-950/80 border border-violet-500/30 p-8 shadow-2xl shadow-violet-950/50">
        <div className="absolute top-0 right-0 w-96 h-96 bg-gradient-to-bl from-cyan-500/10 via-violet-500/10 to-transparent rounded-full blur-3xl pointer-events-none" />
        <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-6 relative z-10">
          <div>
            <div className="flex items-center space-x-2.5 mb-2">
              <span className="px-2.5 py-1 rounded-full text-xs font-semibold bg-violet-500/20 text-violet-300 border border-violet-500/40 flex items-center space-x-1.5">
                <Sparkles className="w-3.5 h-3.5 text-violet-400" />
                <span>Google AI Studio & Gemini Pro</span>
              </span>
              <span className="px-2.5 py-1 rounded-full text-xs font-medium bg-cyan-500/20 text-cyan-300 border border-cyan-500/40">
                Veo Full Motion Video
              </span>
            </div>
            <h1 className="text-3xl font-extrabold text-white tracking-tight">
              Google AI Video Generation Center
            </h1>
            <p className="text-slate-300 text-sm mt-1 max-w-2xl leading-relaxed">
              Transform your raw story concept into a fully animated, timestamped video with Google Gemini Pro narrative decomposition, moving character scenes, and synchronized voiceover.
            </p>
          </div>

          {/* Connection Status Badge */}
          <div className="bg-slate-900/90 border border-slate-700/80 rounded-xl p-3.5 flex items-center space-x-3 text-xs shadow-lg">
            <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-violet-500 to-cyan-500 flex items-center justify-center">
              <Key className="w-4 h-4 text-white" />
            </div>
            <div>
              <div className="font-semibold text-slate-200">
                {isKeyConnected ? 'Google Gemini API Active' : 'Gemini Pro Engine Ready'}
              </div>
              <div className="text-slate-400 text-[11px]">
                {isKeyConnected ? 'Personal Key Connected' : 'Google Direct Mode'}
              </div>
            </div>
          </div>
        </div>

        {/* API Key Connect Input */}
        <div className="mt-6 pt-5 border-t border-slate-800/80 flex flex-col sm:flex-row items-center gap-3">
          <input
            type="password"
            placeholder="Paste your Google AI Studio API Key (AQ... or AIza...)"
            value={apiKey}
            onChange={(e) => setApiKey(e.target.value)}
            className="w-full sm:w-96 px-3.5 py-2 bg-slate-950/70 border border-slate-700/70 rounded-lg text-xs text-white placeholder-slate-500 focus:outline-none focus:border-violet-500"
          />
          <button
            onClick={handleSaveApiKey}
            className="w-full sm:w-auto px-4 py-2 bg-violet-600 hover:bg-violet-500 text-white rounded-lg text-xs font-semibold transition-all shadow-md"
          >
            Connect Gemini API Key
          </button>
          {keyMessage && (
            <span className="text-xs text-violet-300 font-medium">{keyMessage}</span>
          )}
        </div>
      </div>

      {/* Script & Style Configuration Form */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 space-y-4 bg-slate-900/60 border border-slate-800 p-6 rounded-2xl">
          <div className="flex items-center justify-between">
            <label className="text-sm font-semibold text-slate-200 flex items-center space-x-2">
              <Film className="w-4 h-4 text-cyan-400" />
              <span>Enter Script or Story Premise:</span>
            </label>
            <span className="text-xs text-slate-500">{script.length} characters</span>
          </div>

          <textarea
            rows={5}
            value={script}
            onChange={(e) => setScript(e.target.value)}
            placeholder="Describe your story idea or paste a script..."
            className="w-full p-4 bg-slate-950 border border-slate-700/80 rounded-xl text-sm text-slate-100 placeholder-slate-500 focus:outline-none focus:border-cyan-500 transition-colors leading-relaxed"
          />

          {/* Quick Idea Presets */}
          <div className="flex flex-wrap items-center gap-2 pt-1">
            <span className="text-xs text-slate-400">Quick Prompts:</span>
            <button
              onClick={() => setScript('A small boy in village got a chance to study abroad but due to financial issue he decided to stay at village and cook')}
              className="text-xs px-2.5 py-1 rounded-md bg-slate-800 hover:bg-slate-700 text-slate-300 transition-colors border border-slate-700/60"
            >
              Village Boy Cooking Story
            </button>
            <button
              onClick={() => setScript('A young scientist builds an autonomous solar drone that cleans ocean plastic across the Pacific')}
              className="text-xs px-2.5 py-1 rounded-md bg-slate-800 hover:bg-slate-700 text-slate-300 transition-colors border border-slate-700/60"
            >
              Solar Ocean Drone
            </button>
            <button
              onClick={() => setScript('Two childhood friends launch a clean energy startup from an old garage and power their entire city')}
              className="text-xs px-2.5 py-1 rounded-md bg-slate-800 hover:bg-slate-700 text-slate-300 transition-colors border border-slate-700/60"
            >
              Garage Clean Energy
            </button>
          </div>
        </div>

        {/* Style Selector & Action */}
        <div className="space-y-4 bg-slate-900/60 border border-slate-800 p-6 rounded-2xl flex flex-col justify-between">
          <div>
            <label className="text-sm font-semibold text-slate-200 block mb-3">
              Animated Visual Style:
            </label>
            <div className="space-y-2.5">
              {[
                { id: '3d_animation', label: '🎬 3D Pixar / Disney Movie', desc: 'Expressive 3D characters & vibrant lighting' },
                { id: 'anime', label: '🌟 Studio Ghibli Anime', desc: 'Hand-crafted aesthetic & lush emotional skies' },
                { id: 'hyper_realistic', label: '🎥 Veo Hyper-Realistic Motion', desc: '8K cinematic camera with anamorphic blur' },
                { id: 'cyberpunk', label: '⚡ Cyberpunk Neon Motion', desc: 'Holographic glow & dynamic rain particles' },
              ].map((style) => (
                <div
                  key={style.id}
                  onClick={() => setAnimationStyle(style.id)}
                  className={`p-3 rounded-xl border cursor-pointer transition-all ${
                    animationStyle === style.id
                      ? 'bg-violet-950/60 border-violet-500 shadow-md shadow-violet-900/20'
                      : 'bg-slate-950/50 border-slate-800 hover:border-slate-700'
                  }`}
                >
                  <div className="font-medium text-xs text-white">{style.label}</div>
                  <div className="text-[11px] text-slate-400 mt-0.5">{style.desc}</div>
                </div>
              ))}
            </div>
          </div>

          <button
            disabled={isAnalyzing}
            onClick={handleGenerateStoryboard}
            className="w-full py-3.5 px-4 rounded-xl bg-gradient-to-r from-violet-600 via-indigo-600 to-cyan-500 hover:from-violet-500 hover:to-cyan-400 text-white font-bold text-sm transition-all shadow-lg shadow-violet-900/40 flex items-center justify-center space-x-2 disabled:opacity-50"
          >
            {isAnalyzing ? (
              <>
                <RefreshCw className="w-4 h-4 animate-spin" />
                <span>Gemini Pro Directing Scenes...</span>
              </>
            ) : (
              <>
                <Sparkles className="w-4 h-4 text-cyan-300" />
                <span>Direct Storyboard with Gemini Pro</span>
              </>
            )}
          </button>
        </div>
      </div>

      {/* Error Banner */}
      {errorMessage && (
        <div className="p-4 rounded-xl bg-rose-950/50 border border-rose-500/50 text-rose-300 text-xs flex items-center space-x-2.5">
          <AlertCircle className="w-4 h-4 text-rose-400 shrink-0" />
          <span>{errorMessage}</span>
        </div>
      )}

      {/* Storyboard Review Section */}
      {storyboard && (
        <div className="space-y-6 bg-slate-900/80 border border-slate-800 p-8 rounded-2xl shadow-xl">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-slate-800">
            <div>
              <span className="text-xs font-semibold uppercase text-violet-400 tracking-wider">
                Gemini Pro Storyboard Generated
              </span>
              <h2 className="text-2xl font-bold text-white mt-0.5">{storyboard.title}</h2>
              <div className="flex items-center space-x-3 text-xs text-slate-400 mt-1">
                <span>{storyboard.scenes.length} Timestamped Scenes</span>
                <span>•</span>
                <span>{storyboard.total_duration_seconds}s Total Duration</span>
                <span>•</span>
                <span className="text-cyan-400 font-mono">{storyboard.model_used}</span>
              </div>
            </div>

            <button
              disabled={isRendering}
              onClick={handleRenderVideo}
              className="px-6 py-3 rounded-xl bg-gradient-to-r from-cyan-500 to-violet-600 hover:from-cyan-400 hover:to-violet-500 text-white font-bold text-sm shadow-xl shadow-cyan-950/50 flex items-center space-x-2 disabled:opacity-50"
            >
              {isRendering ? (
                <>
                  <RefreshCw className="w-4 h-4 animate-spin" />
                  <span>Rendering Animated Video...</span>
                </>
              ) : (
                <>
                  <Play className="w-4 h-4 fill-white" />
                  <span>Render Full-Motion Animated Video</span>
                </>
              )}
            </button>
          </div>

          {/* Rendering Progress Indicator */}
          {isRendering && (
            <div className="p-4 rounded-xl bg-slate-950 border border-cyan-500/40 space-y-2">
              <div className="flex items-center justify-between text-xs">
                <span className="font-semibold text-cyan-300 flex items-center space-x-2">
                  <RefreshCw className="w-3.5 h-3.5 animate-spin" />
                  <span>{renderStage}</span>
                </span>
                <span className="text-slate-400 font-mono">{renderProgress}%</span>
              </div>
              <div className="w-full bg-slate-800 h-2 rounded-full overflow-hidden">
                <div
                  className="bg-gradient-to-r from-cyan-500 to-violet-500 h-full transition-all duration-300"
                  style={{ width: `${renderProgress}%` }}
                />
              </div>
            </div>
          )}

          {/* Timestamped Scene Cards */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {storyboard.scenes.map((scene) => (
              <div
                key={scene.scene_index}
                className="bg-slate-950 border border-slate-800/90 rounded-xl p-5 space-y-3 relative hover:border-violet-500/50 transition-colors"
              >
                <div className="flex items-center justify-between">
                  <span className="text-xs font-mono font-bold px-2 py-0.5 rounded bg-violet-500/20 text-violet-300 border border-violet-500/30 flex items-center space-x-1.5">
                    <Clock className="w-3 h-3" />
                    <span>{scene.timestamp_start} - {scene.timestamp_end}</span>
                  </span>
                  <span className="text-[11px] text-slate-500">Scene #{scene.scene_index + 1} ({scene.duration_seconds}s)</span>
                </div>

                <div>
                  <h4 className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-1">
                    Voiceover Narration:
                  </h4>
                  <p className="text-sm text-slate-100 font-medium italic">
                    "{scene.narration}"
                  </p>
                </div>

                <div className="grid grid-cols-2 gap-2 pt-2 border-t border-slate-900 text-xs">
                  <div>
                    <span className="text-[10px] text-slate-500 block uppercase font-bold">🏃 Character Motion:</span>
                    <span className="text-slate-300 text-[11px] leading-tight block mt-0.5">{scene.character_action}</span>
                  </div>
                  <div>
                    <span className="text-[10px] text-slate-500 block uppercase font-bold">🎥 Camera Sweep:</span>
                    <span className="text-slate-300 text-[11px] leading-tight block mt-0.5">{scene.camera_movement}</span>
                  </div>
                </div>

                <div className="p-2.5 rounded-lg bg-slate-900/90 border border-slate-800 text-[11px] text-slate-400">
                  <span className="text-cyan-400 font-semibold block mb-0.5">Prompt:</span>
                  <span className="line-clamp-2">{scene.visual_prompt}</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Rendered Finished Video Player */}
      {renderedResult && (
        <div className="bg-slate-900/90 border border-cyan-500/50 rounded-2xl p-8 space-y-6 shadow-2xl shadow-cyan-950/40">
          <div className="flex items-center space-x-3 text-emerald-400 font-semibold text-sm">
            <CheckCircle2 className="w-5 h-5 text-emerald-400" />
            <span>Google AI Full-Motion Animated Video Rendered Successfully!</span>
          </div>

          <div className="aspect-video bg-black rounded-xl overflow-hidden shadow-2xl border border-slate-800">
            <video
              src={renderedResult.video_url}
              controls
              autoPlay
              className="w-full h-full object-contain"
            />
          </div>

          <div className="flex flex-wrap items-center justify-between gap-4 pt-2">
            <div>
              <h3 className="text-lg font-bold text-white">{renderedResult.title}</h3>
              <p className="text-xs text-slate-400 mt-0.5">
                Full-motion animated video • {renderedResult.duration_seconds}s total duration • {renderedResult.scenes_count} scenes
              </p>
            </div>

            <div className="flex items-center space-x-3">
              <a
                href={renderedResult.captions_url}
                download
                className="px-4 py-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-medium flex items-center space-x-1.5 transition-colors"
              >
                <Download className="w-3.5 h-3.5" />
                <span>Captions (SRT)</span>
              </a>

              <a
                href={renderedResult.video_url}
                download
                className="px-5 py-2.5 rounded-lg bg-gradient-to-r from-cyan-500 to-violet-600 hover:from-cyan-400 hover:to-violet-500 text-white text-xs font-bold flex items-center space-x-1.5 shadow-lg shadow-cyan-950/50 transition-all"
              >
                <Download className="w-4 h-4" />
                <span>Download Video (1080p MP4)</span>
              </a>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
