import React from 'react';
import {
  LayoutDashboard,
  FolderKanban,
  Users,
  Database,
  PlayCircle,
  TrendingUp,
  Brain,
  Lightbulb,
  FileText,
  Settings,
  X
} from 'lucide-react';

interface SidebarProps {
  currentTab: string;
  setCurrentTab: (tab: string) => void;
  isOpen: boolean;
  setIsOpen: (open: boolean) => void;
}

export const Sidebar: React.FC<SidebarProps> = ({
  currentTab,
  setCurrentTab,
  isOpen,
  setIsOpen,
}) => {
  const menuItems = [
    { id: 'dashboard', label: 'Dashboard', icon: LayoutDashboard },
    { id: 'projects', label: 'Projects', icon: FolderKanban },
    { id: 'competitors', label: 'Competitors', icon: Users },
    { id: 'repository', label: 'Post Repository', icon: Database },
    { id: 'scraping', label: 'Scraping Jobs', icon: PlayCircle },
    { id: 'trends', label: 'Trends & Analytics', icon: TrendingUp },
    { id: 'analysis', label: 'AI Analysis', icon: Brain },
    { id: 'ideas', label: 'Content Ideas', icon: Lightbulb },
    { id: 'updates', label: 'Generated Updates', icon: FileText },
    { id: 'settings', label: 'Settings', icon: Settings },
  ];

  return (
    <>
      {/* Mobile backdrop */}
      {isOpen && (
        <div
          className="fixed inset-0 z-40 bg-black/60 backdrop-blur-sm lg:hidden"
          onClick={() => setIsOpen(false)}
        />
      )}

      <aside
        className={`fixed top-0 bottom-0 left-0 z-50 flex flex-col w-64 bg-slate-950 border-r border-slate-800 transition-transform duration-300 lg:translate-x-0 ${
          isOpen ? 'translate-x-0' : '-translate-x-full'
        }`}
      >
        {/* Logo and title */}
        <div className="flex items-center justify-between px-5 h-16 border-b border-slate-800">
          <div className="flex items-center space-x-3">
            <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-indigo-500 via-indigo-600 to-sky-400 flex items-center justify-center shadow-lg shadow-indigo-500/20">
              <span className="text-white font-black text-lg tracking-wider">GM</span>
            </div>
            <div>
              <h1 className="text-sm font-bold text-white tracking-tight leading-none">MapIntel AI</h1>
              <p className="text-[10px] text-slate-400 font-medium mt-1">Competitor Updates</p>
            </div>
          </div>
          <button
            onClick={() => setIsOpen(false)}
            className="p-1 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 lg:hidden"
          >
            <X size={20} />
          </button>
        </div>

        {/* Navigation list */}
        <nav className="flex-1 px-3 py-4 space-y-1 overflow-y-auto">
          {menuItems.map((item) => {
            const Icon = item.icon;
            const active = currentTab === item.id;
            return (
              <button
                key={item.id}
                onClick={() => {
                  setCurrentTab(item.id);
                  setIsOpen(false);
                }}
                className={`w-full flex items-center space-x-3 px-3.5 py-2.5 rounded-lg text-sm font-medium transition-all ${
                  active
                    ? 'bg-indigo-600 text-white shadow-md shadow-indigo-600/30'
                    : 'text-slate-400 hover:text-slate-200 hover:bg-slate-900'
                }`}
              >
                <Icon size={18} className={active ? 'text-white' : 'text-slate-400'} />
                <span>{item.label}</span>
              </button>
            );
          })}
        </nav>

        {/* System badge footer */}
        <div className="p-4 border-t border-slate-800/80 bg-slate-950/60">
          <div className="rounded-xl p-3 bg-slate-900 border border-slate-800 flex flex-col space-y-2">
            <div className="flex items-center justify-between">
              <span className="text-xs font-semibold text-slate-300">Engine Status</span>
              <span className="inline-flex items-center px-1.5 py-0.5 rounded-full text-[10px] font-medium bg-emerald-500/20 text-emerald-400 border border-emerald-500/30">
                Active
              </span>
            </div>
            <p className="text-[11px] text-slate-400 leading-tight">
              Selenium + Heuristic & Dual AI Providers Ready
            </p>
          </div>
        </div>
      </aside>
    </>
  );
};
