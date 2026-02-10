import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

// Lazy-loaded route components
const Login = () => import('@/views/Login.vue')
const Signup = () => import('@/views/Signup.vue')
const Dashboard = () => import('@/views/Dashboard.vue')
const SpecDetail = () => import('@/views/SpecDetail.vue')
const JourneyView = () => import('@/views/JourneyView.vue')

const routes = [
    {
        path: '/',
        redirect: '/dashboard',
    },
    {
        path: '/login',
        name: 'Login',
        component: Login,
        meta: { requiresAuth: false },
    },
    {
        path: '/signup',
        name: 'Signup',
        component: Signup,
        meta: { requiresAuth: false },
    },
    {
        path: '/dashboard',
        name: 'Dashboard',
        component: Dashboard,
        meta: { requiresAuth: true },
    },
    {
        path: '/spec/:id',
        name: 'SpecDetail',
        component: SpecDetail,
        meta: { requiresAuth: true },
    },
    {
        path: '/journey/:id',
        name: 'JourneyView',
        component: JourneyView,
        meta: { requiresAuth: true },
    },
]

const router = createRouter({
    history: createWebHistory(),
    routes,
})

// Navigation guard
router.beforeEach(async (to, from, next) => {
    const authStore = useAuthStore()

    // Wait for initial load to complete if it hasn't already
    if (authStore.isInitialLoad) {
        await authStore.fetchCurrentUser()
    }

    const requiresAuth = to.meta.requiresAuth

    if (requiresAuth && !authStore.isAuthenticated) {
        // Redirect to login if route requires auth and user is not authenticated
        next('/login')
    } else if (!requiresAuth && authStore.isAuthenticated && (to.path === '/login' || to.path === '/signup')) {
        // Redirect to dashboard if already logged in and trying to access auth pages
        next('/dashboard')
    } else {
        next()
    }
})

export default router
