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
        <div class="card overflow-hidden">
          <div class="flex flex-col md:flex-row md:items-center justify-between mb-8 gap-4">
            <div>
              <h3 class="text-2xl font-bold bg-gradient-to-r from-white to-gray-400 bg-clip-text text-transparent">Endpoints</h3>
              <p class="text-[10px] text-gray-500 font-bold uppercase tracking-[0.2em] mt-1">{{ filteredEndpoints.length }} of {{ spec.endpoints?.length || 0 }} Operations Active</p>
            </div>
            
            <div class="flex flex-col sm:flex-row gap-3">
              <!-- Search Input -->
              <div class="relative group/search min-w-[280px]">
                <Search :size="16" class="absolute left-3 top-1/2 -translate-y-1/2 text-gray-500 group-focus-within/search:text-primary transition-colors" />
                <input 
                  v-model="searchQuery"
                  type="text"
                  placeholder="Filter by path, name or resource..."
                  class="w-full bg-black/40 border border-gray-800 rounded-xl pl-10 pr-4 py-2 text-sm outline-none focus:border-primary/50 focus:ring-1 focus:ring-primary/20 transition-all placeholder:text-gray-600"
                />
              </div>

              <!-- Filter Button (Optional expansion) -->
              <div class="flex items-center space-x-1 bg-black/40 border border-gray-800 rounded-xl p-1">
                <button 
                  v-for="m in filterableMethods" 
                  :key="m"
                  @click="toggleMethodFilter(m)"
                  :class="[
                    'px-2.5 py-1 rounded-lg text-[10px] font-black tracking-wider uppercase transition-all',
                    selectedMethods.includes(m) 
                      ? getMethodColor(m).replace('bg-', 'bg-').replace('/20', '') + ' shadow-lg'
                      : 'text-gray-600 hover:text-gray-400 hover:bg-white/5'
                  ]"
                >
                  {{ m }}
                </button>
              </div>
            </div>
          </div>

          <div class="space-y-3 max-h-[700px] overflow-y-auto pr-2 custom-scrollbar">
            <TransitionGroup name="list">
              <div
                v-for="(endpoint, index) in filteredEndpoints"
                :key="`${endpoint.method}-${endpoint.path}`"
                class="flex items-center space-x-6 p-5 bg-black/40 border border-gray-800 rounded-2xl hover:bg-gray-800/60 hover:border-primary/40 transition-all group cursor-default shadow-sm"
              >
                <div class="flex-shrink-0">
                  <span
                    :class="[
                      'inline-block min-w-[70px] text-center py-2 rounded-xl font-mono text-[11px] font-black tracking-widest border transition-all group-hover:shadow-[0_0_15px_currentColor]',
                      getMethodColor(endpoint.method),
                      'border-current/30'
                    ]"
                  >
                    {{ endpoint.method }}
                  </span>
                </div>
                
                <div class="flex-1 min-w-0">
                  <div class="flex items-center space-x-3">
                    <span class="font-mono text-base font-bold text-gray-100 group-hover:text-primary transition-colors tracking-tight truncate">{{ endpoint.path }}</span>
                  </div>
                  <div class="text-xs text-gray-400 font-semibold truncate mt-1.5 opacity-70 group-hover:opacity-100 transition-opacity uppercase tracking-wider">
                    {{ endpoint.summary || endpoint.operation_id }}
                  </div>
                </div>

                <div class="flex-shrink-0 opacity-0 group-hover:opacity-100 transition-all translate-x-4 group-hover:translate-x-0">
                  <button class="p-2.5 bg-primary/10 text-primary hover:bg-primary hover:text-black rounded-xl transition-all shadow-lg" title="Add to Journey">
                    <PlusSquare :size="20" />
                  </button>
                </div>
              </div>
            </TransitionGroup>

            <!-- Empty State for Filters -->
            <div v-if="filteredEndpoints.length === 0" class="flex flex-col items-center justify-center py-20 text-center space-y-4">
              <div class="p-4 rounded-full bg-gray-800/30">
                <SearchX :size="48" class="text-gray-600" />
              </div>
              <div>
                <p class="text-gray-400 font-bold uppercase tracking-widest text-xs">No matching endpoints found</p>
                <p class="text-[10px] text-gray-600 mt-1">Try adjusting your filters or search terms</p>
              </div>
              <button @click="resetFilters" class="text-[10px] font-black uppercase tracking-widest text-primary hover:underline">Reset All Filters</button>
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
  Search,
  SearchX,
  PlusSquare,
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
const deletingJourneyIds = ref(new Set())
const journeys = computed(() =>
  journeyStore.journeys.filter(
    (j) => j.spec_id === route.params.id && !deletingJourneyIds.value.has(j.id)
  )
)

// Filtering Logic
const searchQuery = ref('')
const selectedMethods = ref([])
const filterableMethods = ['GET', 'POST', 'PUT', 'DELETE', 'PATCH']

const filteredEndpoints = computed(() => {
  if (!spec.value?.endpoints) return []
  
  return spec.value.endpoints.filter(endpoint => {
    // Search query filter
    const matchesSearch = !searchQuery.value || 
      endpoint.path.toLowerCase().includes(searchQuery.value.toLowerCase()) ||
      (endpoint.summary && endpoint.summary.toLowerCase().includes(searchQuery.value.toLowerCase())) ||
      (endpoint.operation_id && endpoint.operation_id.toLowerCase().includes(searchQuery.value.toLowerCase()))
    
    // Method filter
    const matchesMethod = selectedMethods.value.length === 0 || 
      selectedMethods.value.includes(endpoint.method.toUpperCase())
    
    return matchesSearch && matchesMethod
  })
})

function toggleMethodFilter(method) {
  const index = selectedMethods.value.indexOf(method)
  if (index === -1) {
    selectedMethods.value.push(method)
  } else {
    selectedMethods.value.splice(index, 1)
  }
}

function resetFilters() {
  searchQuery.value = ''
  selectedMethods.value = []
}

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

  // Optimistic update: hide immediately
  deletingJourneyIds.value.add(journeyId)

  // Background request without blocking the UI
  journeyStore.deleteJourney(journeyId).then((result) => {
    if (result.success) {
      toast.success('Journey deleted')
    } else {
      toast.error(result.error || 'Failed to delete journey')
      // Rollback on failure
      deletingJourneyIds.value.delete(journeyId)
    }
  })
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

<style scoped>
/* Endpoints Transition & Custom Scrollbar */
.list-move,
.list-enter-active,
.list-leave-active {
  transition: all 0.3s cubic-bezier(0.55, 0, 0.1, 1);
}

.list-enter-from,
.list-leave-to {
  opacity: 0;
  transform: translateX(30px);
}

.list-leave-active {
  position: absolute;
}

.custom-scrollbar::-webkit-scrollbar {
  width: 4px;
}
.custom-scrollbar::-webkit-scrollbar-track {
  background: transparent;
}
.custom-scrollbar::-webkit-scrollbar-thumb {
  background: #333;
  border-radius: 10px;
}
.custom-scrollbar::-webkit-scrollbar-thumb:hover {
  background: #444;
}
</style>
