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

export const uploadDocument = async (file) => {
  const formData = new FormData();
  formData.append('file', file);
  
  const response = await api.post('/upload', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
  
  return response.data;
};

// Legacy function for backward compatibility
export const uploadPDF = uploadDocument;

export const getSupportedFormats = async () => {
  const response = await api.get('/supported-formats');
  return response.data;
};

export const getDocumentContent = async (docId) => {
  const response = await api.get(`/document/${docId}/content`);
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

// LLM Model Management
export const getAvailableProviders = async () => {
  const response = await api.get('/llm/providers');
  return response.data;
};

export const switchLLMProvider = async (provider, modelName = null) => {
  const params = new URLSearchParams({ provider });
  if (modelName) {
    params.append('model_name', modelName);
  }
  
  const response = await api.post(`/llm/switch?${params.toString()}`);
  return response.data;
};

// Individual provider tests
export const testMistralConnection = async () => {
  const response = await api.post('/mistral/test');
  return response.data;
};

export const testGeminiConnection = async () => {
  const response = await api.post('/gemini/test');
  return response.data;
};

// Session Management
export const createSession = async (documentId, documentName, documentFilename) => {
  const response = await api.post('/sessions', {
    document_id: documentId,
    document_name: documentName,
    document_filename: documentFilename
  });
  return response.data;
};

export const getSessions = async (limit = 50, offset = 0) => {
  const response = await api.get('/sessions', {
    params: { limit, offset }
  });
  return response.data;
};

export const getSessionDetails = async (sessionId) => {
  const response = await api.get(`/sessions/${sessionId}`);
  return response.data;
};

export const deleteSession = async (sessionId) => {
  const response = await api.delete(`/sessions/${sessionId}`);
  return response.data;
};

export const askQuestionInSession = async (sessionId, query) => {
  const response = await api.post(`/sessions/${sessionId}/ask`, { query });
  return response.data;
};

export default api;
