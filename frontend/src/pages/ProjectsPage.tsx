import React, { useState, useEffect } from 'react';
import {
  FolderKanban,
  Plus,
  Trash2,
  Edit2,
  ExternalLink,
  Users,
  Database,
  Tag,
  ArrowRight,
  Check,
  X
} from 'lucide-react';
import type { Project } from '../types';
import { api } from '../services/api';

interface ProjectsPageProps {
  onSelectProject: (id: number) => void;
  onNavigateTab: (tab: string) => void;
}

export const ProjectsPage: React.FC<ProjectsPageProps> = ({
  onSelectProject,
  onNavigateTab,
}) => {
  const [projects, setProjects] = useState<Project[]>([]);
  const [loading, setLoading] = useState(true);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [editingProject, setEditingProject] = useState<Project | null>(null);

  // Form states
  const [name, setName] = useState('');
  const [clientName, setClientName] = useState('');
  const [mapsUrl, setMapsUrl] = useState('');
  const [description, setDescription] = useState('');
  const [verifiedFacts, setVerifiedFacts] = useState('');
  const [keywordsStr, setKeywordsStr] = useState('');

  const loadProjects = async () => {
    setLoading(true);
    try {
      const data = await api.getProjects();
      setProjects(data);
    } catch (err) {
      console.error('Error fetching projects', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadProjects();
  }, []);

  const handleCreateOrUpdate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!name || !clientName) return;

    try {
      const kws = keywordsStr
        .split(',')
        .map((k) => k.trim())
        .filter((k) => k.length > 0);

      if (editingProject) {
        await api.updateProject(editingProject.id, {
          project_name: name,
          client_business_name: clientName,
          google_maps_url: mapsUrl,
          description: description,
          verified_facts: verifiedFacts,
        });
      } else {
        await api.createProject({
          project_name: name,
          client_business_name: clientName,
          google_maps_url: mapsUrl,
          description: description,
          verified_facts: verifiedFacts,
          keywords: kws,
        });
      }

      setShowCreateModal(false);
      setEditingProject(null);
      resetForm();
      loadProjects();
    } catch (err) {
      console.error('Error saving project', err);
    }
  };

  const resetForm = () => {
    setName('');
    setClientName('');
    setMapsUrl('');
    setDescription('');
    setVerifiedFacts('');
    setKeywordsStr('');
  };

  const handleOpenEdit = (p: Project) => {
    setEditingProject(p);
    setName(p.project_name);
    setClientName(p.client_business_name);
    setMapsUrl(p.google_maps_url || '');
    setDescription(p.description || '');
    setVerifiedFacts(p.verified_facts || '');
    setShowCreateModal(true);
  };

  const handleDelete = async (id: number) => {
    if (!window.confirm('Are you sure you want to delete this project and all its associated data?')) return;
    try {
      await api.deleteProject(id);
      loadProjects();
    } catch (err) {
      console.error('Error deleting project', err);
    }
  };

  return (
    <div className="p-6 space-y-6">
      {/* Top Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-black text-white tracking-tight">Project Management</h2>
          <p className="text-xs text-slate-400">
            Create and organize competitor intelligence portfolios for your business profiles.
          </p>
        </div>
        <button
          onClick={() => {
            resetForm();
            setEditingProject(null);
            setShowCreateModal(true);
          }}
          className="inline-flex items-center space-x-2 px-4 py-2 rounded-xl text-xs font-bold bg-indigo-600 hover:bg-indigo-500 text-white transition-all shadow-md shadow-indigo-600/30"
        >
          <Plus size={16} />
          <span>New Project</span>
        </button>
      </div>

      {/* Projects Grid */}
      {loading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5 animate-pulse">
          {[1, 2, 3].map((i) => (
            <div key={i} className="h-56 bg-slate-900 border border-slate-800 rounded-2xl" />
          ))}
        </div>
      ) : projects.length === 0 ? (
        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-12 text-center space-y-3">
          <FolderKanban size={40} className="mx-auto text-slate-600" />
          <h3 className="text-base font-bold text-white">No projects found</h3>
          <p className="text-xs text-slate-400 max-w-sm mx-auto">
            Get started by creating your first client project to track Google Maps competitors.
          </p>
          <button
            onClick={() => setShowCreateModal(true)}
            className="px-4 py-2 rounded-xl text-xs font-bold bg-indigo-600 text-white"
          >
            Create Project
          </button>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
          {projects.map((p) => (
            <div
              key={p.id}
              className="bg-slate-900 border border-slate-800 hover:border-slate-700 rounded-2xl p-5 shadow-sm hover:shadow-xl transition-all flex flex-col justify-between space-y-4"
            >
              <div className="space-y-3">
                <div className="flex items-start justify-between">
                  <div className="space-y-1">
                    <h3 className="text-base font-bold text-white leading-tight">{p.project_name}</h3>
                    <p className="text-xs font-medium text-indigo-400">{p.client_business_name}</p>
                  </div>
                  <div className="flex items-center space-x-1">
                    <button
                      onClick={() => handleOpenEdit(p)}
                      className="p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800"
                      title="Edit project"
                    >
                      <Edit2 size={14} />
                    </button>
                    <button
                      onClick={() => handleDelete(p.id)}
                      className="p-1.5 rounded-lg text-slate-400 hover:text-rose-400 hover:bg-slate-800"
                      title="Delete project"
                    >
                      <Trash2 size={14} />
                    </button>
                  </div>
                </div>

                <p className="text-xs text-slate-400 line-clamp-2 leading-relaxed">
                  {p.description || 'No project description provided.'}
                </p>

                {p.verified_facts && (
                  <div className="bg-slate-950/70 border border-slate-800/80 rounded-xl p-2.5 space-y-1">
                    <span className="text-[10px] font-bold tracking-wide uppercase text-indigo-400 flex items-center gap-1">
                      <Check size={11} className="text-emerald-400" />
                      Client Business Facts (AI Grounding)
                    </span>
                    <p className="text-[11px] text-slate-300 line-clamp-2 leading-tight">
                      {p.verified_facts}
                    </p>
                  </div>
                )}

                {p.google_maps_url && (
                  <a
                    href={p.google_maps_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="inline-flex items-center space-x-1 text-[11px] text-slate-500 hover:text-slate-300 truncate max-w-full"
                  >
                    <ExternalLink size={12} />
                    <span className="truncate">{p.google_maps_url}</span>
                  </a>
                )}
              </div>

              {/* Statistics Row */}
              <div className="space-y-3 pt-3 border-t border-slate-800/80">
                <div className="grid grid-cols-3 gap-2 text-center text-xs">
                  <div className="bg-slate-950 p-2 rounded-xl border border-slate-800">
                    <span className="text-[10px] text-slate-500 block">Competitors</span>
                    <span className="font-bold text-slate-200">{p.competitors_count}</span>
                  </div>
                  <div className="bg-slate-950 p-2 rounded-xl border border-slate-800">
                    <span className="text-[10px] text-slate-500 block">Keywords</span>
                    <span className="font-bold text-slate-200">{p.keywords_count}</span>
                  </div>
                  <div className="bg-slate-950 p-2 rounded-xl border border-slate-800">
                    <span className="text-[10px] text-slate-500 block">Posts</span>
                    <span className="font-bold text-indigo-400">{p.posts_count}</span>
                  </div>
                </div>

                <button
                  onClick={() => {
                    onSelectProject(p.id);
                    onNavigateTab('repository');
                  }}
                  className="w-full inline-flex items-center justify-center space-x-1.5 py-2.5 rounded-xl bg-slate-950 hover:bg-slate-800 text-xs font-bold text-indigo-400 border border-slate-800 hover:border-slate-700 transition-all"
                >
                  <span>Open Intelligence Hub</span>
                  <ArrowRight size={13} />
                </button>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Create / Edit Project Modal */}
      {showCreateModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm animate-in fade-in duration-200">
          <div className="w-full max-w-lg bg-slate-900 border border-slate-700 rounded-2xl shadow-2xl overflow-hidden max-h-[90vh] flex flex-col">
            <div className="flex items-center justify-between px-6 py-4 border-b border-slate-800 bg-slate-950 shrink-0">
              <h3 className="text-sm font-bold text-white">
                {editingProject ? 'Edit Project' : 'Create New Project'}
              </h3>
              <button
                onClick={() => setShowCreateModal(false)}
                className="text-slate-400 hover:text-white p-1 rounded-lg"
              >
                <X size={18} />
              </button>
            </div>

            <form onSubmit={handleCreateOrUpdate} className="p-6 space-y-4 text-xs overflow-y-auto">
              <div className="space-y-1.5">
                <label className="text-slate-300 font-semibold">Project Name *</label>
                <input
                  type="text"
                  required
                  placeholder="e.g. Ravi's Family Salon - Thane WEST"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-700 rounded-xl px-3.5 py-2 text-slate-200 focus:outline-none focus:ring-2 focus:ring-indigo-500"
                />
              </div>

              <div className="space-y-1.5">
                <label className="text-slate-300 font-semibold">Client / Business Name *</label>
                <input
                  type="text"
                  required
                  placeholder="e.g. Ravi's Family Salon"
                  value={clientName}
                  onChange={(e) => setClientName(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-700 rounded-xl px-3.5 py-2 text-slate-200 focus:outline-none focus:ring-2 focus:ring-indigo-500"
                />
              </div>

              <div className="space-y-1.5">
                <label className="text-slate-300 font-semibold">Client Google Maps Profile URL</label>
                <input
                  type="url"
                  placeholder="https://www.google.com/maps/place/..."
                  value={mapsUrl}
                  onChange={(e) => setMapsUrl(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-700 rounded-xl px-3.5 py-2 text-slate-200 focus:outline-none focus:ring-2 focus:ring-indigo-500"
                />
              </div>

              <div className="space-y-1.5">
                <label className="text-slate-300 font-semibold">Description & Positioning</label>
                <textarea
                  rows={2}
                  placeholder="Brief summary of client services, location, and key differentiators..."
                  value={description}
                  onChange={(e) => setDescription(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-700 rounded-xl px-3.5 py-2 text-slate-200 focus:outline-none focus:ring-2 focus:ring-indigo-500 resize-none"
                />
              </div>

              <div className="space-y-1.5 bg-slate-950/60 p-3 rounded-xl border border-indigo-950/60">
                <div className="flex items-center justify-between">
                  <label className="text-indigo-300 font-semibold flex items-center gap-1.5">
                    <span>Client Business Facts (AI Grounding)</span>
                  </label>
                  <span className="text-[10px] text-slate-400">Prevents AI Hallucinations</span>
                </div>
                <textarea
                  rows={3}
                  placeholder="Provide verified business facts only: e.g. Established 2017, certified stylists, free valet parking, 100% ammonia-free L'Oreal products. AI is strictly constrained to these facts."
                  value={verifiedFacts}
                  onChange={(e) => setVerifiedFacts(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-700 rounded-xl px-3.5 py-2 text-slate-200 focus:outline-none focus:ring-2 focus:ring-indigo-500 resize-none font-mono text-[11px]"
                />
                <p className="text-[10px] text-slate-500 leading-tight">
                  The AI update generator will NEVER claim certifications, offers, or amenities unless specified here.
                </p>
              </div>

              {!editingProject && (
                <div className="space-y-1.5">
                  <label className="text-slate-300 font-semibold">
                    Target Project Keywords (comma separated)
                  </label>
                  <input
                    type="text"
                    placeholder="salon in Kharghar, hair spa, keratin treatment"
                    value={keywordsStr}
                    onChange={(e) => setKeywordsStr(e.target.value)}
                    className="w-full bg-slate-950 border border-slate-700 rounded-xl px-3.5 py-2 text-slate-200 focus:outline-none focus:ring-2 focus:ring-indigo-500"
                  />
                </div>
              )}

              <div className="flex items-center justify-end space-x-3 pt-3 border-t border-slate-800">
                <button
                  type="button"
                  onClick={() => setShowCreateModal(false)}
                  className="px-4 py-2 rounded-xl font-semibold text-slate-400 hover:text-white"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-5 py-2 rounded-xl font-bold bg-indigo-600 hover:bg-indigo-500 text-white shadow-md shadow-indigo-600/30"
                >
                  {editingProject ? 'Save Changes' : 'Create Project'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
