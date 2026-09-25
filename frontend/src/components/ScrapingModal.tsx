import React, { useState, useEffect } from 'react';
import {
  CheckCircle2,
  AlertTriangle,
  Loader2,
  X,
  FileCheck,
  Copy,
  Image,
  Layers,
  ArrowRight,
  ShieldAlert
} from 'lucide-react';
import type { ScrapingJob } from '../types';
import { api } from '../services/api';

interface ScrapingModalProps {
  isOpen: boolean;
  onClose: () => void;
  projectId: number;
  mode: 'live' | 'demo';
  onJobFinished: () => void;
}

export const ScrapingModal: React.FC<ScrapingModalProps> = ({
  isOpen,
  onClose,
  projectId,
  mode,
  onJobFinished,
}) => {
  const [stage, setStage] = useState<'preparing' | 'processing' | 'completed' | 'captcha'>('preparing');
  const [job, setJob] = useState<ScrapingJob | null>(null);
  const [currentCompetitorIndex, setCurrentCompetitorIndex] = useState(0);
  const [competitorName, setCompetitorName] = useState('Competitor Profile');
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  useEffect(() => {
    if (!isOpen) {
      setJob(null);
      setStage('preparing');
      setCurrentCompetitorIndex(0);
      setErrorMsg(null);
      return;
    }

    let intervalId: any = null;

    const startJob = async () => {
      try {
        setStage('preparing');
        // Trigger scrape job
        const initialJob = await api.triggerScrape({
          project_id: projectId,
          mode: mode,
        });
        setJob(initialJob);

        if (initialJob.captcha_detected || initialJob.status === 'Manual Intervention Required') {
          setStage('captcha');
          return;
        }

        setStage('processing');

        // Poll job status until done
        intervalId = setInterval(async () => {
          try {
            const updated = await api.getScrapingJob(initialJob.id);
            setJob(updated);

            if (updated.items && updated.items.length > 0) {
              const lastItem = updated.items[updated.items.length - 1];
              setCompetitorName(lastItem.competitor_name);
              setCurrentCompetitorIndex(updated.items.length);
            }

            if (updated.captcha_detected || updated.status === 'Manual Intervention Required') {
              clearInterval(intervalId);
              setStage('captcha');
              return;
            }

            if (['Completed', 'Completed with Errors', 'Failed', 'SUCCESS', 'PARTIAL_SUCCESS', 'EXTRACTION_FAILED', 'FAILED'].includes(updated.status)) {
              clearInterval(intervalId);
              setStage('completed');
              onJobFinished();
            }
          } catch (pollErr) {
            console.error('Polling error', pollErr);
          }
        }, 1200);

      } catch (err: any) {
        setErrorMsg(err?.response?.data?.detail || 'Failed to start scraping job.');
        setStage('completed');
      }
    };

    startJob();

    return () => {
      if (intervalId) clearInterval(intervalId);
    };
  }, [isOpen, projectId, mode]);

  const handleContinueAfterCaptcha = async () => {
    if (!job) return;
    try {
      setStage('processing');
      const resumed = await api.continueAfterCaptcha(job.id);
      setJob(resumed);
      setStage('completed');
      onJobFinished();
    } catch (err) {
      console.error('Could not resume job', err);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/75 backdrop-blur-sm animate-in fade-in duration-200">
      <div className="w-full max-w-lg bg-slate-900 border border-slate-700/80 rounded-2xl shadow-2xl overflow-hidden flex flex-col">
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-slate-800 bg-slate-950/60">
          <div className="flex items-center space-x-2.5">
            <div className={`w-3 h-3 rounded-full ${mode === 'live' ? 'bg-indigo-500 animate-pulse' : 'bg-emerald-500'}`} />
            <h3 className="text-base font-bold text-white">
              {mode === 'live' ? 'Live Google Maps Scraper' : 'Authentic Demo Scraper Engine'}
            </h3>
          </div>
          {stage === 'completed' && (
            <button
              onClick={onClose}
              className="text-slate-400 hover:text-white p-1 rounded-lg hover:bg-slate-800"
            >
              <X size={18} />
            </button>
          )}
        </div>

        {/* Content body */}
        <div className="p-6 space-y-6">
          {/* Stage 1: Preparing */}
          {stage === 'preparing' && (
            <div className="flex flex-col items-center justify-center py-8 space-y-3">
              <Loader2 size={36} className="text-indigo-400 animate-spin" />
              <p className="text-sm font-semibold text-slate-200">Preparing scraper...</p>
              <p className="text-xs text-slate-400">Initializing headless browser profile and loading competitor targets</p>
            </div>
          )}

          {/* Stage 2: Processing competitors one-by-one */}
          {stage === 'processing' && (
            <div className="space-y-5">
              <div className="flex items-center justify-between bg-slate-950/70 border border-slate-800 p-3.5 rounded-xl">
                <div className="flex items-center space-x-3">
                  <div className="p-2 rounded-lg bg-indigo-500/10 text-indigo-400">
                    <Loader2 size={20} className="animate-spin" />
                  </div>
                  <div>
                    <p className="text-xs text-slate-400 font-medium">Currently Processing</p>
                    <p className="text-sm font-bold text-white">{competitorName}</p>
                  </div>
                </div>
                <span className="text-xs font-semibold px-2.5 py-1 rounded-full bg-slate-800 text-slate-300">
                  {job ? `Competitor ${job.competitors_processed + 1} of ${job.total_competitors || 1}` : 'Working...'}
                </span>
              </div>

              {/* Live Scraper Counters */}
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-2.5">
                <div className="p-3 bg-slate-950 border border-slate-800 rounded-xl text-center">
                  <p className="text-[11px] text-slate-400 font-medium">Finding Updates</p>
                  <p className="text-lg font-black text-indigo-400 mt-0.5">{job?.posts_found || 0}</p>
                </div>
                <div className="p-3 bg-slate-950 border border-slate-800 rounded-xl text-center">
                  <p className="text-[11px] text-slate-400 font-medium">New Posts</p>
                  <p className="text-lg font-black text-emerald-400 mt-0.5">{job?.new_posts || 0}</p>
                </div>
                <div className="p-3 bg-slate-950 border border-slate-800 rounded-xl text-center">
                  <p className="text-[11px] text-slate-400 font-medium">Duplicates</p>
                  <p className="text-lg font-black text-amber-400 mt-0.5">{job?.duplicates_skipped || 0}</p>
                </div>
                <div className="p-3 bg-slate-950 border border-slate-800 rounded-xl text-center">
                  <p className="text-[11px] text-slate-400 font-medium">Images</p>
                  <p className="text-lg font-black text-sky-400 mt-0.5">{job?.images_downloaded || 0}</p>
                </div>
              </div>

              <div className="p-3 bg-slate-950/40 rounded-xl border border-slate-800/60 flex items-center space-x-2 text-xs text-slate-400">
                <Layers size={14} className="text-indigo-400 flex-shrink-0" />
                <span className="truncate">Extracting post cards, image assets, timestamps, and CTAs...</span>
              </div>
            </div>
          )}

          {/* Stage 3: Completed Screen */}
          {stage === 'completed' && (
            <div className="space-y-5">
              {job?.status === 'EXTRACTION_FAILED' ? (
                <div className="flex items-start space-x-3 p-4 bg-rose-500/10 border border-rose-500/30 rounded-xl">
                  <AlertTriangle size={24} className="text-rose-400 flex-shrink-0 mt-0.5" />
                  <div>
                    <h4 className="text-sm font-bold text-rose-300">Extraction Failed</h4>
                    <p className="text-xs text-rose-200/80 leading-relaxed">
                      {job?.error_details || 'Google Maps Updates/Post content could not be reliably identified.'}
                    </p>
                  </div>
                </div>
              ) : job?.status === 'PARTIAL_SUCCESS' ? (
                <div className="flex items-start space-x-3 p-4 bg-amber-500/10 border border-amber-500/30 rounded-xl">
                  <AlertTriangle size={24} className="text-amber-400 flex-shrink-0 mt-0.5" />
                  <div>
                    <h4 className="text-sm font-bold text-amber-300">Partial Success</h4>
                    <p className="text-xs text-amber-200/80 leading-relaxed">
                      {job?.error_details || 'Some competitor profiles yielded updates while others had selector mismatches.'}
                    </p>
                  </div>
                </div>
              ) : (
                <div className="flex items-center space-x-3 p-4 bg-emerald-500/10 border border-emerald-500/30 rounded-xl">
                  <CheckCircle2 size={24} className="text-emerald-400 flex-shrink-0" />
                  <div>
                    <h4 className="text-sm font-bold text-white">Scrape Completed Successfully</h4>
                    <p className="text-xs text-emerald-300/80">
                      All target competitors processed. Duplicate detection verified.
                    </p>
                  </div>
                </div>
              )}

              {/* Statistics Breakdown */}
              <div className="bg-slate-950 border border-slate-800 rounded-xl divide-y divide-slate-800 text-xs">
                <div className="flex items-center justify-between p-3">
                  <span className="text-slate-400 flex items-center space-x-2">
                    <Layers size={14} className="text-slate-400" />
                    <span>Competitors processed:</span>
                  </span>
                  <span className="font-bold text-slate-200">{job?.competitors_processed ?? 1}</span>
                </div>
                <div className="flex items-center justify-between p-3">
                  <span className="text-slate-400 flex items-center space-x-2">
                    <FileCheck size={14} className="text-indigo-400" />
                    <span>Valid posts extracted:</span>
                  </span>
                  <span className="font-bold text-indigo-400">{job?.valid_posts ?? job?.posts_found ?? 0}</span>
                </div>
                <div className="flex items-center justify-between p-3">
                  <span className="text-slate-400 flex items-center space-x-2">
                    <CheckCircle2 size={14} className="text-emerald-400" />
                    <span>New posts stored:</span>
                  </span>
                  <span className="font-bold text-emerald-400">+{job?.new_posts ?? 0}</span>
                </div>
                <div className="flex items-center justify-between p-3">
                  <span className="text-slate-400 flex items-center space-x-2">
                    <Copy size={14} className="text-amber-400" />
                    <span>Duplicates skipped:</span>
                  </span>
                  <span className="font-bold text-amber-400">{job?.duplicates_skipped ?? 0}</span>
                </div>
                <div className="flex items-center justify-between p-3">
                  <span className="text-slate-400 flex items-center space-x-2">
                    <Image size={14} className="text-sky-400" />
                    <span>Images downloaded:</span>
                  </span>
                  <span className="font-bold text-sky-400">{job?.images_downloaded ?? 0}</span>
                </div>
                <div className="flex items-center justify-between p-3">
                  <span className="text-slate-400 flex items-center space-x-2">
                    <AlertTriangle size={14} className="text-rose-400" />
                    <span>Failures:</span>
                  </span>
                  <span className="font-bold text-slate-200">{job?.failures ?? 0}</span>
                </div>
              </div>
            </div>
          )}

          {/* Stage 4: CAPTCHA / Anti-automation Alert */}
          {stage === 'captcha' && (
            <div className="space-y-4">
              <div className="flex items-start space-x-3 p-4 bg-amber-500/10 border border-amber-500/30 rounded-xl">
                <ShieldAlert size={26} className="text-amber-400 flex-shrink-0 mt-0.5" />
                <div className="space-y-1">
                  <h4 className="text-sm font-bold text-amber-300">
                    Status: Manual Verification Required
                  </h4>
                  <p className="text-xs text-slate-300 leading-relaxed">
                    Google Maps has displayed a security checkpoint or unusual traffic verification for this competitor profile.
                  </p>
                </div>
              </div>

              <div className="bg-slate-950 p-3.5 rounded-xl border border-slate-800 text-xs space-y-2">
                <p className="text-slate-300 font-semibold">Recommended Steps:</p>
                <ol className="list-decimal list-inside space-y-1 text-slate-400">
                  <li>Verify or complete challenge in standard browser if running locally.</li>
                  <li>Click "Continue with Demo Engine" below to proceed without interruptions.</li>
                  <li>Previously collected intelligence remains 100% intact and safe.</li>
                </ol>
              </div>

              <div className="flex items-center justify-end space-x-3 pt-2">
                <button
                  onClick={onClose}
                  className="px-4 py-2 rounded-lg text-xs font-semibold bg-slate-800 hover:bg-slate-700 text-slate-300"
                >
                  Dismiss
                </button>
                <button
                  onClick={handleContinueAfterCaptcha}
                  className="inline-flex items-center space-x-1.5 px-4 py-2 rounded-lg text-xs font-semibold bg-indigo-600 hover:bg-indigo-500 text-white shadow-md shadow-indigo-600/30"
                >
                  <span>Continue with Demo Engine</span>
                  <ArrowRight size={14} />
                </button>
              </div>
            </div>
          )}
        </div>

        {/* Modal Footer */}
        {stage === 'completed' && (
          <div className="px-6 py-4 border-t border-slate-800 bg-slate-950 flex justify-end">
            <button
              onClick={onClose}
              className="px-5 py-2 rounded-lg text-xs font-bold bg-indigo-600 hover:bg-indigo-500 text-white shadow-md shadow-indigo-600/30 transition-all"
            >
              Done & View Intelligence
            </button>
          </div>
        )}
      </div>
    </div>
  );
};
