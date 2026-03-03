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

        <!-- Ngrok Tunnel Manager (Collapsible) -->
        <div class="flex-1 flex flex-col min-h-0 bg-white/5 border border-white/10 rounded-xl overflow-hidden">
          <button 
            @click="isTunnelCollapsed = !isTunnelCollapsed"
            class="w-full px-4 py-3 flex items-center justify-between hover:bg-white/5 transition-colors group"
          >
            <div class="flex items-center space-x-2">
              <Globe :size="14" :class="isTunnelCollapsed ? 'text-gray-500' : 'text-primary'" />
              <span class="text-[10px] font-black uppercase tracking-widest text-gray-400 group-hover:text-white transition-colors">Tunnel Proxy</span>
            </div>
            <div class="flex items-center space-x-2">
              <span v-if="isTunnelCollapsed" class="text-[9px] text-gray-600 font-bold uppercase">Click to expand</span>
              <ChevronDown 
                :size="14" 
                class="text-gray-500 transition-transform duration-300"
                :class="{ 'rotate-180': !isTunnelCollapsed }"
              />
            </div>
          </button>
          
          <div 
            v-show="!isTunnelCollapsed" 
            class="flex-1 min-h-0 transition-all duration-500"
          >
            <NgrokTunnelManager @use-as-base-url="val => baseUrl = val" />
          </div>

          <!-- Collapsed State Info -->
          <div 
            v-if="isTunnelCollapsed" 
            class="flex-1 flex flex-col items-center justify-center p-6 text-center space-y-4 animate-in fade-in zoom-in duration-500"
          >
            <div class="w-16 h-16 rounded-2xl bg-white/5 border border-white/10 flex items-center justify-center text-gray-600 relative group-hover/btn:border-primary/20 transition-colors">
              <div class="absolute inset-0 bg-primary/5 blur-xl opacity-0 transition-opacity"></div>
              <Terminal :size="32" class="relative z-10 opacity-40" />
              <!-- Small pulsing dot to show it's "monitoring" -->
              <div class="absolute -top-1 -right-1 w-3 h-3 bg-primary/20 rounded-full flex items-center justify-center">
                <div class="w-1.5 h-1.5 bg-primary rounded-full animate-pulse"></div>
              </div>
            </div>
            <div class="space-y-1">
              <p class="text-[10px] font-black uppercase tracking-[0.2em] text-gray-500">Service Active</p>
              <p class="text-[9px] text-gray-600 font-bold leading-relaxed max-w-[150px]">
                Tunneling proxy is hidden to save space. Click the header to manage your local backend connections.
              </p>
            </div>
          </div>
        </div>
      </div>

      <!-- Section 2: Progress & Status -->
      <div class="flex-[2] flex flex-col justify-center space-y-8 h-full">
        <!-- BOLD LIVE STATUS -->
        <div :class="[
          'flex items-center justify-center py-20 rounded-[32px] border transition-all duration-700 relative overflow-hidden group',
          isRunning 
            ? 'bg-red-500/10 border-red-500/50 shadow-[0_0_80px_rgba(239,68,68,0.15)]' 
            : 'bg-white/5 border-white/10'
        ]">
          <!-- Background Glow Effect (Status-based) -->
          <div :class="[
            'absolute inset-0 opacity-20 blur-3xl transition-colors duration-1000',
            isRunning ? 'bg-red-500' : (executionState === 'completed' ? 'bg-primary' : 'bg-transparent')
          ]"></div>

          <div class="text-center relative z-10">
            <p :class="[
              'text-[14px] uppercase font-black tracking-[0.6em] mb-4',
              isRunning ? 'text-red-400' : (executionState === 'failed' ? 'text-red-500' : 'text-gray-500')
            ]">
              {{ executionState === 'failed' ? 'Attention Required' : 'System Status' }}
            </p>
            <p :class="[
              'text-7xl font-black uppercase tracking-tighter transition-all duration-500 scale-100 group-hover:scale-110',
              isRunning ? 'text-red-500 drop-shadow-[0_0_30px_rgba(239,68,68,0.4)]' : 
              (executionState === 'completed' ? 'text-primary' : 
              (executionState === 'failed' ? 'text-red-500 underline decoration-red-900/50' : 'text-gray-800'))
            ]">
              {{ isRunning ? 'Executing' : (executionState === 'completed' ? 'Passed' : (executionState === 'failed' ? 'Failed' : 'Ready')) }}
            </p>
            
            <div class="mt-8 flex flex-col items-center">
              <p v-if="executionState === 'failed'" class="text-[11px] text-red-500/70 font-bold uppercase tracking-[0.2em] animate-pulse">
                One or more steps encountered errors
              </p>
              <p v-else-if="executionState === 'completed'" class="text-[11px] text-primary/70 font-bold uppercase tracking-[0.2em]">
                All endpoints responded successfully
              </p>
              <div v-else-if="isRunning" class="flex space-x-1 mt-2">
                <div v-for="i in 3" :key="i" class="w-1.5 h-1.5 bg-red-500 rounded-full animate-bounce" :style="{animationDelay: i*0.2 + 's'}"></div>
              </div>
            </div>
          </div>
        </div>

        <!-- Progress Bar (Enhanced) -->
        <div v-if="isRunning || executionState !== 'idle'" class="px-6 space-y-4">
          <div class="flex items-center justify-between">
            <div class="flex items-center space-x-2">
              <div v-if="isRunning" class="w-2 h-2 rounded-full bg-primary animate-pulse"></div>
              <span class="text-[11px] font-black uppercase text-gray-400 tracking-widest">Execution Progress</span>
            </div>
            <span class="text-[12px] font-mono text-primary font-black bg-primary/10 px-2 py-1 rounded">
              {{ completedSteps }} / {{ totalSteps }} Steps
            </span>
          </div>
          <div class="w-full h-4 bg-gray-900 rounded-full border border-white/5 p-1 relative overflow-hidden">
            <div
              class="h-full bg-gradient-to-r from-primary-dark via-primary to-primary-light transition-all duration-700 ease-[cubic-bezier(0.34,1.56,0.64,1)] rounded-full relative"
              :style="{ width: progress + '%' }"
            >
               <div class="absolute inset-0 bg-[linear-gradient(45deg,rgba(255,255,255,0.2)_25%,transparent_25%,transparent_50%,rgba(255,255,255,0.2)_50%,rgba(255,255,255,0.2)_75%,transparent_75%,transparent)] bg-[length:20px_20px] animate-[loading-bar_1s_linear_infinite]"></div>
            </div>
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

@keyframes loading-bar {
  0% { background-position: 0 0; }
  100% { background-position: 40px 0; }
}

:root {
  --primary-rgb: 191, 245, 73;
  --primary-light: #D4FF6B;
}
</style>

<script setup>
import { ref, computed } from 'vue'
import { useJourneyStore } from '@/stores/journey'
import { useToast } from 'vue-toastification'
import { Play, Square, RotateCcw, Loader, Globe, X, PlayCircle, ChevronRight, ChevronDown, Terminal } from 'lucide-vue-next'
import NgrokTunnelManager from './NgrokTunnelManager.vue'

const isTunnelCollapsed = ref(false)

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
