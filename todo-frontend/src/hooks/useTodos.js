import { useState, useEffect } from 'react';
import { todoApi } from '../api/todoApi';

export function useTodos() {
  const [todos, setTodos] = useState([]);
  const [loading, setLoading] = useState(true);
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
