import axios from 'axios';

const apiClient = axios.create({
  baseURL: 'http://[IP_ADDRESS]',
  headers: {
    'Content-Type': 'application/json',
  },
});

// Interceptor to add JWT token to requests if it exists in localStorage
apiClient.interceptors.request.use((token) => {
  const token = localStorage.getItem('auth_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export default apiClient;
