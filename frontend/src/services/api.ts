import axios from 'axios';
import type { LearnerLevel } from '../context/AuthContext';

const api = axios.create({
  baseURL: '/api',
});

// Attach JWT token to every request if available
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Handle 401 responses globally
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token');
      localStorage.removeItem('username');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// ── Auth API ───────────────────────────────────────
export async function registerUser(username: string, password: string) {
  const res = await api.post('register', { username, password });
  return res.data;
}

export async function loginUser(username: string, password: string) {
  const formData = new URLSearchParams();
  formData.append('username', username);
  formData.append('password', password);
  const res = await api.post('token', formData, {
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
  });
  return res.data;
}

// ── Document API ───────────────────────────────────
export async function uploadDocument(file: File, category: string = 'LECTURE_NOTES') {
  const formData = new FormData();
  formData.append('file', file);
  formData.append('category', category);
  const res = await api.post('documents/upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
  return res.data;
}

export async function listDocuments() {
  const res = await api.get('documents/');
  return res.data;
}

export async function deleteDocument(documentId: number) {
  const res = await api.delete(`documents/${documentId}`);
  return res.data;
}

// ── Revision API ───────────────────────────────────
export async function generateScenario(
  documentId: number,
  geminiApiKey: string,
  learnerLevel: LearnerLevel = 'undergraduate'
) {
  const res = await api.post('revision/generate', {
    document_id: documentId,
    gemini_api_key: geminiApiKey,
    learner_level: learnerLevel,
  });
  return res.data;
}

export async function getFeedback(
  documentId: number,
  scenario: string,
  userAnswer: string,
  geminiApiKey: string,
  learnerLevel: LearnerLevel = 'undergraduate'
) {
  const res = await api.post('revision/feedback', {
    document_id: documentId,
    scenario,
    user_answer: userAnswer,
    gemini_api_key: geminiApiKey,
    learner_level: learnerLevel,
  });
  return res.data;
}

export default api;
