import { useState, useEffect } from 'react';
import { todoApi } from '../api/todoApi';

/**
 * Custom Hook: useTodos
 * 
 * Which hook is this:
 *   - Custom React Hook utilizing useState and useEffect to manage tasks lifecycle.
 * What it does:
 *   - Fetches the user's task list from the backend API, tracks loading and error states,
 *     and provides optimistic/reactive CRUD functions (addTodo, completeTodo, removeTodo, refresh).
 * Why it is here:
 *   - Separates task data fetching, caching, and state synchronization from UI components,
 *     keeping presentation components clean and single-purposed.
 *   - [Roman Urdu]: Custom hook jo tasks ko backend se mangwane, dikhane aur add/complete/delete karne ke liye use hota hai.
 */
export function useTodos() {
  // Hook: useState
  // What it does: Holds the array of todo objects in component memory.
  // Why it is here: Provides reactive task state so adding, completing, or removing items updates the UI instantly.
  // Roman Urdu: Tasks ki list memory me store karta hai taake naya task aane ya delete hone par screen foran update ho jaye.
  const [todos, setTodos] = useState([]);

  // Hook: useState
  // What it does: Tracks whether the initial or refresh fetch request is in progress.
  // Why it is here: Allows the dashboard to render pulse skeleton loaders while tasks are loading.
  // Roman Urdu: Bataata hai ke tasks abhi server se load ho rahe hain ya nahi, taake skeleton placeholder animations dikh sakein.
  const [loading, setLoading] = useState(true);

  // Hook: useState
  // What it does: Stores error messages encountered during API calls (e.g. session expired, network failure).
  // Why it is here: Gives the UI a reactive error string to display actionable sync error alerts.
  // Roman Urdu: Agar backend band ho ya token expire ho jaye toh error message save karta hai taake user ko laal alert dikh sake.
  const [error, setError] = useState(null);

  const fetchTodos = async () => {
    // Only fetch if the user is actually logged in
    if (!localStorage.getItem('auth_token')) {
      setLoading(false);
      return;
    }

    setLoading(true);
    setError(null);
    try {
      const data = await todoApi.getAll();
      setTodos(data);
    } catch (err) {
      const status = err.response?.status;
      const detail = err.response?.data?.detail;
      
      if (status === 401) {
        setError('Session expired. Please log in again.');
      } else if (status === 403) {
        setError('You do not have permission to access these tasks.');
      } else {
        setError(detail || 'Unable to connect to the server. Is the backend running?');
      }
    } finally {
      setLoading(false);
    }
  };

  // Hook: useEffect
  // What it does: Calls fetchTodos() once after the component mounts.
  // Why it is here: Fetching data from an HTTP API is a side effect that cannot run in pure render passes.
  // The empty dependency array [] guarantees this triggers only once when the component is initially mounted.
  // Roman Urdu: Dashboard khulte hi pehli dafa backend se tasks mangwata hai. Empty array [] ki wajah se yeh sirf ek baar mount hone par chalta hai.
  useEffect(() => {
    fetchTodos();
  }, []);

  const addTodo = async (title, priority) => {
    try {
      const newTodo = await todoApi.create({ title, priority });
      setTodos(prev => [...prev, newTodo]);
      return { success: true };
    } catch (err) {
      return { success: false, error: err.response?.data?.detail || 'Failed to add todo' };
    }
  };

  const completeTodo = async (id) => {
    try {
      const updated = await todoApi.complete(id);
      setTodos(prev => prev.map(t => t.id === id ? updated : t));
      return { success: true };
    } catch (err) {
      return { success: false, error: err.response?.data?.detail || 'Failed to complete todo' };
    }
  };

  const removeTodo = async (id) => {
    try {
      await todoApi.delete(id);
      setTodos(prev => prev.filter(t => t.id !== id));
      return { success: true };
    } catch (err) {
      return { success: false, error: err.response?.data?.detail || 'Failed to delete todo' };
    }
  };

  return { todos, loading, error, addTodo, completeTodo, removeTodo, refresh: fetchTodos };
}
