<template>
  <div class="h-full flex flex-col bg-surface">
    <!-- Header -->
    <div class="flex items-center justify-between mb-4 border-b border-gray-800 pb-4">
      <div>
        <h3 class="text-lg font-semibold">{{ node?.data?.summary || 'Step Details' }}</h3>
        <p class="text-xs text-gray-500 font-mono">{{ node?.data?.method }} {{ node?.data?.path }}</p>
      </div>
      <div class="flex space-x-2">
        <button
          v-if="result"
          @click="copyResult"
          class="p-2 text-gray-400 hover:text-white rounded hover:bg-gray-800"
          title="Copy Result"
        >
          <Copy :size="16" />
        </button>
      </div>
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
            <h4 class="text-sm font-semibold text-gray-400">Request Body (JSON)</h4>
            <button
              @click="generateMock"
              class="text-xs text-primary hover:underline flex items-center"
            >
              <Sparkles :size="12" class="mr-1" />
              Generate Mock
            </button>
          </div>
          <textarea
            v-model="editableBody"
            class="w-full h-64 bg-black border border-gray-800 rounded p-3 font-mono text-xs focus:border-primary outline-none transition-all"
            placeholder="{ ... }"
            @input="handleBodyInput"
          ></textarea>
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
      </div>

      <!-- Execution Result Content -->
      <div v-else-if="result" class="space-y-4">
        <!-- Status & Timing -->
        <div class="flex items-center space-x-4">
          <div
            :class="[
              'px-3 py-1 rounded-full text-sm font-semibold',
              statusClass,
            ]"
          >
            {{ result.statusCode || 'Error' }}
          </div>
          <div v-if="result.duration" class="text-sm text-gray-400">
            {{ Math.round(result.duration) }}ms
          </div>
        </div>

        <!-- Request Result -->
        <div v-if="activeTab === 'request'" class="space-y-4">
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
          <div v-if="result.request?.headers">
            <h4 class="text-sm font-semibold text-gray-400 mb-2">Headers Sent</h4>
            <pre class="bg-black/50 p-3 rounded font-mono text-xs overflow-auto border border-gray-800">{{ formatJSON(result.request.headers) }}</pre>
          </div>
        </div>

        <!-- Response Result -->
        <div v-if="activeTab === 'response'" class="space-y-4">
          <div v-if="result.error">
            <div class="bg-red-500/10 border border-red-500 p-4 rounded text-sm text-red-500">
              {{ result.error }}
            </div>
          </div>
          <div v-else>
            <div v-if="result.responseBody">
              <h4 class="text-sm font-semibold text-gray-400 mb-2">Response Body</h4>
              <pre class="bg-black/50 p-3 rounded font-mono text-xs overflow-auto border border-gray-800">{{ formatJSON(result.responseBody) }}</pre>
            </div>
            <div v-if="result.headers" class="mt-4">
              <h4 class="text-sm font-semibold text-gray-400 mb-2">Response Headers</h4>
              <pre class="bg-black/50 p-3 rounded font-mono text-xs overflow-auto border border-gray-800">{{ formatJSON(result.headers) }}</pre>
            </div>
          </div>
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
import { Copy, Sparkles, Loader, AlertCircle } from 'lucide-vue-next'
import { generateEndpointMock } from '@/utils/mockGenerator'

const props = defineProps({
  result: {
    type: Object,
    default: null,
  },
  node: {
    type: Object,
    default: null,
  }
})

const emit = defineEmits(['update-node'])

const toast = useToast()
const activeTab = ref('config')

const editableBody = ref('')
const editableParams = ref({})

// Initialize internal state from node data
watch(() => props.node, (newNode) => {
  if (newNode) {
    editableBody.value = newNode.data.requestBody 
      ? JSON.stringify(newNode.data.requestBody, null, 2)
      : ''
    
    // Copy parameters
    const params = {}
    if (newNode.data.parameters) {
      newNode.data.parameters.forEach(p => {
        params[p.name] = p.value || ''
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
}, { immediate: true })

// Tabs toggle based on if result exists
const availableTabs = computed(() => {
  const tabs = [{ id: 'config', label: 'Configure' }]
  if (props.result) {
    tabs.push({ id: 'response', label: 'Response' })
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

function handleBodyInput() {
  try {
    const json = JSON.parse(editableBody.value)
    emit('update-node', props.node.id, { requestBody: json })
  } catch (e) {
    // Wait for valid JSON
  }
}

function handleParamsInput() {
  // Update parameter values in the node data
  if (props.node?.data?.parameters) {
    const updatedParameters = props.node.data.parameters.map(p => ({
      ...p,
      value: editableParams.value[p.name]
    }))
    emit('update-node', props.node.id, { parameters: updatedParameters })
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
</script>
