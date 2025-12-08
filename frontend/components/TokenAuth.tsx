'use client';

import { useState } from 'react';
import { api, TokenAuthResponse } from '@/lib/api';

interface TokenAuthProps {
  onAuthenticated: (response: TokenAuthResponse) => void;
}

export default function TokenAuth({ onAuthenticated }: TokenAuthProps) {
  const [token, setToken] = useState('');
  const [companyDomain, setCompanyDomain] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!token.trim()) {
      setError('Please enter a token');
      return;
    }

    if (!companyDomain.trim()) {
      setError('Please enter your company domain');
      return;
    }

    setIsLoading(true);
    setError(null);

    try {
      const response = await api.authenticateToken(token, companyDomain);

      if (response.authenticated) {
        // Include the token in the response
        onAuthenticated({ ...response, token });
      } else {
        setError(response.error || 'Authentication failed');
      }
    } catch (err) {
      setError('Failed to authenticate. Please try again.');
      console.error('Authentication error:', err);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-100">
      <div className="bg-white p-8 rounded-2xl shadow-xl w-full max-w-md">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            🎯 Token-Gated Resume Dashboard
          </h1>
          <p className="text-gray-600">
            Please enter the access token provided and your company domain
          </p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-6">
          <div>
            <label htmlFor="token" className="block text-sm font-medium text-gray-700 mb-2">
              Access Token
            </label>
            <input
              id="token"
              type="text"
              value={token}
              onChange={(e) => setToken(e.target.value)}
              placeholder="Enter your access token"
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              disabled={isLoading}
            />
          </div>

          <div>
            <label htmlFor="companyDomain" className="block text-sm font-medium text-gray-700 mb-2">
              Company Domain
            </label>
            <input
              id="companyDomain"
              type="text"
              value={companyDomain}
              onChange={(e) => setCompanyDomain(e.target.value)}
              placeholder="e.g., acme.com"
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              disabled={isLoading}
            />
            <p className="mt-1 text-xs text-gray-500">
              Enter your company domain in domain format (e.g., company.com)
            </p>
          </div>

          {error && (
            <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg text-sm">
              {error}
            </div>
          )}

          <button
            type="submit"
            disabled={isLoading}
            className="w-full py-3 px-4 bg-blue-600 hover:bg-blue-700 text-white font-semibold rounded-lg transition duration-200 disabled:bg-gray-400 disabled:cursor-not-allowed"
          >
            {isLoading ? 'Authenticating...' : 'Access Dashboard'}
          </button>
        </form>
      </div>
    </div>
  );
}