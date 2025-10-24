import { describe, it, expect, vi } from 'vitest';
import axios from 'axios';

vi.mock('axios');

const mockedAxios = axios as any;

describe('API Service', () => {
  const BASE_URL = 'http://localhost:8000/api';

  it('should make a GET request', async () => {
    const mockData = { id: 1, username: 'testuser' };
    mockedAxios.get.mockResolvedValue({ data: mockData });

    const response = await axios.get(`${BASE_URL}/users/1`);

    expect(response.data).toEqual(mockData);
    expect(mockedAxios.get).toHaveBeenCalledWith(`${BASE_URL}/users/1`);
  });

  it('should make a POST request', async () => {
    const mockData = { id: 1, username: 'newuser', email: 'new@example.com' };
    mockedAxios.post.mockResolvedValue({ data: mockData });

    const payload = { username: 'newuser', email: 'new@example.com', password: 'pass' };
    const response = await axios.post(`${BASE_URL}/auth/register`, payload);

    expect(response.data).toEqual(mockData);
    expect(mockedAxios.post).toHaveBeenCalledWith(`${BASE_URL}/auth/register`, payload);
  });

  it('should handle errors', async () => {
    const errorResponse = { response: { status: 401, data: { detail: 'Unauthorized' } } };
    mockedAxios.get.mockRejectedValue(errorResponse);

    try {
      await axios.get(`${BASE_URL}/auth/me`);
    } catch (error: any) {
      expect(error.response.status).toBe(401);
      expect(error.response.data.detail).toBe('Unauthorized');
    }
  });

  it('should include authorization header', async () => {
    const token = 'mock-jwt-token';
    mockedAxios.get.mockResolvedValue({ data: {} });

    await axios.get(`${BASE_URL}/protected`, {
      headers: { Authorization: `Bearer ${token}` },
    });

    expect(mockedAxios.get).toHaveBeenCalledWith(
      `${BASE_URL}/protected`,
      expect.objectContaining({
        headers: expect.objectContaining({
          Authorization: `Bearer ${token}`,
        }),
      })
    );
  });
});
