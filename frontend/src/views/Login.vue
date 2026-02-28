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
        <p class="text-gray-400 text-lg">Welcome back</p>
      </div>

      <!-- Login Card -->
      <div class="card">
        <form @submit.prevent="handleLogin" class="space-y-6">
          <!-- Email Field -->
          <div>
            <label for="email" class="block text-sm font-medium mb-2">
              Email
            </label>
            <input
              id="email"
              v-model="formData.email"
              type="email"
              required
              class="input-field w-full"
              placeholder="you@example.com"
            />
          </div>

          <!-- Password Field -->
          <div>
            <label for="password" class="block text-sm font-medium mb-2">
              Password
            </label>
            <div class="relative">
              <input
                id="password"
                v-model="formData.password"
                :type="showPassword ? 'text' : 'password'"
                required
                class="input-field w-full pr-10"
                placeholder="••••••••"
              />
              <button
                type="button"
                @click="showPassword = !showPassword"
                class="absolute right-3 top-1/2 -translate-y-1/2 text-gray-500 hover:text-gray-300 transition-colors"
                tabindex="-1"
              >
                <Eye v-if="!showPassword" :size="18" />
                <EyeOff v-else :size="18" />
              </button>
            </div>
          </div>

          <!-- Remember Me & Forgot Password -->
          <div class="flex items-center justify-between">
            <div class="flex items-center">
              <input
                id="remember-me"
                v-model="formData.rememberMe"
                type="checkbox"
                class="h-4 w-4 bg-surface border-gray-700 rounded text-primary focus:ring-primary focus:ring-offset-background"
              />
              <label for="remember-me" class="ml-2 block text-sm text-gray-400 cursor-pointer">
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
            class="btn-primary w-full"
          >
            {{ loading ? 'Logging in...' : 'Log In' }}
          </button>
        </form>

        <!-- Sign up link -->
        <p class="mt-6 text-center text-sm text-gray-400">
          Don't have an account?
          <RouterLink to="/signup" class="link">
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
    router.push('/dashboard')
  } else {
    error.value = result.error
    toast.error(result.error)
  }

  loading.value = false
}
</script>
