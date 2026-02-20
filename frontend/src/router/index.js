import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

// Lazy-loaded route components
const LandingPage = () => import('@/views/LandingPage.vue')
const Login = () => import('@/views/Login.vue')
const Signup = () => import('@/views/Signup.vue')
const Dashboard = () => import('@/views/Dashboard.vue')
const SpecDetail = () => import('@/views/SpecDetail.vue')
const JourneyView = () => import('@/views/JourneyView.vue')

const routes = [
    {
        path: '/',
        name: 'Landing',
        component: LandingPage,
        meta: { requiresAuth: false },
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

    // Only fetch current user on first load (not after logout)
    // The isInitialLoad flag is reset only when explicitly needed
    if (authStore.isInitialLoad && authStore.token) {
        await authStore.fetchCurrentUser()
    } else if (authStore.isInitialLoad && !authStore.token) {
        // If we have no token and are still in initial load, mark as done
        authStore.isInitialLoad = false
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
