import axios from 'axios'

// Create axios instance
const client = axios.create({
    baseURL: import.meta.env.VITE_API_URL || '',
    timeout: 30000,
    withCredentials: true,
    headers: {
        'Content-Type': 'application/json',
    },
})

// Request interceptor
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
            // Only redirect to login if we're not already there
            if (!window.location.pathname.includes('/login') && !window.location.pathname.includes('/signup')) {
                window.location.href = '/login'
            }
        }
        return Promise.reject(error)
    }
)

export default client
