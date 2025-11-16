import api from '../lib/api'
import { useAuthStore, User } from '../store/authStore'

export interface LoginCredentials {
  email: string
  password: string
}

export interface RegisterData {
  email: string
  username: string
  password: string
  password_confirm: string
  first_name: string
  last_name: string
  company_name: string
}

export interface LoginResponse {
  user: User
  tokens: {
    access: string
    refresh: string
  }
}

export const authService = {
  login: async (credentials: LoginCredentials): Promise<LoginResponse> => {
    const response = await api.post('/api/auth/login/', credentials)
    return response.data
  },

  register: async (data: RegisterData): Promise<LoginResponse> => {
    const response = await api.post('/api/auth/register/', data)
    return response.data
  },

  logout: async (refreshToken: string): Promise<void> => {
    await api.post('/api/auth/logout/', { refresh_token: refreshToken })
  },

  getProfile: async (): Promise<User> => {
    const response = await api.get('/api/auth/profile/')
    return response.data
  },

  updateProfile: async (data: Partial<User>): Promise<User> => {
    const response = await api.patch('/api/auth/profile/', data)
    return response.data
  },

  changePassword: async (data: {
    old_password: string
    new_password: string
    new_password_confirm: string
  }): Promise<void> => {
    await api.post('/api/auth/change-password/', data)
  },

  getDashboard: async () => {
    const response = await api.get('/api/auth/dashboard/')
    return response.data
  },
}
