import React, { useState, useEffect } from 'react';
import {
  Database,
  Search,
  Filter,
  Calendar,
  Layers,
  Sparkles,
  ChevronLeft,
  ChevronRight,
  ExternalLink,
  Tag
} from 'lucide-react';
import type { Post, Project } from '../types';
import { PostCard } from '../components/PostCard';
import { PostDetailModal } from '../components/PostDetailModal';
import { api } from '../services/api';

interface RepositoryPageProps {
  selectedProjectId?: number;
  projects: Project[];
  onSelectPost: (post: Post) => void;
  selectedPost: Post | null;
  onCloseDetailModal: () => void;
  onDraftUpdateFromPost: (post: Post) => void;
}

export const RepositoryPage: React.FC<RepositoryPageProps> = ({
  selectedProjectId,
  projects,
  onSelectPost,
  selectedPost,
  onCloseDetailModal,
  onDraftUpdateFromPost,
}) => {
  const [posts, setPosts] = useState<Post[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [loading, setLoading] = useState(true);

  // Filters
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedTopic, setSelectedTopic] = useState('');
  const [selectedContentType, setSelectedContentType] = useState('');
  const [selectedSourceType, setSelectedSourceType] = useState('');
  const [selectedCTA, setSelectedCTA] = useState('');

  const topicsList = [
    'Hair Care Tips',
    'Festival Offer',
    'Before / After Transformation',
    'Skin Glow Treatment',
    'Chef Special',
    'Weekend Brunch',
    'Happy Hours',
    'Teeth Whitening',
    'Clear Aligners',
    'Membership Discount',
    'HIIT Training'
  ];

  const contentTypes = ['Offer', 'Tip', 'Product Update', 'Event', 'Showcase'];

  const loadPosts = async () => {
    setLoading(true);
    try {
      const res = await api.getPosts({
        project_id: selectedProjectId,
        search: searchTerm || undefined,
        topic: selectedTopic || undefined,
        content_type: selectedContentType || undefined,
        call_to_action: selectedCTA || undefined,
        source_type: selectedSourceType || undefined,
        page: page,
        page_size: 12,
      });
      setPosts(res.items);
      setTotal(res.total);
      setTotalPages(res.total_pages);
    } catch (err) {
      console.error('Error loading posts repository', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    setPage(1);
  }, [selectedProjectId, searchTerm, selectedTopic, selectedContentType, selectedSourceType, selectedCTA]);

  useEffect(() => {
    loadPosts();
  }, [selectedProjectId, searchTerm, selectedTopic, selectedContentType, selectedSourceType, selectedCTA, page]);

  const handleResetFilters = () => {
    setSearchTerm('');
    setSelectedTopic('');
    setSelectedContentType('');
    setSelectedSourceType('');
    setSelectedCTA('');
    setPage(1);
  };

  return (
    <div className="p-6 space-y-6">
      {/* Page Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-black text-white tracking-tight">Competitor Posts Repository</h2>
          <p className="text-xs text-slate-400">
            Search, filter, and inspect collected Google Maps updates across your monitored competitors.
          </p>
        </div>
        <div className="flex items-center space-x-2 text-xs text-slate-400 font-semibold bg-slate-900 border border-slate-800 px-3 py-1.5 rounded-xl">
          <Database size={14} className="text-indigo-400" />
          <span>Total Records: {total}</span>
        </div>
      </div>

      {/* Filter and Search Bar */}
      <div className="bg-slate-900 border border-slate-800 rounded-2xl p-4 space-y-3">
        <div className="grid grid-cols-1 sm:grid-cols-12 gap-3 text-xs">
          {/* Search Box */}
          <div className="sm:col-span-3 relative">
            <Search size={15} className="absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-500" />
            <input
              type="text"
              placeholder="Search post copy, competitor, keywords..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full bg-slate-950 border border-slate-700/80 rounded-xl pl-9 pr-3.5 py-2 text-slate-200 focus:outline-none focus:ring-2 focus:ring-indigo-500"
            />
          </div>

          {/* Topic Filter */}
          <div className="sm:col-span-3">
            <select
              value={selectedTopic}
              onChange={(e) => setSelectedTopic(e.target.value)}
              className="w-full bg-slate-950 border border-slate-700/80 rounded-xl px-3 py-2 text-slate-200 focus:outline-none focus:ring-2 focus:ring-indigo-500 cursor-pointer"
            >
              <option value="">All Topics</option>
              {topicsList.map((t) => (
                <option key={t} value={t}>
                  {t}
                </option>
              ))}
            </select>
          </div>

          {/* Content Type Filter */}
          <div className="sm:col-span-2">
            <select
              value={selectedContentType}
              onChange={(e) => setSelectedContentType(e.target.value)}
              className="w-full bg-slate-950 border border-slate-700/80 rounded-xl px-3 py-2 text-slate-200 focus:outline-none focus:ring-2 focus:ring-indigo-500 cursor-pointer"
            >
              <option value="">All Content Types</option>
              {contentTypes.map((ct) => (
                <option key={ct} value={ct}>
                  {ct}
                </option>
              ))}
            </select>
          </div>

          {/* Source Type Filter */}
          <div className="sm:col-span-2">
            <select
              value={selectedSourceType}
              onChange={(e) => setSelectedSourceType(e.target.value)}
              className="w-full bg-slate-950 border border-slate-700/80 rounded-xl px-3 py-2 text-slate-200 focus:outline-none focus:ring-2 focus:ring-indigo-500 cursor-pointer"
            >
              <option value="">All Sources</option>
              <option value="LIVE">Live Scrapes</option>
              <option value="DEMO">Demo Scrapes</option>
              <option value="SEEDED">Seeded Demo Data</option>
            </select>
          </div>

          {/* Reset Filters */}
          <div className="sm:col-span-2 flex items-center">
            <button
              onClick={handleResetFilters}
              className="w-full py-2 rounded-xl text-xs font-semibold bg-slate-950 hover:bg-slate-800 text-slate-400 hover:text-white border border-slate-800 transition-colors"
            >
              Clear Filters
            </button>
          </div>
        </div>
      </div>

      {/* Posts Cards Grid */}
      {loading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5 animate-pulse">
          {[...Array(6)].map((_, i) => (
            <div key={i} className="h-72 bg-slate-900 border border-slate-800 rounded-2xl" />
          ))}
        </div>
      ) : posts.length === 0 ? (
        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-12 text-center space-y-3">
          <Database size={40} className="mx-auto text-slate-600" />
          <h3 className="text-base font-bold text-white">No matching posts found</h3>
          <p className="text-xs text-slate-400 max-w-sm mx-auto">
            Try adjusting your search criteria or run a scrape to discover fresh competitor updates.
          </p>
          <button
            onClick={handleResetFilters}
            className="px-4 py-2 rounded-xl text-xs font-bold bg-indigo-600 text-white"
          >
            Reset Filters
          </button>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
          {posts.map((post) => (
            <PostCard key={post.id} post={post} onSelect={onSelectPost} />
          ))}
        </div>
      )}

      {/* Pagination Controls */}
      {totalPages > 1 && (
        <div className="flex items-center justify-between pt-4 border-t border-slate-800 text-xs text-slate-400">
          <span>
            Page <strong className="text-white">{page}</strong> of <strong className="text-white">{totalPages}</strong> ({total} total posts)
          </span>
          <div className="flex items-center space-x-2">
            <button
              disabled={page <= 1}
              onClick={() => setPage((p) => Math.max(p - 1, 1))}
              className="p-2 rounded-lg bg-slate-900 border border-slate-800 text-slate-300 hover:bg-slate-800 disabled:opacity-40 disabled:cursor-not-allowed"
            >
              <ChevronLeft size={16} />
            </button>
            <button
              disabled={page >= totalPages}
              onClick={() => setPage((p) => Math.min(p + 1, totalPages))}
              className="p-2 rounded-lg bg-slate-900 border border-slate-800 text-slate-300 hover:bg-slate-800 disabled:opacity-40 disabled:cursor-not-allowed"
            >
              <ChevronRight size={16} />
            </button>
          </div>
        </div>
      )}

      {/* Detail Modal */}
      <PostDetailModal
        post={selectedPost}
        onClose={onCloseDetailModal}
        onDraftUpdateFromPost={onDraftUpdateFromPost}
      />
    </div>
  );
};
