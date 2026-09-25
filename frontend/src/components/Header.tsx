import React from 'react';
import { Menu, Play, RefreshCw, Layers } from 'lucide-react';
import type { Project } from '../types';

interface HeaderProps {
  projects: Project[];
  selectedProjectId?: number;
  onSelectProject: (id?: number) => void;
  onOpenMobileMenu: () => void;
  onTriggerScrape: (mode: 'live' | 'demo') => void;
}

export const Header: React.FC<HeaderProps> = ({
  projects,
  selectedProjectId,
  onSelectProject,
  onOpenMobileMenu,
  onTriggerScrape,
}) => {
  return (
    <header className="sticky top-0 z-30 h-16 bg-slate-900/90 backdrop-blur-md border-b border-slate-800 px-4 sm:px-6 flex items-center justify-between">
      <div className="flex items-center space-x-3">
        <button
          onClick={onOpenMobileMenu}
          className="p-2 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 lg:hidden"
        >
          <Menu size={20} />
        </button>

        {/* Project Selector */}
        <div className="flex items-center space-x-2">
          <Layers size={18} className="text-indigo-400 hidden sm:block" />
          <div className="relative">
            <select
              value={selectedProjectId || ''}
              onChange={(e) => {
                const val = e.target.value ? Number(e.target.value) : undefined;
                onSelectProject(val);
              }}
              className="bg-slate-950 border border-slate-700/80 text-slate-200 text-xs sm:text-sm rounded-lg px-3 py-1.5 focus:outline-none focus:ring-2 focus:ring-indigo-500 cursor-pointer pr-8 font-medium"
            >
              <option value="">All Projects (Global Intelligence)</option>
              {projects.map((p) => (
                <option key={p.id} value={p.id}>
                  {p.project_name} ({p.client_business_name})
                </option>
              ))}
            </select>
          </div>
        </div>
      </div>

      {/* Header Actions */}
      <div className="flex items-center space-x-2 sm:space-x-3">
        <button
          onClick={() => onTriggerScrape('demo')}
          className="inline-flex items-center space-x-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold bg-emerald-600/20 text-emerald-300 border border-emerald-500/40 hover:bg-emerald-600/30 transition-all shadow-sm"
          title="Run authentic demo scrape with full duplicate detection"
        >
          <RefreshCw size={13} className="text-emerald-400" />
          <span>Run Demo Scrape</span>
        </button>

        <button
          onClick={() => onTriggerScrape('live')}
          className="inline-flex items-center space-x-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold bg-indigo-600 hover:bg-indigo-500 text-white transition-all shadow-md shadow-indigo-600/25"
          title="Run live Python Selenium Google Maps scraper"
        >
          <Play size={13} className="fill-white" />
          <span>Start Scrape</span>
        </button>
      </div>
    </header>
  );
};
