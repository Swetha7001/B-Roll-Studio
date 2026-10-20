import React, { useEffect, useState } from 'react';
import { Film, History, PlusCircle, FileCode, Sparkles } from 'lucide-react';
import { checkHealth } from '../services/api';

interface NavbarProps {
  currentTab: string;
  setCurrentTab: (tab: string) => void;
}

export const Navbar: React.FC<NavbarProps> = ({ currentTab, setCurrentTab }) => {
  const [isHealthy, setIsHealthy] = useState<boolean | null>(null);

  useEffect(() => {
    checkHealth()
      .then((data) => setIsHealthy(data.status === 'ok'))
      .catch(() => setIsHealthy(false));
  }, []);

  return (
    <header className="border-b border-slate-800 bg-[#090d16]/90 backdrop-blur-md sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        {/* Brand */}
        <div 
          onClick={() => setCurrentTab('dashboard')}
          className="flex items-center space-x-3 cursor-pointer group"
        >
          <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-cyan-500 to-violet-600 flex items-center justify-center shadow-lg shadow-cyan-500/20 group-hover:scale-105 transition-transform">
            <Film className="w-5 h-5 text-white" />
          </div>
          <div>
            <div className="flex items-center space-x-1.5">
              <span className="font-bold text-lg text-white tracking-tight">B-Roll Studio</span>
              <span className="text-[10px] font-semibold px-1.5 py-0.5 rounded bg-cyan-500/10 text-cyan-400 border border-cyan-500/20">PRO</span>
            </div>
            <p className="text-[11px] text-slate-400 hidden sm:block">Script & Voiceover Video Engine</p>
          </div>
        </div>

        {/* Navigation Tabs */}
        <nav className="flex items-center space-x-1 sm:space-x-2">
          <button
            onClick={() => setCurrentTab('dashboard')}
            className={`px-3 py-1.5 rounded-lg text-xs sm:text-sm font-medium transition-colors flex items-center space-x-2 ${
              currentTab === 'dashboard'
                ? 'bg-slate-800 text-cyan-400 border border-cyan-500/20'
                : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'
            }`}
          >
            <Film className="w-4 h-4" />
            <span>Projects</span>
          </button>

          <button
            onClick={() => setCurrentTab('create')}
            className={`px-3.5 py-1.5 rounded-lg text-xs sm:text-sm font-medium transition-all flex items-center space-x-2 ${
              currentTab === 'create'
                ? 'bg-gradient-to-r from-cyan-500 to-violet-600 text-white shadow-lg shadow-cyan-500/20'
                : 'bg-cyan-500/10 text-cyan-300 hover:bg-cyan-500/20 border border-cyan-500/30'
            }`}
          >
            <PlusCircle className="w-4 h-4" />
            <span>New Video</span>
          </button>

          <button
            onClick={() => setCurrentTab('google-studio')}
            className={`px-3.5 py-1.5 rounded-lg text-xs sm:text-sm font-semibold transition-all flex items-center space-x-2 ${
              currentTab === 'google-studio'
                ? 'bg-gradient-to-r from-violet-600 via-indigo-600 to-cyan-500 text-white shadow-lg shadow-violet-500/30 border border-violet-400/40'
                : 'bg-violet-500/10 text-violet-300 hover:bg-violet-500/20 border border-violet-500/30'
            }`}
          >
            <Sparkles className="w-4 h-4 text-violet-400" />
            <span>Google AI Studio</span>
          </button>

          <button
            onClick={() => setCurrentTab('history')}
            className={`px-3 py-1.5 rounded-lg text-xs sm:text-sm font-medium transition-colors flex items-center space-x-2 ${
              currentTab === 'history'
                ? 'bg-slate-800 text-cyan-400 border border-cyan-500/20'
                : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'
            }`}
          >
            <History className="w-4 h-4" />
            <span>History</span>
          </button>

          <a
            href="/docs"
            target="_blank"
            rel="noreferrer"
            className="px-3 py-1.5 rounded-lg text-xs sm:text-sm font-medium text-slate-400 hover:text-slate-200 hover:bg-slate-800/50 transition-colors flex items-center space-x-1.5"
            title="OpenAPI Swagger Documentation"
          >
            <FileCode className="w-4 h-4" />
            <span className="hidden md:inline">API Docs</span>
          </a>
        </nav>

        {/* Backend Status indicator */}
        <div className="flex items-center space-x-2 pl-2">
          <div className="flex items-center space-x-1.5 text-xs px-2.5 py-1 rounded-full bg-slate-900 border border-slate-800">
            <span
              className={`w-2 h-2 rounded-full ${
                isHealthy === true
                  ? 'bg-emerald-400 animate-pulse'
                  : isHealthy === false
                  ? 'bg-rose-500'
                  : 'bg-amber-400'
              }`}
            />
            <span className="text-[11px] font-mono text-slate-400 hidden sm:inline">
              {isHealthy === true ? 'Engine Ready' : isHealthy === false ? 'Engine Offline' : 'Connecting...'}
            </span>
          </div>
        </div>
      </div>
    </header>
  );
};
