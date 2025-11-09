import axios from "axios";

const API_URL = (import.meta as any).env.VITE_API_URL || "http://localhost:8000";

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

export interface UserRegistration {
  username: string;
  email: string;
  password: string;
  first_name?: string;
  last_name?: string;
  institution?: string;
  field_of_study?: string;
}

export interface LoginResponse {
  access_token: string;
  token_type: string;
}

export const authAPI = {
  register: (data: UserRegistration) =>
    apiClient.post("/api/auth/register", data),
  login: (username: string, password: string) => {
    const formData = new URLSearchParams();
    formData.append("username", username);
    formData.append("password", password);
    return apiClient.post<LoginResponse>("/api/auth/token", formData, {
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
    });
  },
  getCurrentUser: () => apiClient.get("/api/auth/me"),
};

export interface ArticleFilters {
  skip?: number;
  limit?: number;
  category_id?: number;
  keyword?: string;
  start_year?: number;
  end_year?: number;
  start_date?: string;
  end_date?: string;
}

export const articlesAPI = {
  list: (filters?: ArticleFilters) =>
    apiClient.get("/api/articles/", { params: filters }),
  get: (id: number) => apiClient.get(`/api/articles/${id}`),
  upload: (file: File, categoryId?: number) => {
    const formData = new FormData();
    formData.append("file", file);
    if (categoryId) formData.append("category_id", categoryId.toString());
    return apiClient.post("/api/articles/upload", formData, {
      headers: { "Content-Type": "multipart/form-data" },
    });
  },
  uploadFromUrl: (url: string, categoryId?: number) => {
    return apiClient.post("/api/articles/upload-url", {
      url,
      category_id: categoryId,
    });
  },
  update: (id: number, data: any) =>
    apiClient.put(`/api/articles/${id}`, data),
  delete: (id: number) => apiClient.delete(`/api/articles/${id}`),
  classify: (id: number) => apiClient.get(`/api/articles/${id}/classify`),
  getBibliography: (id: number, format: "apa" | "mla" | "chicago" | "bibtex" | "ris" = "apa") =>
    apiClient.get(`/api/articles/${id}/bibliography/${format}`),
};

export const libraryAPI = {
  list: (skip?: number, limit?: number, status?: string) =>
    apiClient.get("/api/users/library/", {
      params: { skip, limit, status },
    }),
  add: (articleId: number) =>
    apiClient.post(`/api/users/library/${articleId}`, {}),
  remove: (articleId: number) =>
    apiClient.delete(`/api/users/library/${articleId}`),
  update: (articleId: number, status?: string, rating?: number, notes?: string) =>
    apiClient.put(`/api/users/library/${articleId}`, {
      status,
      rating,
      notes,
    }),
  getStats: () => apiClient.get("/api/users/library/stats"),
};

export const usersAPI = {
  getProfile: (userId: number) => apiClient.get(`/api/users/${userId}`),
  updateProfile: (data: any) => apiClient.put("/api/users/profile", data),
};

export const recommendationsAPI = {
  get: (limit?: number) =>
    apiClient.get("/api/recommendations/", { params: { limit } }),
};

export interface AnnotationCreate {
  article_id: number;
  highlighted_text: string;
  page_number?: number;
  position_data?: any;
  color?: "yellow" | "green" | "blue" | "red" | "purple";
  note?: string;
  tags?: string[];
}

export interface AnnotationUpdate {
  highlighted_text?: string;
  page_number?: number;
  position_data?: any;
  color?: "yellow" | "green" | "blue" | "red" | "purple";
  note?: string;
  tags?: string[];
}

export const annotationsAPI = {
  create: (data: AnnotationCreate) =>
    apiClient.post("/api/annotations/", data),
  getByArticle: (articleId: number, color?: string, tag?: string) =>
    apiClient.get(`/api/annotations/article/${articleId}`, {
      params: { color, tag },
    }),
  getMyAnnotations: (skip?: number, limit?: number, articleId?: number, color?: string) =>
    apiClient.get("/api/annotations/my-annotations", {
      params: { skip, limit, article_id: articleId, color },
    }),
  get: (annotationId: number) =>
    apiClient.get(`/api/annotations/${annotationId}`),
  update: (annotationId: number, data: AnnotationUpdate) =>
    apiClient.put(`/api/annotations/${annotationId}`, data),
  delete: (annotationId: number) =>
    apiClient.delete(`/api/annotations/${annotationId}`),
  getStats: (articleId: number) =>
    apiClient.get(`/api/annotations/article/${articleId}/stats`),
};

export default apiClient;
