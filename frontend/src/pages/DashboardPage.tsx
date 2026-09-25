import React, { useState, useEffect } from 'react';
import {
  FolderKanban,
  Users,
  Database,
  FilePlus,
  Copy,
  AlertTriangle,
  Lightbulb,
  ArrowRight,
  TrendingUp,
  Sparkles,
  RefreshCw,
  ExternalLink
} from 'lucide-react';
import { KPICard } from '../components/KPICard';
import type { DashboardData, Post } from '../types';
import { api } from '../services/api';

interface DashboardPageProps {
  selectedProjectId?: number;
  onNavigateTab: (tab: string) => void;
  onOpenScrapeModal: (mode: 'live' | 'demo') => void;
  onSelectPost: (post: Post) => void;
}

export const DashboardPage: React.FC<DashboardPageProps> = ({
  selectedProjectId,
  onNavigateTab,
  onOpenScrapeModal,
  onSelectPost,
}) => {
  const [data, setData] = useState<DashboardData | null>(null);
  const [loading, setLoading] = useState(true);

  const loadDashboard = async () => {
    setLoading(true);
    try {
      const res = await api.getDashboard(selectedProjectId);
      setData(res);
    } catch (err) {
      console.error('Failed to load dashboard', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadDashboard();
  }, [selectedProjectId]);

  if (loading || !data) {
    return (
      <div className="p-6 space-y-6 animate-pulse">
        <div className="h-8 w-64 bg-slate-800 rounded-lg" />
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {[...Array(4)].map((_, i) => (
            <div key={i} className="h-28 bg-slate-900 border border-slate-800 rounded-xl" />
          ))}
        </div>
        <div className="h-64 bg-slate-900 border border-slate-800 rounded-xl" />
      </div>
    );
  }

  const { kpis } = data;

  return (
    <div className="p-6 space-y-6">
      {/* Welcome Banner */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 bg-gradient-to-r from-indigo-950/70 via-slate-900 to-slate-900 border border-indigo-500/20 p-6 rounded-2xl shadow-sm">
        <div className="space-y-1">
          <div className="flex items-center space-x-2">
            <span className="px-2.5 py-0.5 rounded-full text-xs font-bold bg-indigo-500/20 text-indigo-300 border border-indigo-500/30">
              Intelligence Radar Active
            </span>
          </div>
          <h2 className="text-xl font-black text-white tracking-tight">
            Google Maps Competitor Intelligence
          </h2>
          <p className="text-xs text-slate-400 max-w-xl">
            Continuously tracking competitor updates, detecting duplicates, benchmarking topics, and generating counter-campaigns.
          </p>
        </div>

        <div className="flex items-center space-x-2.5 flex-wrap gap-y-2">
          <button
            onClick={() => onOpenScrapeModal('demo')}
            className="inline-flex items-center space-x-1.5 px-3.5 py-2 rounded-xl text-xs font-bold bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 transition-all shadow-sm"
          >
            <RefreshCw size={13} className="text-emerald-400" />
            <span>Run Demo Scrape</span>
          </button>
          <button
            onClick={() => onOpenScrapeModal('live')}
            className="inline-flex items-center space-x-1.5 px-3.5 py-2 rounded-xl text-xs font-bold bg-indigo-600 hover:bg-indigo-500 text-white transition-all shadow-md shadow-indigo-600/30"
          >
            <Sparkles size={13} />
            <span>Start Live Scrape</span>
          </button>
        </div>
      </div>

      {/* Top KPI Cards (Required from prompt section 18) */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <KPICard
          title="Total Projects"
          value={kpis.total_projects}
          subtitle="Managed business workspaces"
          icon={FolderKanban}
          color="indigo"
        />
        <KPICard
          title="Total Competitors"
          value={kpis.total_competitors}
          subtitle="Monitored Google Maps profiles"
          icon={Users}
          color="sky"
        />
        <KPICard
          title="Total Stored Posts"
          value={kpis.total_posts}
          subtitle="Persistent repository updates"
          icon={Database}
          color="emerald"
        />
        <KPICard
          title="New Posts Latest Scrape"
          value={`+${kpis.new_posts_latest}`}
          subtitle="Newly discovered updates"
          icon={FilePlus}
          color="emerald"
        />
        <KPICard
          title="Duplicates Skipped"
          value={kpis.duplicate_posts_skipped}
          subtitle="Duplicate fingerprints bypassed"
          icon={Copy}
          color="amber"
        />
        <KPICard
          title="Failed Attempts"
          value={kpis.failed_attempts}
          subtitle="Encountered issues or captcha"
          icon={AlertTriangle}
          color="rose"
        />
        <KPICard
          title="Generated Content"
          value={kpis.generated_content_count}
          subtitle="AI Ideas & Publish-ready Updates"
          icon={Lightbulb}
          color="indigo"
        />
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-sm hover:border-slate-700 transition-all flex flex-col justify-between">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">AI Content Hub</span>
            <span className="p-2 rounded-lg bg-indigo-500/10 text-indigo-400 border border-indigo-500/20">
              <Sparkles size={18} />
            </span>
          </div>
          <button
            onClick={() => onNavigateTab('ideas')}
            className="mt-3 inline-flex items-center justify-between w-full px-3 py-2 rounded-lg bg-indigo-600/20 hover:bg-indigo-600/30 text-indigo-300 text-xs font-bold border border-indigo-500/30 transition-all"
          >
            <span>Generate New Ideas</span>
            <ArrowRight size={13} />
          </button>
        </div>
      </div>

      {/* Main Grid: Recent Activity & Topic Analytics */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left: Top Topics & Keywords */}
        <div className="lg:col-span-6 space-y-6">
          {/* Top Topics */}
          <div className="bg-slate-900 border border-slate-800 rounded-2xl p-5 space-y-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-2">
                <TrendingUp size={16} className="text-indigo-400" />
                <h3 className="text-sm font-bold text-white">Dominant Competitor Topics</h3>
              </div>
              <button
                onClick={() => onNavigateTab('trends')}
                className="text-xs font-semibold text-indigo-400 hover:text-indigo-300 flex items-center space-x-1"
              >
                <span>View Full Trends</span>
                <ArrowRight size={12} />
              </button>
            </div>

            <div className="space-y-3">
              {data.top_topics.map((t, idx) => {
                const total = kpis.total_posts || 1;
                const pct = Math.round((t.count / total) * 100);
                return (
                  <div key={idx} className="space-y-1">
                    <div className="flex justify-between text-xs">
                      <span className="font-semibold text-slate-300">{t.topic}</span>
                      <span className="text-slate-400 font-medium">
                        {t.count} posts ({pct}%)
                      </span>
                    </div>
                    <div className="w-full h-2 rounded-full bg-slate-800 overflow-hidden">
                      <div
                        className="h-full bg-indigo-500 rounded-full transition-all duration-500"
                        style={{ width: `${Math.min(pct, 100)}%` }}
                      />
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Keywords Frequency Cloud */}
          <div className="bg-slate-900 border border-slate-800 rounded-2xl p-5 space-y-3">
            <h3 className="text-sm font-bold text-white">Most Frequently Used Keywords</h3>
            <div className="flex flex-wrap gap-2">
              {data.top_keywords.map((kw, idx) => (
                <span
                  key={idx}
                  className="px-3 py-1 rounded-lg text-xs font-medium bg-slate-950 text-slate-300 border border-slate-800 hover:border-indigo-500/40 transition-colors"
                >
                  #{kw.keyword}{' '}
                  <span className="text-[10px] text-slate-500 ml-1 font-bold">({kw.count})</span>
                </span>
              ))}
            </div>
          </div>
        </div>

        {/* Right: Competitor Posting Activity & Recent Jobs */}
        <div className="lg:col-span-6 space-y-6">
          {/* Competitor Activity */}
          <div className="bg-slate-900 border border-slate-800 rounded-2xl p-5 space-y-4">
            <div className="flex items-center justify-between">
              <h3 className="text-sm font-bold text-white">Competitor Post Share</h3>
              <button
                onClick={() => onNavigateTab('competitors')}
                className="text-xs font-semibold text-indigo-400 hover:text-indigo-300 flex items-center space-x-1"
              >
                <span>Manage</span>
                <ArrowRight size={12} />
              </button>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
              {data.competitor_activity.map((comp) => (
                <div
                  key={comp.id}
                  className="p-3.5 bg-slate-950 rounded-xl border border-slate-800/80 flex items-center justify-between"
                >
                  <div className="truncate mr-2">
                    <p className="text-xs font-bold text-slate-200 truncate">{comp.name}</p>
                    <p className="text-[10px] text-slate-400">{comp.post_count} posts collected</p>
                  </div>
                  <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-slate-800 text-slate-300">
                    {comp.status}
                  </span>
                </div>
              ))}
            </div>
          </div>

          {/* AI Intelligence Brief */}
          <div className="p-5 bg-gradient-to-br from-slate-900 to-indigo-950/40 border border-slate-800 rounded-2xl space-y-2">
            <div className="flex items-center space-x-2 text-indigo-400">
              <Sparkles size={16} />
              <h4 className="text-xs font-bold uppercase tracking-wider text-slate-200">
                Automated Strategic Insight
              </h4>
            </div>
            <p className="text-xs text-slate-300 leading-relaxed">{data.ai_overview}</p>
          </div>
        </div>
      </div>

      {/* Latest Competitor Updates */}
      <div className="bg-slate-900 border border-slate-800 rounded-2xl p-5 space-y-4">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-sm font-bold text-white">Latest Competitor Updates</h3>
            <p className="text-xs text-slate-400">Directly extracted from Google Maps business profiles</p>
          </div>
          <button
            onClick={() => onNavigateTab('repository')}
            className="text-xs font-semibold text-indigo-400 hover:text-indigo-300 flex items-center space-x-1"
          >
            <span>Explore All in Repository</span>
            <ArrowRight size={12} />
          </button>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {data.recent_posts.map((post) => (
            <div
              key={post.id}
              onClick={() => onSelectPost(post)}
              className="p-4 bg-slate-950 rounded-xl border border-slate-800 hover:border-slate-700 transition-all cursor-pointer flex flex-col justify-between space-y-3"
            >
              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-bold text-indigo-400 truncate max-w-[180px]">
                    {post.competitor_name}
                  </span>
                  <span className="text-[10px] text-slate-400">
                    {post.published_date
                      ? new Date(post.published_date).toLocaleDateString(undefined, {
                          month: 'short',
                          day: 'numeric',
                        })
                      : 'Recent'}
                  </span>
                </div>
                <p className="text-xs text-slate-300 line-clamp-2 leading-relaxed">
                  {post.post_text}
                </p>
              </div>

              <div className="flex items-center justify-between pt-2 border-t border-slate-800/80 text-[11px]">
                <span className="text-slate-400 font-medium">{post.industry_topic || 'Update'}</span>
                <span className="text-indigo-400 font-bold hover:underline">Inspect Post →</span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
