import axios from 'axios';
import { readToken } from '../features/auth/authStorage';

let unauthorizedHandler = null;

// English: main.jsx gives this file the Redux session-expiry action.
// Roman Urdu: main.jsx is file ko Redux session-expiry action deta hai.
export function setUnauthorizedHandler(handler) {
  unauthorizedHandler = handler;
}

const apiUrl = import.meta.env.VITE_API_URL;

if (!apiUrl) {
  throw new Error('Missing VITE_API_URL in frontend/.env');
}

const apiClient = axios.create({
  baseURL: apiUrl,
  headers: {
    'Content-Type': 'application/json',
  },
});

apiClient.interceptors.request.use((config) => {
  // English: Attach the saved token before every protected API request.
  // Roman Urdu: Har protected API request se pehle saved token lagao.
  const token = readToken();
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    // English: Tell Redux when the backend rejects an expired session.
    // Roman Urdu: Backend session reject kare to Redux ko batao.
    if (error.response?.status === 401) {
      unauthorizedHandler?.();
    }
    return Promise.reject(error);
  },
);

export default apiClient;
