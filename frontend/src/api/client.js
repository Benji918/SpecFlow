import axios from 'axios'

// Create axios instance
const client = axios.create({
    baseURL: import.meta.env.VITE_API_URL || '',
    timeout: 120000,
    withCredentials: true,
    headers: {
        'Content-Type': 'application/json',
    },
})

// Request interceptor - cookies are sent automatically with withCredentials: true
// No need to manually add Authorization header
client.interceptors.request.use(
    (config) => {
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
