import axios from "axios";

const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

const apiClient = axios.create({
  baseURL: API_URL,
});

apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem("access_token");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export const authAPI = {
  register: (data: any) => apiClient.post("/api/auth/register", data),
  login: (username: string, password: string) =>
    apiClient.post("/api/auth/token", {
      username,
      password,
      grant_type: "password",
    }),
  getCurrentUser: () => apiClient.get("/api/auth/me"),
};

export const articlesAPI = {
  list: (skip?: number, limit?: number) =>
    apiClient.get("/api/articles/", { params: { skip, limit } }),
  get: (id: number) => apiClient.get(`/api/articles/${id}`),
  upload: (file: File, categoryId?: number) => {
    const formData = new FormData();
    formData.append("file", file);
    if (categoryId) formData.append("category_id", categoryId.toString());
    return apiClient.post("/api/articles/upload", formData);
  },
  update: (id: number, data: any) =>
    apiClient.put(`/api/articles/${id}`, data),
  delete: (id: number) => apiClient.delete(`/api/articles/${id}`),
};

export const recommendationsAPI = {
  get: (limit?: number) =>
    apiClient.get("/api/recommendations/", { params: { limit } }),
};

export default apiClient;
