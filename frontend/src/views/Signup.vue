<template>
  <div class="min-h-screen flex items-center justify-center px-4">
    <div class="w-full max-w-md">
      <!-- Logo/Title -->
      <div class="text-center mb-8">
        <div class="flex items-center justify-center space-x-2 mb-4">
          <div class="w-12 h-12 bg-primary rounded-lg flex items-center justify-center transform rotate-12 transition-transform">
            <Zap :size="28" class="text-black fill-current" />
          </div>
          <span class="text-5xl font-black tracking-tighter">
            Spec<span class="text-primary">Flow</span>
          </span>
        </div>
        <p class="text-gray-400 text-lg">Create your account</p>
      </div>

      <!-- Signup Card -->
      <div class="card">
        <form @submit.prevent="handleSignup" class="space-y-6">
          <!-- Name Field -->
          <div>
            <label for="name" class="block text-sm font-medium mb-2">
              Name
            </label>
            <input
              id="name"
              v-model="formData.name"
              type="text"
              required
              class="input-field w-full"
              placeholder="John Doe"
            />
          </div>

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
                minlength="8"
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
            <p class="text-xs text-gray-500 mt-1">
              At least 8 characters
            </p>
          </div>

          <!-- Confirm Password Field -->
          <div>
            <label for="confirmPassword" class="block text-sm font-medium mb-2">
              Confirm Password
            </label>
            <div class="relative">
              <input
                id="confirmPassword"
                v-model="formData.confirmPassword"
                :type="showConfirmPassword ? 'text' : 'password'"
                required
                class="input-field w-full pr-10"
                placeholder="••••••••"
              />
              <button
                type="button"
                @click="showConfirmPassword = !showConfirmPassword"
                class="absolute right-3 top-1/2 -translate-y-1/2 text-gray-500 hover:text-gray-300 transition-colors"
                tabindex="-1"
              >
                <Eye v-if="!showConfirmPassword" :size="18" />
                <EyeOff v-else :size="18" />
              </button>
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
            {{ loading ? 'Creating account...' : 'Sign Up' }}
          </button>
        </form>

        <!-- Login link -->
        <p class="mt-6 text-center text-sm text-gray-400">
          Already have an account?
          <RouterLink to="/login" class="link">
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
</script>
