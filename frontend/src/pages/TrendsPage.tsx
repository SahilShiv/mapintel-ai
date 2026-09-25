import React, { useState, useEffect } from 'react';
import {
  TrendingUp,
  BarChart3,
  Calendar,
  Sparkles,
  Layers,
  PieChart,
  Tag,
  ArrowUpRight,
  Flame,
  CheckCircle2
} from 'lucide-react';
import type { TrendAnalysis, Project } from '../types';
import { api } from '../services/api';

interface TrendsPageProps {
  selectedProjectId?: number;
  projects: Project[];
}

export const TrendsPage: React.FC<TrendsPageProps> = ({
  selectedProjectId,
  projects,
}) => {
  const [trends, setTrends] = useState<TrendAnalysis | null>(null);
  const [loading, setLoading] = useState(true);
  const activeProjectId = selectedProjectId || (projects[0]?.id || 1);

  const loadTrends = async () => {
    setLoading(true);
    try {
      const data = await api.getTrends(activeProjectId);
      setTrends(data);
    } catch (err) {
      console.error('Error fetching trends', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (activeProjectId) {
      loadTrends();
    }
  }, [activeProjectId]);

  if (loading || !trends) {
    return (
      <div className="p-6 space-y-6 animate-pulse">
        <div className="h-8 w-64 bg-slate-800 rounded-lg" />
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div className="h-64 bg-slate-900 border border-slate-800 rounded-2xl" />
          <div className="h-64 bg-slate-900 border border-slate-800 rounded-2xl" />
        </div>
      </div>
    );
  }

  return (
    <div className="p-6 space-y-6">
      {/* Page Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-black text-white tracking-tight">Competitor Trend Analytics</h2>
          <p className="text-xs text-slate-400">
            Empirical repository calculations analyzing competitor topic frequency, posting cadences, and conversions.
          </p>
        </div>

        <div className="flex items-center space-x-2 text-xs">
          <span className="px-3 py-1.5 rounded-xl bg-slate-900 border border-slate-800 text-slate-300 font-semibold">
            Based on <strong className="text-indigo-400">{trends.total_posts}</strong> Verified Updates
          </span>
        </div>
      </div>

      {/* AI Automated Synthesis Card (Clearly marked as AI insight) */}
      <div className="p-5 bg-gradient-to-r from-indigo-950/60 via-slate-900 to-slate-900 border border-indigo-500/30 rounded-2xl space-y-2">
        <div className="flex items-center space-x-2 text-indigo-400">
          <Sparkles size={16} />
          <h4 className="text-xs font-bold uppercase tracking-wider text-slate-200">
            AI Market Synthesis & Intelligence Insight
          </h4>
        </div>
        <p className="text-xs text-slate-300 leading-relaxed font-normal">
          {trends.ai_insights}
        </p>
      </div>

      {/* Section 1: Topic Frequency Table & Bar Representation (Prompt Requirement 17) */}
      <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 space-y-5">
        <div className="flex items-center justify-between">
          <div className="space-y-0.5">
            <h3 className="text-sm font-bold text-white flex items-center space-x-2">
              <Flame size={16} className="text-amber-400" />
              <span>Competitor Topic Frequency Distribution</span>
            </h3>
            <p className="text-xs text-slate-400">
              Breakdown of topics, occurrence rate, and competitors deploying each topic.
            </p>
          </div>
          <span className="text-[11px] font-bold text-slate-500 uppercase tracking-wider">
            Repository Metric
          </span>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs divide-y divide-slate-800">
            <thead className="bg-slate-950 text-slate-400 uppercase tracking-wider text-[10px]">
              <tr>
                <th className="px-4 py-3 font-bold">Topic</th>
                <th className="px-4 py-3 font-bold">Competitors Using Topic</th>
                <th className="px-4 py-3 font-bold">Occurrence Rate</th>
                <th className="px-4 py-3 font-bold">Visual Share</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800 text-slate-300">
              {trends.top_topics.map((t, idx) => (
                <tr key={idx} className="hover:bg-slate-950/40 transition-colors">
                  <td className="px-4 py-3.5 font-bold text-white">{t.topic}</td>
                  <td className="px-4 py-3.5 text-slate-300">
                    <span className="font-bold text-indigo-400">{t.competitors_count}</span> competitor{t.competitors_count !== 1 ? 's' : ''} ({t.competitors.slice(0, 2).join(', ')}{t.competitors.length > 2 ? '...' : ''})
                  </td>
                  <td className="px-4 py-3.5">
                    <span className="font-bold text-slate-200">{t.count}</span> / {trends.total_posts} ({t.percentage}%)
                  </td>
                  <td className="px-4 py-3.5 w-48">
                    <div className="w-full h-2.5 rounded-full bg-slate-950 overflow-hidden border border-slate-800">
                      <div
                        className="h-full bg-indigo-500 rounded-full"
                        style={{ width: `${Math.min(t.percentage, 100)}%` }}
                      />
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Section 2: Content Type & CTA Distributions */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Content Type Distribution */}
        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-5 space-y-4">
          <h3 className="text-sm font-bold text-white flex items-center space-x-2">
            <PieChart size={16} className="text-sky-400" />
            <span>Content Type Distribution</span>
          </h3>

          <div className="space-y-3">
            {trends.content_types.map((ct, idx) => (
              <div key={idx} className="space-y-1">
                <div className="flex justify-between text-xs">
                  <span className="font-semibold text-slate-300">{ct.content_type}</span>
                  <span className="text-slate-400 font-medium">
                    {ct.count} posts ({ct.percentage}%)
                  </span>
                </div>
                <div className="w-full h-2 rounded-full bg-slate-950 overflow-hidden">
                  <div
                    className="h-full bg-sky-500 rounded-full"
                    style={{ width: `${Math.min(ct.percentage, 100)}%` }}
                  />
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* CTA Distribution */}
        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-5 space-y-4">
          <h3 className="text-sm font-bold text-white flex items-center space-x-2">
            <BarChart3 size={16} className="text-emerald-400" />
            <span>Call-to-Action (CTA) Distribution</span>
          </h3>

          <div className="space-y-3">
            {trends.call_to_actions.map((cta, idx) => (
              <div key={idx} className="space-y-1">
                <div className="flex justify-between text-xs">
                  <span className="font-semibold text-slate-300">{cta.call_to_action}</span>
                  <span className="text-slate-400 font-medium">
                    {cta.count} ({cta.percentage}%)
                  </span>
                </div>
                <div className="w-full h-2 rounded-full bg-slate-950 overflow-hidden">
                  <div
                    className="h-full bg-emerald-500 rounded-full"
                    style={{ width: `${Math.min(cta.percentage, 100)}%` }}
                  />
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Section 3: Competitor Activity Benchmarks */}
      <div className="bg-slate-900 border border-slate-800 rounded-2xl p-5 space-y-4">
        <h3 className="text-sm font-bold text-white flex items-center space-x-2">
          <Layers size={16} className="text-purple-400" />
          <span>Competitor Publishing Velocity</span>
        </h3>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {trends.competitor_activity.map((comp) => (
            <div
              key={comp.competitor_id}
              className="p-4 bg-slate-950 rounded-xl border border-slate-800 space-y-2.5"
            >
              <div className="flex justify-between items-start">
                <h4 className="text-xs font-bold text-white truncate max-w-[180px]">
                  {comp.competitor_name}
                </h4>
                <span className="text-xs font-bold text-indigo-400 px-2 py-0.5 rounded-lg bg-indigo-500/10">
                  {comp.post_count} posts
                </span>
              </div>

              {comp.latest_post_date && (
                <p className="text-[11px] text-slate-400 flex items-center space-x-1">
                  <Calendar size={12} />
                  <span>Latest: {new Date(comp.latest_post_date).toLocaleDateString()}</span>
                </p>
              )}

              {comp.top_topics.length > 0 && (
                <div className="pt-1">
                  <span className="text-[10px] text-slate-500 block mb-1">Top Focus Topics:</span>
                  <div className="flex flex-wrap gap-1">
                    {comp.top_topics.map((tp, i) => (
                      <span
                        key={i}
                        className="px-2 py-0.5 rounded text-[10px] bg-slate-900 text-slate-300 border border-slate-800"
                      >
                        {tp}
                      </span>
                    ))}
                  </div>
                </div>
              )}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
