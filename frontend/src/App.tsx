import React, { useState, useEffect } from 'react';
import { Sidebar } from './components/Sidebar';
import { Header } from './components/Header';
import { ScrapingModal } from './components/ScrapingModal';
import { DashboardPage } from './pages/DashboardPage';
import { ProjectsPage } from './pages/ProjectsPage';
import { CompetitorsPage } from './pages/CompetitorsPage';
import { RepositoryPage } from './pages/RepositoryPage';
import { ScrapingJobsPage } from './pages/ScrapingJobsPage';
import { TrendsPage } from './pages/TrendsPage';
import { AIAnalysisPage } from './pages/AIAnalysisPage';
import { ContentIdeasPage } from './pages/ContentIdeasPage';
import { GeneratedUpdatesPage } from './pages/GeneratedUpdatesPage';
import { SettingsPage } from './pages/SettingsPage';
import type { Project, Post, GeneratedIdea } from './types';
import { api } from './services/api';

export const App: React.FC = () => {
  const [currentTab, setCurrentTab] = useState<string>('dashboard');
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState<boolean>(false);
  const [projects, setProjects] = useState<Project[]>([]);
  const [selectedProjectId, setSelectedProjectId] = useState<number | undefined>(undefined);

  // Scraping Modal states
  const [isScrapeModalOpen, setIsScrapeModalOpen] = useState(false);
  const [scrapeMode, setScrapeMode] = useState<'live' | 'demo'>('demo');

  // Selected Post for detail modal
  const [selectedPost, setSelectedPost] = useState<Post | null>(null);

  // Prefilled Idea for Complete Update Generator
  const [prefilledIdea, setPrefilledIdea] = useState<GeneratedIdea | null>(null);

  const loadProjects = async () => {
    try {
      const data = await api.getProjects();
      setProjects(data);
      if (data.length > 0 && selectedProjectId === undefined) {
        setSelectedProjectId(data[0].id);
      }
    } catch (err) {
      console.error('Error fetching projects list', err);
    }
  };

  useEffect(() => {
    loadProjects();
  }, []);

  const handleOpenScrape = (mode: 'live' | 'demo') => {
    setScrapeMode(mode);
    setIsScrapeModalOpen(true);
  };

  const handleDraftUpdateFromIdea = (idea: GeneratedIdea) => {
    setPrefilledIdea(idea);
    setCurrentTab('updates');
  };

  const handleDraftUpdateFromPost = (post: Post) => {
    setPrefilledIdea({
      id: 0,
      project_id: post.project_id,
      title: `Response to ${post.competitor_name}'s ${post.industry_topic || 'Update'}`,
      topic: post.industry_topic || 'Special Announcement',
      description: `Counter-campaign addressing: "${post.post_text?.slice(0, 100)}..."`,
      ai_provider: 'gemini',
      model_used: 'gemini-2.5-flash',
      created_at: new Date().toISOString(),
    });
    setSelectedPost(null);
    setCurrentTab('updates');
  };

  return (
    <div className="min-h-screen bg-slate-950 flex flex-col lg:flex-row text-slate-100">
      {/* Navigation Sidebar */}
      <Sidebar
        currentTab={currentTab}
        setCurrentTab={setCurrentTab}
        isOpen={isMobileMenuOpen}
        setIsOpen={setIsMobileMenuOpen}
      />

      {/* Main Content Area */}
      <div className="flex-1 lg:pl-64 flex flex-col min-w-0">
        <Header
          projects={projects}
          selectedProjectId={selectedProjectId}
          onSelectProject={(id) => setSelectedProjectId(id)}
          onOpenMobileMenu={() => setIsMobileMenuOpen(true)}
          onTriggerScrape={handleOpenScrape}
        />

        <main className="flex-1 max-w-7xl w-full mx-auto pb-16">
          {currentTab === 'dashboard' && (
            <DashboardPage
              selectedProjectId={selectedProjectId}
              onNavigateTab={setCurrentTab}
              onOpenScrapeModal={handleOpenScrape}
              onSelectPost={(post) => setSelectedPost(post)}
            />
          )}

          {currentTab === 'projects' && (
            <ProjectsPage
              onSelectProject={(id) => {
                setSelectedProjectId(id);
                setCurrentTab('repository');
              }}
              onNavigateTab={setCurrentTab}
            />
          )}

          {currentTab === 'competitors' && (
            <CompetitorsPage
              selectedProjectId={selectedProjectId}
              projects={projects}
              onOpenScrapeModal={handleOpenScrape}
              onNavigateTab={setCurrentTab}
            />
          )}

          {currentTab === 'repository' && (
            <RepositoryPage
              selectedProjectId={selectedProjectId}
              projects={projects}
              onSelectPost={(post) => setSelectedPost(post)}
              selectedPost={selectedPost}
              onCloseDetailModal={() => setSelectedPost(null)}
              onDraftUpdateFromPost={handleDraftUpdateFromPost}
            />
          )}

          {currentTab === 'scraping' && (
            <ScrapingJobsPage
              selectedProjectId={selectedProjectId}
              onOpenScrapeModal={handleOpenScrape}
            />
          )}

          {currentTab === 'trends' && (
            <TrendsPage
              selectedProjectId={selectedProjectId}
              projects={projects}
            />
          )}

          {currentTab === 'analysis' && (
            <AIAnalysisPage
              selectedProjectId={selectedProjectId}
              projects={projects}
              onSelectPost={(post) => setSelectedPost(post)}
            />
          )}

          {currentTab === 'ideas' && (
            <ContentIdeasPage
              selectedProjectId={selectedProjectId}
              projects={projects}
              onDraftUpdateFromIdea={handleDraftUpdateFromIdea}
            />
          )}

          {currentTab === 'updates' && (
            <GeneratedUpdatesPage
              selectedProjectId={selectedProjectId}
              projects={projects}
              prefilledIdea={prefilledIdea}
              onClearPrefilledIdea={() => setPrefilledIdea(null)}
            />
          )}

          {currentTab === 'settings' && <SettingsPage />}
        </main>
      </div>

      {/* Global Scraping Execution Modal */}
      <ScrapingModal
        isOpen={isScrapeModalOpen}
        onClose={() => setIsScrapeModalOpen(false)}
        projectId={selectedProjectId || (projects[0]?.id || 1)}
        mode={scrapeMode}
        onJobFinished={() => {
          loadProjects();
        }}
      />
    </div>
  );
};

export default App;
