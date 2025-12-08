'use client';

import { useState } from 'react';
import EnhancedChatInterface from './EnhancedChatInterface';
import SQLDemo from './SQLDemo';
import { TokenAuthResponse } from '@/lib/api';

interface DashboardProps {
  authData: TokenAuthResponse;
  onLogout: () => void;
}

type Tab = 'chat' | 'sql' | 'api' | 'feedback';

export default function Dashboard({ authData, onLogout }: DashboardProps) {
  const [activeTab, setActiveTab] = useState<Tab>('chat');

  const tabs = [
    { id: 'chat' as Tab, label: '🤖 AI Chat Assistant', available: true },
    { id: 'sql' as Tab, label: '🗃️ SQL Demonstrations', available: true },
    { id: 'api' as Tab, label: '📊 Live API Integrations', available: false },
    { id: 'feedback' as Tab, label: '👍 Feedback Collection', available: false },
  ];

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-gradient-to-r from-blue-600 to-indigo-700 text-white shadow-lg">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex justify-between items-center">
            <div>
              <h1 className="text-3xl font-bold">🎯 Interactive Resume Dashboard</h1>
              <p className="mt-1 text-blue-100">
                Welcome, {authData.company_name || authData.company}!
              </p>
            </div>
            <button
              onClick={onLogout}
              className="px-4 py-2 bg-white/20 hover:bg-white/30 rounded-lg transition"
            >
              Logout
            </button>
          </div>
        </div>
      </header>

      {/* Navigation Tabs */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 mt-6">
        <div className="border-b border-gray-200">
          <nav className="-mb-px flex space-x-8">
            {tabs.map((tab) => (
              <button
                key={tab.id}
                onClick={() => tab.available && setActiveTab(tab.id)}
                className={`
                  py-2 px-1 border-b-2 font-medium text-sm transition
                  ${!tab.available ? 'cursor-not-allowed opacity-50' : 'cursor-pointer'}
                  ${
                    activeTab === tab.id
                      ? 'border-blue-500 text-blue-600'
                      : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                  }
                `}
                disabled={!tab.available}
              >
                {tab.label}
                {!tab.available && (
                  <span className="ml-2 text-xs bg-gray-200 text-gray-600 px-2 py-1 rounded">
                    Coming Soon
                  </span>
                )}
              </button>
            ))}
          </nav>
        </div>
      </div>

      {/* Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="bg-white rounded-lg shadow-lg p-6">
          {activeTab === 'chat' && (
            <div>
              <h2 className="text-2xl font-bold mb-4">AI Chat Assistant</h2>
              <p className="text-gray-600 mb-6">
                Ask me anything about my experience, skills, projects, or work style!
              </p>
              <EnhancedChatInterface authData={authData} />
            </div>
          )}

          {activeTab === 'sql' && (
            <div>
              <h2 className="text-2xl font-bold mb-4">SQL Query Demonstrations</h2>
              <p className="text-gray-600 mb-6">
                Explore my database skills through interactive SQL queries on real resume data
              </p>
              <SQLDemo />
            </div>
          )}

          {activeTab === 'api' && (
            <div className="text-center py-16">
              <h2 className="text-2xl font-bold mb-4">Live API Integrations</h2>
              <p className="text-gray-600">
                Real-time market data and insights coming soon...
              </p>
            </div>
          )}

          {activeTab === 'feedback' && (
            <div className="text-center py-16">
              <h2 className="text-2xl font-bold mb-4">Feedback Collection</h2>
              <p className="text-gray-600">
                Vision-based feedback with MediaPipe coming soon...
              </p>
            </div>
          )}
        </div>

        {/* Stats */}
        {process.env.NEXT_PUBLIC_ENABLE_ANALYTICS === 'true' && (
          <div className="mt-8 grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="bg-white rounded-lg shadow p-6">
              <h3 className="text-sm font-medium text-gray-500">Session ID</h3>
              <p className="mt-2 text-xs text-gray-900 font-mono">
                {authData.session_id?.slice(0, 8)}...
              </p>
            </div>
            <div className="bg-white rounded-lg shadow p-6">
              <h3 className="text-sm font-medium text-gray-500">Environment</h3>
              <p className="mt-2 text-2xl font-semibold text-gray-900">
                {process.env.NEXT_PUBLIC_ENVIRONMENT}
              </p>
            </div>
            <div className="bg-white rounded-lg shadow p-6">
              <h3 className="text-sm font-medium text-gray-500">API Status</h3>
              <p className="mt-2 text-2xl font-semibold text-green-600">
                Connected
              </p>
            </div>
          </div>
        )}
      </main>
    </div>
  );
}