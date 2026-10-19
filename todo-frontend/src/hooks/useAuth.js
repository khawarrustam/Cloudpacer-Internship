import { useState } from 'react';
import { authApi } from '../api/authApi';

/**
 * Custom Hook: useAuth
 * 
 * Which hook is this:
 *   - Custom React Hook combining multiple useState instances to encapsulate authentication.
 * What it does:
 *   - Manages user identity state, loading status, error messages, and exposes
 *     signup, login, and logout methods synchronized with localStorage and backend auth APIs.
 * Why it is here:
 *   - Centralizes authentication logic in a single reusable place instead of duplicating
 *     token management and API calling logic across components.
 *   - [Roman Urdu]: Custom hook jo authentication (signup, login, logout) ka saara logic ek jagah bandh kar rakhta hai.
 */
export function useAuth() {
  // Hook: useState (with lazy initializer function)
  // What it does: Reads 'user_uid' and 'user_email' from localStorage once to populate the initial user object.
  // Why it is here: Lazy initialization (() => {...}) ensures localStorage is accessed ONLY on the initial mount,
  // avoiding slow storage reads on subsequent re-renders.
  // Roman Urdu: localStorage se user ka UID aur email nikaal kar state banata hai. Lazy function () => {...} is liye lagaya taake har render par storage dobara read na ho aur performance fast rahe.
  const [user, setUser] = useState(() => {
    const uid = localStorage.getItem('user_uid');
    const email = localStorage.getItem('user_email');
    return uid ? { uid, email: email || '' } : null;
  });

  // Hook: useState
  // What it does: Indicates whether an async authentication API request (login/signup) is currently executing.
  // Why it is here: Provides UI components a reactive flag to display loading spinners and disable buttons.
  // Roman Urdu: Yeh bataata hai ke login ya signup API call chal rahi hai ya nahi, taake spinner dikh sake aur double clicks block hon.
  const [loading, setLoading] = useState(false);

  // Hook: useState
  // What it does: Stores error response messages from failed authentication calls.
  // Why it is here: Enables consuming components to show user-facing error banners when requests fail.
  // Roman Urdu: Agar password ghalat ho ya network down ho toh backend ka error message save karta hai taake user ko dikha sakein.
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
