import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { authApi, type User } from '@/api/auth'

export const useAuthStore = defineStore('auth', () => {
  const token = ref<string | null>(localStorage.getItem('token'))
  const user = ref<User | null>(null)

  const isAuthenticated = computed(() => !!token.value)

  async function login(username: string, password: string) {
    const response = await authApi.login({ username, password })
    token.value = response.data.access_token
    user.value = response.data.user
    localStorage.setItem('token', response.data.access_token)
    return response.data
  }

  async function register(username: string, email: string, password: string) {
    const response = await authApi.register({ username, email, password })
    return response.data
  }

  async function fetchUser() {
    if (!token.value) return
    try {
      const response = await authApi.getCurrentUser()
      user.value = response.data
    } catch (error) {
      logout()
      throw error
    }
  }

  function logout() {
    token.value = null
    user.value = null
    localStorage.removeItem('token')
  }

  async function updateProfile(data: { email?: string; password?: string }) {
    const response = await authApi.updateProfile(data)
    user.value = response.data
    return response.data
  }

  return {
    token,
    user,
    isAuthenticated,
    login,
    register,
    fetchUser,
    logout,
    updateProfile,
  }
})
