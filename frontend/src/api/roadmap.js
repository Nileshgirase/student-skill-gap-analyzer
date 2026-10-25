import api from './axios';

export const getRoadmap = async (analysisId) => {
  const response = await api.get(`/analyses/${analysisId}/roadmap`);
  return response.data;
};

export const createRoadmap = async (analysisId) => {
  const response = await api.post(`/analyses/${analysisId}/roadmap`);
  return response.data;
};

export const updateRoadmapItemStatus = async (itemId, status) => {
  const response = await api.patch(`/roadmap-items/${itemId}`, { status });
  return response.data;
};
