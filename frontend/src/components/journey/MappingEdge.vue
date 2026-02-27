<script>
export default {
  inheritAttrs: false,
}
</script>

<script setup>
import { computed, inject } from 'vue'
import { BaseEdge, EdgeLabelRenderer, getBezierPath, useVueFlow } from '@vue-flow/core'
import { Database, ArrowUpRight, Plus } from 'lucide-vue-next'

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
  style: Object,
})

const { findEdge } = useVueFlow()
const onEdgeClick = inject('onEdgeClick')

function handleLabelClick() {
  const edge = findEdge(props.id)
  if (edge && onEdgeClick) {
    onEdgeClick({ edge }) 
  }
}

const path = computed(() => getBezierPath(props))

const mappings = computed(() => {
  return props.data?.dataMapping || []
})

const labelText = computed(() => {
  if (!mappings.value || mappings.value.length === 0) {
    return {
      text: 'LINK DATA',
      type: 'empty'
    }
  }
  
  if (mappings.value.length === 1) {
    const m = mappings.value[0]
    // Clean up keys for display
    const cleanFrom = (m.from || '').split('.').pop().replace(/_/g, ' ').replace(/id$/i, 'ID').toUpperCase()
    const cleanTo = (m.to || '').split('.').pop().replace(/_/g, ' ').replace(/id$/i, 'ID').toUpperCase()
    
    return {
      text: `${cleanFrom} → ${cleanTo}`,
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

  <EdgeLabelRenderer>
    <div
      :style="{
        position: 'absolute',
        transform: `translate(-50%, -50%) translate(${path[1]}px,${path[2]}px)`,
        pointerEvents: 'all',
        zIndex: 100,
      }"
      class="nodrag nopan"
    >
      <div 
        :class="[
          'px-3 py-1.5 rounded-full text-[10px] font-black border transition-all cursor-pointer flex items-center space-x-2 backdrop-blur-md shadow-lg group',
          selected 
            ? 'bg-primary text-black border-primary scale-110 shadow-[0_0_20px_rgba(191,245,73,0.6)]' 
            : labelText?.type === 'empty'
              ? 'bg-black/80 text-gray-400 border-gray-700 hover:text-primary hover:border-primary hover:bg-black'
              : 'bg-surface/90 text-primary border-primary/30 hover:scale-105 hover:bg-black hover:border-primary'
        ]"
        @click.stop="handleLabelClick"
      >
        <Plus v-if="labelText?.type === 'empty'" :size="12" class="group-hover:rotate-90 transition-transform" />
        <Database v-else-if="labelText?.type === 'response'" :size="12" />
        <ArrowUpRight v-else-if="labelText?.type === 'request'" :size="12" />
        <Database v-else-if="labelText?.type === 'multiple'" :size="12" />
        
        <span class="tracking-widest uppercase font-black">{{ labelText?.text }}</span>
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

