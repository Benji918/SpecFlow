<template>
  <div class="h-full flex flex-col bg-surface">
    <!-- Header -->
    <div class="flex items-center justify-between mb-4 border-b border-gray-800 pb-4">
      <div>
        <h3 class="text-lg font-semibold">{{ node?.data?.summary || 'Step Details' }}</h3>
        <p class="text-xs text-gray-500 font-mono">{{ node?.data?.method }} {{ node?.data?.path }}</p>
      </div>
      <div class="flex space-x-1">
        <button
          @click="runIndependentStep"
          :disabled="!canRunStep"
          :class="[
            'p-2 rounded transition-all',
            canRunStep ? 'text-primary hover:text-white hover:bg-gray-800' : 'text-gray-600 cursor-not-allowed opacity-50'
          ]"
          :title="canRunStep ? 'Run Step Independently (Postman Mode)' : 'Set Base URL or run predecessors first'"
        >
          <Play v-if="!isRunningStep" :size="18" />
          <Loader v-else :size="18" class="animate-spin" />
        </button>
        <button
          v-if="result"
          @click="copyResult"
          class="p-2 text-gray-400 hover:text-white rounded hover:bg-gray-800"
          title="Copy Result"
        >
          <Copy :size="16" />
        </button>
        <button
          @click="$emit('close')"
          class="p-2 text-gray-400 hover:text-white rounded hover:bg-gray-800"
        >
          <X :size="20" />
        </button>
      </div>
    </div>

    <!-- Independent Execution Progress Bar -->
    <div v-if="isRunningStep" class="relative h-0.5 w-full bg-gray-900 overflow-hidden -mt-4 mb-4">
      <div class="absolute inset-0 bg-primary/20"></div>
      <div class="absolute h-full bg-primary shadow-[0_0_10px_rgba(191,245,73,0.8)] animate-premium-progress"></div>
    </div>

    <!-- Tabs -->
    <div class="flex border-b border-gray-800 mb-4">
      <button
        v-for="tab in availableTabs"
        :key="tab.id"
        @click="activeTab = tab.id"
        :class="[
          'px-4 py-2 text-sm font-medium transition-colors border-b-2',
          activeTab === tab.id
            ? 'text-primary border-primary'
            : 'text-gray-400 border-transparent hover:text-white',
        ]"
      >
        {{ tab.label }}
      </button>
    </div>

    <!-- Tab Content -->
    <div class="flex-1 overflow-auto min-h-0">
      <!-- Configuration Tab (Editable) -->
      <div v-if="activeTab === 'config'" class="space-y-6">
        <div>
          <div class="flex items-center justify-between mb-2">
            <div class="flex items-center space-x-3 overflow-hidden">
              <h4 class="text-xs font-bold text-gray-400 uppercase tracking-wider shrink-0">Request Body</h4>
              <div v-if="isBodyFromSchema" class="flex items-center space-x-1.5 px-2 py-0.5 rounded-full bg-blue-500/10 border border-blue-500/20 whitespace-nowrap">
                <div class="w-1 h-1 rounded-full bg-blue-400 animate-pulse"></div>
                <span class="text-[9px] font-black text-blue-400 uppercase tracking-widest">Auto Preview</span>
              </div>
            </div>
            <button
              @click="generateMock"
              class="text-[10px] font-bold text-primary hover:text-white flex items-center bg-primary/5 hover:bg-primary/20 px-2 py-1 rounded-lg border border-primary/10 transition-all"
            >
              <Sparkles :size="10" class="mr-1.5" />
              Generate Mock
            </button>
          </div>
          <textarea
            v-model="editableBody"
            class="w-full h-48 bg-black border border-gray-800 rounded p-3 font-mono text-xs focus:border-primary outline-none transition-all"
            placeholder="{ ... }"
            @input="handleBodyInput"
          ></textarea>

          <!-- Binary Field Notice -->
          <div v-if="hasBinaryField" class="mt-2 p-3 bg-blue-500/5 border border-blue-500/20 rounded-lg flex items-start shadow-sm">
            <AlertCircle :size="16" class="text-blue-400 mr-2 shrink-0 mt-0.5" />
            <div class="space-y-1">
              <p class="text-[11px] font-bold text-blue-300 uppercase tracking-wider">File Upload Information</p>
              <p class="text-[10px] text-blue-200/70 leading-relaxed">
                This endpoint requires a file. Provide a public image URL in the binary property, and our executor will automatically fetch it and perform an actual multipart file upload.
              </p>
            </div>
          </div>
          
          <!-- Request Schema Preview -->
          <div v-if="node?.data?.requestBodySpec" class="mt-2">
            <details class="group">
              <summary class="text-[10px] text-gray-500 cursor-pointer hover:text-gray-300 list-none flex items-center">
                <ChevronRight :size="10" class="mr-1 group-open:rotate-90 transition-transform" />
                View Request Schema
              </summary>
              <pre class="mt-2 bg-black/30 p-2 rounded text-[10px] text-gray-400 font-mono overflow-auto max-h-40 border border-gray-800/50">
                {{ formatJSON(node.data.requestBodySpec) }}
              </pre>
            </details>
          </div>
        </div>

        <div>
          <h4 class="text-sm font-semibold text-gray-400 mb-2">Parameters</h4>
          <div v-if="node?.data?.parameters?.length" class="space-y-3">
            <div v-for="param in node.data.parameters" :key="param.name" class="flex flex-col">
              <label class="text-xs font-mono text-gray-500 mb-1">
                {{ param.name }} <span class="text-gray-700">({{ param.in }})</span>
              </label>
              <input
                v-model="editableParams[param.name]"
                class="bg-black border border-gray-800 rounded p-2 text-xs font-mono outline-none focus:border-primary"
                @input="handleParamsInput"
              />
            </div>
          </div>
          <div v-else class="text-xs text-gray-600 italic">No parameters defined</div>
        </div>

        <!-- Data Mappings Section -->
        <div class="space-y-4">
          <div class="flex items-center space-x-2">
            <LinkIcon :size="14" class="text-primary" />
            <h4 class="text-xs font-bold text-gray-400 uppercase tracking-wider">Intelligence Data Links</h4>
          </div>
          
          <!-- Quick Map From Sources (Prevents clicking wires) -->
          <div v-if="incomingEdges.length" class="space-y-2">
            <div class="text-[9px] text-gray-500 uppercase font-black tracking-widest pl-1">Available Context Sources</div>
            <div class="space-y-1.5">
              <div 
                v-for="edge in incomingEdges" 
                :key="edge.id" 
                class="p-2.5 bg-black/40 border border-gray-800/80 rounded-xl flex items-center justify-between group hover:border-primary/30 transition-all shadow-sm"
              >
                <div class="flex items-center min-w-0">
                  <div :class="['w-1.5 h-1.5 rounded-full mr-2 shrink-0', edge.data?.dataMapping?.length ? 'bg-primary' : 'bg-gray-700']"></div>
                  <div class="min-w-0">
                    <div class="text-[10px] font-bold text-gray-300 truncate">
                      {{ getSourceNode(edge.source)?.data?.summary || 'Previous Step' }}
                    </div>
                  </div>
                </div>
                
                <button 
                  @click="$emit('select-edge', edge)"
                  class="px-2 py-0.5 bg-primary/10 hover:bg-primary text-primary hover:text-black rounded text-[9px] font-black border border-primary/20 transition-all flex items-center uppercase"
                >
                  <ArrowRight :size="10" class="mr-1" />
                  Map
                </button>
              </div>
            </div>
          </div>

          <!-- Active Mappings View -->
          <div v-if="incomingMappings.length || outgoingMappings.length" class="space-y-4 pt-2 border-t border-gray-800/50">
            <!-- Incoming Mappings -->
            <div v-if="incomingMappings.length" class="space-y-2">
              <div class="text-[9px] text-gray-500 uppercase font-black tracking-widest pl-1">Active Incoming Data</div>
              <div class="space-y-1.5">
                <div v-for="(m, i) in incomingMappings" :key="i" class="p-2.5 bg-black/20 border border-gray-800/50 rounded-lg">
                  <div class="flex items-center text-[10px] font-mono justify-between">
                    <div class="px-1.5 py-0.5 rounded bg-blue-500/10 text-blue-400 border border-blue-500/20 truncate max-w-[120px]">
                      {{ m.from.split('.').pop() }}
                    </div>
                    <ArrowRight :size="10" class="mx-2 text-gray-700" />
                    <div class="px-1.5 py-0.5 rounded bg-primary/10 text-primary border border-primary/20 truncate">
                      {{ m.to.split('.').pop() }}
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <!-- Outgoing Mappings -->
            <div v-if="outgoingMappings.length" class="space-y-2">
              <div class="text-[9px] text-gray-500 uppercase font-black tracking-widest pl-1">Providing Data To Next Steps</div>
              <div class="space-y-1.5">
                <div v-for="(m, i) in outgoingMappings" :key="i" class="p-2.5 bg-black/20 border border-gray-800/50 rounded-lg">
                  <div class="flex items-center text-[10px] font-mono justify-between">
                    <div class="px-1.5 py-0.5 rounded bg-primary/10 text-primary border border-primary/20 truncate max-w-[120px]">
                      {{ m.from.split('.').pop() }}
                    </div>
                    <ArrowRight :size="10" class="mx-2 text-gray-700" />
                    <div class="px-1.5 py-0.5 rounded bg-blue-500/10 text-blue-400 border border-blue-500/20 truncate">
                      {{ m.to.split('.').pop() }}
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
          
          <div v-else-if="!incomingEdges.length" class="p-4 bg-black/20 border border-dashed border-gray-800 rounded-xl text-center">
            <p class="text-[10px] text-gray-600 font-bold uppercase tracking-widest">No Intelligence Links</p>
          </div>
        </div>

        <!-- Response Schema Section -->
        <div>
          <h4 class="text-sm font-semibold text-gray-400 mb-2">Expected Responses</h4>
          <div v-if="node?.data?.responses" class="space-y-4">
            <div v-for="(resp, code) in node.data.responses" :key="code" class="border border-gray-800 rounded p-3">
              <div class="flex items-center justify-between mb-2">
                <span :class="['text-xs font-bold px-2 py-0.5 rounded', parseInt(code) < 300 ? 'bg-green-500/10 text-green-500' : 'bg-red-500/10 text-red-500']">
                  {{ code }}
                </span>
                <span class="text-[10px] text-gray-500 uppercase font-mono">{{ resp.description || 'No description' }}</span>
              </div>
              <pre v-if="resp.content?.['application/json']?.schema" class="bg-black/50 p-2 rounded font-mono text-[10px] overflow-auto border border-gray-800/50 max-h-40">
                {{ formatJSON(resp.content['application/json'].schema) }}
              </pre>
            </div>
          </div>
          <div v-else class="text-xs text-gray-600 italic">No response schema available</div>
        </div>
      </div>

      <!-- Execution Result Content -->
      <div v-else-if="result || node?.data?.responses" class="space-y-4">
        <!-- Result Header (Status & Timing) - Only if executed -->
        <div v-if="result" class="flex items-center space-x-4">
          <div
            :class="[
              'px-3 py-1 rounded-full text-sm font-semibold',
              statusClass,
            ]"
          >
            {{ result.statusCode || 'Error' }}
          </div>
          <div v-if="result.duration" class="text-[11px] text-gray-400 font-bold uppercase tracking-widest bg-white/5 px-2 py-1 rounded">
            • {{ Math.round(result.duration) }}ms
          </div>
        </div>

        <!-- If no result yet, show a placeholder or schema -->
        <div v-if="!result" class="bg-blue-500/5 border border-blue-500/20 p-4 rounded text-sm text-blue-400 flex items-center mb-4">
          <AlertCircle :size="16" class="mr-2" />
          Execution pending. Showing default schema.
        </div>

        <!-- Response tab content -->
        <div v-if="activeTab === 'response'" class="space-y-4">
          <div v-if="result?.error">
            <div class="bg-red-500/10 border border-red-500 p-4 rounded text-sm text-red-500">
              {{ result.error }}
            </div>
          </div>
          <div v-else-if="result">
            <div v-if="result.responseBody">
              <h4 class="text-sm font-semibold text-gray-400 mb-2">Response Body</h4>
              <pre class="bg-black/50 p-3 rounded font-mono text-xs overflow-auto border border-gray-800">{{ formatJSON(result.responseBody) }}</pre>
            </div>
            <div v-if="result.headers" class="mt-4">
              <h4 class="text-sm font-semibold text-gray-400 mb-2">Response Headers</h4>
              <pre class="bg-black/50 p-3 rounded font-mono text-xs overflow-auto border border-gray-800">{{ formatJSON(result.headers) }}</pre>
            </div>
          </div>
          <div v-else-if="node?.data?.responses" class="space-y-2">
            <h4 class="text-sm font-semibold text-gray-400 mb-2">Expected Response (Schema)</h4>
            <div v-for="(resp, code) in node.data.responses" :key="code" class="border border-gray-800 rounded p-3">
              <div class="text-xs font-bold text-gray-400 mb-1">Status: {{ code }}</div>
              <pre v-if="resp.content?.['application/json']?.schema" class="bg-black/50 p-2 rounded font-mono text-xs overflow-auto border border-gray-800">
                {{ formatJSON(resp.content['application/json'].schema) }}
              </pre>
            </div>
          </div>
        </div>
        
        <!-- Request tab content -->
        <div v-if="activeTab === 'request'" class="space-y-4">
          <div v-if="result">
            <div>
              <h4 class="text-sm font-semibold text-gray-400 mb-2">URL</h4>
              <div class="bg-black/50 p-3 rounded font-mono text-xs break-all border border-gray-800">
                {{ result.request?.method }} {{ result.request?.url }}
              </div>
            </div>
            <div v-if="result.request?.body">
              <h4 class="text-sm font-semibold text-gray-400 mb-2">Body Sent</h4>
              <pre class="bg-black/50 p-3 rounded font-mono text-xs overflow-auto border border-gray-800">{{ formatJSON(result.request.body) }}</pre>
            </div>
            <div v-if="result.request?.headers" class="mt-4">
              <h4 class="text-sm font-semibold text-gray-400 mb-2">Request Headers</h4>
              <pre class="bg-black/50 p-3 rounded font-mono text-xs overflow-auto border border-gray-800">{{ formatJSON(result.request.headers) }}</pre>
            </div>
          </div>
          <div v-else class="text-xs text-gray-600 italic">No request data available yet</div>
        </div>
      </div>

      <!-- Result Pending state -->
      <div v-else class="flex flex-col items-center justify-center h-full text-gray-600 py-12">
        <Loader :size="32" class="mb-4 opacity-50" />
        <p class="text-sm">Wait for execution or run the journey</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { useToast } from 'vue-toastification'
import { useJourneyStore } from '@/stores/journey'
import { 
  Copy, 
  Sparkles, 
  Loader, 
  AlertCircle, 
  X, 
  ChevronRight, 
  Link as LinkIcon, 
  ArrowRight,
  Play
} from 'lucide-vue-next'
import { generateEndpointMock, generateMockFromSchema } from '@/utils/mockGenerator'

const props = defineProps({
  result: {
    type: Object,
    default: null,
  },
  node: {
    type: Object,
    default: null,
  },
  edges: {
    type: Array,
    default: () => [],
  }
})

const emit = defineEmits(['update-node', 'close'])

const journeyStore = useJourneyStore()
const toast = useToast()
const activeTab = ref('config')
const isRunningStep = ref(false)

const canRunStep = computed(() => {
  if (isRunningStep.value || journeyStore.executionState === 'running') return false
  if (!journeyStore.runnerConfig?.baseUrl) return false
  
  // POSTMAN MODE LOGIC:
  // 1. If we already have a result, we can definitely re-run it
  if (props.result) return true
  
  // 2. If we have authentication context, we can run almost any step
  if (journeyStore.sessionData?.auth_token || journeyStore.sessionData?.token || journeyStore.sessionData?.['headers.Authorization']) return true
  
  // 3. Root nodes are always runnable
  const hasIncoming = props.edges?.some(e => e.target === props.node.id)
  if (!hasIncoming) return true
  
  // 4. If we've run any steps successfully, we might have context
  if (Object.keys(journeyStore.sessionData).length > 0) return true
  
  return false
})

const editableBody = ref('')
const editableParams = ref({})

const isUpdating = ref(false)

// Initialize internal state from node data
watch(() => props.node, (newNode) => {
  if (newNode && !isUpdating.value) {
    // FIX: Handle Manual Journey nodes where requestBody contains the Spec instead of Value
    if (!newNode.data.requestBodySpec && newNode.data.requestBody?.content) {
      // First set the editable body from the schema before emitting update
      const schema = newNode.data.requestBody.content?.['application/json']?.schema
      if (schema) {
        editableBody.value = JSON.stringify(generateMockFromSchema(schema), null, 2)
      }
      
      // Then emit update to normalize the node data
      emit('update-node', props.node.id, {
        requestBodySpec: newNode.data.requestBody,
        requestBody: null
      })
      // Don't return early - continue to set up parameters
    }

    // First priority: Show saved request body value if it exists AND has actual content
    // Note: requestBody can be an empty object {} from backend, which should be treated as "no content"
    const hasRequestBodyContent = newNode.data.requestBody && typeof newNode.data.requestBody === 'object' && Object.keys(newNode.data.requestBody).length > 0
    if (hasRequestBodyContent) {
      editableBody.value = JSON.stringify(newNode.data.requestBody, null, 2)
    } 
    // Second priority: Show request body schema if available (from endpoint spec)
    else if (newNode.data.requestBodySpec) {
      // Extract example from schema to show as preview
      const schema = newNode.data.requestBodySpec.content?.['application/json']?.schema
      if (schema) {
        editableBody.value = JSON.stringify(generateMockFromSchema(schema), null, 2)
      } else {
        editableBody.value = ''
      }
    } 
    // No body defined
    else {
      editableBody.value = ''
    }
    
    // Copy parameters
    const params = {}
    if (newNode.data.parameters) {
      newNode.data.parameters.forEach(p => {
        // Fix: Handle falsey values like boolean false correctly
        params[p.name] = (p.value !== undefined && p.value !== null) ? p.value : ''
        
      })
    }
    editableParams.value = params

    // Switch to response tab if result exists and we just selected a new node
    if (props.result) {
      activeTab.value = 'response'
    } else {
      activeTab.value = 'config'
    }
  }
}, { immediate: true, deep: true })

// Data Mappings Computing
const incomingMappings = computed(() => {
  if (!props.node || !props.edges) return []
  return props.edges
    .filter(e => e.target === props.node.id)
    .flatMap(e => e.data?.dataMapping || [])
})

const outgoingMappings = computed(() => {
  if (!props.node || !props.edges) return []
  return props.edges
    .filter(e => e.source === props.node.id)
    .flatMap(e => e.data?.dataMapping || [])
})

const incomingEdges = computed(() => {
  if (!props.node || !props.edges) return []
  return props.edges.filter(e => e.target === props.node.id)
})

function getSourceNode(sourceId) {
  return props.nodes?.find(n => n.id === sourceId)
}

const hasBinaryField = computed(() => {
  const spec = props.node?.data?.requestBodySpec?.content
  if (!spec) return false
  
  const multipart = spec['multipart/form-data']
  if (!multipart || !multipart.schema || !multipart.schema.properties) return false
  
  return Object.values(multipart.schema.properties).some(prop => prop.format === 'binary')
})

const availableTabs = computed(() => {
  const tabs = [{ id: 'config', label: 'Configure' }]
  // Response tab is now always available if schema exists
  if (props.result || props.node?.data?.responses) {
    tabs.push({ id: 'response', label: 'Response' })
  }
  if (props.result) {
    tabs.push({ id: 'request', label: 'Last Request' })
  }
  return tabs
})

const statusClass = computed(() => {
  if (!props.result?.statusCode) return 'bg-red-500/20 text-red-400'
  const code = props.result.statusCode
  if (code >= 200 && code < 300) return 'bg-green-500/20 text-green-400'
  if (code >= 400) return 'bg-red-500/20 text-red-400'
  return 'bg-blue-500/20 text-blue-400'
})

// Track if current body is from schema (preview) vs user-entered
const isBodyFromSchema = computed(() => {
  if (!props.node?.data) return false
  // If there's no saved requestBody with actual content but there's a requestBodySpec, it's from schema
  const hasRequestBodyContent = props.node.data.requestBody && typeof props.node.data.requestBody === 'object' && Object.keys(props.node.data.requestBody).length > 0
  return !hasRequestBodyContent && props.node.data.requestBodySpec
})

function handleBodyInput() {
  try {
    isUpdating.value = true
    const json = JSON.parse(editableBody.value)
    emit('update-node', props.node.id, { requestBody: json })
  } catch (e) {
    // Wait for valid JSON
  } finally {
    // Allow reactivity to settle before enabling watch again
    setTimeout(() => { isUpdating.value = false }, 100)
  }
}

function handleParamsInput() {
  try {
    isUpdating.value = true
    // Update parameter values in the node data
    if (props.node?.data?.parameters) {
      const updatedParameters = props.node.data.parameters.map(p => ({
        ...p,
        value: editableParams.value[p.name]
      }))
      emit('update-node', props.node.id, { parameters: updatedParameters })
    }
  } finally {
    setTimeout(() => { isUpdating.value = false }, 100)
  }
}

function generateMock() {
  if (!props.node?.data) return

  const mock = generateEndpointMock(props.node.data)
  
  if (mock.body) {
    editableBody.value = JSON.stringify(mock.body, null, 2)
    handleBodyInput()
  }

  if (mock.params) {
    Object.keys(mock.params).forEach(key => {
      editableParams.value[key] = mock.params[key]
    })
    handleParamsInput()
  }

  toast.success('Mock data generated')
}

function formatJSON(data) {
  if (typeof data === 'string') {
    try {
      return JSON.stringify(JSON.parse(data), null, 2)
    } catch { return data }
  }
  return JSON.stringify(data, null, 2)
}


async function copyResult() {
  try {
    const text = JSON.stringify(props.result, null, 2)
    await navigator.clipboard.writeText(text)
    toast.success('Result copied to clipboard!')
  } catch (error) {
    toast.error('Failed to copy')
  }
}

async function runIndependentStep() {
  if (isRunningStep.value) return
  
  const baseUrl = journeyStore.runnerConfig.baseUrl
  if (!baseUrl) {
    toast.warning('Please set a Base URL in the Journey Runner first')
    return
  }

  isRunningStep.value = true
  
  // Build WebSocket URL
  const wsBaseUrl = import.meta.env.VITE_WS_URL || ''
  let wsUrl
  
  if (wsBaseUrl) {
    wsUrl = `${wsBaseUrl}/api/ws/journey/${journeyStore.activeJourney.id}/execute`
  } else {
    const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
    const wsHost = window.location.host.replace(':5173', ':8000')
    wsUrl = `${wsProtocol}//${wsHost}/api/ws/journey/${journeyStore.activeJourney.id}/execute`
  }

  try {
    const ws = new WebSocket(wsUrl)
    
    ws.onopen = () => {
      ws.send(JSON.stringify({
        baseUrl: baseUrl,
        sessionData: journeyStore.sessionData,
        singleStepId: props.node.id,
        nodes: journeyStore.activeJourney.nodes,
        edges: journeyStore.activeJourney.edges
      }))
    }

    ws.onmessage = (event) => {
      const message = JSON.parse(event.data)
      
      if (message.type === 'step_result') {
        journeyStore.saveStepResult(message.result.stepId, message.result)
        toast.success(`Step executed: ${message.result.statusCode}`)
        activeTab.value = 'response'
      } else if (message.type === 'error') {
        toast.error(message.message)
      } else if (message.type === 'execution_complete') {
        isRunningStep.value = false
        ws.close()
      }
    }

    ws.onerror = () => {
      toast.error('Execution failed')
      isRunningStep.value = false
    }

    ws.onclose = () => {
      isRunningStep.value = false
    }
  } catch (error) {
    toast.error('Failed to connect to executor')
    isRunningStep.value = false
  }
}
</script>

<style scoped>
@keyframes premium-progress {
  0% { left: -40%; width: 40%; }
  100% { left: 100%; width: 40%; }
}

.animate-premium-progress {
  animation: premium-progress 1.5s infinite ease-in-out;
}
</style>
