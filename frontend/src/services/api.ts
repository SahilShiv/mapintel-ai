import axios from 'axios';
import type {
  Project,
  ProjectDetail,
  Competitor,
  Post,
  PostListResponse,
  ScrapingJob,
  TrendAnalysis,
  ContentIdeaBatch,
  GeneratedIdea,
  GeneratedUpdate,
  DashboardData
} from '../types';

const getBaseUrl = (): string => {
  const envUrl = import.meta.env.VITE_API_BASE_URL || import.meta.env.VITE_API_URL;
  if (envUrl) {
    const cleaned = envUrl.replace(/\/+$/, '');
    return cleaned.endsWith('/api') ? cleaned : `${cleaned}/api`;
  }
  return 'http://localhost:8000/api';
};

const API_BASE = getBaseUrl();

const client = axios.create({
  baseURL: API_BASE,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const api = {
  // Dashboard
  getDashboard: async (projectId?: number): Promise<DashboardData> => {
    const res = await client.get('/dashboard', { params: { project_id: projectId } });
    return res.data;
  },

  // Projects
  getProjects: async (): Promise<Project[]> => {
    const res = await client.get('/projects');
    return res.data;
  },
  getProject: async (id: number): Promise<ProjectDetail> => {
    const res = await client.get(`/projects/${id}`);
    return res.data;
  },
  createProject: async (data: {
    project_name: string;
    client_business_name: string;
    google_maps_url?: string;
    description?: string;
    verified_facts?: string;
    keywords?: string[];
  }): Promise<Project> => {
    const res = await client.post('/projects', data);
    return res.data;
  },
  updateProject: async (id: number, data: Partial<Project>): Promise<Project> => {
    const res = await client.put(`/projects/${id}`, data);
    return res.data;
  },
  deleteProject: async (id: number): Promise<void> => {
    await client.delete(`/projects/${id}`);
  },

  // Competitors
  addCompetitor: async (projectId: number, data: {
    business_name: string;
    google_maps_url: string;
    place_identifier?: string;
  }): Promise<Competitor> => {
    const res = await client.post(`/projects/${projectId}/competitors`, data);
    return res.data;
  },
  updateCompetitor: async (id: number, data: Partial<Competitor>): Promise<Competitor> => {
    const res = await client.put(`/competitors/${id}`, data);
    return res.data;
  },
  deleteCompetitor: async (id: number): Promise<void> => {
    await client.delete(`/competitors/${id}`);
  },
  scrapeCompetitor: async (id: number, mode: 'live' | 'demo' = 'demo'): Promise<ScrapingJob> => {
    const res = await client.post(`/competitors/${id}/scrape`, null, { params: { mode } });
    return res.data;
  },
  getCompetitorPosts: async (id: number): Promise<Post[]> => {
    const res = await client.get(`/competitors/${id}/posts`);
    return res.data;
  },

  // Keywords
  addKeyword: async (projectId: number, keyword: string) => {
    const res = await client.post(`/projects/${projectId}/keywords`, { keyword });
    return res.data;
  },
  deleteKeyword: async (projectId: number, kwId: number): Promise<void> => {
    await client.delete(`/projects/${projectId}/keywords/${kwId}`);
  },
  discoverCompetitors: async (projectId: number, keyword: string) => {
    const res = await client.post(`/projects/${projectId}/discover-competitors`, null, {
      params: { keyword }
    });
    return res.data;
  },

  // Posts Repository
  getPosts: async (params: {
    project_id?: number;
    competitor_id?: number;
    search?: string;
    topic?: string;
    keyword?: string;
    content_type?: string;
    call_to_action?: string;
    source_type?: string;
    start_date?: string;
    end_date?: string;
    page?: number;
    page_size?: number;
  }): Promise<PostListResponse> => {
    const res = await client.get('/posts', { params });
    return res.data;
  },
  getPost: async (id: number): Promise<Post> => {
    const res = await client.get(`/posts/${id}`);
    return res.data;
  },

  // Scraping Jobs
  triggerScrape: async (data: {
    project_id: number;
    competitor_ids?: number[];
    mode?: 'live' | 'demo';
  }): Promise<ScrapingJob> => {
    const res = await client.post('/scrape', data);
    return res.data;
  },
  triggerDemoScrape: async (projectId: number, simulateCaptcha: boolean = false): Promise<ScrapingJob> => {
    const res = await client.post('/scrape/demo', null, {
      params: { project_id: projectId, simulate_captcha: simulateCaptcha }
    });
    return res.data;
  },
  getScrapingJobs: async (projectId?: number): Promise<ScrapingJob[]> => {
    const res = await client.get('/scrape/jobs', { params: { project_id: projectId } });
    return res.data;
  },
  getScrapingJob: async (id: number): Promise<ScrapingJob> => {
    const res = await client.get(`/scrape/jobs/${id}`);
    return res.data;
  },
  continueAfterCaptcha: async (jobId: number): Promise<ScrapingJob> => {
    const res = await client.post(`/scrape/jobs/${jobId}/continue`);
    return res.data;
  },

  // AI Analysis & Trends
  triggerAnalysis: async (projectId: number, forceReanalyze: boolean = false, provider?: string) => {
    const res = await client.post('/analysis', {
      project_id: projectId,
      force_reanalyze: forceReanalyze,
      provider: provider
    });
    return res.data;
  },
  getTrends: async (projectId: number): Promise<TrendAnalysis> => {
    const res = await client.get(`/trends/${projectId}`);
    return res.data;
  },

  // Content Ideas
  generateIdeas: async (data: {
    project_id: number;
    count: number;
    focus_topic?: string;
    provider?: string;
  }): Promise<ContentIdeaBatch> => {
    const res = await client.post('/content-ideas', data);
    return res.data;
  },
  getGeneratedIdeas: async (projectId?: number): Promise<GeneratedIdea[]> => {
    const res = await client.get('/content-ideas', { params: { project_id: projectId } });
    return res.data;
  },
  deleteIdea: async (id: number): Promise<void> => {
    await client.delete(`/content-ideas/${id}`);
  },

  // Complete Updates
  generateUpdate: async (data: {
    project_id: number;
    idea_id?: number;
    topic?: string;
    custom_prompt?: string;
    provider?: string;
  }): Promise<GeneratedUpdate> => {
    const res = await client.post('/generate-update', data);
    return res.data;
  },
  getGeneratedUpdates: async (projectId?: number): Promise<GeneratedUpdate[]> => {
    const res = await client.get('/generated-updates', { params: { project_id: projectId } });
    return res.data;
  },
  deleteUpdate: async (id: number): Promise<void> => {
    await client.delete(`/generated-updates/${id}`);
  },

  // Settings & System
  getAIProviders: async () => {
    const res = await client.get('/settings/ai-providers');
    return res.data;
  },
  getSystemInfo: async () => {
    const res = await client.get('/settings/system-info');
    return res.data;
  }
};
