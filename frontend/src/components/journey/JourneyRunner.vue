<template>
  <div class="h-full flex flex-col">
    <!-- Header with Close button -->
    <div class="flex items-center justify-between mb-4">
      <div class="flex items-center space-x-2">
        <PlayCircle :size="18" class="text-primary" />
        <h3 class="text-sm font-bold uppercase tracking-wider text-gray-400">Journey Runner</h3>
      </div>
      <button 
        @click="$emit('close')" 
        class="p-1 hover:bg-white/10 rounded transition-colors text-gray-400 hover:text-white"
        title="Close Runner"
      >
        <X :size="18" />
      </button>
    </div>

    <!-- Horizontal Layout Sections -->
    <div class="flex flex-1 gap-6 min-h-0">
      <!-- Section 1: Config & Context -->
      <div class="flex-[1.2] flex flex-col space-y-4 min-h-0">
        <div>
          <label for="base-url" class="block text-[10px] font-bold uppercase text-gray-500 mb-1">
            Base URL
          </label>
          <div class="relative group">
            <Globe :size="14" class="absolute left-3 top-[50%] -translate-y-1/2 text-gray-500 group-focus-within:text-primary transition-colors" />
            <input
              id="base-url"
              v-model="baseUrl"
              type="url"
              required
              :disabled="isRunning"
              style="padding-left: 2.25rem !important;"
              class="input-field w-full py-2 text-xs"
              placeholder="https://api.example.com"
            />
            <!-- Warning for localhost URLs in cloud environment -->
            <div v-if="isLocalUrl(baseUrl) && isCloudEnvironment()" class="mt-2 p-2 bg-orange-500/20 border border-orange-500/50 rounded text-xs text-orange-400">
              <p class="font-bold mb-1">⚠️ Localhost URLs in Cloud Environment</p>
              <p>Requests to localhost/127.0.0.1 won't work in the cloud app.</p>
              <p class="mt-1 text-[10px]">To test local APIs, run SpecFlow locally on your machine. See <a href="https://github.com/your-repo/specflow#local-development" target="_blank" class="text-white underline">Local Development</a>.</p>
            </div>
          </div>
        </div>

        <!-- Ngrok Tunnel Manager -->
        <div class="flex-1 min-h-0">
          <NgrokTunnelManager @use-as-base-url="val => baseUrl = val" />
        </div>
      </div>

      <!-- Section 2: Progress & Status -->
      <div class="flex-[1.8] flex flex-col justify-center space-y-6">
        <!-- BOLD LIVE STATUS -->
        <div :class="[
          'flex items-center justify-center py-8 rounded-2xl border transition-all duration-500',
          isRunning 
            ? 'bg-red-500/20 border-red-500 shadow-[0_0_50px_rgba(239,68,68,0.2)]' 
            : 'bg-white/5 border-white/10'
        ]">
          <div class="text-center">
            <p :class="[
              'text-[12px] uppercase font-black tracking-[0.4em] mb-2',
              isRunning ? 'text-red-400' : (executionState === 'failed' ? 'text-red-500' : 'text-gray-500')
            ]">
              {{ executionState === 'failed' ? 'Attention Required' : 'System Status' }}
            </p>
            <p :class="[
              'text-5xl font-black uppercase tracking-tighter transition-all duration-300',
              isRunning ? 'text-red-500 drop-shadow-[0_0_15px_rgba(239,68,68,0.5)]' : 
              (executionState === 'completed' ? 'text-primary' : 
              (executionState === 'failed' ? 'text-red-500 underline decoration-red-900/50' : 'text-gray-700'))
            ]">
              {{ isRunning ? 'Executing' : (executionState === 'completed' ? 'Passed' : (executionState === 'failed' ? 'Failed' : 'Ready')) }}
            </p>
            <p v-if="executionState === 'failed'" class="text-[10px] text-red-500/70 font-bold mt-2 uppercase tracking-widest">
              One or more steps encountered errors
            </p>
            <p v-else-if="executionState === 'completed'" class="text-[10px] text-primary/70 font-bold mt-2 uppercase tracking-widest">
              All endpoints responded successfully
            </p>
          </div>
        </div>

        <!-- Progress Bar -->
        <div v-if="isRunning || executionState !== 'idle'" class="px-4">
          <div class="flex items-center justify-between mb-2">
            <span class="text-[11px] font-bold uppercase text-gray-500 tracking-wider">Execution Progress</span>
            <span class="text-[11px] font-mono text-primary font-bold">
              {{ completedSteps }} / {{ totalSteps }} Steps
            </span>
          </div>
          <div class="w-full h-3 bg-gray-800 rounded-full overflow-hidden border border-gray-700/50 p-0.5">
            <div
              class="h-full bg-gradient-to-r from-primary via-primary-light to-primary transition-all duration-500 ease-out shadow-[0_0_15px_rgba(var(--primary-rgb),0.6)] rounded-full"
              :style="{ width: progress + '%' }"
            ></div>
          </div>
        </div>
      </div>

      <!-- Section 3: Status Console & Actions -->
      <div class="flex-[1.5] flex flex-col space-y-4 min-h-0">
        <!-- Status Messages -->
        <div class="flex-1 bg-black/40 border border-gray-800 rounded overflow-hidden flex flex-col min-h-0">
          <div class="px-2 py-1 border-b border-gray-800 bg-white/5 text-[9px] uppercase font-bold text-gray-500">Console Log</div>
          <div class="flex-1 p-2 overflow-auto font-mono text-[10px] space-y-1 custom-scrollbar">
            <div
              v-for="(msg, index) in statusMessages"
              :key="index"
              class="flex border-l-2 pl-2 mb-1"
              :class="{
                'border-primary/50': msg.type === 'info',
                'border-green-500/50': msg.type === 'success',
                'border-red-500/50': msg.type === 'error',
              }"
            >
              <span class="text-gray-600 mr-2 tabular-nums">{{ new Date(msg.time).toLocaleTimeString([], {hour12:false, hour:'2-digit', minute:'2-digit', second:'2-digit'}) }}</span>
              <span :class="{
                'text-primary': msg.type === 'info',
                'text-green-400': msg.type === 'success',
                'text-red-400': msg.type === 'error',
              }">{{ msg.text }}</span>
            </div>
          </div>
        </div>

        <!-- Actions -->
        <div class="flex flex-col space-y-2">
          <button
            @click="startExecution"
            :disabled="!canStart"
            class="w-full py-3 rounded-lg bg-primary hover:bg-primary-dark disabled:opacity-30 disabled:grayscale text-black font-black text-xs uppercase tracking-widest flex items-center justify-center transition-all shadow-[0_4px_20px_rgba(191,245,73,0.2)] hover:shadow-[0_4px_25px_rgba(191,245,73,0.4)] active:scale-95"
          >
            <Play v-if="!isRunning" :size="16" class="mr-2 fill-current" />
            <Loader v-else :size="16" class="mr-2 animate-spin" />
            {{ isRunning ? 'Processing...' : 'Execute Journey' }}
          </button>

          <div class="flex gap-2">
            <button
              v-if="isRunning"
              @click="stopExecution"
              class="flex-1 py-1.5 rounded-lg border border-red-500/50 hover:bg-red-500/10 text-red-500 text-[10px] font-bold uppercase transition-all"
            >
              <Square :size="12" class="inline mr-1 fill-current" />
              Emergency Stop
            </button>

            <button
              v-if="!isRunning"
              @click="resetExecution"
              class="flex-1 py-1.5 rounded-lg border border-gray-700 hover:bg-white/5 text-gray-400 text-[10px] font-bold uppercase transition-all flex items-center justify-center"
            >
              <RotateCcw :size="12" class="mr-1" />
              Reset Runner
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.custom-scrollbar::-webkit-scrollbar {
  width: 4px;
  height: 4px;
}

.custom-scrollbar::-webkit-scrollbar-track {
  background: transparent;
}

.custom-scrollbar::-webkit-scrollbar-thumb {
  background: rgba(255, 255, 255, 0.1);
  border-radius: 10px;
}

.custom-scrollbar::-webkit-scrollbar-thumb:hover {
  background: rgba(255, 255, 255, 0.2);
}

:deep(.input-field) {
  padding-top: 0.375rem;
  padding-bottom: 0.375rem;
}

/* Local primary variables as fallbacks */
:root {
  --primary-rgb: 191, 245, 73;
  --primary-light: #D4FF6B;
}
</style>

<script setup>
import { ref, computed } from 'vue'
import { useJourneyStore } from '@/stores/journey'
import { useToast } from 'vue-toastification'
import { Play, Square, RotateCcw, Loader, Globe, X, PlayCircle, ChevronRight } from 'lucide-vue-next'
import NgrokTunnelManager from './NgrokTunnelManager.vue'

const props = defineProps({
  journeyId: {
    type: String,
    required: true,
  },
  nodes: {
    type: Array,
    required: true,
  },
  edges: {
    type: Array,
    required: true,
  },
})

const emit = defineEmits(['step-start', 'step-complete', 'execution-complete'])

const journeyStore = useJourneyStore()
const toast = useToast()

const baseUrl = computed({
  get: () => journeyStore.runnerConfig.baseUrl,
  set: (val) => journeyStore.runnerConfig.baseUrl = val
})

const isRunning = ref(false)
const executionState = ref('idle')
const completedSteps = ref(0)
const totalSteps = computed(() => props.nodes.length)
const statusMessages = ref([])
const ws = ref(null)

const canStart = computed(() => {
  const hasBaseUrl = baseUrl.value.trim() !== ''
  const hasNodes = props.nodes && props.nodes.length > 0
  const hasEdges = props.edges && props.edges.length > 0 // A journey needs connections
  const isLocalUrlValid = !isLocalUrl(baseUrl.value) || !isCloudEnvironment()
  
  return !isRunning.value && hasBaseUrl && hasNodes && hasEdges && isLocalUrlValid
})

const progress = computed(() => {
  if (totalSteps.value === 0) return 0
  return (completedSteps.value / totalSteps.value) * 100
})

// Helper function to detect local URLs
function isLocalUrl(url) {
  if (!url) return false
  const lowerUrl = url.toLowerCase()
  return lowerUrl.includes('localhost') || lowerUrl.includes('127.0.0.1') || lowerUrl.includes('0.0.0.0')
}

// Helper function to detect cloud environment
function isCloudEnvironment() {
  return import.meta.env.MODE === 'production' || window.location.hostname.includes('code.run') || window.location.hostname.includes('vercel.app') || window.location.hostname.includes('netlify.app')
}

async function startExecution() {
  // Reset state
  isRunning.value = true
  executionState.value = 'running'
  completedSteps.value = 0
  statusMessages.value = []
  journeyStore.resetExecution()

  // Build WebSocket URL - use environment variable if available, otherwise derive from current location
  const wsBaseUrl = import.meta.env.VITE_WS_URL || ''
  let wsUrl
  
  if (wsBaseUrl) {
    // Use explicit WebSocket URL from environment variable (for deployed apps)
    wsUrl = `${wsBaseUrl}/api/ws/journey/${props.journeyId}/execute`
    
  } else {
    // Derive from current location (for local development)
    const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
    const wsHost = window.location.host.replace(':5173', ':8000')
    wsUrl = `${wsProtocol}//${wsHost}/api/ws/journey/${props.journeyId}/execute`
  }

  console.log('Connecting to WebSocket:', wsUrl)

  try {
    ws.value = new WebSocket(wsUrl)

    ws.value.onopen = () => {
      addStatusMessage('Connected to server', 'info')
      
      // Send execution parameters including latest FE nodes/edges
      ws.value.send(
        JSON.stringify({
          baseUrl: baseUrl.value,
          sessionData: {},
          nodes: props.nodes,
          edges: props.edges,
          errorInjections: {}, // Can be extended for error injection UI
        })
      )
      
      addStatusMessage('Starting execution...', 'info')
    }

    ws.value.onmessage = (event) => {
      const message = JSON.parse(event.data)
      handleWebSocketMessage(message)
    }

    ws.value.onerror = (error) => {
      console.error('WebSocket error:', error)
      addStatusMessage('Connection error', 'error')
      toast.error('WebSocket connection failed')
      stopExecution()
    }

    ws.value.onclose = () => {
      addStatusMessage('Disconnected', 'info')
      isRunning.value = false
    }
  } catch (error) {
    console.error('Failed to connect:', error)
    toast.error('Failed to start execution')
    isRunning.value = false
    executionState.value = 'failed'
  }
}



function handleWebSocketMessage(message) {
  switch (message.type) {
    case 'step_start':
      emit('step-start', message.stepId)
      journeyStore.setStepStatus(message.stepId, 'running')
      addStatusMessage(`Executing step ${message.stepId}...`, 'info')
      break

    case 'step_result':
      completedSteps.value++
      emit('step-complete', message.result)
      
      if (message.result.error) {
        journeyStore.saveStepError(message.result.stepId, message.result.error)
        addStatusMessage(
          `Step ${message.result.stepId} failed: ${message.result.error}`,
          'error'
        )
      } else {
        journeyStore.saveStepResult(message.result.stepId, message.result)
        addStatusMessage(
          `Step ${message.result.stepId} completed (${message.result.statusCode})`,
          'success'
        )
      }
      break

    case 'execution_complete':
      executionState.value = message.status === 'completed' ? 'completed' : 'failed'
      emit('execution-complete', message)
      
      if (message.status === 'completed') {
        toast.success('Journey executed successfully!')
        addStatusMessage('All steps completed', 'success')
      } else {
        toast.warning('Journey execution failed')
        addStatusMessage('Execution stopped due to errors', 'error')
      }
      
      stopExecution()
      break

    case 'error':
      toast.error(message.message)
      addStatusMessage(`Error: ${message.message}`, 'error')
      executionState.value = 'failed'
      stopExecution()
      break
  }
}

function addStatusMessage(text, type = 'info') {
  statusMessages.value.push({ text, type, time: new Date() })
  
  // Keep only last 10 messages
  if (statusMessages.value.length > 10) {
    statusMessages.value.shift()
  }
}

function stopExecution() {
  if (ws.value) {
    ws.value.close()
    ws.value = null
  }
  isRunning.value = false
}

function resetExecution() {
  executionState.value = 'idle'
  completedSteps.value = 0
  statusMessages.value = []
  journeyStore.resetExecution()
  emit('execution-complete', null)
}
</script>
