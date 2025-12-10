'use client';

import { useState, useEffect } from 'react';

interface Visitor {
  company: string;
  company_name: string;
  last_accessed: string;
  first_accessed: string;
  visit_count: number;
}

interface AnalyticsData {
  visitors: Visitor[];
}

export default function AdminPage() {
  const [adminToken, setAdminToken] = useState('');
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [analytics, setAnalytics] = useState<AnalyticsData | null>(null);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  // Check if token is saved in localStorage
  useEffect(() => {
    const savedToken = localStorage.getItem('adminToken');
    if (savedToken) {
      setAdminToken(savedToken);
      fetchAnalytics(savedToken);
    }
  }, []);

  const fetchAnalytics = async (token: string) => {
    setLoading(true);
    setError('');

    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'https://thisisjia.com';
      const response = await fetch(`${apiUrl}/admin/analytics`, {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      if (response.status === 403) {
        setError('Invalid admin token');
        setIsAuthenticated(false);
        localStorage.removeItem('adminToken');
        return;
      }

      if (!response.ok) {
        throw new Error('Failed to fetch analytics');
      }

      const data = await response.json();
      setAnalytics(data);
      setIsAuthenticated(true);
      localStorage.setItem('adminToken', token);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch analytics');
      setIsAuthenticated(false);
    } finally {
      setLoading(false);
    }
  };

  const handleLogin = (e: React.FormEvent) => {
    e.preventDefault();
    fetchAnalytics(adminToken);
  };

  const handleLogout = () => {
    setIsAuthenticated(false);
    setAdminToken('');
    setAnalytics(null);
    localStorage.removeItem('adminToken');
  };

  const formatDate = (dateString: string) => {
    try {
      const date = new Date(dateString);
      return date.toLocaleString('en-US', {
        month: 'short',
        day: 'numeric',
        year: 'numeric',
        hour: 'numeric',
        minute: '2-digit',
        hour12: true,
      });
    } catch {
      return dateString;
    }
  };

  const thisWeekCount = analytics?.visitors.filter(v => {
    if (!v.last_accessed) return false;
    const lastAccessed = new Date(v.last_accessed);
    const weekAgo = new Date();
    weekAgo.setDate(weekAgo.getDate() - 7);
    return lastAccessed >= weekAgo;
  }).length || 0;

  if (!isAuthenticated) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-gray-900 via-purple-900 to-gray-900 flex items-center justify-center p-4">
        <div className="bg-white rounded-lg shadow-xl p-8 max-w-md w-full">
          <div className="text-center mb-8">
            <h1 className="text-3xl font-bold text-gray-900 mb-2">🔐 Admin Login</h1>
            <p className="text-gray-600">Enter your admin token to access analytics</p>
          </div>

          <form onSubmit={handleLogin} className="space-y-4">
            <div>
              <label htmlFor="token" className="block text-sm font-medium text-gray-700 mb-2">
                Admin Token
              </label>
              <input
                id="token"
                type="password"
                value={adminToken}
                onChange={(e) => setAdminToken(e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent text-gray-900"
                placeholder="Enter admin token"
                required
              />
            </div>

            {error && (
              <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg text-sm">
                {error}
              </div>
            )}

            <button
              type="submit"
              disabled={loading}
              className="w-full bg-gradient-to-r from-purple-600 to-indigo-600 text-white font-semibold py-2 px-4 rounded-lg hover:from-purple-700 hover:to-indigo-700 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? 'Authenticating...' : 'Login'}
            </button>
          </form>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 p-4 md:p-8">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="bg-gradient-to-r from-purple-600 to-indigo-600 rounded-lg shadow-lg p-6 md:p-8 mb-8 text-white">
          <div className="flex justify-between items-center">
            <div>
              <h1 className="text-3xl md:text-4xl font-bold mb-2">🔐 Admin Analytics Dashboard</h1>
              <p className="text-purple-100">Resume Dashboard Access Logs</p>
            </div>
            <button
              onClick={handleLogout}
              className="bg-white text-purple-600 px-4 py-2 rounded-lg font-semibold hover:bg-purple-50 transition-colors"
            >
              Logout
            </button>
          </div>
        </div>

        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <div className="bg-white rounded-lg shadow p-6">
            <div className="text-4xl font-bold text-purple-600 mb-2">
              {analytics?.visitors.length || 0}
            </div>
            <div className="text-gray-600">Total Visitors</div>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <div className="text-4xl font-bold text-purple-600 mb-2">
              {analytics?.visitors.reduce((sum, v) => sum + (v.visit_count || 1), 0) || 0}
            </div>
            <div className="text-gray-600">Total Visits</div>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <div className="text-4xl font-bold text-purple-600 mb-2">
              {thisWeekCount}
            </div>
            <div className="text-gray-600">This Week</div>
          </div>
        </div>

        {/* Visitors Table */}
        <div className="bg-white rounded-lg shadow overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-purple-600 text-white">
                <tr>
                  <th className="px-6 py-4 text-left font-semibold">Company Domain</th>
                  <th className="px-6 py-4 text-left font-semibold">Company Name</th>
                  <th className="px-6 py-4 text-left font-semibold">Last Accessed</th>
                  <th className="px-6 py-4 text-left font-semibold">First Accessed</th>
                  <th className="px-6 py-4 text-left font-semibold">Visit Count</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200">
                {analytics?.visitors && analytics.visitors.length > 0 ? (
                  analytics.visitors.map((visitor, index) => (
                    <tr key={index} className="hover:bg-gray-50 transition-colors">
                      <td className="px-6 py-4 font-medium text-gray-900">{visitor.company}</td>
                      <td className="px-6 py-4 text-gray-700">{visitor.company_name}</td>
                      <td className="px-6 py-4 text-gray-600 text-sm">
                        {formatDate(visitor.last_accessed)}
                      </td>
                      <td className="px-6 py-4 text-gray-600 text-sm">
                        {formatDate(visitor.first_accessed)}
                      </td>
                      <td className="px-6 py-4">
                        <span className="bg-purple-100 text-purple-800 px-3 py-1 rounded-full text-sm font-semibold">
                          {visitor.visit_count || 1} visits
                        </span>
                      </td>
                    </tr>
                  ))
                ) : (
                  <tr>
                    <td colSpan={5} className="px-6 py-12 text-center text-gray-500">
                      No visitors yet
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </div>

        {/* Refresh Button */}
        <div className="mt-6 text-center">
          <button
            onClick={() => fetchAnalytics(adminToken)}
            disabled={loading}
            className="bg-purple-600 text-white px-6 py-2 rounded-lg font-semibold hover:bg-purple-700 transition-colors disabled:opacity-50"
          >
            {loading ? 'Refreshing...' : 'Refresh Data'}
          </button>
        </div>
      </div>
    </div>
  );
}
