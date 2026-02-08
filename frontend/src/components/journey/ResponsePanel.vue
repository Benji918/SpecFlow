<template>
  <div class="card h-full flex flex-col">
    <div class="flex items-center justify-between mb-4">
      <h3 class="text-lg font-semibold">Execution Results</h3>
      <button
        v-if="result"
        @click="copyToClipboard"
        class="btn-secondary text-xs py-1 px-3"
      >
        <Copy :size="14" class="inline mr-1" />
        Copy
      </button>
    </div>

    <!-- No Result State -->
    <div
      v-if="!result"
      class="flex-1 flex items-center justify-center text-gray-500"
    >
      <div class="text-center">
        <FileQuestion :size="48" class="mx-auto mb-2 text-gray-600" />
        <p>No execution result selected</p>
        <p class="text-sm mt-1">Run a journey or click on a step</p>
      </div>
    </div>

    <!-- Result Display -->
    <div v-else class="flex-1 flex flex-col space-y-4 overflow-auto">
      <!-- Status and Timing -->
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
        <div v-if="result.timestamp" class="text-sm text-gray-400">
          {{ formatTime(result.timestamp) }}
        </div>
      </div>

      <!-- Tabs -->
      <div class="border-b border-gray-800">
        <div class="flex space-x-1">
          <button
            v-for="tab in tabs"
            :key="tab.id"
            @click="activeTab = tab.id"
            :class="[
              'px-4 py-2 text-sm font-medium transition-colors',
              activeTab === tab.id
                ? 'text-primary border-b-2 border-primary'
                : 'text-gray-400 hover:text-white',
            ]"
          >
            {{ tab.label }}
          </button>
        </div>
      </div>

      <!-- Tab Content -->
      <div class="flex-1 overflow-auto">
        <!-- Request Tab -->
        <div v-if="activeTab === 'request'" class="space-y-4">
          <div>
            <h4 class="text-sm font-semibold text-gray-400 mb-2">URL</h4>
            <div class="bg-black/50 p-3 rounded font-mono text-sm break-all">
              {{ result.request?.method || 'GET' }} {{ result.request?.url || 'N/A' }}
            </div>
          </div>

          <div v-if="result.request?.headers">
            <h4 class="text-sm font-semibold text-gray-400 mb-2">Headers</h4>
            <pre class="bg-black/50 p-3 rounded font-mono text-xs overflow-auto">{{ formatJSON(result.request.headers) }}</pre>
          </div>

          <div v-if="result.request?.body">
            <h4 class="text-sm font-semibold text-gray-400 mb-2">Body</h4>
            <pre class="bg-black/50 p-3 rounded font-mono text-xs overflow-auto">{{ formatJSON(result.request.body) }}</pre>
          </div>
        </div>

        <!-- Response Tab -->
        <div v-if="activeTab === 'response'" class="space-y-4">
          <div v-if="result.error">
            <div class="bg-red-500/10 border border-red-500 p-4 rounded">
              <div class="flex items-start space-x-2">
                <AlertCircle :size="20" class="text-red-500 mt-0.5" />
                <div>
                  <h4 class="font-semibold text-red-500">Error</h4>
                  <p class="text-sm text-red-400 mt-1">{{ result.error }}</p>
                </div>
              </div>
            </div>
          </div>

          <div v-else>
            <div v-if="result.headers">
              <h4 class="text-sm font-semibold text-gray-400 mb-2">Headers</h4>
              <pre class="bg-black/50 p-3 rounded font-mono text-xs overflow-auto">{{ formatJSON(result.headers) }}</pre>
            </div>

            <div v-if="result.responseBody">
              <h4 class="text-sm font-semibold text-gray-400 mb-2">Body</h4>
              <pre class="bg-black/50 p-3 rounded font-mono text-xs overflow-auto">{{ formatJSON(result.responseBody) }}</pre>
            </div>
          </div>
        </div>

        <!-- Headers Tab -->
        <div v-if="activeTab === 'headers'" class="space-y-2">
          <div
            v-for="(value, key) in result.headers"
            :key="key"
            class="flex items-start space-x-2 p-2 bg-surface rounded"
          >
            <span class="font-mono text-sm text-gray-400 min-w-[150px]">
              {{ key }}:
            </span>
            <span class="font-mono text-sm break-all">{{ value }}</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useToast } from 'vue-toastification'
import { Copy, FileQuestion, AlertCircle } from 'lucide-vue-next'

const props = defineProps({
  result: {
    type: Object,
    default: null,
  },
})

const toast = useToast()
const activeTab = ref('response')

const tabs = [
  { id: 'response', label: 'Response' },
  { id: 'request', label: 'Request' },
  { id: 'headers', label: 'Headers' },
]

const statusClass = computed(() => {
  if (!props.result?.statusCode) {
    return 'bg-red-500/20 text-red-400'
  }

  const code = props.result.statusCode
  if (code >= 200 && code < 300) {
    return 'bg-green-500/20 text-green-400'
  } else if (code >= 300 && code < 400) {
    return 'bg-blue-500/20 text-blue-400'
  } else if (code >= 400 && code < 500) {
    return 'bg-yellow-500/20 text-yellow-400'
  } else {
    return 'bg-red-500/20 text-red-400'
  }
})

function formatJSON(data) {
  if (typeof data === 'string') {
    try {
      return JSON.stringify(JSON.parse(data), null, 2)
    } catch {
      return data
    }
  }
  return JSON.stringify(data, null, 2)
}

function formatTime(timestamp) {
  const date = new Date(timestamp)
  return date.toLocaleTimeString('en-US', {
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
  })
}

async function copyToClipboard() {
  try {
    const text = JSON.stringify(props.result, null, 2)
    await navigator.clipboard.writeText(text)
    toast.success('Copied to clipboard!')
  } catch (error) {
    toast.error('Failed to copy')
  }
}
</script>
