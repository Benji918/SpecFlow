import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import apiClient from '@/api/client'

export const useAuthStore = defineStore('auth', () => {
    // State
    const user = ref(null)
    const token = ref(localStorage.getItem('token') || null)

    // Getters
    const isAuthenticated = computed(() => !!token.value && !!user.value)

    // Actions
    async function register(email, password, name) {
        try {
            const response = await apiClient.post('/api/auth/register', {
                email,
                password,
                name,
            })

            token.value = response.data.token
            user.value = response.data.user
            localStorage.setItem('token', response.data.token)

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

            token.value = response.data.token
            user.value = response.data.user
            localStorage.setItem('token', response.data.token)

            return { success: true }
        } catch (error) {
            return {
                success: false,
                error: error.response?.data?.detail || 'Login failed',
            }
        }
    }

    async function fetchCurrentUser() {
        if (!token.value) return

        try {
            const response = await apiClient.get('/api/auth/me')
            user.value = response.data
        } catch (error) {
            // Token might be invalid, logout
            logout()
        }
    }

    function logout() {
        user.value = null
        token.value = null
        localStorage.removeItem('token')
    }

    async function refreshToken() {
        if (!token.value) return

        try {
            const response = await apiClient.post('/api/auth/refresh')
            token.value = response.data.token
            localStorage.setItem('token', response.data.token)
        } catch (error) {
            logout()
        }
    }

    return {
        user,
        token,
        isAuthenticated,
        register,
        login,
        logout,
        fetchCurrentUser,
        refreshToken,
    }
})
