/// <reference types="vite/client" />

import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5000/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  withCredentials: true,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor for adding auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor for handling common errors
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    if (error.response?.status === 401) {
      // Handle token refresh or redirect to login
      localStorage.removeItem('token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export const authService = {
  login: async (credentials: { email: string; password: string }) => {
    const response = await api.post('/auth/login', credentials);
    return response.data;
  },
  
  logout: async () => {
    const response = await api.post('/auth/logout');
    return response.data;
  },
  
  getCurrentUser: async () => {
    const response = await api.get('/auth/me');
    return response.data;
  },
  
  refreshToken: async () => {
    const response = await api.post('/auth/refresh');
    return response.data;
  },
};

export const googleService = {
  getAuthUrl: async () => {
    const response = await api.get('/auth/google/url');
    return response.data;
  },
  
  handleCallback: async (code: string) => {
    const response = await api.post('/auth/google/callback', { code });
    return response.data;
  },
};

export const driveService = {
  listFiles: async () => {
    const response = await api.get('/drive/files');
    return response.data;
  },
  
  uploadFile: async (file: File) => {
    const formData = new FormData();
    formData.append('file', file);
    const response = await api.post('/drive/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },
};

export const sheetsService = {
  listSheets: async () => {
    const response = await api.get('/sheets/list');
    return response.data;
  },
  
  getSheetData: async (sheetId: string) => {
    const response = await api.get(`/sheets/${sheetId}`);
    return response.data;
  },
};

export default api; 