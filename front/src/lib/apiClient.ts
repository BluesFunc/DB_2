import axios, { AxiosInstance } from 'axios'
import { API_BASE_URL } from './api'

class ApiClient {
  private client: AxiosInstance

  constructor() {
    this.client = axios.create({
      baseURL: API_BASE_URL,
      headers: {
        'Content-Type': 'application/json',
      },
    })

    // Add interceptor to include auth token
    this.client.interceptors.request.use((config) => {
      const token = typeof window !== 'undefined' ? localStorage.getItem('access_token') : null
      if (token) {
        config.headers.Authorization = `Bearer ${token}`
      }
      return config
    })

    // Handle token refresh on 401
    this.client.interceptors.response.use(
      (response) => response,
      async (error) => {
        const originalRequest = error.config
        if (error.response?.status === 401 && !originalRequest._retry) {
          originalRequest._retry = true
          try {
            const refreshToken = localStorage.getItem('refresh_token')
            if (refreshToken) {
              const response = await this.client.post('/v1/auth/refresh', {
                refresh_token: refreshToken,
              })
              const { access_token } = response.data
              localStorage.setItem('access_token', access_token)
              originalRequest.headers.Authorization = `Bearer ${access_token}`
              return this.client(originalRequest)
            }
          } catch (err) {
            localStorage.removeItem('access_token')
            localStorage.removeItem('refresh_token')
            window.location.href = '/login'
          }
        }
        return Promise.reject(error)
      }
    )
  }

  get<T>(url: string, config?: any) {
    return this.client.get<T>(url, config)
  }

  post<T>(url: string, data?: any, config?: any) {
    return this.client.post<T>(url, data, config)
  }

  put<T>(url: string, data?: any, config?: any) {
    return this.client.put<T>(url, data, config)
  }

  delete<T>(url: string, config?: any) {
    return this.client.delete<T>(url, config)
  }
}

export const apiClient = new ApiClient()
