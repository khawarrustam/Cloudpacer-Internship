import apiClient from './client';

export const authApi = {
  // English: API files only send requests and return response data.
  // Roman Urdu: API files sirf request bhejti aur response data wapas deti hain.
  async signup(data) {
    const response = await apiClient.post('/auth/signup', data);
    return response.data;
  },
  async login(data) {
    const response = await apiClient.post('/auth/login', data);
    return response.data;
  },
};
