import React, { useState } from 'react';

// Mock data for initial state
const mockData = {
  news: [
    {
      id: 1,
      title: 'Zero-Day Vulnerability Discovered in Popular Web Framework',
      summary: 'A critical zero-day vulnerability has been identified in a widely-used web framework affecting millions of websites worldwide.',
      source: 'TechDaily',
      publishedAt: '2024-01-15T09:30:00Z',
      imageUrl: 'https://images.unsplash.com/photo-1558494949-e7c0f8a7ca36?w=400',
      tags: ['Zero-day', 'Web Security'],
    },
    {
      id: 2,
      title: 'AI-Powered Phishing Detection System Shows 95% Accuracy',
      summary: 'Researchers have developed an AI system that can detect phishing attempts with 95% accuracy, significantly outperforming traditional methods.',
      source: 'CyberSec World',
      publishedAt: '2024-01-14T14:00:00Z',
      imageUrl: 'https://images.unsplash.com/photo-1558494949-e7c0f8a7ca36?w=400',
      tags: ['AI', 'Phishing'],
    },
    {
      id: 3,
      title: 'New Ransomware Strain Targets Healthcare Sector',
      summary: 'A new ransomware variant specifically targeting healthcare organizations has been detected, encrypting patient records and critical systems.',
      source: 'HealthTech News',
      publishedAt: '2024-01-13T11:45:00Z',
      imageUrl: 'https://images.unsplash.com/photo-1558494949-e7c0f8a7ca36?w=400',
      tags: ['Ransomware', 'Healthcare'],
    },
  ],
  user: {
    name: 'Alex Thompson',
    avatar: 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=200',
  },
};

function App() {
  const [news, setNews] = useState(mockData.news);
  const [user] = useState(mockData.user);

  const addNewsHandler = () => {
    alert('Add news functionality would go here - placeholder for now');
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4 flex items-center justify-between">
          {/* Logo and Title */}
          <div>
            <h1 className="text-xl font-bold text-gray-900">
              CyberGuard<span className="text-indigo-600">News</span>
            </h1>
            <p className="text-sm text-gray-500 mt-1">Your trusted cybersecurity intelligence source</p>
          </div>

          {/* User Profile */}
          <div className="flex items-center space-x-3">
            <img
              src={user.avatar}
              alt="Profile photo of user"
              className="w-8 h-8 rounded-full object-cover ring-2 ring-indigo-100"
              onError={(e) => { e.target.src = 'https://via.placeholder.com/32'; }}
            />
            <span className="text-sm font-medium text-gray-700">{user.name}</span>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Stats Overview */}
        <section className="mb-8">
          <h2 className="text-lg font-semibold text-gray-800 mb-4">News Dashboard</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <StatCard title="Breaking News" value={news.length} description={`${news.length} recent cybersecurity articles`} />
            <StatCard title="Top Sources" value="5" description="Trusted security news outlets" />
            <StatCard title="Categories" value="8" description="Threat intelligence categories" />
          </div>
        </section>

        {/* News Feed */}
        <section className="mb-8">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold text-gray-800">Latest Threat Intelligence</h2>
            <button
              onClick={addNewsHandler}
              aria-label="Add new cybersecurity news"
              className="inline-flex items-center px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors font-medium shadow-sm text-sm"
            >
              + Add News
            </button>
          </div>

          {news.length === 0 ? (
            <EmptyState />
          ) : (
            <NewsFeed news={news} onArticleClick={() => alert('Navigate to article')} />
          )}
        </section>
      </main>

      {/* Footer */}
      <footer className="bg-white border-t border-gray-200 mt-auto">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6 text-center">
          <p className="text-sm text-gray-500">
            &copy; 2024 CyberGuardNews. All rights reserved. | Built with React and TailwindCSS
          </p>
        </div>
      </footer>
    </div>
  );
}

// Reusable stat card component
function StatCard({ title, value, description }) {
  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 hover:shadow-md transition-shadow">
      <h3 className="text-sm font-medium text-gray-500 mb-1">{title}</h3>
      <p className="text-3xl font-bold text-indigo-600 mb-2">{value.toLocaleString()}</p>
      <p className="text-xs text-gray-400">{description}</p>
    </div>
  );
}

// Empty state when no news articles are available
function EmptyState() {
  return (
    <div className="bg-white rounded-lg shadow-sm border border-dashed border-indigo-200 p-12 text-center">
      <div className="w-16 h-16 bg-indigo-50 rounded-full flex items-center justify-center mx-auto mb-4">
        <svg className="w-8 h-8 text-indigo-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M19 20H5a2 2 0 01-2-2V6a2 2 0 012-2h10a2 2 0 012 2v1m2 13a2 2 0 01-2-2V7m2 13a2 2 0 002-2V9a2 2 0 00-2-2h-2m2 0V5m2 5H4" />
        </svg>
      </div>
      <p className="text-gray-600 font-medium mb-1">No cybersecurity news available</p>
      <p className="text-sm text-gray-400">Click "Add News" to contribute your first article.</p>
    </div>
  );
}

// News feed component with individual article cards
function NewsFeed({ news, onArticleClick }) {
  return (
    <div className="space-y-4">
      {news.map((article) => (
        <NewsItem key={article.id} article={article} onClick={() => onArticleClick(article)} />
      ))}
    </div>
  );
}

// Individual news article card with image, title, summary and tags
function NewsItem({ article, onClick }) {
  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden hover:shadow-md transition-shadow cursor-pointer" onClick={() => onClick(article)}>
      {/* Article Image */}
      <img
        src={article.imageUrl || 'https://via.placeholder.com/400x200?text=No+Image'}
        alt="News article image"
        className="w-full h-48 object-cover"
        onError={(e) => { e.target.src = 'https://via.placeholder.com/400x200?text=No+Image'; }}
      />

      {/* Article Content */}
      <div className="p-5">
        {/* Tags */}
        <div className="flex flex-wrap gap-2 mb-3">
          {article.tags.map((tag, i) => (
            <span key={i} className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-indigo-100 text-indigo-700">
              {tag}
            </span>
          ))}
        </div>

        {/* Title */}
        <h3 className="text-lg font-semibold text-gray-900 mb-2 line-clamp-2" title={article.title}>
          {article.title}
        </h3>

        {/* Summary */}
        <p className="text-sm text-gray-600 mb-4 line-clamp-3">{article.summary}</p>

        {/* Footer with source and date */}
        <div className="flex items-center justify-between text-xs text-gray-400">
          <span>{article.source}</span>
          <span>{new Date(article.publishedAt).toLocaleDateString()}</span>
        </div>
      </div>
    </div>
  );
}

export default App;
