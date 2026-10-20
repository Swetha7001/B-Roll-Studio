import React, { useState } from 'react';
import {
  FileText, Mic, ListTree, Sparkles, UploadCloud,
  AlertCircle, Monitor, Smartphone, Square, Layers
} from 'lucide-react';
import { createJob, uploadAudioJob } from '../services/api';

interface CreateJobProps {
  onJobCreated: (jobId: string) => void;
}

export const CreateJob: React.FC<CreateJobProps> = ({ onJobCreated }) => {
  const [inputMode, setInputMode] = useState<'script' | 'audio' | 'scenes'>('script');

  // Form states
  const [scriptText, setScriptText] = useState(
    'Save money automatically every single month. Consistent small habits build substantial financial freedom over time. Deploying automated cloud systems protects your business revenue.'
  );
  const [audioUrl, setAudioUrl] = useState('');
  const [audioFile, setAudioFile] = useState<File | null>(null);

  const [structuredScenes, setStructuredScenes] = useState([
    { text: 'Managing corporate finances requires strategic planning and disciplined saving.', visual_hint: 'counting currency banknotes' },
    { text: 'Deploying scalable infrastructure to the cloud protects company uptime.', visual_hint: 'server rack with blinking led lights' },
    { text: 'True professional partnerships are founded on mutual trust and shared values.', visual_hint: 'business partners shaking hands firmly' }
  ]);

  const [voice, setVoice] = useState('en-IN-female');
  const [aspectRatios, setAspectRatios] = useState<string[]>(['16:9', '9:16']);
  const [style, setStyle] = useState('bright, modern, real-world footage');
  const [avoidTagInput, setAvoidTagInput] = useState('');
  const [avoidTags, setAvoidTags] = useState<string[]>(["people's faces"]);
  const [burnInCaptions, setBurnInCaptions] = useState(true);
  const [genSrt, setGenSrt] = useState(true);

  const [isLoading, setIsLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const toggleRatio = (ratio: string) => {
    if (aspectRatios.includes(ratio)) {
      if (aspectRatios.length === 1) return; // Must keep at least one
      setAspectRatios(aspectRatios.filter((r) => r !== ratio));
    } else {
      setAspectRatios([...aspectRatios, ratio]);
    }
  };

  const addAvoidTag = () => {
    const trimmed = avoidTagInput.trim();
    if (trimmed && !avoidTags.includes(trimmed)) {
      setAvoidTags([...avoidTags, trimmed]);
      setAvoidTagInput('');
    }
  };

  const removeAvoidTag = (tag: string) => {
    setAvoidTags(avoidTags.filter((t) => t !== tag));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setErrorMessage(null);

    try {
      if (inputMode === 'audio' && audioFile) {
        // Direct file upload
        const res = await uploadAudioJob(audioFile, {
          voice,
          aspect_ratios: aspectRatios,
          style,
          avoid: avoidTags,
        });
        onJobCreated(res.job_id);
      } else {
        const payload: any = {
          voice,
          aspect_ratios: aspectRatios,
          style,
          avoid: avoidTags,
          captions: { burn_in: burnInCaptions, srt: genSrt },
        };

        if (inputMode === 'script') {
          if (!scriptText.trim()) throw new Error('Please enter script text.');
          payload.script = scriptText.trim();
        } else if (inputMode === 'audio') {
          if (!audioUrl.trim()) throw new Error('Please enter a valid remote audio URL or upload an audio file.');
          payload.audio_url = audioUrl.trim();
        } else if (inputMode === 'scenes') {
          if (structuredScenes.length === 0) throw new Error('Please provide at least one scene.');
          payload.scenes = structuredScenes;
        }

        const res = await createJob(payload);
        onJobCreated(res.job_id);
      }
    } catch (err: any) {
      setErrorMessage(err.message || 'Failed to submit generation job');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8 animate-fadeIn space-y-6">
      {/* Title */}
      <div>
        <h1 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight flex items-center space-x-2">
          <Sparkles className="w-6 h-6 text-cyan-400" />
          <span>New Video Production</span>
        </h1>
        <p className="text-sm text-slate-400 mt-1">
          Configure narration, style guidelines, and output parameters.
        </p>
      </div>

      {/* Error Alert */}
      {errorMessage && (
        <div className="p-4 rounded-xl bg-rose-500/10 border border-rose-500/20 text-rose-400 text-xs sm:text-sm flex items-start space-x-3">
          <AlertCircle className="w-5 h-5 flex-shrink-0 mt-0.5" />
          <div>
            <p className="font-semibold">Submission Error</p>
            <p className="text-xs text-rose-300 mt-0.5">{errorMessage}</p>
          </div>
        </div>
      )}

      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Input Mode Selector */}
        <div className="p-1.5 rounded-2xl bg-slate-900 border border-slate-800 flex flex-wrap gap-1">
          <button
            type="button"
            onClick={() => setInputMode('script')}
            className={`flex-1 min-w-[120px] py-2.5 px-4 rounded-xl text-xs sm:text-sm font-semibold transition-all flex items-center justify-center space-x-2 ${
              inputMode === 'script'
                ? 'bg-gradient-to-r from-cyan-500 to-violet-600 text-white shadow-md'
                : 'text-slate-400 hover:text-white'
            }`}
          >
            <FileText className="w-4 h-4" />
            <span>Script Text</span>
          </button>

          <button
            type="button"
            onClick={() => setInputMode('audio')}
            className={`flex-1 min-w-[120px] py-2.5 px-4 rounded-xl text-xs sm:text-sm font-semibold transition-all flex items-center justify-center space-x-2 ${
              inputMode === 'audio'
                ? 'bg-gradient-to-r from-cyan-500 to-violet-600 text-white shadow-md'
                : 'text-slate-400 hover:text-white'
            }`}
          >
            <Mic className="w-4 h-4" />
            <span>Voiceover Audio</span>
          </button>

          <button
            type="button"
            onClick={() => setInputMode('scenes')}
            className={`flex-1 min-w-[120px] py-2.5 px-4 rounded-xl text-xs sm:text-sm font-semibold transition-all flex items-center justify-center space-x-2 ${
              inputMode === 'scenes'
                ? 'bg-gradient-to-r from-cyan-500 to-violet-600 text-white shadow-md'
                : 'text-slate-400 hover:text-white'
            }`}
          >
            <ListTree className="w-4 h-4" />
            <span>Structured Scenes</span>
          </button>
        </div>

        {/* Dynamic Input Body */}
        <div className="p-6 rounded-2xl bg-slate-900/80 border border-slate-800 shadow-xl space-y-4">
          {inputMode === 'script' && (
            <div className="space-y-2">
              <label className="text-xs font-semibold uppercase tracking-wider text-slate-400 flex items-center justify-between">
                <span>Narration Script:</span>
                <span className="font-mono text-[11px] text-slate-500">{scriptText.length} characters</span>
              </label>
              <textarea
                rows={6}
                value={scriptText}
                onChange={(e) => setScriptText(e.target.value)}
                placeholder="Enter script lines. Sentences will be analyzed for semantic scene matching..."
                className="w-full p-4 bg-slate-950 border border-slate-800 rounded-xl text-sm text-slate-100 placeholder-slate-600 focus:outline-none focus:border-cyan-500 transition-colors font-sans leading-relaxed resize-y"
              />
            </div>
          )}

          {inputMode === 'audio' && (
            <div className="space-y-4">
              <div className="space-y-1.5">
                <label className="text-xs font-semibold uppercase tracking-wider text-slate-400">
                  Direct Audio Upload (MP3, WAV, M4A up to 10 min):
                </label>
                <div className="p-6 border-2 border-dashed border-slate-800 hover:border-cyan-500/50 rounded-xl bg-slate-950/60 text-center transition-colors">
                  <UploadCloud className="w-8 h-8 text-cyan-400 mx-auto mb-2" />
                  <input
                    type="file"
                    accept=".mp3,.wav,.m4a"
                    onChange={(e) => setAudioFile(e.target.files?.[0] || null)}
                    className="text-xs text-slate-400 file:mr-4 file:py-2 file:px-4 file:rounded-xl file:border-0 file:text-xs file:font-semibold file:bg-cyan-500/10 file:text-cyan-300 hover:file:bg-cyan-500/20"
                  />
                  {audioFile && (
                    <p className="text-xs text-emerald-400 mt-2 font-mono">
                      Selected: {audioFile.name} ({(audioFile.size / (1024 * 1024)).toFixed(2)} MB)
                    </p>
                  )}
                </div>
              </div>

              <div className="relative flex py-2 items-center">
                <div className="flex-grow border-t border-slate-800"></div>
                <span className="flex-shrink mx-4 text-xs text-slate-500 font-mono">OR REMOTE URL</span>
                <div className="flex-grow border-t border-slate-800"></div>
              </div>

              <div className="space-y-1.5">
                <label className="text-xs font-semibold uppercase tracking-wider text-slate-400">
                  Remote Audio URL:
                </label>
                <input
                  type="url"
                  value={audioUrl}
                  onChange={(e) => setAudioUrl(e.target.value)}
                  placeholder="https://example.com/narration.mp3"
                  className="w-full px-4 py-2.5 bg-slate-950 border border-slate-800 rounded-xl text-sm text-slate-100 placeholder-slate-600 focus:outline-none focus:border-cyan-500"
                />
              </div>
            </div>
          )}

          {inputMode === 'scenes' && (
            <div className="space-y-3">
              <label className="text-xs font-semibold uppercase tracking-wider text-slate-400">
                IncuBrix Structured Scenes:
              </label>
              {structuredScenes.map((sc, i) => (
                <div key={i} className="p-3 bg-slate-950/80 rounded-xl border border-slate-800 space-y-2">
                  <div className="text-xs font-mono text-cyan-400 font-bold">Scene #{i + 1}</div>
                  <input
                    type="text"
                    value={sc.text}
                    onChange={(e) => {
                      const updated = [...structuredScenes];
                      updated[i].text = e.target.value;
                      setStructuredScenes(updated);
                    }}
                    placeholder="Narration text line..."
                    className="w-full px-3 py-1.5 bg-slate-900 border border-slate-800 rounded-lg text-xs text-white"
                  />
                  <input
                    type="text"
                    value={sc.visual_hint}
                    onChange={(e) => {
                      const updated = [...structuredScenes];
                      updated[i].visual_hint = e.target.value;
                      setStructuredScenes(updated);
                    }}
                    placeholder="Visual hint (e.g. data server rack)..."
                    className="w-full px-3 py-1.5 bg-slate-900 border border-slate-800 rounded-lg text-xs text-slate-300"
                  />
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Configuration Row */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Voice Selector */}
          <div className="p-5 rounded-2xl bg-slate-900/80 border border-slate-800 space-y-3 shadow-lg">
            <label className="text-xs font-semibold uppercase tracking-wider text-slate-400 flex items-center space-x-1.5">
              <Mic className="w-3.5 h-3.5 text-cyan-400" />
              <span>Narration Voice (TTS):</span>
            </label>
            <select
              value={voice}
              onChange={(e) => setVoice(e.target.value)}
              className="w-full px-4 py-2.5 bg-slate-950 border border-slate-800 rounded-xl text-xs sm:text-sm text-slate-200 focus:outline-none focus:border-cyan-500"
            >
              <option value="en-IN-female">Indian English — Female (en-IN-Neerja)</option>
              <option value="en-IN-male">Indian English — Male (en-IN-Prabhat)</option>
              <option value="en-US-female">US English — Female (en-US-Jenny)</option>
              <option value="en-US-male">US English — Male (en-US-Guy)</option>
              <option value="hi-IN-female">Hindi — Swara (hi-IN-Swara)</option>
              <option value="ta-IN-female">Tamil — Pallavi (ta-IN-Pallavi)</option>
            </select>
          </div>

          {/* Aspect Ratios Selection */}
          <div className="p-5 rounded-2xl bg-slate-900/80 border border-slate-800 space-y-3 shadow-lg">
            <label className="text-xs font-semibold uppercase tracking-wider text-slate-400 flex items-center space-x-1.5">
              <Layers className="w-3.5 h-3.5 text-cyan-400" />
              <span>Target Aspect Ratios:</span>
            </label>
            <div className="flex gap-2">
              {[
                { id: '16:9', icon: Monitor },
                { id: '9:16', icon: Smartphone },
                { id: '1:1', icon: Square },
              ].map(({ id, icon: Icon }) => {
                const checked = aspectRatios.includes(id);
                return (
                  <button
                    key={id}
                    type="button"
                    onClick={() => toggleRatio(id)}
                    className={`flex-1 p-2.5 rounded-xl border text-xs font-medium flex flex-col items-center justify-center space-y-1 transition-all ${
                      checked
                        ? 'bg-cyan-500/10 border-cyan-500 text-cyan-300 shadow-md'
                        : 'bg-slate-950/60 border-slate-800 text-slate-400 hover:border-slate-700'
                    }`}
                  >
                    <Icon className="w-4 h-4" />
                    <span>{id}</span>
                  </button>
                );
              })}
            </div>
          </div>
        </div>

        {/* Visual Style & Avoid Guardrails */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Visual Style */}
          <div className="p-5 rounded-2xl bg-slate-900/80 border border-slate-800 space-y-3 shadow-lg">
            <label className="text-xs font-semibold uppercase tracking-wider text-slate-400">
              Visual Style Direction:
            </label>
            <input
              type="text"
              value={style}
              onChange={(e) => setStyle(e.target.value)}
              placeholder="e.g. bright, modern, real-world footage"
              className="w-full px-4 py-2.5 bg-slate-950 border border-slate-800 rounded-xl text-xs sm:text-sm text-slate-200 focus:outline-none focus:border-cyan-500"
            />
          </div>

          {/* Avoid Constraints */}
          <div className="p-5 rounded-2xl bg-slate-900/80 border border-slate-800 space-y-3 shadow-lg">
            <label className="text-xs font-semibold uppercase tracking-wider text-slate-400">
              Content Elements to Avoid:
            </label>
            <div className="flex gap-2">
              <input
                type="text"
                value={avoidTagInput}
                onChange={(e) => setAvoidTagInput(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === 'Enter') {
                    e.preventDefault();
                    addAvoidTag();
                  }
                }}
                placeholder="e.g. alcohol, weapons"
                className="flex-1 px-3 py-2 bg-slate-950 border border-slate-800 rounded-xl text-xs text-slate-200 focus:outline-none focus:border-cyan-500"
              />
              <button
                type="button"
                onClick={addAvoidTag}
                className="px-3 py-2 rounded-xl bg-slate-800 text-xs font-medium hover:bg-slate-700 text-white"
              >
                Add
              </button>
            </div>

            <div className="flex flex-wrap gap-1.5 pt-1">
              {avoidTags.map((tag) => (
                <span
                  key={tag}
                  onClick={() => removeAvoidTag(tag)}
                  className="px-2.5 py-1 rounded-lg text-xs bg-rose-500/10 text-rose-300 border border-rose-500/20 cursor-pointer hover:bg-rose-500/20 flex items-center space-x-1"
                >
                  <span>{tag}</span>
                  <span className="text-rose-400 text-xs font-bold">×</span>
                </span>
              ))}
            </div>
          </div>
        </div>

        {/* Captions Config & Submit Button */}
        <div className="p-5 rounded-2xl bg-slate-900/80 border border-slate-800 flex flex-wrap items-center justify-between gap-4 shadow-xl">
          <div className="flex items-center space-x-4 text-xs text-slate-300">
            <label className="flex items-center space-x-2 cursor-pointer">
              <input
                type="checkbox"
                checked={burnInCaptions}
                onChange={(e) => setBurnInCaptions(e.target.checked)}
                className="rounded accent-cyan-500 w-4 h-4 cursor-pointer"
              />
              <span>Burn-in Subtitles</span>
            </label>
            <label className="flex items-center space-x-2 cursor-pointer">
              <input
                type="checkbox"
                checked={genSrt}
                onChange={(e) => setGenSrt(e.target.checked)}
                className="rounded accent-cyan-500 w-4 h-4 cursor-pointer"
              />
              <span>Generate SRT File</span>
            </label>
          </div>

          <button
            type="submit"
            disabled={isLoading}
            className="px-8 py-3.5 rounded-xl bg-gradient-to-r from-cyan-500 to-violet-600 text-white font-bold text-sm shadow-xl shadow-cyan-500/25 hover:opacity-95 transition-all flex items-center space-x-2 disabled:opacity-50"
          >
            {isLoading ? (
              <>
                <Sparkles className="w-4 h-4 animate-spin" />
                <span>Submitting Job...</span>
              </>
            ) : (
              <>
                <Sparkles className="w-4 h-4" />
                <span>Generate Video</span>
              </>
            )}
          </button>
        </div>
      </form>
    </div>
  );
};
