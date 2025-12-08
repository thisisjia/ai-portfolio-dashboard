'use client';

import { useState, useEffect } from 'react';
import TokenAuth from '@/components/TokenAuth';
import Dashboard from '@/components/Dashboard';
import { TokenAuthResponse } from '@/lib/api';

export default function Home() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [authData, setAuthData] = useState<TokenAuthResponse | null>(null);

  useEffect(() => {
    // Check if there's a stored session
    const storedAuth = localStorage.getItem('authData');
    if (storedAuth) {
      const data = JSON.parse(storedAuth);
      setAuthData(data);
      setIsAuthenticated(true);
    }
  }, []);

  const handleAuthenticated = (response: TokenAuthResponse) => {
    setAuthData(response);
    setIsAuthenticated(true);
    localStorage.setItem('authData', JSON.stringify(response));
  };

  const handleLogout = () => {
    setIsAuthenticated(false);
    setAuthData(null);
    localStorage.removeItem('authData');
  };

  if (!isAuthenticated || !authData) {
    return <TokenAuth onAuthenticated={handleAuthenticated} />;
  }

  return <Dashboard authData={authData} onLogout={handleLogout} />;
}