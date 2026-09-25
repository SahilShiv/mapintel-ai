import React from 'react';
import { ExternalLink, Calendar, Tag, ArrowUpRight } from 'lucide-react';
import type { Post } from '../types';

interface PostCardProps {
  post: Post;
  onSelect: (post: Post) => void;
}

export const PostCard: React.FC<PostCardProps> = ({ post, onSelect }) => {
  const thumbnail = post.media && post.media.length > 0 ? post.media[0].media_url : null;
  const keywords = post.detected_keywords ? post.detected_keywords.split(',').slice(0, 3) : [];

  const getSourceBadge = (source?: string, sourceType?: string) => {
    const s = sourceType || source || '';
    if (s === 'LIVE' || s === 'LIVE_SCRAPE') {
      return <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-indigo-500/20 text-indigo-400 border border-indigo-500/30">LIVE SCRAPE</span>;
    }
    if (s === 'DEMO' || s === 'DEMO_SCRAPE') {
      return <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-emerald-500/20 text-emerald-400 border border-emerald-500/30">DEMO SCRAPE</span>;
    }
    return <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-sky-500/20 text-sky-400 border border-sky-500/30">SEEDED DEMO</span>;
  };

  const getContentTypeBadge = (type?: string) => {
    const t = type || 'Update';
    const colors: Record<string, string> = {
      Offer: 'bg-amber-500/10 text-amber-400 border-amber-500/30',
      Tip: 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30',
      Showcase: 'bg-purple-500/10 text-purple-400 border-purple-500/30',
      Event: 'bg-rose-500/10 text-rose-400 border-rose-500/30',
      'Product Update': 'bg-blue-500/10 text-blue-400 border-blue-500/30',
    };
    const c = colors[t] || 'bg-slate-800 text-slate-300 border-slate-700';
    return (
      <span className={`px-2 py-0.5 rounded-full text-[10px] font-semibold border ${c}`}>
        {t}
      </span>
    );
  };

  return (
    <div
      onClick={() => onSelect(post)}
      className="group bg-slate-900 border border-slate-800 hover:border-slate-700 rounded-xl overflow-hidden shadow-sm hover:shadow-xl transition-all duration-200 cursor-pointer flex flex-col justify-between"
    >
      <div>
        {/* Media Thumbnail */}
        {thumbnail && (
          <div className="relative h-44 w-full bg-slate-950 overflow-hidden">
            <img
              src={thumbnail}
              alt={post.competitor_name}
              className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
              loading="lazy"
            />
            <div className="absolute top-2.5 left-2.5 flex items-center space-x-1.5">
              {getSourceBadge(post.source_information, post.source_type)}
            </div>
            {post.call_to_action && (
              <div className="absolute bottom-2.5 right-2.5 bg-slate-950/80 backdrop-blur-md px-2.5 py-1 rounded-lg text-[10px] font-bold text-white border border-slate-700/80">
                {post.call_to_action}
              </div>
            )}
          </div>
        )}

        {/* Content Details */}
        <div className="p-4 space-y-3">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold text-slate-300 truncate max-w-[160px]">
              {post.competitor_name}
            </span>
            <div className="flex items-center space-x-2">
              {!thumbnail && getSourceBadge(post.source_information, post.source_type)}
              <div className="flex items-center space-x-1 text-[11px] text-slate-400">
                <Calendar size={12} />
                <span>
                  {post.published_date
                    ? new Date(post.published_date).toLocaleDateString(undefined, { month: 'short', day: 'numeric' })
                    : 'Recent'}
                </span>
              </div>
            </div>
          </div>

          <div className="flex items-center space-x-1.5 flex-wrap gap-y-1">
            {getContentTypeBadge(post.content_type)}
            {post.industry_topic && (
              <span className="px-2 py-0.5 rounded-full text-[10px] font-semibold bg-slate-800 text-slate-300 border border-slate-700">
                {post.industry_topic}
              </span>
            )}
          </div>

          <p className="text-xs text-slate-300 line-clamp-3 leading-relaxed">
            {post.post_text || 'No text snippet available.'}
          </p>
        </div>
      </div>

      {/* Footer tags and link */}
      <div className="px-4 py-3 border-t border-slate-800/80 bg-slate-950/40 flex items-center justify-between">
        <div className="flex items-center space-x-1 truncate max-w-[200px]">
          {keywords.map((kw, i) => (
            <span key={i} className="text-[10px] text-slate-400 bg-slate-800 px-1.5 py-0.5 rounded truncate">
              #{kw.trim()}
            </span>
          ))}
        </div>
        <span className="text-indigo-400 group-hover:text-indigo-300 text-xs font-semibold flex items-center space-x-0.5">
          <span>View</span>
          <ArrowUpRight size={13} />
        </span>
      </div>
    </div>
  );
};
