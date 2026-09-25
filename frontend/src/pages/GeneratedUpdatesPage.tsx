import React, { useState, useEffect } from 'react';
import {
  FileText,
  Sparkles,
  Copy,
  Check,
  Trash2,
  Image as ImageIcon,
  Tag,
  ArrowRight,
  ExternalLink,
  Layers,
  Building
} from 'lucide-react';
import type { GeneratedUpdate, GeneratedIdea, Project } from '../types';
import { api } from '../services/api';

interface GeneratedUpdatesPageProps {
  selectedProjectId?: number;
  projects: Project[];
  prefilledIdea: GeneratedIdea | null;
  onClearPrefilledIdea: () => void;
}

export const GeneratedUpdatesPage: React.FC<GeneratedUpdatesPageProps> = ({
  selectedProjectId,
  projects,
  prefilledIdea,
  onClearPrefilledIdea,
}) => {
  const [updates, setUpdates] = useState<GeneratedUpdate[]>([]);
  const [loading, setLoading] = useState(true);
  const [generating, setGenerating] = useState(false);
  const [copiedId, setCopiedId] = useState<number | null>(null);

  // Form states
  const activeProjectId = selectedProjectId || (projects[0]?.id || 1);
  const [topic, setTopic] = useState(prefilledIdea?.topic || 'Seasonal Promotion');
  const [customPrompt, setCustomPrompt] = useState(prefilledIdea?.description || '');
  const [provider, setProvider] = useState<'gemini' | 'grok' | 'fallback_nlp'>('gemini');

  useEffect(() => {
    if (prefilledIdea) {
      setTopic(prefilledIdea.topic);
      setCustomPrompt(`Idea: ${prefilledIdea.title}. ${prefilledIdea.description}`);
    }
  }, [prefilledIdea]);

  const loadUpdates = async () => {
    setLoading(true);
    try {
      const data = await api.getGeneratedUpdates(activeProjectId);
      setUpdates(data);
    } catch (err) {
      console.error('Error fetching updates', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (activeProjectId) {
      loadUpdates();
    }
  }, [activeProjectId]);

  const handleGenerate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!topic) return;

    setGenerating(true);
    try {
      const res = await api.generateUpdate({
        project_id: activeProjectId,
        idea_id: prefilledIdea?.id,
        topic: topic,
        custom_prompt: customPrompt,
        provider: provider,
      });

      onClearPrefilledIdea();
      loadUpdates();
    } catch (err) {
      console.error('Error generating update draft', err);
    } finally {
      setGenerating(false);
    }
  };

  const handleCopy = (id: number, text: string) => {
    navigator.clipboard.writeText(text);
    setCopiedId(id);
    setTimeout(() => setCopiedId(null), 2000);
  };

  const handleDelete = async (id: number) => {
    try {
      await api.deleteUpdate(id);
      setUpdates(updates.filter((u) => u.id !== id));
    } catch (err) {
      console.error('Error deleting update', err);
    }
  };

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-black text-white tracking-tight">
            Complete Google Maps Update Generator
          </h2>
          <p className="text-xs text-slate-400">
            Generate publish-ready Google Maps updates influenced by competitor intelligence, complete with hashtags, CTAs, and art direction concepts.
          </p>
        </div>
      </div>

      {/* Generator Form */}
      <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-sm space-y-4">
        <div className="flex items-center space-x-2 text-indigo-400">
          <Sparkles size={16} />
          <h3 className="text-xs font-bold uppercase tracking-wider text-slate-200">
            Craft Publish-Ready Google Maps Update
          </h3>
        </div>

        <form onSubmit={handleGenerate} className="space-y-4 text-xs">
          <div className="grid grid-cols-1 md:grid-cols-12 gap-4">
            <div className="md:col-span-8 space-y-1.5">
              <label className="text-slate-300 font-semibold block">Update Topic / Campaign Theme *</label>
              <input
                type="text"
                required
                placeholder="e.g. Summer Hair Care Treatment, Weekend Brunch Special..."
                value={topic}
                onChange={(e) => setTopic(e.target.value)}
                className="w-full bg-slate-950 border border-slate-700/80 rounded-xl px-3.5 py-2.5 text-slate-200 focus:outline-none focus:ring-2 focus:ring-indigo-500"
              />
            </div>

            <div className="md:col-span-4 space-y-1.5">
              <label className="text-slate-300 font-semibold block">AI Provider</label>
              <select
                value={provider}
                onChange={(e: any) => setProvider(e.target.value)}
                className="w-full bg-slate-950 border border-slate-700/80 rounded-xl px-3 py-2.5 text-slate-200 focus:outline-none focus:ring-2 focus:ring-indigo-500 cursor-pointer"
              >
                <option value="gemini">Google Gemini</option>
                <option value="grok">xAI Grok</option>
                <option value="fallback_nlp">NLP Heuristic Engine</option>
              </select>
            </div>
          </div>

          <div className="space-y-1.5">
            <label className="text-slate-300 font-semibold block">
              Additional Context / Strategic Direction (Optional)
            </label>
            <textarea
              rows={2}
              placeholder="Highlight specific offers, seasonal hooks, client differentiators, or specific service details..."
              value={customPrompt}
              onChange={(e) => setCustomPrompt(e.target.value)}
              className="w-full bg-slate-950 border border-slate-700/80 rounded-xl px-3.5 py-2 text-slate-200 focus:outline-none focus:ring-2 focus:ring-indigo-500 resize-none"
            />
          </div>

          <div className="flex justify-end pt-1">
            <button
              type="submit"
              disabled={generating || !topic}
              className="inline-flex items-center space-x-2 px-6 py-2.5 rounded-xl font-bold text-xs bg-indigo-600 hover:bg-indigo-500 text-white shadow-lg shadow-indigo-600/30 transition-all disabled:opacity-50"
            >
              <Sparkles size={14} className={generating ? 'animate-spin' : ''} />
              <span>{generating ? 'Drafting Complete Update...' : 'Generate Complete Update'}</span>
            </button>
          </div>
        </form>
      </div>

      {/* Generated Updates Feed / History */}
      <div className="space-y-4">
        <h3 className="text-sm font-bold text-white flex items-center space-x-2">
          <FileText size={16} className="text-indigo-400" />
          <span>Publish-Ready Updates History ({updates.length} Records)</span>
        </h3>

        {loading ? (
          <div className="space-y-4 animate-pulse">
            {[1, 2].map((i) => (
              <div key={i} className="h-44 bg-slate-900 border border-slate-800 rounded-2xl" />
            ))}
          </div>
        ) : updates.length === 0 ? (
          <div className="bg-slate-900 border border-slate-800 rounded-2xl p-12 text-center space-y-3">
            <FileText size={36} className="mx-auto text-slate-600" />
            <h4 className="text-sm font-bold text-white">No published update drafts created yet</h4>
            <p className="text-xs text-slate-400 max-w-sm mx-auto">
              Use the generator above or click "Draft Complete Update" on any content idea to produce complete copy.
            </p>
          </div>
        ) : (
          <div className="space-y-5">
            {updates.map((item) => {
              const isCopied = copiedId === item.id;
              const keywords = item.relevant_keywords ? item.relevant_keywords.split(',') : [];

              return (
                <div
                  key={item.id}
                  className="bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-sm space-y-4 transition-all"
                >
                  {/* Topic & Metadata Header */}
                  <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 pb-3 border-b border-slate-800 text-xs">
                    <div className="flex items-center space-x-2.5">
                      <span className="px-2.5 py-0.5 rounded-full text-xs font-bold bg-indigo-500/10 text-indigo-400 border border-indigo-500/30">
                        Topic: {item.topic}
                      </span>
                      <span className="text-slate-500">
                        {new Date(item.created_at).toLocaleString()}
                      </span>
                    </div>

                    <div className="flex items-center space-x-2">
                      <button
                        onClick={() => handleCopy(item.id, item.update_copy)}
                        className="inline-flex items-center space-x-1.5 px-3 py-1.5 rounded-lg text-xs font-bold bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 transition-colors"
                      >
                        {isCopied ? (
                          <>
                            <Check size={13} className="text-emerald-400" />
                            <span className="text-emerald-400">Copied!</span>
                          </>
                        ) : (
                          <>
                            <Copy size={13} />
                            <span>Copy Update Copy</span>
                          </>
                        )}
                      </button>
                      <button
                        onClick={() => handleDelete(item.id)}
                        className="p-1.5 rounded-lg text-slate-500 hover:text-rose-400 hover:bg-slate-800"
                        title="Delete update draft"
                      >
                        <Trash2 size={14} />
                      </button>
                    </div>
                  </div>

                  {/* Complete Copy Block */}
                  <div className="bg-slate-950 p-4 rounded-xl border border-slate-800/80">
                    <p className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">
                      Google Maps Ready-To-Publish Text
                    </p>
                    <p className="text-sm text-slate-200 whitespace-pre-wrap leading-relaxed">
                      {item.update_copy}
                    </p>
                  </div>

                  {/* Image Concept & CTAs */}
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs">
                    {/* Suggested Image Concept */}
                    <div className="p-3.5 bg-slate-950 rounded-xl border border-slate-800 space-y-1.5">
                      <div className="flex items-center space-x-1.5 text-sky-400 font-bold">
                        <ImageIcon size={14} />
                        <span>Suggested Visual Direction / Image Concept</span>
                      </div>
                      <p className="text-slate-400 leading-relaxed text-[11px]">
                        {item.image_concept || 'Engaging high-quality business photo showing customer experience.'}
                      </p>
                    </div>

                    {/* Keywords and CTA button */}
                    <div className="p-3.5 bg-slate-950 rounded-xl border border-slate-800 flex flex-col justify-between space-y-2">
                      <div>
                        <span className="text-slate-500 block text-[10px] font-semibold uppercase tracking-wider mb-1">
                          Relevant Local Keywords:
                        </span>
                        <div className="flex flex-wrap gap-1">
                          {keywords.map((kw, i) => (
                            <span
                              key={i}
                              className="px-2 py-0.5 rounded text-[10px] bg-slate-900 text-slate-300 border border-slate-800"
                            >
                              {kw.trim()}
                            </span>
                          ))}
                        </div>
                      </div>

                      {item.call_to_action && (
                        <div className="flex items-center justify-between pt-2 border-t border-slate-900">
                          <span className="text-[11px] text-slate-400">Google Maps Action Button:</span>
                          <span className="font-bold text-white px-3 py-1 rounded-lg bg-indigo-600 text-xs">
                            {item.call_to_action}
                          </span>
                        </div>
                      )}
                    </div>
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
