import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import apiClient from '@/api/client'

export const useAuthStore = defineStore('auth', () => {
    // State
    const user = ref(null)
    const token = ref(null)
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

            const data = response.data
            user.value = data?.user ?? data
            token.value = data?.token ?? null
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

            const data = response.data
            user.value = data?.user ?? data
            token.value = data?.token ?? null
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
            // Use /me-with-token to get token for WebSocket authentication
            const response = await apiClient.get('/api/auth/me-with-token')
            user.value = response.data
            // Store token for WebSocket use
            token.value = response.data.token || null
        } catch (error) {
            user.value = null
            token.value = null
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
            token.value = null
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
        token,
        isInitialLoad,
        isAuthenticated,
        register,
        login,
        logout,
        fetchCurrentUser,
        refreshToken,
    }
})
