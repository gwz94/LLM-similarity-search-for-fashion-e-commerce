import getBaseUrl from './getBaseUrl';

const API_BASE_URL = getBaseUrl();

export const API_ENDPOINTS = {
  SEARCH: `${API_BASE_URL}/search`,
  HEALTH: `${API_BASE_URL}/health`,
} as const;

export default API_ENDPOINTS;