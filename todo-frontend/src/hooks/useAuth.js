import { useState } from 'react';
import { authApi } from '../api/authApi';

export function useAuth() {
  const [user, setUser] = useState(() => {
    const uid = localStorage.getItem('user_uid');
    const email = localStorage.getItem('user_email');
    return uid ? { uid, email: email || '' } : null;
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleAuthResponse = (data) => {
    localStorage.setItem('auth_token', data.token);
    localStorage.setItem('user_uid', data.uid);
    localStorage.setItem('user_email', data.email || '');
    setUser({ uid: data.uid, email: data.email });
    return { success: true };
  };

  const signup = async (email, password, displayName) => {
    setLoading(true);
    setError(null);
    try {
      const data = await authApi.signup({ email, password, display_name: displayName });
      return handleAuthResponse(data);
    } catch (err) {
      const msg = err.response?.data?.detail || 'Signup failed';
      setError(msg);
      return { success: false, error: msg };
    } finally {
      setLoading(false);
    }
  };

  const login = async (email, password) => {
    setLoading(true);
    setError(null);
    try {
      const data = await authApi.login({ email, password });
      return handleAuthResponse(data);
    } catch (err) {
      const msg = err.response?.data?.detail || 'Login failed. Please check your credentials.';
      setError(msg);
      return { success: false, error: msg };
    } finally {
      setLoading(false);
    }
  };

  const logout = () => {
    localStorage.removeItem('auth_token');
    localStorage.removeItem('user_uid');
    localStorage.removeItem('user_email');
    setUser(null);
  };

  return { user, loading, error, signup, login, logout };
}
