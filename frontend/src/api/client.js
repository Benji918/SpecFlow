import axios from 'axios'
import { useAuthStore } from '@/stores/auth'

// Create axios instance
const client = axios.create({
    baseURL: import.meta.env.VITE_API_URL || '',
    timeout: 30000,
    withCredentials: true,
    headers: {
        'Content-Type': 'application/json',
    },
})

// Request interceptor - add auth token to requests
client.interceptors.request.use(
    (config) => {
        // Try to get token from auth store, fallback to localStorage
        let authToken = null
        try {
            const authStore = useAuthStore()
            authToken = authStore.token
        } catch (e) {
            // Auth store not yet initialized
        }
        
        // Fallback to localStorage if no token in store
        if (!authToken) {
            authToken = localStorage.getItem('auth_token')
        }
        
        if (authToken) {
            config.headers.Authorization = `Bearer ${authToken}`
        }
        return config
    },
    (error) => {
        return Promise.reject(error)
    }
)

// Response interceptor - handle errors
client.interceptors.response.use(
    (response) => response,
    (error) => {
        if (error.response?.status === 401) {
            // Only redirect to login if we're not already there and not on an auth endpoint
            const isAuthEndpoint = error.config?.url?.includes('/auth/')
            const isOnAuthPage = window.location.pathname.includes('/login') || window.location.pathname.includes('/signup')
            
            if (!isAuthEndpoint && !isOnAuthPage) {
                window.location.href = '/login'
            }
        }
        return Promise.reject(error)
    }
)

export default client
