<script>
export default {
  inheritAttrs: false,
}
</script>

<script setup>
import { computed } from 'vue'
import { BaseEdge, EdgeLabelRenderer, getBezierPath } from '@vue-flow/core'
import { Database, ArrowUpRight } from 'lucide-vue-next'

const props = defineProps({
  id: {
    type: String,
    required: true,
  },
  source: {
    type: String,
    required: true,
  },
  target: {
    type: String,
    required: true,
  },
  sourceX: {
    type: Number,
    required: true,
  },
  sourceY: {
    type: Number,
    required: true,
  },
  targetX: {
    type: Number,
    required: true,
  },
  targetY: {
    type: Number,
    required: true,
  },
  sourcePosition: {
    type: String,
    required: true,
  },
  targetPosition: {
    type: String,
    required: true,
  },
  data: {
    type: Object,
    default: () => ({}),
  },
  selected: {
    type: Boolean,
    default: false,
  },
  sourceNode: {
    type: Object,
    required: false,
  },
  targetNode: {
    type: Object,
    required: false,
  },
  type: String,
  updatable: Boolean,
  animated: Boolean,
  label: [String, Object],
  labelStyle: Object,
  labelShowBg: Boolean,
  labelBgStyle: Object,
  labelBgPadding: Array,
  labelBgBorderRadius: Number,
  markerStart: String,
  markerEnd: String,
  sourceHandleId: String,
  targetHandleId: String,
  interactionWidth: Number,
  events: Object,
  style: Object,
})

const path = computed(() => getBezierPath(props))

const mappings = computed(() => {
  return props.data?.dataMapping || []
})

const labelText = computed(() => {
  if (!mappings.value || mappings.value.length === 0) return null
  if (mappings.value.length === 1) {
    const m = mappings.value[0]
    return {
      text: `${String(m.from || '').split('.').pop()} → ${String(m.to || '').split('.').pop()}`,
      type: (m.from || '').startsWith('request') ? 'request' : 'response'
    }
  }
  return {
    text: `${mappings.value.length} LINKS`,
    type: 'multiple'
  }
})
</script>

<template>
  <g :class="{ 'is-selected': selected }">
    <path
      :id="id"
      :d="path[0]"
      class="mapping-edge-bg"
      fill="none"
    />

    <path
      :d="path[0]"
      class="mapping-edge-flow"
      fill="none"
      :stroke-dasharray="selected ? '10, 20' : '4, 16'"
    />
  </g>

  <EdgeLabelRenderer v-if="labelText">
    <div
      :style="{
        position: 'absolute',
        transform: `translate(-50%, -50%) translate(${path[1]}px,${path[2]}px)`,
        pointerEvents: 'all',
      }"
      class="nodrag nopan"
    >
      <div 
        :class="[
          'px-2 py-1 rounded-full text-[9px] font-black border transition-all cursor-pointer flex items-center space-x-1.5 backdrop-blur-md',
          selected 
            ? 'bg-primary text-black border-primary scale-110 shadow-[0_0_15px_rgba(191,245,73,0.4)]' 
            : 'bg-black/60 border-gray-700 text-gray-400 hover:border-primary/50'
        ]"
        @click="$emit('edge-click', { id, data })"
      >
        <Database v-if="labelText.type === 'response'" :size="10" />
        <ArrowUpRight v-if="labelText.type === 'request'" :size="10" />
        <span class="tracking-widest uppercase">{{ labelText.text }}</span>
      </div>
    </div>
  </EdgeLabelRenderer>
</template>

<style scoped>
.mapping-edge-bg {
  stroke: rgba(191, 245, 73, 0.1);
  stroke-width: 3;
}

.mapping-edge-flow {
  stroke: #BFF549;
  stroke-width: 3;
  stroke-linecap: round;
  animation: svg-flow 1.5s linear infinite;
  filter: drop-shadow(0 0 3px rgba(191, 245, 73, 0.4));
}

.is-selected .mapping-edge-flow {
  stroke-width: 5;
  animation-duration: 0.8s;
  filter: drop-shadow(0 0 8px rgba(191, 245, 73, 0.8));
}

@keyframes svg-flow {
  from {
    stroke-dashoffset: 40;
  }
  to {
    stroke-dashoffset: 0;
  }
}

.edge-label {
  pointer-events: all;
}
</style>

