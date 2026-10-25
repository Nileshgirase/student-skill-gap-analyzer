import api from './axios';

export const listAnalyses = async () => {
  const response = await api.get('/analyses');
  return response.data;
};

export const createAnalysis = async (payload) => {
  const response = await api.post('/analyses', payload);
  return response.data;
};

export const getAnalysis = async (analysisId) => {
  const response = await api.get(`/analyses/${analysisId}`);
  return response.data;
};

export const deleteAnalysis = async (analysisId) => {
  const response = await api.delete(`/analyses/${analysisId}`);
  return response.data;
};

export const searchJobs = async (analysisId) => {
  const response = await api.post(`/analyses/${analysisId}/search-jobs`);
  return response.data;
};

export const runGapAnalysis = async (analysisId) => {
  const response = await api.post(`/analyses/${analysisId}/run-gap-analysis`);
  return response.data;
};

export const updateStudentSkills = async (analysisId, studentSkills) => {
  const response = await api.post(`/analyses/${analysisId}/student-skills`, {
    student_skills: studentSkills,
  });
  return response.data;
};
