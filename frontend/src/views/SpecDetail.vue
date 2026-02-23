<template>
  <div class="min-h-screen bg-background">
    <!-- Header -->
    <header class="border-b border-gray-800 bg-surface/50 backdrop-blur-lg sticky top-0 z-10">
      <div class="max-w-7xl mx-auto px-4 py-4">
        <div class="flex items-center justify-between">
          <div class="flex items-center space-x-4">
            <button @click="router.push('/dashboard')" class="text-gray-400 hover:text-white">
              <ArrowLeft :size="24" />
            </button>
            <h1 class="text-2xl font-bold">Specification Details</h1>
          </div>
          <div class="flex items-center space-x-2">
            <button 
              @click="handleLogout" 
              class="text-gray-400 hover:text-white hover:bg-white/10 px-3 py-2 rounded-lg transition-colors flex items-center space-x-2"
              title="Logout"
            >
              <LogOut :size="20" />
              <span class="text-sm hidden sm:inline">Logout</span>
            </button>
          </div>
        </div>
      </div>
    </header>

    <main class="max-w-7xl mx-auto px-4 py-8 relative">
      <!-- Loading State -->
      <div v-if="loading" class="space-y-6">
        <div class="card">
          <div class="skeleton h-8 w-1/3 mb-4"></div>
          <div class="skeleton-text mb-2"></div>
          <div class="skeleton-text w-2/3"></div>
        </div>
      </div>

      <!-- Loaded State -->
      <div v-else-if="spec" class="space-y-6 pb-40">
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
            <div class="flex items-center space-x-3">
              <!-- Re-sync Button -->
              <label
                for="resync-file-input"
                class="btn-secondary text-sm py-2 px-4 hover:bg-primary/20 hover:text-primary cursor-pointer inline-flex items-center"
                :class="{'opacity-50 cursor-not-allowed': resyncingSpec}"
              >
                <RefreshCw :size="16" class="inline mr-2" :class="{'animate-spin': resyncingSpec}" />
                {{ resyncingSpec ? 'Re-syncing...' : 'Re-sync Spec' }}
              </label>
              <input
                id="resync-file-input"
                type="file"
                accept=".json,.yaml,.yml"
                @change="handleResyncSpec"
                class="hidden"
                :disabled="resyncingSpec"
              />
              
              <button
                @click="handleDeleteSpec"
                class="btn-secondary text-sm py-2 px-4 hover:bg-red-500/20 hover:text-red-500"
              >
                <Trash2 :size="16" class="inline mr-2" />
                Delete
              </button>
            </div>
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
            <div class="flex items-center space-x-3">
              <button
                v-if="selectedJourneyIds.size > 0"
                @click="batchDeleteJourneys"
                class="btn-secondary text-red-400 hover:text-red-500 hover:bg-red-500/10"
              >
                <Trash2 :size="16" class="inline mr-2" />
                Delete ({{ selectedJourneyIds.size }})
              </button>
              <button
                @click="generateJourneys"
                :disabled="generatingJourneys"
                class="btn-primary"
              >
                <Sparkles v-if="!generatingJourneys" :size="20" class="inline mr-2" />
                <Loader v-else :size="20" class="inline mr-2 animate-spin" />
                {{ generatingJourneys ? 'Generating...' : 'Generate with AI' }}
              </button>
              <!-- Cancel Button -->
              <button
                v-if="generatingJourneys"
                @click="cancelGeneration"
                class="btn-secondary text-red-400 hover:text-red-500 hover:bg-red-500/10"
              >
                <X :size="20" class="inline mr-2" />
                Cancel
              </button>
            </div>
          </div>

          <!-- Generation Progress -->
          <div v-if="generatingJourneys" class="mb-4 p-4 bg-surface rounded-lg">
            <div class="flex items-center justify-between mb-2">
              <span class="text-sm text-gray-400">{{ generationMessage }}</span>
              <span class="text-sm font-medium">{{ progress }}%</span>
            </div>
            <div class="w-full bg-gray-700 rounded-full h-2">
              <div 
                class="bg-primary h-2 rounded-full transition-all duration-300" 
                :style="{ width: `${progress}%` }"
              ></div>
            </div>
            <p v-if="generationError" class="mt-2 text-sm text-red-400">
              {{ generationError }}
            </p>
          </div>
          
          <!-- Bulk Selection Header -->
          <div v-if="journeys.length > 0 && selectedJourneyIds.size > 0" class="flex items-center px-4 py-2 border-b border-gray-800/50 mb-2 transition-all">
            <input 
              type="checkbox" 
              :checked="isAllSelected"
              :indeterminate="isIndeterminate"
              @change="toggleSelectAll"
              class="w-4 h-4 rounded bg-black/40 border-gray-600 text-primary focus:ring-0 focus:ring-offset-0 mr-4 cursor-pointer" 
            />
            <span class="text-xs text-gray-500 font-bold uppercase tracking-wider">Select All</span>
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
              @click="handleJourneyClick(journey.id, $event)"
              class="p-4 bg-surface hover:bg-gray-800 rounded-lg cursor-pointer transition-all group border border-transparent hover:border-primary/50"
              :class="{'border-primary/30 bg-gray-800': selectedJourneyIds.has(journey.id)}"
            >
              <div class="flex items-start justify-between">
                <div 
                  class="flex items-center mr-4 pt-1 transition-opacity duration-200"
                  :class="selectedJourneyIds.size > 0 || isMobile ? 'opacity-100' : 'opacity-0 group-hover:opacity-100'"
                >
                   <input 
                    type="checkbox" 
                    :checked="selectedJourneyIds.has(journey.id)"
                    @click.stop="toggleJourneySelection(journey.id)"
                    class="w-4 h-4 rounded bg-black/40 border-gray-600 text-primary focus:ring-0 focus:ring-offset-0 cursor-pointer" 
                  />
                </div>
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
                    <span
                      v-else-if="journey.generation_method === 'manual'"
                      class="px-2 py-1 bg-blue-500/10 text-blue-400 text-xs rounded-full"
                    >
                      Manual Journey
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
            <TransitionGroup name="list" tag="div">
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

                <div class="flex-shrink-0 opacity-0 group-hover:opacity-100 transition-all translate-x-4 group-hover:translate-x-0 flex items-center space-x-2">
                  <button 
                    @click="addEndpointToSelection(endpoint)"
                    class="p-2.5 rounded-xl transition-all shadow-lg"
                    :class="isSelected(endpoint) ? 'bg-primary text-black font-bold' : 'bg-primary/10 text-primary hover:bg-primary hover:text-black hover:scale-110'"
                    title="Add to Journey Builder"
                  >
                    <Check v-if="isSelected(endpoint)" :size="20" />
                    <PlusSquare v-else :size="20" />
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

        <!-- Manual Journey Builder Tray (Fixed Bottom) -->
        <Transition name="slide-up">
          <div v-if="selectedEndpoints.length > 0" class="fixed bottom-0 left-0 right-0 z-50 p-4 md:p-6 bg-surface/80 backdrop-blur-2xl border-t border-white/10 shadow-[0_-20px_50px_rgba(0,0,0,0.5)]">
            <div class="max-w-7xl mx-auto">
              <!-- Selection List logic remains same -->
              <div class="flex flex-col lg:flex-row items-center gap-6">
                <!-- Selection List -->
                <div class="flex-1 w-full overflow-hidden">
                  <div class="flex items-center justify-between mb-3 px-1">
                    <div class="flex items-center space-x-2">
                      <Workflow :size="26" class="text-primary" />
                      <span class="text-[10px] font-black uppercase tracking-[0.2em] text-gray-400">Manual Journey Builder</span>
                    </div>
                    <button @click="clearSelection" class="text-[10px] font-bold text-red-400/70 hover:text-red-400 uppercase tracking-widest transition-colors">
                      Clear All
                    </button>
                  </div>
                  
                  <div class="flex items-center space-x-3 overflow-x-auto pb-2 custom-scrollbar">
                    <div 
                      v-for="(ep, idx) in selectedEndpoints" 
                      :key="idx"
                      class="flex-shrink-0 flex items-center space-x-2 bg-black/60 border border-gray-800 p-2 rounded-xl group relative"
                    >
                      <div class="absolute -top-1.5 -left-1.5 w-5 h-5 bg-gray-800 text-[10px] font-bold flex items-center justify-center rounded-full border border-gray-700 text-primary">
                        {{ idx + 1 }}
                      </div>
                      <span :class="['text-[8px] font-black px-1.5 py-0.5 rounded', getMethodColor(ep.method)]">{{ ep.method }}</span>
                      <span class="text-[10px] font-mono text-gray-300 max-w-[120px] truncate">{{ ep.path }}</span>
                      <button @click="removeEndpointFromSelection(idx)" class="text-gray-600 hover:text-red-400 transition-colors">
                        <X :size="12" />
                      </button>
                    </div>
                  </div>
                </div>

                <!-- Action Panel -->
                <div class="lg:w-[420px] w-full flex flex-col sm:flex-row items-center gap-4 border-l border-white/10 pl-6">
                  <div class="flex-1 w-full space-y-2">
                    <div class="flex items-center justify-between">
                      <label class="text-[9px] text-gray-500 uppercase font-black tracking-widest pl-1">Journey Name</label>
                      <!-- Validation Badge -->
                      <div v-if="isValidFirstNode" class="flex items-center text-[8px] text-green-400 font-black uppercase">
                        <CheckCircle :size="10" class="mr-1" /> Auth Verified
                      </div>
                      <div v-else class="flex items-center text-[8px] text-yellow-500 font-bold uppercase animate-pulse">
                        <AlertTriangle :size="10" class="mr-1" /> Login/Register Required First
                      </div>
                    </div>
                    <input 
                      v-model="newJourneyName"
                      @input="validateJourneyName"
                      type="text"
                      placeholder="e.g. User Checkout Flow"
                      :class="{'border-red-500 focus:border-red-500': journeyNameError}"
                      class="w-full bg-black/40 border border-gray-800 rounded-xl px-4 py-2.5 text-xs text-primary outline-none focus:border-primary/50 transition-all font-bold"
                    />
                    <p v-if="journeyNameError" class="text-[9px] text-red-500 font-bold mt-1 pl-1">{{ journeyNameError }}</p>
                  </div>

                  <button 
                    @click="createManualJourney"
                    :disabled="!canCreateJourney || creatingManual"
                    class="sm:w-auto w-full px-8 py-3 bg-primary text-black font-black text-[11px] uppercase tracking-[0.2em] rounded-xl shadow-[0_4px_20px_rgba(191,245,73,0.3)] hover:shadow-[0_4px_30px_rgba(191,245,73,0.5)] transition-all active:scale-95 disabled:opacity-30 disabled:grayscale shrink-0"
                  >
                    <span v-if="!creatingManual">Assemble Journey</span>
                    <Loader v-else :size="16" class="animate-spin mx-auto" />
                  </button>
                </div>
              </div>
            </div>
          </div>
        </Transition>
      </div>

      <!-- Error State -->
      <div v-else class="card text-center py-12">
        <AlertCircle :size="48" class="mx-auto text-red-500 mb-4" />
        <p class="text-gray-400">Failed to load specification</p>
        <button @click="router.push('/dashboard')" class="btn-secondary mt-4">
          Go Back
        </button>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useSpecStore } from '@/stores/spec'
import { useJourneyStore } from '@/stores/journey'
import { useAuthStore } from '@/stores/auth'
import { useToast } from 'vue-toastification'
import apiClient from '@/api/client'
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
  X,
  Plus,
  Check,
  CheckCircle,
  AlertTriangle,
  RefreshCw,
  LogOut,
} from 'lucide-vue-next'

const router = useRouter()
const route = useRoute()
const specStore = useSpecStore()
const journeyStore = useJourneyStore()
const authStore = useAuthStore()
const toast = useToast()

const loading = ref(true)
const loadingJourneys = ref(true)
const generatingJourneys = ref(false)
const creatingManual = ref(false)

// WebSocket state for journey generation
const ws = ref(null)
const progress = ref(0)
const generationMessage = ref('')
const generationError = ref(null)

// Mobile detection for checkbox visibility
const isMobile = ref(false)
const checkMobile = () => {
  isMobile.value = window.innerWidth < 768
}

// Generate a unique session ID for this generation process
function generateSessionId() {
  return `gen_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`
}

// Get WebSocket URL based on environment
function getWsUrl(specId) {
  // Use wss for HTTPS (production), ws for HTTP (development)
  const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
  
  // In production, use the VITE_API_URL (without the /api prefix for WebSocket)
  // In development, use localhost:8000
  let host
  if (import.meta.env.VITE_API_URL) {
    // Production: extract host from VITE_API_URL (e.g., https://backend--specflow--j29wymgjz5b5.code.run)
    const apiUrl = import.meta.env.VITE_API_URL
    host = apiUrl.replace(/^https?:\/\//, '').replace(/\/$/, '')
  } else {
    // Development: use localhost
    host = '127.0.0.1:8000'
  }
  
  return `${protocol}//${host}/api/ws/specs/${specId}/generate-journeys`
}

// Save generation state to localStorage
function saveGenerationState(state) {
  localStorage.setItem('journeyGeneration', JSON.stringify(state))
}

// Get generation state from localStorage
function getGenerationState() {
  const saved = localStorage.getItem('journeyGeneration')
  return saved ? JSON.parse(saved) : null
}

// Clear generation state from localStorage
function clearGenerationState() {
  localStorage.removeItem('journeyGeneration')
}

// Reconnect to an ongoing generation
async function reconnectToGeneration(specId, sessionId) {
  generatingJourneys.value = true
  progress.value = 0
  generationMessage.value = 'Reconnecting...'
  generationError.value = null

  // Fetch WebSocket token first (since HttpOnly cookie can't be accessed via JS)
  generationMessage.value = 'Authenticating...'
  const token = await getWsToken()
  
  if (!token) {
    generationError.value = 'Authentication failed'
    generationMessage.value = 'Failed to authenticate'
    generatingJourneys.value = false
    toast.error('Failed to authenticate - please try logging in again')
    return
  }

  const wsUrl = getWsUrl(specId)
  console.log('Reconnecting to WebSocket:', wsUrl)

  ws.value = new WebSocket(wsUrl)

  ws.value.onopen = () => {
    console.log('WebSocket reconnected')
    generationMessage.value = 'Reconnected to server'
    
    ws.value.send(JSON.stringify({
      token: token,
      strategy: 'ai',
      sessionId: sessionId  // Request to resume this session
    }))
  }

  ws.value.onmessage = (event) => {
    try {
      const data = JSON.parse(event.data)
      console.log('WebSocket message:', data)

      switch (data.type) {
        case 'progress':
          progress.value = data.progress
          generationMessage.value = data.message
          // Update localStorage with current progress
          saveGenerationState({
            specId,
            sessionId,
            progress: data.progress,
            message: data.message,
            timestamp: Date.now()
          })
          break

        case 'complete':
          progress.value = 100
          generationMessage.value = data.message || 'Generation complete!'
          generatingJourneys.value = false
          toast.success(`Generated ${data.data.length} journey(s)!`)
          fetchJourneys()
          ws.value.close()
          clearGenerationState()
          break

        case 'error':
          generationError.value = data.message
          generationMessage.value = `Error: ${data.message}`
          generatingJourneys.value = false
          toast.error(data.message)
          ws.value.close()
          clearGenerationState()
          break

        case 'resumed':
          // Server confirmed session resume
          progress.value = data.progress || 0
          generationMessage.value = data.message || 'Resuming generation...'
          saveGenerationState({
            specId,
            sessionId,
            progress: data.progress || 0,
            message: data.message || 'Resuming generation...',
            timestamp: Date.now()
          })
          break

        default:
          console.warn('Unknown message type:', data.type)
      }
    } catch (err) {
      console.error('Failed to parse WebSocket message:', err)
      generationError.value = 'Failed to parse server response'
    }
  }

  ws.value.onclose = () => {
    console.log('WebSocket closed')
    if (generatingJourneys.value) {
      generationError.value = 'Connection closed unexpectedly'
      generatingJourneys.value = false
      toast.error('Connection closed unexpectedly')
      clearGenerationState()
    }
  }

  ws.value.onerror = (err) => {
    console.error('WebSocket error:', err)
    generationError.value = 'WebSocket connection error'
    generationMessage.value = 'Connection error'
    generatingJourneys.value = false
    toast.error('WebSocket connection error')
    clearGenerationState()
  }
}

onMounted(async () => {
  checkMobile()
  window.addEventListener('resize', checkMobile)
  
  // Check for ongoing generation from previous session
  const savedState = getGenerationState()
  if (savedState && savedState.specId === route.params.id) {
    // Check if the saved generation is recent (within last 5 minutes)
    const fiveMinutes = 5 * 60 * 1000
    if (Date.now() - savedState.timestamp < fiveMinutes) {
      // Restore UI state
      generatingJourneys.value = true
      progress.value = savedState.progress || 0
      generationMessage.value = savedState.message || 'Reconnecting...'
      
      // Ask user if they want to reconnect
      const shouldReconnect = confirm('A journey generation is in progress. Would you like to reconnect and continue viewing the progress?')
      if (shouldReconnect) {
        await reconnectToGeneration(savedState.specId, savedState.sessionId)
      } else {
        // User declined, clear the state
        clearGenerationState()
        generatingJourneys.value = false
      }
    } else {
      // Generation expired, clear state
      clearGenerationState()
    }
  }
})

onUnmounted(() => {
  window.removeEventListener('resize', checkMobile)
  // Close WebSocket if still connected when leaving page
  if (ws.value && ws.value.readyState === WebSocket.OPEN) {
    ws.value.close()
  }
})

// Bulk Selection State
const selectedJourneyIds = ref(new Set())

const isAllSelected = computed(() => {
  return journeys.value.length > 0 && selectedJourneyIds.value.size === journeys.value.length
})

const isIndeterminate = computed(() => {
  return selectedJourneyIds.value.size > 0 && selectedJourneyIds.value.size < journeys.value.length
})

function toggleSelectAll() {
  if (isAllSelected.value) {
    selectedJourneyIds.value.clear()
  } else {
    journeys.value.forEach(j => selectedJourneyIds.value.add(j.id))
  }
}

function toggleJourneySelection(id) {
  if (selectedJourneyIds.value.has(id)) {
    selectedJourneyIds.value.delete(id)
  } else {
    selectedJourneyIds.value.add(id)
  }
}

function handleJourneyClick(id, event) {
  // If clicking checkbox, handled by stop propagation
  // If clicking row:
  // - if in selection mode (some selected), toggle selection
  // - else navigate
  if (selectedJourneyIds.value.size > 0 && !event.target.closest('button')) {
    toggleJourneySelection(id)
  } else if (!event.target.closest('button') && !event.target.closest('input')) {
    navigateToJourney(id)
  }
}

function handleLogout() {
  authStore.logout()
}

// Manual Journey Selection
const selectedEndpoints = ref([])
const newJourneyName = ref('')
const journeyNameError = ref('')

// Fetch WebSocket token from the server
async function getWsToken() {
  try {
    const response = await apiClient.get('/api/auth/me-with-token')
    return response.data.token
  } catch (error) {
    console.error('Failed to get WebSocket token:', error)
    return null
  }
}

// Generate a random name for manual journey
function generateRandomJourneyName() {
  const adjectives = ['Quick', 'Simple', 'Basic', 'User', 'Admin', 'Test', 'Demo', 'Sample', 'Main', 'Primary']
  const nouns = ['Flow', 'Path', 'Route', 'Sequence', 'Process', 'Workflow', 'Chain', 'Trip', 'Journey', 'Cycle']
  const adj = adjectives[Math.floor(Math.random() * adjectives.length)]
  const noun = nouns[Math.floor(Math.random() * nouns.length)]
  const randomNum = Math.floor(Math.random() * 1000)
  return `Manual ${adj} ${noun} ${randomNum}`
}

// Check if journey name already exists
function isDuplicateJourneyName(name) {
  const existingNames = journeys.value.map(j => j.name.toLowerCase())
  return existingNames.includes(name.toLowerCase())
}

function validateJourneyName() {
  const name = newJourneyName.value.trim()
  journeyNameError.value = ''
  
  if (!name) return

  // Check for duplicates
  if (isDuplicateJourneyName(name)) {
    journeyNameError.value = 'A journey with this name already exists'
    return
  }

  // Frontend Validation for XSS/SQL Injection
  const xssPattern = /<[^>]*>|javascript:|on\w+=/i
  const sqlPattern = /(\b(select|update|delete|insert|drop|alter)\b.*\b(from|table|into)\b)|(--)/i
  
  if (xssPattern.test(name)) {
    journeyNameError.value = 'Invalid characters detected (XSS)'
  } else if (sqlPattern.test(name)) {
    journeyNameError.value = 'Invalid characters detected (SQL Injection)'
  }
}

function isSelected(endpoint) {
  return selectedEndpoints.value.some(e => e.path === endpoint.path && e.method === endpoint.method)
}

function addEndpointToSelection(endpoint) {
  if (isSelected(endpoint)) {
    selectedEndpoints.value = selectedEndpoints.value.filter(e => e.path !== endpoint.path || e.method !== endpoint.method)
    return
  }
  selectedEndpoints.value.push(JSON.parse(JSON.stringify(endpoint)))
  
  if (selectedEndpoints.value.length === 1 && !newJourneyName.value) {
    // Generate name based on endpoint, but ensure no duplicates
    let baseName = endpoint.summary || endpoint.path.split('/').pop() || 'Journey'
    let generatedName = `Manual: ${baseName}`
    
    // If duplicate, generate random name
    if (isDuplicateJourneyName(generatedName)) {
      generatedName = generateRandomJourneyName()
    }
    
    // Keep generating until we find a unique name
    let counter = 1
    while (isDuplicateJourneyName(generatedName)) {
      generatedName = `${generateRandomJourneyName()} ${counter}`
      counter++
    }
    
    newJourneyName.value = generatedName
  }
}

function removeEndpointFromSelection(idx) {
  selectedEndpoints.value.splice(idx, 1)
}

function clearSelection() {
  selectedEndpoints.value = []
  newJourneyName.value = ''
  journeyNameError.value = ''
}

const isValidFirstNode = computed(() => {
  if (selectedEndpoints.value.length === 0) return true
  const first = selectedEndpoints.value[0]
  
  // Get path segments (e.g., "/api/v1/auth/login" -> ["api", "v1", "auth", "login"])
  const pathSegments = first.path
    .toLowerCase()
    .split('/')
    .filter(s => s.length > 0)
  
  // Only check the last segment (the actual endpoint/action)
  const lastSegment = pathSegments[pathSegments.length - 1] || ''
  
  // Authentication keywords - only use the last path segment
  const authKeywords = ['login', 'token', 'auth', 'signin',
  'register', 'signup', 'sign-up', 'create-account', 'create_user', 'createuser', 'account', 'users',
  'authenticate', 'session']
  
  // Check if last segment matches any auth keyword
  const isAuth = authKeywords.some(k => 
    lastSegment.includes(k)
  )
  
  return isAuth
})

const canCreateJourney = computed(() => {
  return selectedEndpoints.value.length >= 1 && newJourneyName.value.trim() !== '' && isValidFirstNode.value && !journeyNameError.value
})

async function createManualJourney() {
  if (!canCreateJourney.value) return
  
  creatingManual.value = true
  
  // Transform selected endpoints into nodes and edges
  const nodes = selectedEndpoints.value.map((ep, idx) => ({
    id: `step-${idx}-${Date.now()}`,
    type: 'endpoint',
    position: { x: 250, y: 100 + (idx * 250) },
    data: { ...ep, status: 'pending' }
  }))
  
  const edges = []
  for (let i = 0; i < nodes.length - 1; i++) {
    edges.push({
      id: `step-${i}-${Date.now()}`,
      source: nodes[i].id,
      target: nodes[i+1].id,
      type: 'mapping',
      data: { dataMapping: [] } // Auto-mapping will kick in on load if needed
    })
  }
  
  const result = await journeyStore.createJourney({
    name: newJourneyName.value,
    spec_id: route.params.id,
    nodes,
    edges,
    generation_method: 'manual'
  })
  
  if (result.success) {
    toast.success('Manual journey created successfully!')
    clearSelection()
    await fetchJourneys()
    router.push(`/journey/${result.data.id}`)
  } else {
    toast.error(result.error || 'Failed to create journey')
  }
  
  creatingManual.value = false
}

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

// Watch for route changes to refetch spec when navigating between specs
watch(() => route.params.id, async (newId, oldId) => {
  if (newId && newId !== oldId) {
    // Clear current state
    selectedJourneyIds.value.clear()
    selectedEndpoints.value = []
    newJourneyName.value = ''
    journeyNameError.value = ''
    
    // Fetch new spec and journeys
    await Promise.all([fetchSpec(), fetchJourneys()])
  }
})

async function fetchSpec() {
  loading.value = true
  const result = await specStore.fetchSpec(route.params.id)
  if (!result.success) {
    toast.error('Failed to load specification')
  }
  loading.value = false
}

// Re-sync Spec Functionality
const resyncingSpec = ref(false)

async function handleResyncSpec(event) {
  const file = event.target.files?.[0]
  if (!file) return

  resyncingSpec.value = true

  try {
    // Read file
    const text = await file.text()
    let specData

    // Parse based on file type
    if (file.name.endsWith('.json')) {
      specData = JSON.parse(text)
    } else if (file.name.endsWith('.yaml') || file.name.endsWith('.yml')) {
      // For YAML, we'll need to use a library or send to backend
      // For now, show error and suggest JSON
      toast.error('Please convert YAML to JSON format for re-sync')
      resyncingSpec.value = false
      event.target.value = '' // Reset input
      return
    } else {
      toast.error('Unsupported file format')
      resyncingSpec.value = false
      event.target.value = ''
      return
    }

    // Validate it's an OpenAPI spec
    if (!specData.openapi && !specData.swagger) {
      toast.error('Invalid OpenAPI specification')
      resyncingSpec.value = false
      event.target.value = ''
      return
    }

    // Call API to update the spec
    const result = await specStore.resyncSpec(route.params.id, specData)

    if (result.success) {
      toast.success('Specification re-synced successfully! Endpoints updated.')
      // Refresh the spec and journeys
      await Promise.all([fetchSpec(), fetchJourneys()])
    } else {
      toast.error(result.error || 'Failed to re-sync specification')
    }
  } catch (error) {
    console.error('Re-sync error:', error)
    toast.error('Failed to parse or upload specification file')
  } finally {
    resyncingSpec.value = false
    event.target.value = '' // Reset file input
  }
}


async function fetchJourneys() {
  loadingJourneys.value = true
  await journeyStore.fetchJourneys()
  loadingJourneys.value = false
}

async function generateJourneys() {
  generatingJourneys.value = true
  progress.value = 0
  generationMessage.value = 'Connecting...'
  generationError.value = null

  const specId = route.params.id
  const sessionId = generateSessionId()
  
  // Fetch WebSocket token first (since HttpOnly cookie can't be accessed via JS)
  generationMessage.value = 'Authenticating...'
  const token = await getWsToken()
  
  if (!token) {
    generationError.value = 'Authentication failed'
    generationMessage.value = 'Failed to authenticate'
    generatingJourneys.value = false
    toast.error('Failed to authenticate - please try logging in again')
    return
  }
  
  // Set timeout for 5 minutes (300000ms)
  const timeoutId = setTimeout(() => {
    if (generatingJourneys.value) {
      generationError.value = 'Generation timed out after 5 minutes'
      generationMessage.value = 'Request timed out'
      generatingJourneys.value = false
      if (ws.value && ws.value.readyState === WebSocket.OPEN) {
        ws.value.close()
      }
      toast.error('Generation timed out - please try again')
      clearGenerationState()
    }
  }, 300000)
  
  // Save initial state to localStorage
  saveGenerationState({
    specId,
    sessionId,
    progress: 0,
    message: 'Starting generation...',
    timestamp: Date.now()
  })

  const wsUrl = getWsUrl(specId)
  console.log('WebSocket URL:', wsUrl)

  // Create WebSocket connection
  ws.value = new WebSocket(wsUrl)

  // Connection opened
  ws.value.onopen = () => {
    console.log('WebSocket connected')
    generationMessage.value = 'Connected to server'
    
    // Send token and strategy
    ws.value.send(JSON.stringify({
      token: token,
      strategy: 'ai',
      sessionId: sessionId
    }))
  }

  // Listen for messages
  ws.value.onmessage = (event) => {
    try {
      const data = JSON.parse(event.data)
      console.log('WebSocket message:', data)

      switch (data.type) {
        case 'progress':
          progress.value = data.progress
          generationMessage.value = data.message
          // Update localStorage
          saveGenerationState({
            specId,
            sessionId,
            progress: data.progress,
            message: data.message,
            timestamp: Date.now()
          })
          break

        case 'complete':
          clearTimeout(timeoutId)
          progress.value = 100
          generationMessage.value = data.message || 'Generation complete!'
          generatingJourneys.value = false
          toast.success(`Generated ${data.data.length} journey(s)!`)
          fetchJourneys() // Refresh the journeys list
          ws.value.close()
          clearGenerationState()
          break

        case 'error':
          generationError.value = data.message
          generationMessage.value = `Error: ${data.message}`
          generatingJourneys.value = false
          toast.error(data.message)
          ws.value.close()
          clearGenerationState()
          break

        default:
          console.warn('Unknown message type:', data.type)
      }
    } catch (err) {
      console.error('Failed to parse WebSocket message:', err)
      generationError.value = 'Failed to parse server response'
      generatingJourneys.value = false
      toast.error('Failed to parse server response')
    }
  }

  // Connection closed
  ws.value.onclose = () => {
    console.log('WebSocket closed')
    clearTimeout(timeoutId)
    if (generatingJourneys.value) {
      // Connection closed before completion
      generationError.value = 'Connection closed unexpectedly'
      generatingJourneys.value = false
      toast.error('Connection closed unexpectedly')
      clearGenerationState()
    }
  }

  // Error occurred
  ws.value.onerror = (err) => {
    console.error('WebSocket error:', err)
    clearTimeout(timeoutId)
    generationError.value = 'WebSocket connection error'
    generationMessage.value = 'Connection error'
    generatingJourneys.value = false
    toast.error('WebSocket connection error')
    clearGenerationState()
  }
}

/**
 * Cancel ongoing generation
 */
function cancelGeneration() {
  if (ws.value) {
    // Close the WebSocket if it's still open or connecting
    if (ws.value.readyState === WebSocket.OPEN || ws.value.readyState === WebSocket.CONNECTING) {
      ws.value.close()
    }
    ws.value = null
  }
  generatingJourneys.value = false
  progress.value = 0
  generationMessage.value = 'Cancelled'
  generationError.value = null
  
  // Clear localStorage state
  clearGenerationState()
  
  toast.info('Generation cancelled')
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
  selectedJourneyIds.value.delete(journeyId)

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

async function batchDeleteJourneys() {
  const count = selectedJourneyIds.value.size
  if (count === 0) return
  
  if (!confirm(`Delete ${count} selected journeys? This action cannot be undone.`)) {
    return
  }
  
  const idsToDelete = Array.from(selectedJourneyIds.value)
  
  // Optimistic hide
  idsToDelete.forEach(id => deletingJourneyIds.value.add(id))
  selectedJourneyIds.value.clear()
  
  // Use bulk delete for efficiency
  const result = await journeyStore.bulkDeleteJourneys(idsToDelete)
  
  if (result.success) {
    toast.success(`Deleted ${result.deleted} journeys`)
  } else {
    toast.error(result.error || 'Failed to delete journeys')
    // Refresh to get correct state
    await fetchJourneys()
    deletingJourneyIds.value.clear()
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

/* Animations */
.slide-up-enter-active,
.slide-up-leave-active {
  transition: transform 0.4s cubic-bezier(0.16, 1, 0.3, 1), opacity 0.4s ease;
}

.slide-up-enter-from,
.slide-up-leave-to {
  transform: translateY(100%);
  opacity: 0;
}
</style>
