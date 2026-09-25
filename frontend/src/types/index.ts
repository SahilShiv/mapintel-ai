export interface Keyword {
  id: number;
  project_id: number;
  keyword: string;
  created_at: string;
}

export interface Competitor {
  id: number;
  project_id: number;
  business_name: string;
  google_maps_url: string;
  place_identifier?: string;
  status: string;
  last_scraped_at?: string;
  total_posts: number;
  scraping_status: string;
  created_at: string;
  updated_at: string;
}

export interface Project {
  id: number;
  project_name: string;
  client_business_name: string;
  google_maps_url?: string;
  description?: string;
  verified_facts?: string;
  created_at: string;
  updated_at: string;
  competitors_count: number;
  keywords_count: number;
  posts_count: number;
  last_scraped_at?: string;
}

export interface ProjectDetail extends Project {
  competitors: Competitor[];
  keywords: Keyword[];
}

export interface PostMedia {
  id: number;
  media_type: string;
  media_url: string;
  thumbnail_url?: string;
  caption?: string;
}

export interface PostAnalysis {
  id: number;
  main_topic?: string;
  sub_topic?: string;
  keywords?: string;
  content_type?: string;
  call_to_action?: string;
  offer_pattern?: string;
  sentiment?: string;
  ai_provider?: string;
  analyzed_at: string;
}

export interface Post {
  id: number;
  project_id: number;
  competitor_id: number;
  competitor_name: string;
  google_maps_profile_url?: string;
  post_url?: string;
  post_text?: string;
  published_date?: string;
  call_to_action?: string;
  detected_keywords?: string;
  industry_topic?: string;
  content_type?: string;
  source_information: string;
  source_type: 'LIVE' | 'DEMO' | 'SEEDED' | string;
  is_valid: boolean;
  validation_error?: string;
  fingerprint: string;
  scraped_at: string;
  created_at: string;
  media: PostMedia[];
  analysis?: PostAnalysis;
}

export interface PostListResponse {
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
  items: Post[];
}

export interface ScrapingJobItem {
  id: number;
  competitor_id?: number;
  competitor_name: string;
  status: string;
  posts_found: number;
  valid_posts: number;
  new_posts: number;
  duplicates_skipped: number;
  error_message?: string;
  log_message?: string;
  timestamp: string;
}

export interface ScrapingJob {
  id: number;
  project_id: number;
  job_type: string;
  start_time: string;
  end_time?: string;
  status: string;
  competitors_processed: number;
  total_competitors: number;
  posts_found: number;
  valid_posts: number;
  new_posts: number;
  duplicates_skipped: number;
  images_downloaded: number;
  failures: number;
  captcha_detected: boolean;
  error_details?: string;
  created_at: string;
  items: ScrapingJobItem[];
}

export interface TopicMetric {
  topic: string;
  count: number;
  percentage: number;
  competitors_count: number;
  competitors: string[];
}

export interface KeywordMetric {
  keyword: string;
  count: number;
  percentage: number;
}

export interface ContentTypeMetric {
  content_type: string;
  count: number;
  percentage: number;
}

export interface CTAMetric {
  call_to_action: string;
  count: number;
  percentage: number;
}

export interface CompetitorPostingMetric {
  competitor_id: number;
  competitor_name: string;
  post_count: number;
  latest_post_date?: string;
  top_topics: string[];
}

export interface TimelinePoint {
  period: string;
  count: number;
}

export interface TrendAnalysis {
  project_id: number;
  total_posts: number;
  top_topics: TopicMetric[];
  top_keywords: KeywordMetric[];
  content_types: ContentTypeMetric[];
  call_to_actions: CTAMetric[];
  competitor_activity: CompetitorPostingMetric[];
  posting_timeline: TimelinePoint[];
  ai_insights?: string;
  calculated_at: string;
}

export interface GeneratedIdea {
  id: number;
  project_id: number;
  title: string;
  topic: string;
  description: string;
  relevant_keywords?: string;
  suggested_cta?: string;
  competitor_insight?: string;
  ai_provider: string;
  model_used: string;
  created_at: string;
}

export interface ContentIdeaBatch {
  project_id: number;
  requested_count: number;
  generated_count: number;
  skipped_duplicates: number;
  ideas: GeneratedIdea[];
}

export interface GeneratedUpdate {
  id: number;
  project_id: number;
  idea_id?: number;
  topic: string;
  update_copy: string;
  relevant_keywords?: string;
  call_to_action?: string;
  image_concept?: string;
  generated_image_url?: string;
  ai_provider: string;
  model_used: string;
  created_at: string;
}

export interface DashboardData {
  kpis: {
    total_projects: number;
    total_competitors: number;
    total_posts: number;
    new_posts_latest: number;
    duplicate_posts_skipped: number;
    failed_attempts: number;
    generated_content_count: number;
  };
  recent_jobs: ScrapingJob[];
  recent_posts: Post[];
  top_topics: { topic: string; count: number }[];
  top_keywords: { keyword: string; count: number }[];
  competitor_activity: { id: number; name: string; post_count: number; status: string }[];
  ai_overview: string;
}

export const _types_loaded = true;

