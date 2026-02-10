import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import apiClient from '@/api/client'

export const useAuthStore = defineStore('auth', () => {
    // State
    const user = ref(null)
    const isInitialLoad = ref(true)

    // Getters
    const isAuthenticated = computed(() => !!user.value)

    // Actions
    async function register(email, password, name) {
        try {
            const response = await apiClient.post('/api/auth/register', {
                email,
                password,
                name,
            })

            user.value = response.data
            return { success: true }
        } catch (error) {
            return {
                success: false,
                error: error.response?.data?.detail || 'Registration failed',
            }
        }
    }

    async function login(email, password) {
        try {
            const response = await apiClient.post('/api/auth/login', {
                email,
                password,
            })

            user.value = response.data
            return { success: true }
        } catch (error) {
            return {
                success: false,
                error: error.response?.data?.detail || 'Login failed',
            }
        }
    }

    async function fetchCurrentUser() {
        try {
            const response = await apiClient.get('/api/auth/me')
            user.value = response.data
        } catch (error) {
            user.value = null
        } finally {
            isInitialLoad.value = false
        }
    }

    async function logout() {
        try {
            await apiClient.post('/api/auth/logout')
        } catch (error) {
            console.error('Logout failed', error)
        } finally {
            user.value = null
            window.location.href = '/login'
        }
    }

    async function refreshToken() {
        try {
            await apiClient.post('/api/auth/refresh')
        } catch (error) {
            logout()
        }
    }

    return {
        user,
        isInitialLoad,
        isAuthenticated,
        register,
        login,
        logout,
        fetchCurrentUser,
        refreshToken,
    }
})
