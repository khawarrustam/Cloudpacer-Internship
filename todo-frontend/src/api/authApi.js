import apiClient from './client';

export const authApi = {
  async signup(data) {
    const response = await apiClient.post('/auth/signup', data);
    return response.data;
  },
  async login(data) {
    const response = await apiClient.post('/auth/login', data);
    return response.data;
  },
};
