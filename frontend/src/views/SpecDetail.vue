<template>
  <div class="min-h-screen bg-background">
    <!-- Header -->
    <header class="border-b border-gray-800 bg-surface/50 backdrop-blur-lg sticky top-0 z-10">
      <div class="max-w-7xl mx-auto px-4 py-4">
        <div class="flex items-center space-x-4">
          <button @click="router.back()" class="text-gray-400 hover:text-white">
            <ArrowLeft :size="24" />
          </button>
          <h1 class="text-2xl font-bold">Specification Details</h1>
        </div>
      </div>
    </header>

    <main class="max-w-7xl mx-auto px-4 py-8">
      <!-- Loading State -->
      <div v-if="loading" class="space-y-6">
        <div class="card">
          <div class="skeleton h-8 w-1/3 mb-4"></div>
          <div class="skeleton-text mb-2"></div>
          <div class="skeleton-text w-2/3"></div>
        </div>
      </div>

      <!-- Loaded State -->
      <div v-else-if="spec" class="space-y-6">
        <!-- Spec Info Card -->
        <div class="card">
          <div class="flex items-start justify-between mb-6">
            <div>
              <h2 class="text-3xl font-bold mb-2">{{ spec.name }}</h2>
              <div class="flex items-center space-x-4 text-sm text-gray-400">
                <span v-if="spec.version">Version {{ spec.version }}</span>
                <span>{{ spec.endpoints?.length || 0 }} endpoints</span>
                <span>Uploaded {{ formatDate(spec.uploaded_at) }}</span>
              </div>
            </div>
            <button
              @click="handleDeleteSpec"
              class="btn-secondary text-sm py-2 px-4 hover:bg-red-500/20 hover:text-red-500"
            >
              <Trash2 :size="16" class="inline mr-2" />
              Delete
            </button>
          </div>

          <!-- Endpoints Summary -->
          <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div
              v-for="method in methodStats"
              :key="method.name"
              class="bg-surface p-4 rounded-lg"
            >
              <div class="text-2xl font-bold" :class="method.color">
                {{ method.count }}
              </div>
              <div class="text-sm text-gray-400 uppercase">{{ method.name }}</div>
            </div>
          </div>
        </div>

        <!-- Journeys Section -->
        <div class="card">
          <div class="flex items-center justify-between mb-6">
            <h3 class="text-2xl font-semibold">Journeys</h3>
            <button
              @click="generateJourneys"
              :disabled="generatingJourneys"
              class="btn-primary"
            >
              <Sparkles v-if="!generatingJourneys" :size="20" class="inline mr-2" />
              <Loader v-else :size="20" class="inline mr-2 animate-spin" />
              {{ generatingJourneys ? 'Generating...' : 'Generate with AI' }}
            </button>
          </div>

          <!-- Loading Journeys -->
          <div v-if="loadingJourneys" class="space-y-4">
            <div v-for="i in 2" :key="i" class="p-4 bg-surface rounded-lg">
              <div class="skeleton h-6 w-1/2 mb-2"></div>
              <div class="skeleton-text"></div>
            </div>
          </div>

          <!-- No Journeys -->
          <div v-else-if="journeys.length === 0" class="text-center py-12">
            <Workflow :size="48" class="mx-auto text-gray-600 mb-4" />
            <p class="text-gray-400 mb-4">
              No journeys yet. Generate them using AI or create manually.
            </p>
          </div>

          <!-- Journeys List -->
          <div v-else class="space-y-4">
            <div
              v-for="journey in journeys"
              :key="journey.id"
              @click="navigateToJourney(journey.id)"
              class="p-4 bg-surface hover:bg-gray-800 rounded-lg cursor-pointer transition-all group border border-transparent hover:border-primary/50"
            >
              <div class="flex items-start justify-between">
                <div class="flex-1">
                  <div class="flex items-center space-x-3 mb-2">
                    <h4 class="text-lg font-semibold group-hover:text-primary transition-colors">
                      {{ journey.name }}
                    </h4>
                    <span
                      v-if="journey.generation_method === 'ai'"
                      class="px-2 py-1 bg-primary/10 text-primary text-xs rounded-full"
                    >
                      AI Generated
                    </span>
                  </div>
                  <div class="flex items-center space-x-4 text-sm text-gray-400">
                    <span>{{ journey.nodes?.length || 0 }} steps</span>
                    <span>Created {{ formatDate(journey.created_at) }}</span>
                  </div>
                </div>
                <div class="flex items-center space-x-2">
                  <button
                    @click.stop="handleDeleteJourney(journey.id)"
                    class="p-2 text-gray-400 hover:text-red-500 transition-colors"
                  >
                    <Trash2 :size="18" />
                  </button>
                  <ChevronRight :size="20" class="text-gray-400 group-hover:text-primary transition-colors" />
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Endpoints List -->
        <div class="card">
          <h3 class="text-2xl font-semibold mb-6">Endpoints</h3>
          <div class="space-y-2">
            <div
              v-for="(endpoint, index) in spec.endpoints"
              :key="index"
              class="flex items-center space-x-4 p-3 bg-surface rounded-lg hover:bg-gray-800 transition-colors"
            >
              <span
                :class="[
                  'px-3 py-1 rounded font-mono text-xs font-bold',
                  getMethodColor(endpoint.method),
                ]"
              >
                {{ endpoint.method }}
              </span>
              <span class="font-mono text-sm">{{ endpoint.path }}</span>
              <span class="text-sm text-gray-400 ml-auto">
                {{ endpoint.summary || endpoint.operation_id }}
              </span>
            </div>
          </div>
        </div>
      </div>

      <!-- Error State -->
      <div v-else class="card text-center py-12">
        <AlertCircle :size="48" class="mx-auto text-red-500 mb-4" />
        <p class="text-gray-400">Failed to load specification</p>
        <button @click="router.back()" class="btn-secondary mt-4">
          Go Back
        </button>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useSpecStore } from '@/stores/spec'
import { useJourneyStore } from '@/stores/journey'
import { useToast } from 'vue-toastification'
import {
  ArrowLeft,
  Trash2,
  Sparkles,
  Loader,
  Workflow,
  ChevronRight,
  AlertCircle,
} from 'lucide-vue-next'

const router = useRouter()
const route = useRoute()
const specStore = useSpecStore()
const journeyStore = useJourneyStore()
const toast = useToast()

const loading = ref(true)
const loadingJourneys = ref(true)
const generatingJourneys = ref(false)

const spec = computed(() => specStore.currentSpec)
const journeys = computed(() =>
  journeyStore.journeys.filter((j) => j.spec_id === route.params.id)
)

const methodStats = computed(() => {
  if (!spec.value?.endpoints) return []

  const methods = ['GET', 'POST', 'PUT', 'DELETE']
  return methods.map((method) => ({
    name: method,
    count: spec.value.endpoints.filter((e) => e.method === method).length,
    color: getMethodColor(method).replace('bg-', 'text-'),
  }))
})

onMounted(async () => {
  await Promise.all([fetchSpec(), fetchJourneys()])
})

async function fetchSpec() {
  loading.value = true
  const result = await specStore.fetchSpec(route.params.id)
  if (!result.success) {
    toast.error('Failed to load specification')
  }
  loading.value = false
}

async function fetchJourneys() {
  loadingJourneys.value = true
  await journeyStore.fetchJourneys()
  loadingJourneys.value = false
}

async function generateJourneys() {
  generatingJourneys.value = true

  const result = await journeyStore.generateJourneys(route.params.id, 'ai')

  if (result.success) {
    toast.success(`Generated ${result.data.length} journey(s)!`)
    await fetchJourneys()
  } else {
    toast.error(result.error || 'Failed to generate journeys')
  }

  generatingJourneys.value = false
}

async function handleDeleteSpec() {
  if (!confirm('Delete this specification and all its journeys?')) {
    return
  }

  const result = await specStore.deleteSpec(route.params.id)
  if (result.success) {
    toast.success('Specification deleted')
    router.push('/dashboard')
  } else {
    toast.error(result.error)
  }
}

async function handleDeleteJourney(journeyId) {
  if (!confirm('Delete this journey?')) {
    return
  }

  const result = await journeyStore.deleteJourney(journeyId)
  if (result.success) {
    toast.success('Journey deleted')
  } else {
    toast.error(result.error)
  }
}

function navigateToJourney(journeyId) {
  router.push(`/journey/${journeyId}`)
}

function getMethodColor(method) {
  const colors = {
    GET: 'bg-blue-500/20 text-blue-400',
    POST: 'bg-green-500/20 text-green-400',
    PUT: 'bg-yellow-500/20 text-yellow-400',
    DELETE: 'bg-red-500/20 text-red-400',
    PATCH: 'bg-purple-500/20 text-purple-400',
  }
  return colors[method] || 'bg-gray-500/20 text-gray-400'
}

function formatDate(dateString) {
  const date = new Date(dateString)
  const now = new Date()
  const diffMs = now - date
  const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24))

  if (diffDays === 0) return 'today'
  if (diffDays === 1) return 'yesterday'
  if (diffDays < 7) return `${diffDays} days ago`

  return date.toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
  })
}
</script>
