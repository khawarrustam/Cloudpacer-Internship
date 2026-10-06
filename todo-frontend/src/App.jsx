import React, { useState, useEffect } from 'react';
import { useAuth } from './hooks/useAuth';
import TodoDashboard from './components/TodoDashboard';
import AuthForm from './components/AuthForm';

export default function App() {
  const { user, loading: authLoading, signup, login, logout } = useAuth();
  const [isLoggedIn, setIsLoggedIn] = useState(null);

  useEffect(() => {
    const checkAuth = () => {
      const token = localStorage.getItem('auth_token');
      setIsLoggedIn(!!token);
    };

    checkAuth();

    // Listen for the custom auth-failure event from the API client
    const handleAuthFailure = () => {
      setIsLoggedIn(false);
    };

    window.addEventListener('auth-failure', handleAuthFailure);
    return () => window.removeEventListener('auth-failure', handleAuthFailure);
  }, []);

  const handleSignup = async (email, password, name) => {
    const result = await signup(email, password, name);
    if (result.success) {
      setIsLoggedIn(true);
    }
    return result;
  };

  const handleLogin = async (email, password) => {
    const result = await login(email, password);
    if (result.success) {
      setIsLoggedIn(true);
    }
    return result;
  };

  const handleLogout = () => {
    logout();
    setIsLoggedIn(false);
  };

  if (isLoggedIn === null) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-slate-50">
        <div className="flex flex-col items-center gap-3">
          <div className="w-10 h-10 border-4 border-indigo-600 border-t-transparent rounded-full animate-spin" />
          <p className="text-slate-500 font-medium">Loading your session...</p>
        </div>
      </div>
    );
  }

  if (!isLoggedIn) {
    return (
      <div className="min-h-screen bg-slate-50">
        <AuthForm 
          onSignup={handleSignup} 
          onLogin={handleLogin} 
          loading={authLoading} 
        />
      </div>
    );
  }

  return (
    <TodoDashboard user={user} onLogout={handleLogout} />
  );
}
