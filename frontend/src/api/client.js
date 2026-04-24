import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  timeout: 60000,
  headers: { 'Content-Type': 'application/json' }
})

export const verifyClaim = (claim) =>
  api.post('/verify', { claim }).then(r => r.data)

export const searchEvidence = (query, maxResults = 5) =>
  api.post('/search', { query, max_results: maxResults }).then(r => r.data)

export const getExamples = () =>
  api.get('/examples').then(r => r.data)

export const checkHealth = () =>
  api.get('/health').then(r => r.data)

export default api
