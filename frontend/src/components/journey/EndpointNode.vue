<template>
  <div
    :class="[
      'px-4 py-3 rounded-lg border-2 shadow-lg min-w-[280px] transition-all',
      nodeClasses,
    ]"
  >
    <!-- Node Header -->
    <div class="flex items-center justify-between mb-3">
      <div class="flex items-center space-x-2">
        <span
          :class="[
            'px-2 py-1 rounded font-mono text-xs font-bold',
            methodColor,
          ]"
        >
          {{ data.method }}
        </span>
        <span
          v-if="data.status"
          :class="['w-2 h-2 rounded-full', statusColor]"
        ></span>
      </div>
      <button
        @click.stop="$emit('delete')"
        class="text-gray-400 hover:text-red-500 transition-colors"
      >
        <X :size="16" />
      </button>
    </div>

    <!-- Node Content -->
    <div class="space-y-2">
      <div class="font-mono text-sm font-semibold text-white">
        {{ data.path }}
      </div>
      <div v-if="data.summary" class="text-xs text-gray-400">
        {{ data.summary }}
      </div>
      <div v-if="data.operationId" class="text-xs text-gray-500 font-mono">
        {{ data.operationId }}
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
      class="!w-3 !h-3 !bg-primary !border-2 !border-gray-900"
    />
    <Handle
      v-if="!isLast"
      type="source"
      :position="Position.Bottom"
      class="!w-3 !h-3 !bg-primary !border-2 !border-gray-900"
    />
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { Handle, Position } from '@vue-flow/core'
import { X } from 'lucide-vue-next'

const props = defineProps({
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

defineEmits(['delete', 'view-result'])

const nodeClasses = computed(() => {
  const classes = ['bg-surface']

  if (props.selected) {
    classes.push('border-primary shadow-glow')
  } else {
    classes.push('border-gray-700')
  }

  if (props.data.status) {
    if (props.data.status === 'running') {
      classes.push('animate-pulse')
    } else if (props.data.status === 'error') {
      classes.push('border-red-500')
    } else if (props.data.status === 'success') {
      classes.push('border-green-500')
    }
  }

  return classes.join(' ')
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
