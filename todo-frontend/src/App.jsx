import React, { useState, useEffect } from 'react';
import { useAuth } from './hooks/useAuth';
import TodoDashboard from './components/TodoDashboard';
import AuthForm from './components/AuthForm';

export default function App() {
  // ============================================================================
  // HOOKS USED IN THIS COMPONENT:
  // 1. useAuth (Custom Hook)
  // 2. useState (Built-in React Hook)
  // 3. useEffect (Built-in React Hook)
  // [Roman Urdu]: App component auth verify karta hai aur sahi view render karta hai.
  // ============================================================================

  // Hook: useAuth (Custom Hook)
  // What it does: Supplies authentication state (user, loading status) and auth actions (signup, login, logout).
  // Why it is here: Abstracts away token persistence and backend API calls, decoupling auth logic from view rendering.
  // Roman Urdu: Hamara custom hook jo user ka login status, loading state, aur login/logout functions provide karta hai.
  const { user, loading: authLoading, signup, login, logout } = useAuth();

  // Hook: useState
  // What it does: Tracks tri-state authentication status:
  //               - null  : Initial loading/verification state (checking storage)
  //               - true  : User is logged in
  //               - false : User is logged out
  // Why it is here: Prevents UI flickering by showing a loading screen until the session verification completes.
  // Roman Urdu: Yeh track karta hai ke user logged in hai ya nahi. Shuru me null hota hai taake jab tak token check ho raha hai, tab tak loading spinner dikhe.
  const [isLoggedIn, setIsLoggedIn] = useState(null);

  // Hook: useEffect
  // What it does: 
  //   1. Reads 'auth_token' from localStorage to restore existing session on page load.
  //   2. Subscribes to the window's 'auth-failure' event (dispatched if a 401 occurs in axios interceptor).
  //   3. Cleans up the event listener when App unmounts.
  // Why it is here: Session verification and browser event subscriptions are side effects that cannot run in
  // pure rendering logic. The empty dependency array [] ensures this executes exactly once upon mount.
  // Roman Urdu: Component load hote hi localStorage se auth_token check karta hai aur global 401 unauthorized event sunta hai. Empty array [] ka matlab yeh sirf pehli dafa mount hone par chalega.
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
      <div className="flex min-h-screen items-center justify-center bg-[var(--bg-main)]">
        <div className="flex flex-col items-center gap-4">
          <div className="relative flex h-12 w-12 items-center justify-center rounded-2xl bg-[var(--text-primary)] text-white shadow-lg">
            <div className="h-5 w-5 animate-spin rounded-full border-2 border-white/30 border-t-white" />
          </div>
          <p className="text-xs font-bold text-[var(--text-secondary)]">Opening your workspace...</p>
        </div>
      </div>
    );
  }

  if (!isLoggedIn) {
    return (
      <div className="min-h-screen bg-[var(--bg-main)]">
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
