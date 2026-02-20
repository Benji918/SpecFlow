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
        // Only add token if auth store is initialized and has a token
        try {
            const authStore = useAuthStore()
            if (authStore.token) {
                config.headers.Authorization = `Bearer ${authStore.token}`
            }
        } catch (e) {
            // Auth store not yet initialized, skip adding token
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
