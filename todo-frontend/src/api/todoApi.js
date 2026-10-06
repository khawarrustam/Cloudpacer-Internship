import apiClient from './client';

export const todoApi = {
  async getAll() {
    const response = await apiClient.get('/todos');
    return response.data;
  },
  async create(data) {
    const response = await apiClient.post('/todos', data);
    return response.data;
  },
  async complete(id) {
    const response = await apiClient.patch(`/todos/${id}/complete`);
    return response.data;
  },
  async delete(id) {
    await apiClient.delete(`/todos/${id}`);
    return true;
  },
};
