import React, { useState, useEffect } from 'react';
import {
  Lightbulb,
  Sparkles,
  ShieldCheck,
  Tag,
  ArrowRight,
  Trash2,
  CheckCircle2,
  Layers,
  FileText
} from 'lucide-react';
import type { GeneratedIdea, Project } from '../types';
import { api } from '../services/api';

interface ContentIdeasPageProps {
  selectedProjectId?: number;
  projects: Project[];
  onDraftUpdateFromIdea: (idea: GeneratedIdea) => void;
}

export const ContentIdeasPage: React.FC<ContentIdeasPageProps> = ({
  selectedProjectId,
  projects,
  onDraftUpdateFromIdea,
}) => {
  const [ideas, setIdeas] = useState<GeneratedIdea[]>([]);
  const [loading, setLoading] = useState(true);
  const [generating, setGenerating] = useState(false);

  // Exact Requested Count selector: 3, 5, 10, 20, 50
  const [count, setCount] = useState<number>(10);
  const [focusTopic, setFocusTopic] = useState('');
  const [provider, setProvider] = useState<'gemini' | 'grok' | 'fallback_nlp'>('gemini');
  const [generationInfo, setGenerationInfo] = useState<{ count: number; duplicatesSkipped: number } | null>(null);

  const activeProjectId = selectedProjectId || (projects[0]?.id || 1);

  const loadIdeas = async () => {
    setLoading(true);
    try {
      const data = await api.getGeneratedIdeas(activeProjectId);
      setIdeas(data);
    } catch (err) {
      console.error('Error fetching ideas', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (activeProjectId) {
      loadIdeas();
    }
  }, [activeProjectId]);

  const handleGenerate = async () => {
    setGenerating(true);
    setGenerationInfo(null);
    try {
      const res = await api.generateIdeas({
        project_id: activeProjectId,
        count: count,
        focus_topic: focusTopic || undefined,
        provider: provider,
      });

      setGenerationInfo({
        count: res.generated_count,
        duplicatesSkipped: res.skipped_duplicates,
      });
      loadIdeas();
    } catch (err) {
      console.error('Error generating ideas', err);
    } finally {
      setGenerating(false);
    }
  };

  const handleDelete = async (id: number) => {
    try {
      await api.deleteIdea(id);
      setIdeas(ideas.filter((i) => i.id !== id));
    } catch (err) {
      console.error('Error deleting idea', err);
    }
  };

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-black text-white tracking-tight">AI Content Idea Generator</h2>
          <p className="text-xs text-slate-400">
            Formulate targeted Google Maps update ideas based on competitor trends, topic gaps, and stored intelligence.
          </p>
        </div>

        {/* Duplicate Prevention Status Badge */}
        <div className="flex items-center space-x-2 px-3 py-1.5 rounded-xl bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 text-xs font-semibold">
          <ShieldCheck size={15} />
          <span>Semantic Duplicate Prevention Active</span>
        </div>
      </div>

      {/* Generation Control Panel */}
      <div className="bg-slate-900 border border-slate-800 rounded-2xl p-5 space-y-4">
        <h3 className="text-xs font-bold uppercase tracking-wider text-slate-400">
          Configure Generation Parameters
        </h3>

        <div className="grid grid-cols-1 md:grid-cols-12 gap-4 text-xs">
          {/* Requested Number of Ideas (Prompt requirement: 3, 5, 10, 20, 50) */}
          <div className="md:col-span-5 space-y-1.5">
            <label className="text-slate-300 font-semibold block">Requested Ideas Count</label>
            <div className="flex items-center space-x-2">
              {[3, 5, 10, 20, 50].map((num) => (
                <button
                  key={num}
                  type="button"
                  onClick={() => setCount(num)}
                  className={`flex-1 py-2 rounded-xl font-bold border transition-all text-xs ${
                    count === num
                      ? 'bg-indigo-600 text-white border-indigo-500 shadow-md shadow-indigo-600/30'
                      : 'bg-slate-950 text-slate-400 border-slate-800 hover:border-slate-700 hover:text-white'
                  }`}
                >
                  {num} Ideas
                </button>
              ))}
            </div>
          </div>

          {/* Focus Topic (Optional) */}
          <div className="md:col-span-4 space-y-1.5">
            <label className="text-slate-300 font-semibold block">Focus Topic (Optional)</label>
            <input
              type="text"
              placeholder="e.g. Monsoon Hair Care, Festival Offers..."
              value={focusTopic}
              onChange={(e) => setFocusTopic(e.target.value)}
              className="w-full bg-slate-950 border border-slate-700/80 rounded-xl px-3.5 py-2 text-slate-200 focus:outline-none focus:ring-2 focus:ring-indigo-500"
            />
          </div>

          {/* AI Provider Switcher */}
          <div className="md:col-span-3 space-y-1.5">
            <label className="text-slate-300 font-semibold block">AI Provider</label>
            <select
              value={provider}
              onChange={(e: any) => setProvider(e.target.value)}
              className="w-full bg-slate-950 border border-slate-700/80 rounded-xl px-3 py-2 text-slate-200 focus:outline-none focus:ring-2 focus:ring-indigo-500 cursor-pointer"
            >
              <option value="gemini">Google Gemini</option>
              <option value="grok">xAI Grok</option>
              <option value="fallback_nlp">NLP Heuristic (Local)</option>
            </select>
          </div>
        </div>

        {/* Generate Action Button */}
        <div className="pt-2 flex justify-end">
          <button
            onClick={handleGenerate}
            disabled={generating}
            className="inline-flex items-center space-x-2 px-6 py-2.5 rounded-xl font-bold text-xs bg-indigo-600 hover:bg-indigo-500 text-white shadow-lg shadow-indigo-600/30 transition-all disabled:opacity-50"
          >
            <Sparkles size={14} className={generating ? 'animate-spin' : ''} />
            <span>{generating ? `Synthesizing ${count} Unique Ideas...` : `Generate ${count} Ideas`}</span>
          </button>
        </div>
      </div>

      {/* Generation Confirmation Banner */}
      {generationInfo && (
        <div className="p-4 bg-emerald-500/10 border border-emerald-500/30 rounded-2xl flex items-center justify-between text-xs">
          <div className="flex items-center space-x-2 text-emerald-400 font-semibold">
            <CheckCircle2 size={16} />
            <span>
              Generated {generationInfo.count} new ideas. Semantic duplicate prevention successfully skipped {generationInfo.duplicatesSkipped} similar concepts to avoid repetition!
            </span>
          </div>
        </div>
      )}

      {/* Generated Ideas Grid */}
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <h3 className="text-sm font-bold text-white flex items-center space-x-2">
            <Lightbulb size={16} className="text-amber-400" />
            <span>Generated Content Repository ({ideas.length} Ideas Stored)</span>
          </h3>
        </div>

        {loading ? (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 animate-pulse">
            {[1, 2, 3, 4].map((i) => (
              <div key={i} className="h-48 bg-slate-900 border border-slate-800 rounded-2xl" />
            ))}
          </div>
        ) : ideas.length === 0 ? (
          <div className="bg-slate-900 border border-slate-800 rounded-2xl p-12 text-center space-y-3">
            <Lightbulb size={36} className="mx-auto text-slate-600" />
            <h4 className="text-sm font-bold text-white">No content ideas generated yet</h4>
            <p className="text-xs text-slate-400 max-w-sm mx-auto">
              Select your desired idea count above and click Generate to produce competitor-beating update ideas.
            </p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {ideas.map((idea) => {
              const keywords = idea.relevant_keywords ? idea.relevant_keywords.split(',') : [];
              return (
                <div
                  key={idea.id}
                  className="bg-slate-900 border border-slate-800 hover:border-slate-700 rounded-2xl p-5 shadow-sm flex flex-col justify-between space-y-4 transition-all"
                >
                  <div className="space-y-2.5">
                    <div className="flex items-start justify-between">
                      <div className="space-y-1">
                        <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-indigo-500/10 text-indigo-400 border border-indigo-500/30">
                          {idea.topic}
                        </span>
                        <h4 className="text-sm font-bold text-white leading-tight mt-1">
                          {idea.title}
                        </h4>
                      </div>
                      <button
                        onClick={() => handleDelete(idea.id)}
                        className="p-1 rounded-lg text-slate-500 hover:text-rose-400 hover:bg-slate-800"
                        title="Delete idea"
                      >
                        <Trash2 size={13} />
                      </button>
                    </div>

                    <p className="text-xs text-slate-300 leading-relaxed">{idea.description}</p>

                    {/* Competitor Insight Hook */}
                    {idea.competitor_insight && (
                      <div className="p-3 bg-slate-950 rounded-xl border border-slate-800/80 text-[11px] text-slate-400 space-y-1">
                        <span className="font-semibold text-indigo-300 block">Competitor Insight:</span>
                        <p>{idea.competitor_insight}</p>
                      </div>
                    )}
                  </div>

                  <div className="space-y-3 pt-3 border-t border-slate-800/80">
                    <div className="flex items-center justify-between text-xs">
                      {idea.suggested_cta && (
                        <div className="flex items-center space-x-1.5">
                          <span className="text-[10px] text-slate-500 font-semibold">CTA:</span>
                          <span className="font-bold text-slate-300 px-2 py-0.5 rounded bg-slate-800 text-[11px]">
                            {idea.suggested_cta}
                          </span>
                        </div>
                      )}
                      <span className="text-[10px] text-slate-500">
                        Model: {idea.ai_provider}
                      </span>
                    </div>

                    {/* Fast Action: Draft Complete Update */}
                    <button
                      onClick={() => onDraftUpdateFromIdea(idea)}
                      className="w-full inline-flex items-center justify-center space-x-1.5 py-2.5 rounded-xl bg-indigo-600/15 hover:bg-indigo-600/25 text-indigo-300 text-xs font-bold border border-indigo-500/30 transition-all shadow-sm"
                    >
                      <FileText size={13} />
                      <span>Draft Complete Google Maps Update</span>
                      <ArrowRight size={13} />
                    </button>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
};
