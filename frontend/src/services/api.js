import axios from 'axios'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'https://biu-traffic-api.onrender.com/api/',
})

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config
    if (error.response && error.response.status === 401 && !originalRequest._retry) {
      const refreshToken = localStorage.getItem('refresh_token')
      if (refreshToken && !originalRequest.url?.includes('auth/login') && !originalRequest.url?.includes('auth/token/refresh')) {
        originalRequest._retry = true
        try {
          const authBase = import.meta.env.VITE_API_URL || 'https://biu-traffic-api.onrender.com/api/'
          const res = await axios.post(`${authBase.replace(/\/+$/, '')}/auth/token/refresh/`, { refresh: refreshToken })
          if (res.data?.access) {
            localStorage.setItem('access_token', res.data.access)
            originalRequest.headers.Authorization = `Bearer ${res.data.access}`
            return api(originalRequest)
          }
        } catch {
          localStorage.removeItem('access_token')
          localStorage.removeItem('refresh_token')
          localStorage.removeItem('biu_user')
        }
      } else {
        localStorage.removeItem('access_token')
        localStorage.removeItem('refresh_token')
        localStorage.removeItem('biu_user')
      }
    }
    return Promise.reject(error)
  }
)

export const trafficService = {
  // AI Inference Scan API
  scanImage: (formData, onProgress) =>
    api.post('scan/image/', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
      onUploadProgress: onProgress,
    }),

  scanVideo: (formData, onProgress) =>
    api.post('scan/video/', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
      onUploadProgress: onProgress,
    }),

  getViolations: (page = 1, pageSize = 12) =>
    api.get(`violations/?page=${page}&page_size=${pageSize}`),

  // Live video stream & legacy endpoints
  streamUrl: () => `${api.defaults.baseURL}traffic/stream/`,
  stopStream: () => api.post('traffic/stream/stop/'),
  liveViolations: () => api.get('traffic/violations/'),
  liveStats: () => api.get('traffic/stats/'),

  // Backwards compatibility aliases
  violations: () => api.get('traffic/violations/'),
  stats: () => api.get('traffic/stats/'),
}

export const trafficApi = trafficService

export default api
