import React, { useState, useEffect } from 'react';
import {
  PlayCircle,
  CheckCircle2,
  AlertTriangle,
  Clock,
  ShieldAlert,
  Copy,
  Layers,
  ArrowRight,
  RefreshCw,
  ChevronDown,
  ChevronUp
} from 'lucide-react';
import type { ScrapingJob } from '../types';
import { api } from '../services/api';

interface ScrapingJobsPageProps {
  selectedProjectId?: number;
  onOpenScrapeModal: (mode: 'live' | 'demo') => void;
}

export const ScrapingJobsPage: React.FC<ScrapingJobsPageProps> = ({
  selectedProjectId,
  onOpenScrapeModal,
}) => {
  const [jobs, setJobs] = useState<ScrapingJob[]>([]);
  const [loading, setLoading] = useState(true);
  const [expandedJobId, setExpandedJobId] = useState<number | null>(null);

  const loadJobs = async () => {
    setLoading(true);
    try {
      const data = await api.getScrapingJobs(selectedProjectId);
      setJobs(data);
    } catch (err) {
      console.error('Error loading scraping jobs', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadJobs();
  }, [selectedProjectId]);

  const toggleExpand = (jobId: number) => {
    setExpandedJobId(expandedJobId === jobId ? null : jobId);
  };

  const getStatusBadge = (status: string, isCaptcha: boolean) => {
    if (isCaptcha || status === 'Manual Intervention Required' || status === 'CAPTCHA_REQUIRED') {
      return (
        <span className="inline-flex items-center space-x-1 px-2.5 py-1 rounded-full text-xs font-bold bg-amber-500/10 text-amber-400 border border-amber-500/30">
          <ShieldAlert size={12} />
          <span>Manual Verification Required</span>
        </span>
      );
    }
    if (status === 'EXTRACTION_FAILED') {
      return (
        <span className="inline-flex items-center space-x-1 px-2.5 py-1 rounded-full text-xs font-bold bg-rose-500/10 text-rose-400 border border-rose-500/30">
          <AlertTriangle size={12} />
          <span>Extraction Failed</span>
        </span>
      );
    }
    if (status === 'PARTIAL_SUCCESS') {
      return (
        <span className="inline-flex items-center space-x-1 px-2.5 py-1 rounded-full text-xs font-bold bg-amber-500/10 text-amber-400 border border-amber-500/30">
          <CheckCircle2 size={12} />
          <span>Partial Success</span>
        </span>
      );
    }
    if (status === 'Completed' || status === 'SUCCESS') {
      return (
        <span className="inline-flex items-center space-x-1 px-2.5 py-1 rounded-full text-xs font-bold bg-emerald-500/10 text-emerald-400 border border-emerald-500/30">
          <CheckCircle2 size={12} />
          <span>Completed</span>
        </span>
      );
    }
    if (status === 'Running' || status === 'PENDING') {
      return (
        <span className="inline-flex items-center space-x-1 px-2.5 py-1 rounded-full text-xs font-bold bg-indigo-500/10 text-indigo-400 border border-indigo-500/30">
          <Clock size={12} className="animate-spin" />
          <span>{status === 'PENDING' ? 'Pending' : 'Running'}</span>
        </span>
      );
    }
    return (
      <span className="inline-flex items-center space-x-1 px-2.5 py-1 rounded-full text-xs font-bold bg-rose-500/10 text-rose-400 border border-rose-500/30">
        <AlertTriangle size={12} />
        <span>{status}</span>
      </span>
    );
  };

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-black text-white tracking-tight">Scraping Jobs & Execution History</h2>
          <p className="text-xs text-slate-400">
            Audit every scraping run, itemized competitor log, duplicate skipping stats, and anti-automation events.
          </p>
        </div>

        <div className="flex items-center space-x-3">
          <button
            onClick={() => onOpenScrapeModal('demo')}
            className="inline-flex items-center space-x-1.5 px-3.5 py-2 rounded-xl text-xs font-bold bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700"
          >
            <RefreshCw size={13} className="text-emerald-400" />
            <span>Run Demo Scrape</span>
          </button>
          <button
            onClick={() => onOpenScrapeModal('live')}
            className="inline-flex items-center space-x-1.5 px-3.5 py-2 rounded-xl text-xs font-bold bg-indigo-600 hover:bg-indigo-500 text-white shadow-md shadow-indigo-600/30"
          >
            <PlayCircle size={14} />
            <span>Start Live Scrape</span>
          </button>
        </div>
      </div>

      {/* Jobs List */}
      <div className="space-y-4">
        {loading ? (
          <div className="space-y-3">
            {[1, 2, 3].map((i) => (
              <div key={i} className="h-28 bg-slate-900 border border-slate-800 rounded-2xl animate-pulse" />
            ))}
          </div>
        ) : jobs.length === 0 ? (
          <div className="bg-slate-900 border border-slate-800 rounded-2xl p-12 text-center space-y-3">
            <PlayCircle size={36} className="mx-auto text-slate-600" />
            <h3 className="text-base font-bold text-white">No scraping jobs recorded yet</h3>
            <p className="text-xs text-slate-400 max-w-sm mx-auto">
              Run your first live or demo scrape to start collecting competitor intelligence.
            </p>
            <button
              onClick={() => onOpenScrapeModal('demo')}
              className="px-4 py-2 rounded-xl text-xs font-bold bg-indigo-600 text-white"
            >
              Trigger First Scrape
            </button>
          </div>
        ) : (
          jobs.map((job) => {
            const isExpanded = expandedJobId === job.id;
            return (
              <div
                key={job.id}
                className="bg-slate-900 border border-slate-800 rounded-2xl overflow-hidden shadow-sm transition-all"
              >
                {/* Job Summary Banner */}
                <div
                  onClick={() => toggleExpand(job.id)}
                  className="p-5 flex flex-col lg:flex-row lg:items-center justify-between gap-4 cursor-pointer hover:bg-slate-950/40 transition-colors"
                >
                  <div className="space-y-1.5">
                    <div className="flex items-center space-x-3 flex-wrap gap-y-1">
                      <span className="text-sm font-bold text-white">Job #{job.id}</span>
                      <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-slate-800 text-slate-400 uppercase">
                        {job.job_type} Mode
                      </span>
                      {getStatusBadge(job.status, job.captcha_detected)}
                    </div>
                    <div className="flex items-center space-x-3 text-xs text-slate-400">
                      <span>Started: {new Date(job.start_time).toLocaleString()}</span>
                      {job.end_time && (
                        <span>
                          Duration:{' '}
                          {Math.max(
                            1,
                            Math.round(
                              (new Date(job.end_time).getTime() - new Date(job.start_time).getTime()) / 1000
                            )
                          )}
                          s
                        </span>
                      )}
                    </div>
                  </div>

                  {/* Summary Metric Badges */}
                  <div className="flex items-center space-x-3 flex-wrap gap-y-2">
                    <div className="flex items-center space-x-2 text-xs">
                      <div className="bg-slate-950 px-3 py-1.5 rounded-xl border border-slate-800 text-center">
                        <span className="text-[10px] text-slate-500 block">Competitors</span>
                        <span className="font-bold text-slate-200">
                          {job.competitors_processed} / {job.total_competitors}
                        </span>
                      </div>
                      <div className="bg-slate-950 px-3 py-1.5 rounded-xl border border-slate-800 text-center">
                        <span className="text-[10px] text-slate-500 block">Valid Posts</span>
                        <span className="font-bold text-indigo-400">{job.valid_posts ?? job.posts_found}</span>
                      </div>
                      <div className="bg-slate-950 px-3 py-1.5 rounded-xl border border-slate-800 text-center">
                        <span className="text-[10px] text-slate-500 block">New Posts</span>
                        <span className="font-bold text-emerald-400">+{job.new_posts}</span>
                      </div>
                      <div className="bg-slate-950 px-3 py-1.5 rounded-xl border border-slate-800 text-center">
                        <span className="text-[10px] text-slate-500 block">Duplicates</span>
                        <span className="font-bold text-amber-400">{job.duplicates_skipped}</span>
                      </div>
                      <div className="bg-slate-950 px-3 py-1.5 rounded-xl border border-slate-800 text-center">
                        <span className="text-[10px] text-slate-500 block">Failures</span>
                        <span className="font-bold text-slate-300">{job.failures}</span>
                      </div>
                    </div>

                    <div className="p-1 rounded-lg text-slate-400 hover:text-white">
                      {isExpanded ? <ChevronUp size={18} /> : <ChevronDown size={18} />}
                    </div>
                  </div>
                </div>

                {/* Expanded Itemized Execution Logs */}
                {isExpanded && (
                  <div className="border-t border-slate-800 bg-slate-950 p-5 space-y-4">
                    <h4 className="text-xs font-bold uppercase tracking-wider text-slate-400">
                      Itemized Scraping & Duplicate Inspection Logs
                    </h4>

                    {job.error_details && (
                      <div className="p-3 rounded-xl bg-amber-500/10 border border-amber-500/30 text-xs text-amber-300">
                        {job.error_details}
                      </div>
                    )}

                    {job.items && job.items.length > 0 ? (
                      <div className="divide-y divide-slate-800 border border-slate-800 rounded-xl overflow-hidden">
                        {job.items.map((item) => (
                          <div
                            key={item.id}
                            className="p-3.5 bg-slate-900/60 flex flex-col sm:flex-row sm:items-center justify-between gap-2 text-xs"
                          >
                            <div className="space-y-0.5">
                              <span className="font-bold text-slate-200">{item.competitor_name}</span>
                              <p className="text-[11px] text-slate-400">{item.log_message}</p>
                            </div>
                            <div className="flex items-center space-x-3 text-[11px]">
                              <span className="text-emerald-400 font-semibold">+{item.new_posts} new</span>
                              <span className="text-amber-400 font-semibold">{item.duplicates_skipped} skipped</span>
                              <span className="text-slate-500">
                                {new Date(item.timestamp).toLocaleTimeString()}
                              </span>
                            </div>
                          </div>
                        ))}
                      </div>
                    ) : (
                      <p className="text-xs text-slate-500">No itemized logs recorded.</p>
                    )}
                  </div>
                )}
              </div>
            );
          })
        )}
      </div>
    </div>
  );
};
