import React, { useState, useEffect } from 'react';
import {
  Brain,
  Sparkles,
  RefreshCw,
  CheckCircle2,
  Tag,
  Building,
  ArrowRight,
  Sliders,
  Filter
} from 'lucide-react';
import type { Post, Project } from '../types';
import { api } from '../services/api';

interface AIAnalysisPageProps {
  selectedProjectId?: number;
  projects: Project[];
  onSelectPost: (post: Post) => void;
}

export const AIAnalysisPage: React.FC<AIAnalysisPageProps> = ({
  selectedProjectId,
  projects,
  onSelectPost,
}) => {
  const [posts, setPosts] = useState<Post[]>([]);
  const [loading, setLoading] = useState(true);
  const [analyzing, setAnalyzing] = useState(false);
  const [provider, setProvider] = useState<'gemini' | 'grok' | 'fallback_nlp'>('gemini');
  const [forceReanalyze, setForceReanalyze] = useState(false);
  const [analysisStats, setAnalysisStats] = useState<{ analyzed_now: number; already_analyzed: number } | null>(null);

  const activeProjectId = selectedProjectId || (projects[0]?.id || 1);

  const loadPosts = async () => {
    setLoading(true);
    try {
      const res = await api.getPosts({ project_id: activeProjectId, page_size: 20 });
      setPosts(res.items);
    } catch (err) {
      console.error('Error fetching posts for AI analysis', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (activeProjectId) {
      loadPosts();
    }
  }, [activeProjectId]);

  const handleRunAnalysis = async () => {
    setAnalyzing(true);
    setAnalysisStats(null);
    try {
      const res = await api.triggerAnalysis(activeProjectId, forceReanalyze, provider);
      setAnalysisStats({
        analyzed_now: res.analyzed_now,
        already_analyzed: res.already_analyzed,
      });
      loadPosts();
    } catch (err) {
      console.error('Error triggering AI analysis', err);
    } finally {
      setAnalyzing(false);
    }
  };

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-black text-white tracking-tight">AI Content Intelligence Analysis</h2>
          <p className="text-xs text-slate-400">
            Extract semantic topics, offer patterns, CTAs, and keywords from stored competitor Google Maps posts.
          </p>
        </div>

        {/* Action Controls */}
        <div className="flex items-center space-x-3 flex-wrap gap-y-2">
          {/* AI Provider Switcher */}
          <div className="flex items-center space-x-1 bg-slate-900 border border-slate-800 p-1 rounded-xl text-xs">
            <button
              onClick={() => setProvider('gemini')}
              className={`px-3 py-1.5 rounded-lg font-semibold transition-all ${
                provider === 'gemini' ? 'bg-indigo-600 text-white' : 'text-slate-400 hover:text-white'
              }`}
            >
              Gemini
            </button>
            <button
              onClick={() => setProvider('grok')}
              className={`px-3 py-1.5 rounded-lg font-semibold transition-all ${
                provider === 'grok' ? 'bg-indigo-600 text-white' : 'text-slate-400 hover:text-white'
              }`}
            >
              Grok
            </button>
            <button
              onClick={() => setProvider('fallback_nlp')}
              className={`px-3 py-1.5 rounded-lg font-semibold transition-all ${
                provider === 'fallback_nlp' ? 'bg-indigo-600 text-white' : 'text-slate-400 hover:text-white'
              }`}
            >
              NLP Heuristic
            </button>
          </div>

          <button
            onClick={handleRunAnalysis}
            disabled={analyzing}
            className="inline-flex items-center space-x-2 px-4 py-2 rounded-xl text-xs font-bold bg-indigo-600 hover:bg-indigo-500 text-white shadow-md shadow-indigo-600/30 transition-all disabled:opacity-50"
          >
            <Sparkles size={14} className={analyzing ? 'animate-spin' : ''} />
            <span>{analyzing ? 'Analyzing Repository...' : 'Run AI Analysis'}</span>
          </button>
        </div>
      </div>

      {/* Analysis Status Banner */}
      {analysisStats && (
        <div className="p-4 bg-emerald-500/10 border border-emerald-500/30 rounded-2xl flex items-center justify-between text-xs">
          <div className="flex items-center space-x-2.5 text-emerald-400">
            <CheckCircle2 size={18} />
            <span className="font-semibold">
              Analysis Completed! Analyzed {analysisStats.analyzed_now} posts ({analysisStats.already_analyzed} previously cached in database).
            </span>
          </div>
          <span className="text-slate-400 text-[11px]">Results saved persistently.</span>
        </div>
      )}

      {/* Analyzed Posts Breakdown */}
      <div className="bg-slate-900 border border-slate-800 rounded-2xl overflow-hidden shadow-sm">
        <div className="p-4 border-b border-slate-800 flex items-center justify-between bg-slate-950/60">
          <div className="flex items-center space-x-2 text-xs font-bold text-white">
            <Brain size={16} className="text-indigo-400" />
            <span>Structured Intelligence Matrix ({posts.length} Posts)</span>
          </div>
          <label className="flex items-center space-x-2 text-xs text-slate-400 cursor-pointer">
            <input
              type="checkbox"
              checked={forceReanalyze}
              onChange={(e) => setForceReanalyze(e.target.checked)}
              className="rounded bg-slate-950 border-slate-700 text-indigo-600 focus:ring-0"
            />
            <span>Force Re-analyze Existing Records</span>
          </label>
        </div>

        {loading ? (
          <div className="p-8 text-center text-xs text-slate-400 animate-pulse">Loading analyzed items...</div>
        ) : (
          <div className="divide-y divide-slate-800">
            {posts.map((post) => (
              <div
                key={post.id}
                onClick={() => onSelectPost(post)}
                className="p-5 hover:bg-slate-950/40 transition-colors cursor-pointer space-y-3"
              >
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 text-xs">
                  <div className="flex items-center space-x-2 font-bold text-white">
                    <Building size={14} className="text-indigo-400" />
                    <span>{post.competitor_name}</span>
                  </div>
                  <div className="flex items-center space-x-2 flex-wrap">
                    <span className="px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-indigo-500/10 text-indigo-400 border border-indigo-500/30">
                      Topic: {post.industry_topic || 'General'}
                    </span>
                    <span className="px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-purple-500/10 text-purple-400 border border-purple-500/30">
                      Type: {post.content_type || 'Update'}
                    </span>
                    {post.call_to_action && (
                      <span className="px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-emerald-500/10 text-emerald-400 border border-emerald-500/30">
                        CTA: {post.call_to_action}
                      </span>
                    )}
                  </div>
                </div>

                <p className="text-xs text-slate-300 line-clamp-2 leading-relaxed">
                  {post.post_text}
                </p>

                {post.analysis && (
                  <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 pt-1 text-[11px]">
                    <div className="p-2 rounded-lg bg-slate-950 border border-slate-800">
                      <span className="text-slate-500 block text-[10px]">Sub-topic:</span>
                      <span className="font-semibold text-slate-300">{post.analysis.sub_topic || 'Standard'}</span>
                    </div>
                    <div className="p-2 rounded-lg bg-slate-950 border border-slate-800">
                      <span className="text-slate-500 block text-[10px]">Offer Pattern:</span>
                      <span className="font-semibold text-slate-300">{post.analysis.offer_pattern || 'None'}</span>
                    </div>
                    <div className="p-2 rounded-lg bg-slate-950 border border-slate-800">
                      <span className="text-slate-500 block text-[10px]">Sentiment:</span>
                      <span className="font-semibold text-emerald-400 capitalize">{post.analysis.sentiment || 'Positive'}</span>
                    </div>
                    <div className="p-2 rounded-lg bg-slate-950 border border-slate-800">
                      <span className="text-slate-500 block text-[10px]">Analyzed By:</span>
                      <span className="font-semibold text-slate-400">{post.analysis.ai_provider || 'local'}</span>
                    </div>
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};
