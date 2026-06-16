<template>
  <div class="min-h-screen bg-background">
    <!-- Header -->
    <header class="border-b border-gray-800 bg-surface/50 backdrop-blur-lg sticky top-0 z-10">
      <div class="max-w-7xl mx-auto px-4 py-4 flex items-center justify-between">
        <RouterLink to="/" class="flex items-center space-x-2 group">
          <div class="w-8 h-8 bg-primary rounded-lg flex items-center justify-center transform rotate-12 group-hover:rotate-0 transition-transform">
            <Zap :size="20" class="text-black fill-current" />
          </div>
          <span class="text-2xl font-black tracking-tighter text-white">
            Spec<span class="text-primary">Flow</span>
          </span>
        </RouterLink>
        <div class="flex items-center space-x-4">
          <span class="text-sm text-gray-400">{{ authStore.user?.email }}</span>
          <RouterLink v-if="authStore.user?.is_admin" to="/admin" target="_blank" class="btn-secondary text-sm py-2 px-4 flex items-center space-x-2 border-primary/30 hover:border-primary">
            <ShieldCheck :size="16" class="text-primary" />
            <span>Admin Panel</span>
          </RouterLink>
          <button @click="confirmDeleteAccount" class="text-sm py-2 px-4 border rounded-full border-red-600 text-red-500 hover:bg-red-600 hover:text-white transition-colors">
            Delete Account
          </button>
          <button @click="handleLogout" class="btn-secondary text-sm py-2 px-4">
            Logout
          </button>
        </div>
      </div>
    </header>

    <main class="max-w-7xl mx-auto px-4 py-8">
      <!-- Welcome Section -->
      <div class="mb-8">
        <h2 class="text-4xl font-bold mb-2">
          Welcome back, {{ authStore.user?.name || 'there' }}!
        </h2>
        <p class="text-gray-400">
          Manage your API specifications and test journeys
        </p>
      </div>

      <!-- Upload Section -->
      <div v-if="showUploader" class="mb-8">
        <SpecUploader />
      </div>

      <!-- New Project Button (when uploader is hidden) -->
      <div v-else class="mb-8">
        <button @click="showUploader = true" class="btn-primary">
          <Plus :size="20" class="inline mr-2" />
          New Project
        </button>
      </div>

      <!-- Loading State -->
      <div v-if="loading" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <div v-for="i in 3" :key="i" class="card">
          <div class="skeleton h-6 w-3/4 mb-4"></div>
          <div class="skeleton-text mb-2"></div>
          <div class="skeleton-text w-1/2"></div>
        </div>
      </div>

      <!-- Empty State -->
      <div
        v-else-if="!loading && specStore.specs.length === 0"
        class="card text-center py-16"
      >
        <FileText :size="64" class="mx-auto text-gray-600 mb-4" />
        <h3 class="text-2xl font-semibold mb-2">No specifications yet</h3>
        <p class="text-gray-400 mb-6">
          Upload your first OpenAPI specification to get started
        </p>
        <button @click="showUploader = true" class="btn-primary">
          <Plus :size="20" class="inline mr-2" />
          Upload Specification
        </button>
      </div>

      <!-- Specs Grid -->
      <div v-else class="space-y-6">
        <div class="flex items-center justify-between">
          <h3 class="text-2xl font-semibold">Your Specifications</h3>
          <span class="text-sm text-gray-400">
            {{ specStore.specs.length }} {{ specStore.specs.length === 1 ? 'spec' : 'specs' }}
          </span>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          <div
            v-for="spec in specStore.specs"
            :key="spec.id"
            @click="navigateToSpec(spec.id)"
            class="card group cursor-pointer hover:border-primary/50 transition-all"
          >
            <!-- Spec Icon -->
            <div class="flex items-start justify-between mb-4">
              <div class="p-3 bg-primary/10 rounded-lg">
                <FileCode2 :size="24" class="text-primary" />
              </div>
              <button
                @click.stop="handleDeleteSpec(spec.id)"
                class="opacity-0 group-hover:opacity-100 transition-opacity text-gray-400 hover:text-red-500"
              >
                <Trash2 :size="18" />
              </button>
            </div>

            <!-- Spec Info -->
            <h4 class="text-lg font-semibold mb-2 group-hover:text-primary transition-colors">
              {{ spec.name }}
            </h4>
            <div class="space-y-1 text-sm text-gray-400">
              <p v-if="spec.version">Version {{ spec.version }}</p>
              <p>{{ spec.endpoints?.length || 0 }} endpoints</p>
              <p>Uploaded {{ formatDate(spec.uploaded_at) }}</p>
            </div>

            <!-- Action -->
            <div class="mt-4 pt-4 border-t border-gray-800">
              <div class="flex items-center text-primary text-sm font-medium">
                <span>View Details</span>
                <ChevronRight :size="16" class="ml-1" />
              </div>
            </div>
          </div>
        </div>
      </div>
    </main>

    <!-- Delete Account Confirmation Modal -->
    <div v-if="showDeleteModal" class="fixed inset-0 z-50 flex items-center justify-center">
      <div class="absolute inset-0 bg-black/50" @click="cancelDelete"></div>
      <div class="bg-surface/90 backdrop-blur-md border border-gray-800 rounded-lg p-6 w-full max-w-lg z-10">
        <h3 class="text-xl font-semibold text-white mb-2">Delete account</h3>
        <p class="text-gray-400 mb-6">This will permanently delete your account and all associated data. This action cannot be undone. Are you sure you want to continue?</p>
        <div class="flex justify-end space-x-3">
          <button @click="cancelDelete" class="btn-secondary py-2 px-4">Cancel</button>
          <button @click="performDeleteAccount" :disabled="deleteInProgress" class="py-2 px-4 bg-red-600 text-white rounded-full hover:bg-red-700 disabled:opacity-60">
            <span v-if="!deleteInProgress">Yes, delete my account</span>
            <span v-else>Deleting…</span>
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useSpecStore } from '@/stores/spec'
import { useToast } from 'vue-toastification'
import {
  Plus,
  FileText,
  FileCode2,
  ChevronRight,
  Trash2,
  Zap,
  ShieldCheck,
} from 'lucide-vue-next'
import SpecUploader from '@/components/spec/SpecUploader.vue'

const router = useRouter()
const authStore = useAuthStore()
const specStore = useSpecStore()
const toast = useToast()

const showUploader = ref(false)
const loading = ref(true)
const showDeleteModal = ref(false)
const deleteInProgress = ref(false)

onMounted(async () => {
  // Fetch current user in background to ensure we have late-breaking data
  // but don't await it to avoid blocking the initial render
  authStore.fetchCurrentUser()
  await fetchSpecs()
})

async function fetchSpecs() {
  loading.value = true
  await specStore.fetchSpecs()
  loading.value = false
}

function navigateToSpec(specId) {
  router.push(`/spec/${specId}`)
}

async function handleDeleteSpec(specId) {
  if (!confirm('Are you sure you want to delete this specification?')) {
    return
  }

  const result = await specStore.deleteSpec(specId)
  if (result.success) {
    toast.success('Specification deleted')
  } else {
    toast.error(result.error)
  }
}

function handleLogout() {
  authStore.logout()
}

function confirmDeleteAccount() {
  showDeleteModal.value = true
}

function cancelDelete() {
  showDeleteModal.value = false
}

async function performDeleteAccount() {
  if (!authStore.user?.id) return
  deleteInProgress.value = true

  const res = await authStore.deleteCurrentAccount(authStore.user.id)
  deleteInProgress.value = false
  showDeleteModal.value = false

  if (res?.success) {
    toast.success('Account deleted')
    // Redirect to login/landing
    window.location.href = '/login?account_deleted'
  } else {
    toast.error(res?.error || 'Failed to delete account')
  }
}

function formatDate(dateString) {
  const date = new Date(dateString)
  const now = new Date()
  const diffMs = now - date
  const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24))

  if (diffDays === 0) return 'today'
  if (diffDays === 1) return 'yesterday'
  if (diffDays < 7) return `${diffDays} days ago`
  if (diffDays < 30) return `${Math.floor(diffDays / 7)} weeks ago`
  
  return date.toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    year: date.getFullYear() !== now.getFullYear() ? 'numeric' : undefined,
  })
}
</script>
