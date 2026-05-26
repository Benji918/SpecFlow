  <template>
  <div class="min-h-screen flex items-center justify-center px-4 relative overflow-hidden bg-background">
    <!-- Premium Interactive Brand Background -->
    <div class="absolute inset-0 overflow-hidden pointer-events-none z-0">
      <!-- Grid Overlay (subtle tech grid) -->
      <div class="absolute inset-0 bg-[radial-gradient(rgba(191,245,73,0.06)_1.5px,transparent_1.5px)] bg-[size:32px_32px] opacity-70"></div>
      
      <!-- Glowing ambient blobs (high-energy lime green brand glows) -->
      <div class="absolute top-[-10%] left-[-10%] w-[500px] h-[500px] rounded-full bg-primary/10 blur-[130px] animate-pulse" style="animation-duration: 8s;"></div>
      <div class="absolute bottom-[-10%] right-[-10%] w-[600px] h-[600px] rounded-full bg-primary/5 blur-[160px] animate-pulse" style="animation-duration: 14s;"></div>
      <div class="absolute top-[40%] left-[50%] -translate-x-1/2 w-[300px] h-[300px] rounded-full bg-primary/[0.03] blur-[100px] animate-pulse" style="animation-duration: 11s;"></div>
      
      <!-- Tech line borders for structure -->
      <div class="absolute top-0 left-1/4 w-[1px] h-full bg-white/[0.02]"></div>
      <div class="absolute top-0 right-1/4 w-[1px] h-full bg-white/[0.02]"></div>
      
      <!-- Rotating Watermark Logo (Bottom Right) -->
      <div class="absolute right-[-120px] bottom-[-120px] md:right-[-60px] md:bottom-[-60px] opacity-[0.035] text-primary select-none transform rotate-12 transition-transform duration-1000 hover:rotate-[30deg]">
        <svg width="500" height="500" viewBox="0 0 100 100" fill="none" xmlns="http://www.w3.org/2000/svg">
          <!-- Rotated outer dashed square matching logo concept -->
          <rect x="10" y="10" width="80" height="80" rx="18" stroke="currentColor" stroke-width="2.5" stroke-dasharray="6 4" class="animate-[spin_180s_linear_infinite]" />
          <!-- Inner Lightning Bolt watermark -->
          <path d="M55 15 L20 55 H51 L48 85 L80 40 H49 Z" fill="currentColor" />
        </svg>
      </div>

      <!-- Rotating Watermark Logo (Top Left) -->
      <div class="absolute left-[-150px] top-[15%] opacity-[0.025] text-primary select-none transform -rotate-12 hidden lg:block">
        <svg width="350" height="350" viewBox="0 0 100 100" fill="none" xmlns="http://www.w3.org/2000/svg">
          <rect x="10" y="10" width="80" height="80" rx="18" stroke="currentColor" stroke-width="2.5" stroke-dasharray="4 6" class="animate-[spin_120s_linear_infinite_reverse]" />
          <path d="M55 15 L20 55 H51 L48 85 L80 40 H49 Z" fill="currentColor" />
        </svg>
      </div>
    </div>

    <!-- Content Card -->
    <div class="w-full max-w-md relative z-10 my-8">
      <!-- Logo/Title -->
      <div class="text-center mb-8">
        <RouterLink to="/" class="inline-flex items-center space-x-2 mb-4 hover:opacity-90 transition-opacity">
          <div class="w-12 h-12 bg-primary rounded-lg flex items-center justify-center transform rotate-12 transition-transform hover:rotate-0 shadow-lg shadow-primary/20">
            <Zap :size="28" class="text-black fill-current" />
          </div>
          <span class="text-5xl font-black tracking-tighter">
            Spec<span class="text-primary">Flow</span>
          </span>
        </RouterLink>
        <p class="text-gray-400 text-lg">Welcome back</p>
      </div>

      <!-- Login Card (Upgraded to premium Glassmorphism) -->
      <div class="card-glass border border-white/[0.08] shadow-2xl hover:border-primary/20 transition-all duration-500">
        <form @submit.prevent="handleLogin" class="space-y-5">
          <!-- Credentials Row -->
          <div class="grid grid-cols-1 sm:grid-cols-2 gap-4 items-start">
            <!-- Email Field -->
            <div>
              <label for="email" class="block text-xs font-semibold uppercase tracking-wider text-gray-500 mb-1.5 ml-1">
                Email
              </label>
              <div class="relative">
                <input
                  id="email"
                  v-model="formData.email"
                  type="email"
                  required
                  class="input-field w-full py-2.5 px-4 text-sm font-sans"
                  placeholder="you@example.com"
                />
              </div>
            </div>

            <!-- Password Field -->
            <div>
              <label for="password" class="block text-xs font-semibold uppercase tracking-wider text-gray-500 mb-1.5 ml-1">
                Password
              </label>
              <div class="relative">
                <input
                  id="password"
                  v-model="formData.password"
                  :type="showPassword ? 'text' : 'password'"
                  required
                  class="input-field w-full pr-10 py-2.5 px-4 text-sm font-sans"
                  placeholder="••••••••"
                />
                <button
                  type="button"
                  @click="showPassword = !showPassword"
                  class="absolute right-3 top-1/2 -translate-y-1/2 text-gray-500 hover:text-gray-300 transition-colors"
                  tabindex="-1"
                >
                  <Eye v-if="!showPassword" :size="16" />
                  <EyeOff v-else :size="16" />
                </button>
              </div>
            </div>
          </div>

          <!-- Remember Me & Forgot Password -->
          <div class="flex items-center justify-between">
            <div class="flex items-center">
              <input
                id="remember-me"
                v-model="formData.rememberMe"
                type="checkbox"
                class="h-4 w-4 bg-surface border-gray-700 rounded text-primary focus:ring-primary focus:ring-offset-background cursor-pointer"
              />
              <label for="remember-me" class="ml-2 block text-sm text-gray-400 cursor-pointer select-none">
                Remember me
              </label>
            </div>
            <div class="text-sm">
              <a href="#" class="link" @click.prevent="toast.info('Password reset is not implemented yet.')">
                Forgot password?
              </a>
            </div>
          </div>

          <!-- Error Message -->
          <div v-if="error" class="text-red-500 text-sm">
            {{ error }}
          </div>

          <!-- Submit Button -->
          <button
            type="submit"
            :disabled="loading"
            class="btn-primary w-full hover:shadow-primary/30 transition-all duration-300"
          >
            {{ loading ? 'Logging in...' : 'Log In' }}
          </button>
        </form>

        <!-- Divider -->
        <div class="relative my-8">
          <div class="absolute inset-0 flex items-center">
            <div class="w-full border-t border-gray-800"></div>
          </div>
          <div class="relative flex justify-center text-xs uppercase">
            <span class="px-2 bg-surface text-gray-500 tracking-widest">Or continue with</span>
          </div>
        </div>

        <!-- Social Login -->
        <button
          type="button"
          @click="handleGoogleLogin"
          class="btn-secondary w-full flex items-center justify-center space-x-3 hover:bg-gray-700 transition-all duration-300 group"
        >
          <div class="w-5 h-5 flex items-center justify-center">
            <svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg" class="w-full h-full">
              <path d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" fill="#4285F4"/>
              <path d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-1 .67-2.28 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" fill="#34A853"/>
              <path d="M5.84 14.09c-.22-.67-.35-1.39-.35-2.09s.13-1.42.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l3.66-2.84z" fill="#FBBC05"/>
              <path d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" fill="#EA4335"/>
            </svg>
          </div>
          <span class="group-hover:text-white transition-colors">Continue with Google</span>
        </button>

        <!-- Sign up link -->
        <p class="mt-8 text-center text-sm text-gray-400">
          Don't have an account?
          <RouterLink to="/signup" class="link font-medium">
            Sign up
          </RouterLink>
        </p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useToast } from 'vue-toastification'
import { Eye, EyeOff, Zap } from 'lucide-vue-next'
import MailChecker from 'mailchecker'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()
const toast = useToast()

const formData = ref({
  email: '',
  password: '',
  rememberMe: false,
})

const loading = ref(false)
const error = ref(null)
const showPassword = ref(false)

// Simple sanitization: strip HTML tags
function sanitize(str) {
  if (typeof str !== 'string') return str
  return str.replace(/<[^>]*>?/gm, '').trim()
}

// Email validation using MailChecker
function isValidEmail(email) {
  return MailChecker.isValid(email)
}

onMounted(() => {
  if (route.query.logout === 'success') {
    toast.success('Successfully logged out!')
  }
})

async function handleLogin() {
  // Reset error
  error.value = null

  // Sanitize
  const email = sanitize(formData.value.email)
  const password = formData.value.password // Don't sanitize passwords

  // Basic validation
  if (!isValidEmail(email)) {
    error.value = 'Please enter a valid email address'
    toast.error(error.value)
    return
  }

  // Check for common SQL injection characters in email
  const sqlPattern = /['";\\]/
  if (sqlPattern.test(email)) {
    error.value = 'Invalid characters detected in email'
    toast.error(error.value)
    return
  }

  loading.value = true

  const result = await authStore.login(email, password)

  if (result.success) {
    toast.success('Logged in successfully!')
    // Force a full page reload to ensure the cookie is properly sent with subsequent requests
    window.location.href = '/dashboard'
  } else {
    error.value = result.error
    toast.error(result.error)
  }

  loading.value = false
}

function handleGoogleLogin() {
  if (authStore.isAuthenticated) {
    router.push('/dashboard')
    return
  }
  authStore.loginWithGoogle()
}
</script>
