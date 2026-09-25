import React from 'react';
import {
  X,
  ExternalLink,
  Calendar,
  Tag,
  Sparkles,
  Fingerprint,
  Building,
  Clock,
  ArrowRight
} from 'lucide-react';
import type { Post } from '../types';

interface PostDetailModalProps {
  post: Post | null;
  onClose: () => void;
  onDraftUpdateFromPost?: (post: Post) => void;
}

export const PostDetailModal: React.FC<PostDetailModalProps> = ({
  post,
  onClose,
  onDraftUpdateFromPost,
}) => {
  if (!post) return null;

  const keywords = post.detected_keywords ? post.detected_keywords.split(',') : [];

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm animate-in fade-in duration-200">
      <div className="w-full max-w-3xl bg-slate-900 border border-slate-700/80 rounded-2xl shadow-2xl overflow-hidden flex flex-col max-h-[90vh]">
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-slate-800 bg-slate-950">
          <div className="flex items-center space-x-3">
            <div className="p-2 rounded-xl bg-indigo-500/10 text-indigo-400">
              <Building size={18} />
            </div>
            <div>
              <h3 className="text-base font-bold text-white leading-tight">
                {post.competitor_name}
              </h3>
              <p className="text-xs text-slate-400">Google Maps Competitor Update</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="text-slate-400 hover:text-white p-1.5 rounded-lg hover:bg-slate-800 transition-colors"
          >
            <X size={18} />
          </button>
        </div>

        {/* Scrollable Content */}
        <div className="overflow-y-auto p-6 space-y-6">
          {/* Main Post Media & Copy */}
          <div className="grid grid-cols-1 md:grid-cols-12 gap-6">
            {post.media && post.media.length > 0 && (
              <div className="md:col-span-5 rounded-xl overflow-hidden bg-slate-950 border border-slate-800">
                <img
                  src={post.media[0].media_url}
                  alt={post.competitor_name}
                  className="w-full h-64 md:h-full object-cover"
                />
              </div>
            )}

            <div className={`${post.media && post.media.length > 0 ? 'md:col-span-7' : 'md:col-span-12'} space-y-4`}>
              <div className="flex items-center justify-between text-xs text-slate-400">
                <div className="flex items-center space-x-1.5">
                  <Calendar size={13} className="text-slate-400" />
                  <span>
                    Published:{' '}
                    {post.published_date
                      ? new Date(post.published_date).toLocaleDateString(undefined, {
                          year: 'numeric',
                          month: 'long',
                          day: 'numeric',
                        })
                      : 'N/A'}
                  </span>
                </div>
                <div className="flex items-center space-x-2">
                  <span className={`px-2 py-0.5 rounded-full text-[10px] font-bold ${
                    post.source_type === 'LIVE' ? 'bg-indigo-500/20 text-indigo-400 border border-indigo-500/30' :
                    post.source_type === 'DEMO' ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30' :
                    'bg-sky-500/20 text-sky-400 border border-sky-500/30'
                  }`}>
                    {post.source_type || post.source_information}
                  </span>
                </div>
              </div>

              <div className="bg-slate-950 p-4 rounded-xl border border-slate-800/80">
                <p className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-1.5">
                  Post Copy
                </p>
                <p className="text-sm text-slate-200 leading-relaxed whitespace-pre-wrap">
                  {post.post_text}
                </p>
              </div>

              {post.call_to_action && (
                <div className="flex items-center justify-between p-3 bg-indigo-500/10 border border-indigo-500/30 rounded-xl">
                  <span className="text-xs text-indigo-300 font-medium">Detected Call-To-Action:</span>
                  <span className="text-xs font-bold text-white px-2.5 py-1 rounded bg-indigo-600">
                    {post.call_to_action}
                  </span>
                </div>
              )}
            </div>
          </div>

          {/* AI Content Intelligence Extraction */}
          <div className="p-4 rounded-xl bg-slate-950 border border-slate-800 space-y-3">
            <div className="flex items-center space-x-2 text-indigo-400">
              <Sparkles size={16} />
              <h4 className="text-xs font-bold uppercase tracking-wider text-slate-200">
                AI Content Intelligence
              </h4>
            </div>

            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-xs">
              <div className="p-2.5 bg-slate-900 rounded-lg border border-slate-800">
                <span className="text-slate-400 block text-[10px] font-medium">Main Topic</span>
                <span className="font-semibold text-slate-200">{post.industry_topic || 'General Update'}</span>
              </div>
              <div className="p-2.5 bg-slate-900 rounded-lg border border-slate-800">
                <span className="text-slate-400 block text-[10px] font-medium">Content Type</span>
                <span className="font-semibold text-slate-200">{post.content_type || 'Update'}</span>
              </div>
              <div className="p-2.5 bg-slate-900 rounded-lg border border-slate-800">
                <span className="text-slate-400 block text-[10px] font-medium">Offer Pattern</span>
                <span className="font-semibold text-slate-200">{post.analysis?.offer_pattern || 'Standard Post'}</span>
              </div>
              <div className="p-2.5 bg-slate-900 rounded-lg border border-slate-800">
                <span className="text-slate-400 block text-[10px] font-medium">Sentiment</span>
                <span className="font-semibold text-emerald-400 capitalize">{post.analysis?.sentiment || 'Positive'}</span>
              </div>
            </div>

            {keywords.length > 0 && (
              <div className="pt-1">
                <span className="text-[11px] text-slate-400 block mb-1.5 font-medium">Extracted Keywords:</span>
                <div className="flex flex-wrap gap-1.5">
                  {keywords.map((kw, idx) => (
                    <span
                      key={idx}
                      className="px-2 py-0.5 rounded-md text-[11px] font-medium bg-slate-800 text-slate-300 border border-slate-700"
                    >
                      {kw.trim()}
                    </span>
                  ))}
                </div>
              </div>
            )}
          </div>

          {/* Technical Metadata & Fingerprint verification */}
          <div className="p-4 rounded-xl bg-slate-950/60 border border-slate-800 text-xs space-y-2">
            <div className="flex items-center space-x-2 text-slate-400">
              <Fingerprint size={15} className="text-slate-400" />
              <span className="font-mono text-[11px] text-slate-300 truncate">
                Fingerprint SHA256: {post.fingerprint}
              </span>
            </div>
            <div className="flex items-center justify-between text-slate-400 text-[11px] pt-1">
              <span className="flex items-center space-x-1">
                <Clock size={12} />
                <span>Scraped: {new Date(post.scraped_at).toLocaleString()}</span>
              </span>
              {post.post_url ? (
                <a
                  href={post.post_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="inline-flex items-center space-x-1 text-indigo-400 hover:text-indigo-300 font-semibold"
                >
                  <span>View Original Post</span>
                  <ExternalLink size={12} />
                </a>
              ) : (
                <span className="text-slate-500 italic">Original post URL unavailable.</span>
              )}
            </div>
          </div>
        </div>

        {/* Footer actions */}
        <div className="px-6 py-4 border-t border-slate-800 bg-slate-950 flex items-center justify-between">
          {post.google_maps_profile_url ? (
            <a
              href={post.google_maps_profile_url}
              target="_blank"
              rel="noopener noreferrer"
              className="text-xs font-semibold text-slate-400 hover:text-white inline-flex items-center space-x-1"
            >
              <span>View Business Profile</span>
              <ExternalLink size={13} />
            </a>
          ) : <div />}

          <div className="flex items-center space-x-3">
            {onDraftUpdateFromPost && (
              <button
                onClick={() => {
                  onDraftUpdateFromPost(post);
                  onClose();
                }}
                className="inline-flex items-center space-x-1.5 px-4 py-2 rounded-lg text-xs font-bold bg-indigo-600 hover:bg-indigo-500 text-white shadow-md shadow-indigo-600/30"
              >
                <Sparkles size={13} />
                <span>Create Counter-Update</span>
              </button>
            )}
            <button
              onClick={onClose}
              className="px-4 py-2 rounded-lg text-xs font-semibold bg-slate-800 hover:bg-slate-700 text-slate-300"
            >
              Close
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
