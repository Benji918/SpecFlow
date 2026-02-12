<script setup>
import { computed } from 'vue'
import { BaseEdge, EdgeLabelRenderer, getBezierPath } from '@vue-flow/core'

const props = defineProps({
  id: {
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
})

const path = computed(() => getBezierPath(props))

const mappings = computed(() => {
  return props.data?.dataMapping || []
})

const labelText = computed(() => {
  if (!mappings.value || mappings.value.length === 0) return null
  if (mappings.value.length === 1) {
    const m = mappings.value[0]
    return `${String(m.from || '').replace('response.', '')} → ${m.to || '?'}`
  }
  return `${mappings.value.length} mappings`
})
</script>

<template>
  <BaseEdge :id="id" :path="path[0]" :style="{ strokeWidth: selected ? 4 : 3 }" />

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
          'px-2 py-1 rounded-md text-[10px] font-mono border transition-all cursor-pointer',
          selected ? 'bg-primary text-black border-primary scale-110 shadow-lg' : 'bg-surface border-gray-700 text-gray-400 hover:border-primary/50'
        ]"
        @click="$emit('edge-click', { id, data })"
      >
        {{ labelText }}
      </div>
    </div>
  </EdgeLabelRenderer>
</template>

<style scoped>
.edge-label {
  pointer-events: all;
}
</style>
