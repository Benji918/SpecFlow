<template>
  <div class="min-h-screen flex items-center justify-center px-4">
    <div class="w-full max-w-md">
      <!-- Logo/Title -->
      <div class="text-center mb-8">
        <RouterLink to="/" class="inline-flex items-center space-x-2 mb-4 hover:opacity-80 transition-opacity">
          <div class="w-12 h-12 bg-primary rounded-lg flex items-center justify-center transform rotate-12 transition-transform hover:rotate-0">
            <Zap :size="28" class="text-black fill-current" />
          </div>
          <span class="text-5xl font-black tracking-tighter">
            Spec<span class="text-primary">Flow</span>
          </span>
        </RouterLink>
        <p class="text-gray-400 text-lg">Create your account</p>
      </div>

      <!-- Signup Card -->
      <div class="card">
        <form @submit.prevent="handleSignup" class="space-y-4">
          <!-- Name & Email Row -->
          <div class="grid grid-cols-1 sm:grid-cols-2 gap-4 items-start">
            <!-- Name Field -->
            <div>
              <label for="name" class="block text-xs font-semibold uppercase tracking-wider text-gray-500 mb-1.5 ml-1">
                Name
              </label>
              <div class="relative">
                <input
                  id="name"
                  v-model="formData.name"
                  type="text"
                  required
                  class="input-field w-full py-2.5 px-4 text-sm font-sans"
                  placeholder="John Doe"
                />
              </div>
            </div>

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
          </div>

          <!-- Password Row -->
          <div class="grid grid-cols-1 sm:grid-cols-2 gap-4 items-start">
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
                  minlength="8"
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

            <!-- Confirm Password Field -->
            <div>
              <label for="confirmPassword" class="block text-xs font-semibold uppercase tracking-wider text-gray-500 mb-1.5 ml-1">
                Confirm
              </label>
              <div class="relative">
                <input
                  id="confirmPassword"
                  v-model="formData.confirmPassword"
                  :type="showConfirmPassword ? 'text' : 'password'"
                  required
                  class="input-field w-full pr-10 py-2.5 px-4 text-sm font-sans"
                  placeholder="••••••••"
                />
                <button
                  type="button"
                  @click="showConfirmPassword = !showConfirmPassword"
                  class="absolute right-3 top-1/2 -translate-y-1/2 text-gray-500 hover:text-gray-300 transition-colors"
                  tabindex="-1"
                >
                  <Eye v-if="!showConfirmPassword" :size="16" />
                  <EyeOff v-else :size="16" />
                </button>
              </div>
            </div>
          </div>

          <p class="text-[10px] text-gray-500 text-center opacity-60">
            Password must be at least 8 characters
          </p>


          <!-- Error Message -->
          <div v-if="error" class="text-red-500 text-sm">
            {{ error }}
          </div>

          <!-- Submit Button -->
          <button
            type="submit"
            :disabled="loading"
            class="btn-primary w-full"
          >
            {{ loading ? 'Creating account...' : 'Sign Up' }}
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

        <!-- Login link -->
        <p class="mt-8 text-center text-sm text-gray-400">
          Already have an account?
          <RouterLink to="/login" class="link font-medium">
            Log in
          </RouterLink>
        </p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useToast } from 'vue-toastification'
import { Eye, EyeOff, Zap } from 'lucide-vue-next'
import MailChecker from 'mailchecker'

const router = useRouter()
const authStore = useAuthStore()
const toast = useToast()

const formData = ref({
  name: '',
  email: '',
  password: '',
  confirmPassword: '',
})

const loading = ref(false)
const error = ref(null)
const showPassword = ref(false)
const showConfirmPassword = ref(false)

// Simple sanitization: strip HTML tags
function sanitize(str) {
  if (typeof str !== 'string') return str
  return str.replace(/<[^>]*>?/gm, '').trim()
}

// Email validation using MailChecker
function isValidEmail(email) {
  return MailChecker.isValid(email)
}

async function handleSignup() {
  // Reset error
  error.value = null

  // Sanitize
  const name = sanitize(formData.value.name)
  const email = sanitize(formData.value.email)
  const password = formData.value.password // Don't sanitize passwords as they can contain symbols
  const confirmPassword = formData.value.confirmPassword

  // Basic validation
  if (!name || name.length < 2) {
    error.value = 'Name must be at least 2 characters'
    toast.error(error.value)
    return
  }

  if (!isValidEmail(email)) {
    error.value = 'Please enter a valid email address with a valid domain'
    toast.error(error.value)
    return
  }

  if (password.length < 8) {
    error.value = 'Password must be at least 8 characters'
    toast.error(error.value)
    return
  }

  if (password !== confirmPassword) {
    error.value = 'Passwords do not match'
    toast.error(error.value)
    return
  }

  // Check for common SQL injection characters in name/email
  const sqlPattern = /['";\\]/
  if (sqlPattern.test(name) || sqlPattern.test(email)) {
    error.value = 'Invalid characters detected in name or email'
    toast.error(error.value)
    return
  }

  // Security check: Ensure is_admin is not being sent
  if ('is_admin' in formData.value) {
    console.error('Security alert: unauthorized field detected')
    delete formData.value.is_admin
  }


  loading.value = true

  const result = await authStore.register(
    email,
    password,
    name
  )

  if (result.success) {
    toast.success('Account created successfully!')
    router.push('/dashboard')
  } else {
    error.value = result.error
    toast.error(result.error)
  }

  loading.value = false
}

function handleGoogleLogin() {
  toast.info('Google login feature is coming soon!')
}
</script>
