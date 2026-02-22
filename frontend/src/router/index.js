import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

// Eagerly loaded route components (login/signup are high-priority pages)
import LandingPage from '@/views/LandingPage.vue'
import Login from '@/views/Login.vue'
import Signup from '@/views/Signup.vue'

// Lazy-loaded route components (loaded in background)
const Dashboard = () => import('@/views/Dashboard.vue')
const SpecDetail = () => import('@/views/SpecDetail.vue')
const JourneyView = () => import('@/views/JourneyView.vue')
const AdminDashboard = () => import('@/views/AdminDashboard.vue')

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
    {
        path: '/admin',
        name: 'AdminDashboard',
        component: AdminDashboard,
        meta: { requiresAuth: true, requiresAdmin: true },
    },
]

const router = createRouter({
    history: createWebHistory(),
    routes,
})

// Navigation guard - optimized to skip API calls for public routes
router.beforeEach(async (to, from, next) => {
    const authStore = useAuthStore()

    // Public routes that don't need authentication check
    const publicRoutes = ['/login', '/signup', '/']
    const isPublicRoute = publicRoutes.includes(to.path)

    // Fetch current user on initial load when navigating to protected routes
    if (authStore.isInitialLoad && !isPublicRoute) {
        await authStore.fetchCurrentUser()
    }

    const requiresAuth = to.meta.requiresAuth
    const requiresAdmin = to.meta.requiresAdmin

    if (requiresAuth && !authStore.isAuthenticated) {
        // Redirect to login if route requires auth and user is not authenticated
        next('/login')
    } else if (requiresAdmin && !authStore.user?.is_admin) {
        // Redirect to dashboard if user is not an admin
        next('/dashboard')
    } else if (!requiresAuth && authStore.isAuthenticated && (to.path === '/login' || to.path === '/signup')) {
        // Redirect to dashboard if already logged in and trying to access auth pages
        next('/dashboard')
    } else {
        next()
    }
})

export default router
