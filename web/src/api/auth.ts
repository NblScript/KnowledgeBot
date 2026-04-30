import apiClient from './client'

export interface LoginRequest {
  username: string
  password: string
}

export interface RegisterRequest {
  username: string
  email: string
  password: string
}

export interface User {
  id: number
  username: string
  email: string
  created_at: string
}

export interface LoginResponse {
  access_token: string
  token_type: string
  user: User
}

export const authApi = {
  login(data: LoginRequest) {
    const formData = new FormData()
    formData.append('username', data.username)
    formData.append('password', data.password)
    return apiClient.post<LoginResponse>('/auth/login', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
  },

  register(data: RegisterRequest) {
    return apiClient.post<{ message: string; user: User }>('/auth/register', data)
  },

  getCurrentUser() {
    return apiClient.get<User>('/auth/me')
  },

  updateProfile(data: Partial<{ email: string; password: string }>) {
    return apiClient.put<User>('/auth/profile', data)
  },
}