<template>
  <div class="min-h-screen flex items-center justify-center px-4">
    <div class="w-full max-w-md">
      <!-- Logo/Title -->
      <div class="text-center mb-8">
        <h1 class="text-5xl font-bold mb-2">
          Spec<span class="text-primary">Flow</span>
        </h1>
        <p class="text-gray-400">Create your account</p>
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

          <!-- Agree to TOS -->
          <div class="flex items-center">
            <input
              id="agreeToTos"
              v-model="formData.agreeToTos"
              type="checkbox"
              required
              class="h-4 w-4 bg-surface border-gray-700 rounded text-primary focus:ring-primary focus:ring-offset-background"
            />
            <label for="agreeToTos" class="ml-2 block text-sm text-gray-400 cursor-pointer">
              I agree to the <a href="#" class="link" @click.prevent="">Terms of Service</a>
            </label>
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
import { Eye, EyeOff } from 'lucide-vue-next'
import MailChecker from 'mailchecker'

const router = useRouter()
const authStore = useAuthStore()
const toast = useToast()

const formData = ref({
  name: '',
  email: '',
  password: '',
  confirmPassword: '',
  agreeToTos: false,
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

  if (!formData.value.agreeToTos) {
    error.value = 'You must agree to the Terms of Service'
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
