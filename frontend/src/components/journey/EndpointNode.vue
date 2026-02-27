<template>
  <div
    :class="[
      'px-4 py-3 rounded-lg border-2 shadow-lg min-w-[280px] transition-all',
      nodeClasses,
    ]"
  >
    <!-- Node Header -->
    <div class="flex items-center justify-between mb-3 pb-2 border-b border-gray-800/50">
      <div class="flex items-center space-x-2">
        <span
          :class="[
            'px-2 py-0.5 rounded font-mono text-[10px] font-bold uppercase tracking-wider',
            methodColor,
          ]"
        >
          {{ data.method }}
        </span>
        
        <!-- Status Indicator -->
        <div class="flex items-center">
          <div v-if="data.status === 'running'" class="flex space-x-1 ml-1">
            <div class="w-1.5 h-1.5 bg-primary rounded-full animate-bounce"></div>
            <div class="w-1.5 h-1.5 bg-primary rounded-full animate-bounce [animation-delay:0.2s]"></div>
            <div class="w-1.5 h-1.5 bg-primary rounded-full animate-bounce [animation-delay:0.4s]"></div>
          </div>
          <div v-else-if="data.status === 'success'" class="text-green-500 ml-1">
            <CheckCircle :size="14" />
          </div>
          <div v-else-if="data.status === 'error'" class="text-red-500 ml-1">
            <AlertCircle :size="14" />
          </div>
          <div v-else :class="['w-2 h-2 rounded-full ml-1', statusColor]"></div>
        </div>
      </div>
      <button
        @click.stop="handleDelete"
        class="text-gray-500 hover:text-red-500 transition-colors p-1"
      >
        <X :size="14" />
      </button>
    </div>

    <!-- Node Content -->
    <div class="space-y-2">
      <div class="font-mono text-sm font-semibold text-white break-all">
        {{ data.path }}
      </div>
      <div v-if="data.summary" class="text-xs text-gray-400">
        {{ data.summary }}
      </div>
      
      <!-- Mini Preview -->
      <div class="mt-2 space-y-1">
        <div v-if="data.responses" class="flex flex-col">
          <span class="text-[10px] text-gray-500 uppercase font-bold">Expected Response</span>
          <div class="flex flex-wrap gap-1 mt-0.5">
            <span v-for="(resp, code) in data.responses" :key="code" 
              :class="['text-[8px] px-1 rounded font-bold', parseInt(code) < 300 ? 'bg-green-500/20 text-green-500' : 'bg-red-500/20 text-red-500']">
              {{ code }}
            </span>
          </div>
        </div>

        <!-- Data Link Indicator -->
        <div v-if="data.dataMapping?.length" class="flex items-center space-x-1 px-2 py-1 rounded bg-primary/10 border border-primary/20 w-fit">
          <Database :size="10" class="text-primary" />
          <span class="text-[9px] font-black text-primary uppercase tracking-widest">
            {{ data.dataMapping.length }} Data Links
          </span>
        </div>
      </div>
    </div>

    <!-- Execution Result (if available) -->
    <div v-if="executionResult" class="mt-3 pt-3 border-t border-gray-700">
      <div class="flex items-center justify-between text-xs">
        <span class="text-gray-400">
          {{ executionResult.statusCode }}
          <span v-if="executionResult.duration">
            • {{ Math.round(executionResult.duration) }}ms
          </span>
        </span>
        <button
          @click.stop="$emit('view-result', executionResult)"
          class="text-primary hover:underline"
        >
          View
        </button>
      </div>
    </div>

    <!-- Handles for connections -->
    <Handle
      v-if="!isFirst"
      type="target"
      :position="Position.Top"
      :connectable="true"
      class="!w-3 !h-3 !bg-primary !border-2 !border-gray-900"
    />
    <Handle
      v-if="!isLast"
      type="source"
      :position="Position.Bottom"
      :connectable="true"
      class="!w-3 !h-3 !bg-primary !border-2 !border-gray-900"
    />
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { Handle, Position, useVueFlow } from '@vue-flow/core'
import { X, CheckCircle, AlertCircle } from 'lucide-vue-next'

const props = defineProps({
  id: {
    type: String,
    required: true,
  },
  data: {
    type: Object,
    required: true,
  },
  isFirst: {
    type: Boolean,
    default: false,
  },
  isLast: {
    type: Boolean,
    default: false,
  },
  selected: {
    type: Boolean,
    default: false,
  },
  executionResult: {
    type: Object,
    default: null,
  },
})

const emit = defineEmits(['view-result'])

const { removeNodes } = useVueFlow()

function handleDelete() {
  removeNodes([props.id])
}

const nodeClasses = computed(() => {
  return [
    props.selected ? 'border-primary ring-2 ring-primary/20 scale-[1.02]' : 'border-gray-800',
    props.data.status === 'running' ? 'shadow-[0_0_20px_rgba(191,245,73,0.3)] border-primary/50' : '',
    props.data.status === 'success' ? 'shadow-[0_0_20px_rgba(34,197,94,0.2)] border-green-500/40' : '',
    props.data.status === 'error' ? 'shadow-[0_0_20px_rgba(239,68,68,0.2)] border-red-500/40' : '',
    'bg-surface/80 backdrop-blur-sm'
  ].join(' ')
})

const methodColor = computed(() => {
  const colors = {
    GET: 'bg-blue-500/20 text-blue-400 border border-blue-500/30',
    POST: 'bg-green-500/20 text-green-400 border border-green-500/30',
    PUT: 'bg-yellow-500/20 text-yellow-400 border border-yellow-500/30',
    DELETE: 'bg-red-500/20 text-red-400 border border-red-500/30',
    PATCH: 'bg-purple-500/20 text-purple-400 border border-purple-500/30',
  }
  return colors[props.data.method] || 'bg-gray-500/20 text-gray-400'
})

const statusColor = computed(() => {
  const colors = {
    pending: 'bg-gray-500',
    running: 'bg-yellow-500 animate-pulse',
    success: 'bg-green-500',
    error: 'bg-red-500',
  }
  return colors[props.data.status] || 'bg-gray-500'
})
</script>
