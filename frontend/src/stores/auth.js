import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import apiClient from '@/api/client'

// Token storage key
const TOKEN_KEY = 'auth_token'

export const useAuthStore = defineStore('auth', () => {
    // State - initialize from localStorage if available
    const storedToken = localStorage.getItem(TOKEN_KEY)
    const user = ref(null)
    const token = ref(storedToken)
    const isInitialLoad = ref(!storedToken)

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
            // Persist token to localStorage
            if (token.value) {
                localStorage.setItem(TOKEN_KEY, token.value)
            }
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
            // Persist token to localStorage
            if (token.value) {
                localStorage.setItem(TOKEN_KEY, token.value)
            }
            return { success: true }
        } catch (error) {
            return {
                success: false,
                error: error.response?.data?.detail || 'Login failed',
            }
        }
    }

    async function fetchCurrentUser() {
        // If no token, try to get one from localStorage
        if (!token.value) {
            const storedToken = localStorage.getItem(TOKEN_KEY)
            if (storedToken) {
                token.value = storedToken
            }
        }
        
        // Still no token? User is not authenticated
        if (!token.value) {
            isInitialLoad.value = false
            return
        }
        
        try {
            // Use /me-with-token to get token for WebSocket authentication
            const response = await apiClient.get('/api/auth/me-with-token')
            user.value = response.data
            // Store token for WebSocket use
            token.value = response.data.token || token.value
            // Ensure token is persisted
            if (token.value) {
                localStorage.setItem(TOKEN_KEY, token.value)
            }
        } catch (error) {
            // Token invalid or expired - clear everything
            user.value = null
            token.value = null
            localStorage.removeItem(TOKEN_KEY)
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
            // Clear token from localStorage
            localStorage.removeItem(TOKEN_KEY)
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
