import React, { useState, useEffect } from 'react';
import {
  Users,
  Plus,
  Play,
  Trash2,
  Edit2,
  ExternalLink,
  Search,
  Sparkles,
  AlertCircle,
  CheckCircle2,
  Clock,
  Layers,
  X
} from 'lucide-react';
import type { Competitor, Project } from '../types';
import { api } from '../services/api';

interface CompetitorsPageProps {
  selectedProjectId?: number;
  projects: Project[];
  onOpenScrapeModal: (mode: 'live' | 'demo') => void;
  onNavigateTab: (tab: string) => void;
}

export const CompetitorsPage: React.FC<CompetitorsPageProps> = ({
  selectedProjectId,
  projects,
  onOpenScrapeModal,
  onNavigateTab,
}) => {
  const [competitors, setCompetitors] = useState<Competitor[]>([]);
  const [loading, setLoading] = useState(true);
  const [showAddModal, setShowAddModal] = useState(false);
  const [editingComp, setEditingComp] = useState<Competitor | null>(null);

  // Discovery Bonus Feature Modal
  const [showDiscoveryModal, setShowDiscoveryModal] = useState(false);
  const [discoveryKeyword, setDiscoveryKeyword] = useState('');
  const [discoveredCandidates, setDiscoveredCandidates] = useState<any[]>([]);
  const [discovering, setDiscovering] = useState(false);

  // Form states
  const [targetProjectId, setTargetProjectId] = useState<number>(selectedProjectId || (projects[0]?.id || 1));
  const [businessName, setBusinessName] = useState('');
  const [mapsUrl, setMapsUrl] = useState('');
  const [placeId, setPlaceId] = useState('');

  const loadCompetitors = async () => {
    setLoading(true);
    try {
      if (selectedProjectId) {
        const detail = await api.getProject(selectedProjectId);
        setCompetitors(detail.competitors || []);
      } else {
        // Collect across all projects
        const all: Competitor[] = [];
        for (const p of projects) {
          const d = await api.getProject(p.id);
          if (d.competitors) all.push(...d.competitors);
        }
        setCompetitors(all);
      }
    } catch (err) {
      console.error('Error fetching competitors', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (selectedProjectId) {
      setTargetProjectId(selectedProjectId);
    } else if (projects.length > 0) {
      setTargetProjectId(projects[0].id);
    }
    loadCompetitors();
  }, [selectedProjectId, projects]);

  const handleSaveCompetitor = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!businessName || !mapsUrl) return;

    try {
      if (editingComp) {
        await api.updateCompetitor(editingComp.id, {
          business_name: businessName,
          google_maps_url: mapsUrl,
          place_identifier: placeId || undefined,
        });
      } else {
        await api.addCompetitor(targetProjectId, {
          business_name: businessName,
          google_maps_url: mapsUrl,
          place_identifier: placeId || undefined,
        });
      }

      setShowAddModal(false);
      setEditingComp(null);
      resetForm();
      loadCompetitors();
    } catch (err) {
      console.error('Error adding competitor', err);
    }
  };

  const resetForm = () => {
    setBusinessName('');
    setMapsUrl('');
    setPlaceId('');
  };

  const handleSingleScrape = async (comp: Competitor) => {
    try {
      await api.scrapeCompetitor(comp.id, 'demo');
      loadCompetitors();
    } catch (err) {
      console.error('Error scraping competitor', err);
    }
  };

  const handleDelete = async (id: number) => {
    if (!window.confirm('Delete this competitor and all collected posts?')) return;
    try {
      await api.deleteCompetitor(id);
      loadCompetitors();
    } catch (err) {
      console.error('Error deleting competitor', err);
    }
  };

  const handleDiscover = async () => {
    if (!discoveryKeyword) return;
    setDiscovering(true);
    try {
      const res = await api.discoverCompetitors(targetProjectId, discoveryKeyword);
      setDiscoveredCandidates(res.candidates || []);
    } catch (err) {
      console.error('Discovery error', err);
    } finally {
      setDiscovering(false);
    }
  };

  const handleAddDiscovered = async (cand: any) => {
    try {
      await api.addCompetitor(targetProjectId, {
        business_name: cand.business_name,
        google_maps_url: cand.google_maps_url,
      });
      cand.is_already_added = true;
      loadCompetitors();
    } catch (err) {
      console.error('Failed to add candidate', err);
    }
  };

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'completed':
        return <span className="inline-flex items-center space-x-1 px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-emerald-500/10 text-emerald-400 border border-emerald-500/30"><CheckCircle2 size={11} /><span>Completed</span></span>;
      case 'running':
        return <span className="inline-flex items-center space-x-1 px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-indigo-500/10 text-indigo-400 border border-indigo-500/30"><Clock size={11} className="animate-spin" /><span>Running</span></span>;
      case 'captcha_required':
        return <span className="inline-flex items-center space-x-1 px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-amber-500/10 text-amber-400 border border-amber-500/30"><AlertCircle size={11} /><span>Captcha</span></span>;
      default:
        return <span className="inline-flex items-center space-x-1 px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-slate-800 text-slate-300"><span>Idle</span></span>;
    }
  };

  return (
    <div className="p-6 space-y-6">
      {/* Page Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-black text-white tracking-tight">Competitor Management</h2>
          <p className="text-xs text-slate-400">
            Add competitors manually, track Google Maps URLs, and monitor individual profile updates.
          </p>
        </div>

        <div className="flex items-center space-x-2.5 flex-wrap gap-y-2">
          {/* Bonus Discovery Button */}
          <button
            onClick={() => {
              setDiscoveryKeyword('');
              setDiscoveredCandidates([]);
              setShowDiscoveryModal(true);
            }}
            className="inline-flex items-center space-x-1.5 px-3.5 py-2 rounded-xl text-xs font-bold bg-indigo-500/10 hover:bg-indigo-500/20 text-indigo-300 border border-indigo-500/30 transition-all"
          >
            <Sparkles size={14} className="text-indigo-400" />
            <span>Discover by Keyword</span>
          </button>

          <button
            onClick={() => {
              resetForm();
              setEditingComp(null);
              setShowAddModal(true);
            }}
            className="inline-flex items-center space-x-1.5 px-4 py-2 rounded-xl text-xs font-bold bg-indigo-600 hover:bg-indigo-500 text-white shadow-md shadow-indigo-600/30 transition-all"
          >
            <Plus size={16} />
            <span>Add Competitor Manually</span>
          </button>
        </div>
      </div>

      {/* Competitors Table */}
      <div className="bg-slate-900 border border-slate-800 rounded-2xl overflow-hidden shadow-sm">
        <div className="p-4 border-b border-slate-800 flex items-center justify-between bg-slate-950/60">
          <div className="flex items-center space-x-2">
            <Users size={16} className="text-indigo-400" />
            <h3 className="text-sm font-bold text-white">Tracked Google Maps Competitors</h3>
            <span className="px-2 py-0.5 rounded-full text-xs font-bold bg-slate-800 text-slate-400">
              {competitors.length}
            </span>
          </div>
          <button
            onClick={() => onOpenScrapeModal('demo')}
            className="text-xs font-bold text-indigo-400 hover:text-indigo-300 flex items-center space-x-1"
          >
            <span>Scrape All Profiles</span>
            <Play size={12} className="fill-indigo-400" />
          </button>
        </div>

        {loading ? (
          <div className="p-8 text-center text-xs text-slate-400 animate-pulse">Loading competitors...</div>
        ) : competitors.length === 0 ? (
          <div className="p-12 text-center space-y-3">
            <Users size={36} className="mx-auto text-slate-600" />
            <p className="text-sm font-bold text-white">No competitors configured yet</p>
            <p className="text-xs text-slate-400 max-w-sm mx-auto">
              Add your first competitor manually using their Google Maps profile link.
            </p>
            <button
              onClick={() => setShowAddModal(true)}
              className="px-4 py-2 rounded-xl text-xs font-bold bg-indigo-600 text-white"
            >
              Add Competitor
            </button>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs divide-y divide-slate-800">
              <thead className="bg-slate-950 text-slate-400 uppercase tracking-wider text-[10px]">
                <tr>
                  <th className="px-5 py-3.5 font-bold">Business Name</th>
                  <th className="px-5 py-3.5 font-bold">Google Maps Profile</th>
                  <th className="px-5 py-3.5 font-bold">Collected Posts</th>
                  <th className="px-5 py-3.5 font-bold">Scraping Status</th>
                  <th className="px-5 py-3.5 font-bold">Last Scraped</th>
                  <th className="px-5 py-3.5 font-bold text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800 text-slate-300">
                {competitors.map((c) => (
                  <tr key={c.id} className="hover:bg-slate-950/40 transition-colors">
                    <td className="px-5 py-4 font-bold text-white flex items-center space-x-2">
                      <span>{c.business_name}</span>
                    </td>
                    <td className="px-5 py-4 max-w-xs truncate">
                      <a
                        href={c.google_maps_url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-indigo-400 hover:text-indigo-300 inline-flex items-center space-x-1 truncate"
                      >
                        <span className="truncate">{c.google_maps_url}</span>
                        <ExternalLink size={12} className="flex-shrink-0" />
                      </a>
                    </td>
                    <td className="px-5 py-4">
                      <span className="font-bold text-slate-200">{c.total_posts}</span> posts
                    </td>
                    <td className="px-5 py-4">{getStatusBadge(c.scraping_status)}</td>
                    <td className="px-5 py-4 text-slate-400 text-[11px]">
                      {c.last_scraped_at ? new Date(c.last_scraped_at).toLocaleString() : 'Never'}
                    </td>
                    <td className="px-5 py-4 text-right space-x-2">
                      <button
                        onClick={() => handleSingleScrape(c)}
                        className="px-2.5 py-1 rounded-lg text-xs font-semibold bg-indigo-600/20 text-indigo-300 hover:bg-indigo-600/30 border border-indigo-500/30"
                        title="Re-scrape this profile"
                      >
                        Scrape Now
                      </button>
                      <button
                        onClick={() => {
                          setEditingComp(c);
                          setBusinessName(c.business_name);
                          setMapsUrl(c.google_maps_url);
                          setPlaceId(c.place_identifier || '');
                          setShowAddModal(true);
                        }}
                        className="p-1 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800"
                        title="Edit competitor"
                      >
                        <Edit2 size={13} />
                      </button>
                      <button
                        onClick={() => handleDelete(c.id)}
                        className="p-1 rounded-lg text-slate-400 hover:text-rose-400 hover:bg-slate-800"
                        title="Delete competitor"
                      >
                        <Trash2 size={13} />
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Manual Competitor Modal */}
      {showAddModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm animate-in fade-in duration-200">
          <div className="w-full max-w-md bg-slate-900 border border-slate-700 rounded-2xl shadow-2xl overflow-hidden">
            <div className="flex items-center justify-between px-6 py-4 border-b border-slate-800 bg-slate-950">
              <h3 className="text-sm font-bold text-white">
                {editingComp ? 'Edit Competitor' : 'Add Competitor Manually'}
              </h3>
              <button
                onClick={() => setShowAddModal(false)}
                className="text-slate-400 hover:text-white p-1 rounded-lg"
              >
                <X size={18} />
              </button>
            </div>

            <form onSubmit={handleSaveCompetitor} className="p-6 space-y-4 text-xs">
              {!editingComp && projects.length > 1 && (
                <div className="space-y-1.5">
                  <label className="text-slate-300 font-semibold">Assign to Project</label>
                  <select
                    value={targetProjectId}
                    onChange={(e) => setTargetProjectId(Number(e.target.value))}
                    className="w-full bg-slate-950 border border-slate-700 rounded-xl px-3.5 py-2 text-slate-200 focus:outline-none focus:ring-2 focus:ring-indigo-500"
                  >
                    {projects.map((p) => (
                      <option key={p.id} value={p.id}>
                        {p.project_name} ({p.client_business_name})
                      </option>
                    ))}
                  </select>
                </div>
              )}

              <div className="space-y-1.5">
                <label className="text-slate-300 font-semibold">Competitor Business Name *</label>
                <input
                  type="text"
                  required
                  placeholder="e.g. Enrich Hair & Beauty Lounge"
                  value={businessName}
                  onChange={(e) => setBusinessName(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-700 rounded-xl px-3.5 py-2 text-slate-200 focus:outline-none focus:ring-2 focus:ring-indigo-500"
                />
              </div>

              <div className="space-y-1.5">
                <label className="text-slate-300 font-semibold">Google Maps Profile URL *</label>
                <input
                  type="url"
                  required
                  placeholder="https://www.google.com/maps/place/..."
                  value={mapsUrl}
                  onChange={(e) => setMapsUrl(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-700 rounded-xl px-3.5 py-2 text-slate-200 focus:outline-none focus:ring-2 focus:ring-indigo-500"
                />
              </div>

              <div className="space-y-1.5">
                <label className="text-slate-300 font-semibold">Place Identifier (CID / Place ID)</label>
                <input
                  type="text"
                  placeholder="Optional Google Place ID (e.g. ChIJz2_12345)"
                  value={placeId}
                  onChange={(e) => setPlaceId(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-700 rounded-xl px-3.5 py-2 text-slate-200 focus:outline-none focus:ring-2 focus:ring-indigo-500"
                />
              </div>

              <div className="flex items-center justify-end space-x-3 pt-3 border-t border-slate-800">
                <button
                  type="button"
                  onClick={() => setShowAddModal(false)}
                  className="px-4 py-2 rounded-xl font-semibold text-slate-400 hover:text-white"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-5 py-2 rounded-xl font-bold bg-indigo-600 hover:bg-indigo-500 text-white shadow-md shadow-indigo-600/30"
                >
                  {editingComp ? 'Update' : 'Add Competitor'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Bonus Keyword Discovery Modal */}
      {showDiscoveryModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm animate-in fade-in duration-200">
          <div className="w-full max-w-lg bg-slate-900 border border-slate-700 rounded-2xl shadow-2xl overflow-hidden">
            <div className="flex items-center justify-between px-6 py-4 border-b border-slate-800 bg-slate-950">
              <div className="flex items-center space-x-2">
                <Sparkles size={16} className="text-indigo-400" />
                <h3 className="text-sm font-bold text-white">Keyword-Based Competitor Discovery</h3>
              </div>
              <button
                onClick={() => setShowDiscoveryModal(false)}
                className="text-slate-400 hover:text-white p-1 rounded-lg"
              >
                <X size={18} />
              </button>
            </div>

            <div className="p-6 space-y-4 text-xs">
              <p className="text-slate-400">
                Search Google Maps for competitor profiles matching target local keywords. Candidates are automatically compared against your repository to prevent duplicates.
              </p>

              <div className="flex items-center space-x-2">
                <input
                  type="text"
                  placeholder="e.g. salon in Kharghar"
                  value={discoveryKeyword}
                  onChange={(e) => setDiscoveryKeyword(e.target.value)}
                  className="flex-1 bg-slate-950 border border-slate-700 rounded-xl px-3.5 py-2.5 text-slate-200 focus:outline-none focus:ring-2 focus:ring-indigo-500"
                />
                <button
                  onClick={handleDiscover}
                  disabled={discovering || !discoveryKeyword}
                  className="px-4 py-2.5 rounded-xl font-bold bg-indigo-600 hover:bg-indigo-500 text-white disabled:opacity-50"
                >
                  {discovering ? 'Searching...' : 'Discover'}
                </button>
              </div>

              {discoveredCandidates.length > 0 && (
                <div className="space-y-2 pt-2 max-h-60 overflow-y-auto">
                  <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400 block">
                    Discovered Profiles:
                  </span>
                  {discoveredCandidates.map((cand, idx) => (
                    <div
                      key={idx}
                      className="p-3 bg-slate-950 border border-slate-800 rounded-xl flex items-center justify-between"
                    >
                      <div className="truncate mr-3">
                        <p className="font-bold text-slate-200 truncate">{cand.business_name}</p>
                        <p className="text-[10px] text-slate-400 truncate">{cand.google_maps_url}</p>
                      </div>
                      {cand.is_already_added ? (
                        <span className="px-2.5 py-1 rounded-lg text-[10px] font-semibold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                          Tracked
                        </span>
                      ) : (
                        <button
                          onClick={() => handleAddDiscovered(cand)}
                          className="px-2.5 py-1 rounded-lg text-[10px] font-bold bg-indigo-600 hover:bg-indigo-500 text-white"
                        >
                          + Add
                        </button>
                      )}
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
