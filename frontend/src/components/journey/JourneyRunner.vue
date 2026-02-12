<template>
  <div class="card">
    <h3 class="text-lg font-semibold mb-4">Journey Execution</h3>

    <!-- Configuration -->
    <div class="space-y-4 mb-6">
      <!-- Base URL -->
      <div>
        <label for="base-url" class="block text-sm font-medium mb-2">
          Base URL
        </label>
        <input
          id="base-url"
          v-model="baseUrl"
          type="url"
          required
          :disabled="isRunning"
          class="input-field w-full"
          placeholder="https://api.example.com"
        />
      </div>

      <!-- Initial Session Data (Optional) -->
      <div>
        <label class="block text-sm font-medium mb-2">
          Initial Session Data (Optional)
        </label>
        <textarea
          v-model="sessionDataInput"
          :disabled="isRunning"
          class="input-field w-full font-mono text-sm"
          rows="4"
          placeholder='{"auth_token": "...", "user_id": "..."}'
        ></textarea>
        <p class="text-xs text-gray-500 mt-1">
          JSON object with initial session values
        </p>
      </div>
    </div>

    <!-- Progress -->
    <div v-if="isRunning || executionState === 'completed'" class="mb-6">
      <div class="flex items-center justify-between mb-2">
        <span class="text-sm font-medium">Progress</span>
        <span class="text-sm text-gray-400">
          {{ completedSteps }} / {{ totalSteps }} steps
        </span>
      </div>
      <div class="w-full h-2 bg-gray-800 rounded-full overflow-hidden">
        <div
          class="h-full bg-primary transition-all duration-300"
          :style="{ width: progress + '%' }"
        ></div>
      </div>
    </div>

    <!-- Live Session Context -->
    <div v-if="Object.keys(journeyStore.sessionData).length > 0" class="mb-6">
      <h4 class="text-xs font-bold text-gray-500 uppercase mb-2 flex items-center">
        <Database :size="12" class="mr-1" />
        Session Context
      </h4>
      <div class="bg-black/40 border border-gray-800 rounded p-3 space-y-1 max-h-48 overflow-auto">
        <div v-for="(value, key) in journeyStore.sessionData" :key="key" class="flex items-start justify-between text-xs font-mono">
          <span class="text-gray-500 mr-2">{{ key }}:</span>
          <span :class="['break-all text-right', key.includes('token') ? 'text-primary' : 'text-blue-400']">
            {{ formatSessionValue(value) }}
          </span>
        </div>
      </div>
    </div>

    <!-- Status Messages -->
    <div v-if="statusMessages.length > 0" class="mb-6 space-y-2 max-h-32 overflow-auto">
      <div
        v-for="(msg, index) in statusMessages"
        :key="index"
        class="text-sm p-2 bg-surface rounded"
        :class="{
          'text-primary': msg.type === 'info',
          'text-green-400': msg.type === 'success',
          'text-red-400': msg.type === 'error',
        }"
      >
        {{ msg.text }}
      </div>
    </div>

    <!-- Actions -->
    <div class="flex space-x-3">
      <button
        @click="startExecution"
        :disabled="!canStart"
        class="btn-primary flex-1"
      >
        <Play v-if="!isRunning" :size="20" class="inline mr-2" />
        <Loader v-else :size="20" class="inline mr-2 animate-spin" />
        {{ isRunning ? 'Running...' : 'Run Journey' }}
      </button>

      <button
        v-if="isRunning"
        @click="stopExecution"
        class="btn-secondary"
      >
        <Square :size="20" class="inline mr-2" />
        Stop
      </button>

      <button
        v-if="executionState === 'completed' || executionState === 'failed'"
        @click="resetExecution"
        class="btn-secondary"
      >
        <RotateCcw :size="20" class="inline mr-2" />
        Reset
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useJourneyStore } from '@/stores/journey'
import { useToast } from 'vue-toastification'
import { Play, Square, RotateCcw, Loader, Database } from 'lucide-vue-next'

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

const sessionDataInput = computed({
  get: () => journeyStore.runnerConfig.initialSessionData,
  set: (val) => journeyStore.runnerConfig.initialSessionData = val
})

const isRunning = ref(false)
const executionState = ref('idle')
const completedSteps = ref(0)
const totalSteps = computed(() => props.nodes.length)
const statusMessages = ref([])
const ws = ref(null)

const canStart = computed(() => {
  return !isRunning.value && baseUrl.value.trim() !== ''
})

const progress = computed(() => {
  if (totalSteps.value === 0) return 0
  return (completedSteps.value / totalSteps.value) * 100
})

async function startExecution() {
  // Validate session data if provided
  let sessionData = {}
  if (sessionDataInput.value.trim()) {
    try {
      sessionData = JSON.parse(sessionDataInput.value)
    } catch (error) {
      toast.error('Invalid JSON in session data')
      return
    }
  }

  // Reset state
  isRunning.value = true
  executionState.value = 'running'
  completedSteps.value = 0
  statusMessages.value = []
  journeyStore.resetExecution()

  // Connect to WebSocket
  const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
  const wsHost = window.location.host.replace(':5173', ':8000')
  const wsUrl = `${wsProtocol}//${wsHost}/api/ws/journey/${props.journeyId}/execute`

  try {
    ws.value = new WebSocket(wsUrl)

    ws.value.onopen = () => {
      addStatusMessage('Connected to server', 'info')
      
      // Send execution parameters including latest FE nodes/edges
      ws.value.send(
        JSON.stringify({
          baseUrl: baseUrl.value,
          sessionData: sessionData,
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

function formatSessionValue(val) {
  if (typeof val === 'string' && val.length > 30) {
    return val.substring(0, 27) + '...'
  }
  return val
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
