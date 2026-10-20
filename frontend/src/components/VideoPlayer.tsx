import React, { useRef, useState, useEffect } from 'react';
import { Play, Pause, Volume2, VolumeX, Maximize, Smartphone, Monitor, Square } from 'lucide-react';

interface VideoPlayerProps {
  artifacts: Record<string, string>;
  selectedRatio: string;
  setSelectedRatio: (ratio: string) => void;
  availableRatios: string[];
}

export const VideoPlayer: React.FC<VideoPlayerProps> = ({
  artifacts,
  selectedRatio,
  setSelectedRatio,
  availableRatios,
}) => {
  const videoRef = useRef<HTMLVideoElement | null>(null);
  const [isPlaying, setIsPlaying] = useState(false);
  const [currentTime, setCurrentTime] = useState(0);
  const [duration, setDuration] = useState(0);
  const [isMuted, setIsMuted] = useState(false);

  const ratioKey = `video_${selectedRatio.replace(':', '_')}`;
  const videoUrl = artifacts[ratioKey];

  useEffect(() => {
    setIsPlaying(false);
    setCurrentTime(0);
    if (videoRef.current) {
      videoRef.current.load();
    }
  }, [selectedRatio, videoUrl]);

  const togglePlay = () => {
    if (!videoRef.current) return;
    if (isPlaying) {
      videoRef.current.pause();
    } else {
      videoRef.current.play();
    }
    setIsPlaying(!isPlaying);
  };

  const handleTimeUpdate = () => {
    if (videoRef.current) {
      setCurrentTime(videoRef.current.currentTime);
      setDuration(videoRef.current.duration || 0);
    }
  };

  const handleSeek = (e: React.ChangeEvent<HTMLInputElement>) => {
    const time = parseFloat(e.target.value);
    if (videoRef.current) {
      videoRef.current.currentTime = time;
      setCurrentTime(time);
    }
  };

  const toggleMute = () => {
    if (!videoRef.current) return;
    videoRef.current.muted = !isMuted;
    setIsMuted(!isMuted);
  };

  const toggleFullscreen = () => {
    if (!videoRef.current) return;
    if (videoRef.current.requestFullscreen) {
      videoRef.current.requestFullscreen();
    }
  };

  const formatTime = (secs: number) => {
    const m = Math.floor(secs / 60);
    const s = Math.floor(secs % 60);
    return `${m}:${s < 10 ? '0' : ''}${s}`;
  };

  return (
    <div className="bg-slate-900/90 border border-slate-800 rounded-2xl overflow-hidden flex flex-col shadow-2xl">
      {/* Aspect Ratio Switcher Header */}
      <div className="px-4 py-3 border-b border-slate-800/80 flex items-center justify-between bg-slate-950/60">
        <div className="flex items-center space-x-2">
          <span className="text-xs font-semibold uppercase tracking-wider text-slate-400">Aspect Ratio:</span>
          <div className="flex bg-slate-900 p-0.5 rounded-lg border border-slate-800">
            {availableRatios.map((ratio) => {
              const active = ratio === selectedRatio;
              return (
                <button
                  key={ratio}
                  onClick={() => setSelectedRatio(ratio)}
                  className={`flex items-center space-x-1 px-3 py-1 text-xs font-medium rounded-md transition-all ${
                    active
                      ? 'bg-gradient-to-r from-cyan-500 to-violet-600 text-white shadow-md'
                      : 'text-slate-400 hover:text-slate-200'
                  }`}
                >
                  {ratio === '16:9' && <Monitor className="w-3.5 h-3.5" />}
                  {ratio === '9:16' && <Smartphone className="w-3.5 h-3.5" />}
                  {ratio === '1:1' && <Square className="w-3.5 h-3.5" />}
                  <span>{ratio}</span>
                </button>
              );
            })}
          </div>
        </div>

        <div className="flex items-center space-x-2 text-[11px] font-mono text-slate-400">
          <span className="px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
            1080p H.264
          </span>
          <span className="px-2 py-0.5 rounded bg-cyan-500/10 text-cyan-400 border border-cyan-500/20">
            30 fps
          </span>
        </div>
      </div>

      {/* Video Viewport Container */}
      <div className="relative bg-black flex items-center justify-center min-h-[380px] max-h-[520px] overflow-hidden group">
        {videoUrl ? (
          <video
            ref={videoRef}
            src={videoUrl}
            onTimeUpdate={handleTimeUpdate}
            onEnded={() => setIsPlaying(false)}
            onClick={togglePlay}
            className={`max-h-[500px] object-contain transition-all duration-300 ${
              selectedRatio === '9:16'
                ? 'aspect-[9/16] w-auto max-w-[280px]'
                : selectedRatio === '1:1'
                ? 'aspect-square w-auto max-w-[420px]'
                : 'aspect-video w-full'
            }`}
          />
        ) : (
          <div className="text-center p-8 text-slate-500 text-sm">
            No video rendered for {selectedRatio} ratio.
          </div>
        )}

        {/* Big play button overlay when paused */}
        {videoUrl && !isPlaying && (
          <button
            onClick={togglePlay}
            className="absolute inset-0 flex items-center justify-center bg-black/40 group-hover:bg-black/30 transition-all"
          >
            <div className="w-16 h-16 rounded-full bg-cyan-500/90 text-white flex items-center justify-center shadow-xl shadow-cyan-500/40 hover:scale-110 transition-transform">
              <Play className="w-7 h-7 ml-1 fill-white" />
            </div>
          </button>
        )}
      </div>

      {/* Control Bar */}
      <div className="p-3 bg-slate-950/80 border-t border-slate-800/80 flex flex-col space-y-2">
        {/* Scrubber */}
        <input
          type="range"
          min="0"
          max={duration || 100}
          value={currentTime}
          onChange={handleSeek}
          className="w-full h-1.5 bg-slate-800 rounded-lg appearance-none cursor-pointer accent-cyan-500 hover:h-2 transition-all"
        />

        <div className="flex items-center justify-between text-xs text-slate-300">
          <div className="flex items-center space-x-3">
            <button
              onClick={togglePlay}
              className="p-1.5 hover:text-cyan-400 rounded-md transition-colors"
            >
              {isPlaying ? <Pause className="w-4 h-4" /> : <Play className="w-4 h-4 fill-current" />}
            </button>

            <button
              onClick={toggleMute}
              className="p-1.5 hover:text-cyan-400 rounded-md transition-colors"
            >
              {isMuted ? <VolumeX className="w-4 h-4 text-rose-400" /> : <Volume2 className="w-4 h-4" />}
            </button>

            <span className="font-mono text-[11px] text-slate-400">
              {formatTime(currentTime)} / {formatTime(duration)}
            </span>
          </div>

          <div className="flex items-center space-x-2">
            <button
              onClick={toggleFullscreen}
              className="p-1.5 hover:text-cyan-400 rounded-md transition-colors"
              title="Fullscreen"
            >
              <Maximize className="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
