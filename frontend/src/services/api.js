import axios from 'axios';

// API base URL configuration
// In production (common Docker), API is served from the same origin at /api/v1
// In development, it connects to the backend server directly
const API_BASE_URL = process.env.REACT_APP_BACKEND_URL || 
                    (process.env.NODE_ENV === 'production' ? '/api/v1' : 'http://localhost:8000/api/v1');

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const uploadPDF = async (file) => {
  const formData = new FormData();
  formData.append('file', file);
  
  const response = await api.post('/upload', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
  
  return response.data;
};

export const askQuestion = async (query, docId = null) => {
  const payload = { query };
  if (docId) {
    payload.doc_id = docId;
  }
  
  const response = await api.post('/ask', payload);
  return response.data;
};

export const searchDocuments = async (query, docId = null) => {
  const payload = { query };
  if (docId) {
    payload.doc_id = docId;
  }
  
  const response = await api.post('/search', payload);
  return response.data;
};

export const clearDocuments = async () => {
  const response = await api.delete('/clear');
  return response.data;
};

export const checkHealth = async () => {
  const response = await api.get('/health');
  return response.data;
};

export default api;
