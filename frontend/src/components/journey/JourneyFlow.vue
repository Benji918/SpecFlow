<template>
  <div class="h-full w-full bg-black rounded-lg overflow-hidden border border-gray-800">
    <VueFlow
      v-model:nodes="nodes"
      v-model:edges="edges"
      :default-viewport="{ zoom: 1 }"
      :min-zoom="0.2"
      :max-zoom="4"
      fit-view-on-init
      @nodes-change="onNodesChange"
      @edges-change="onEdgesChange"
      @node-click="onNodeClick"
      @edge-click="onEdgeClick"
      class="vue-flow-custom"
      :node-types="nodeTypes"
    >
      <Background pattern-color="#333" :gap="16" />
      <Controls />
      <MiniMap />
    </VueFlow>

    <!-- Floating Action Buttons -->
    <div class="absolute bottom-4 right-4 flex flex-col space-y-2">
      <button
        @click="autoLayout"
        class="btn-secondary text-sm py-2 px-3 shadow-lg"
        title="Auto Layout"
      >
        <GitBranch :size="16" class="inline mr-1" />
        Layout
      </button>
      <button
        v-if="hasChanges"
        @click="saveJourney"
        :disabled="saving"
        class="btn-primary text-sm py-2 px-3 shadow-lg"
        title="Save Changes"
      >
        <Save v-if="!saving" :size="16" class="inline mr-1" />
        <Loader v-else :size="16" class="inline mr-1 animate-spin" />
        Save
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, markRaw } from 'vue'
import { VueFlow, useVueFlow } from '@vue-flow/core'
import { Background } from '@vue-flow/background'
import { Controls } from '@vue-flow/controls'
import { MiniMap } from '@vue-flow/minimap'
import { useJourneyStore } from '@/stores/journey'
import { useToast } from 'vue-toastification'
import { Save, GitBranch, Loader } from 'lucide-vue-next'
import EndpointNode from './EndpointNode.vue'

const props = defineProps({
  journeyId: {
    type: String,
    required: true,
  },
  initialNodes: {
    type: Array,
    default: () => [],
  },
  initialEdges: {
    type: Array,
    default: () => [],
  },
})

const emit = defineEmits(['node-selected', 'save'])

const journeyStore = useJourneyStore()
const toast = useToast()
const { fitView } = useVueFlow()

// Register custom node type
const nodeTypes = {
  endpoint: markRaw(EndpointNode),
}

const nodes = ref([...props.initialNodes])
const edges = ref([...props.initialEdges])
const selectedNode = ref(null)
const hasChanges = ref(false)
const saving = ref(false)
const originalState = ref(JSON.stringify({ nodes: props.initialNodes, edges: props.initialEdges }))

// Watch for changes
watch([nodes, edges], () => {
  const currentState = JSON.stringify({ nodes: nodes.value, edges: edges.value })
  hasChanges.value = currentState !== originalState.value
}, { deep: true })

function onNodesChange(changes) {
  // VueFlow handles this automatically with v-model
}

function onEdgesChange(changes) {
  // VueFlow handles this automatically with v-model
}

function onNodeClick(event) {
  selectedNode.value = event.node
  emit('node-selected', event.node)
}

function onEdgeClick(event) {
  // Can implement edge editing here
  console.log('Edge clicked:', event.edge)
}

function autoLayout() {
  // Vertical layout with fixed spacing
  const nodeHeight = 120
  const nodeSpacing = 100
  
  nodes.value.forEach((node, index) => {
    node.position = {
      x: 300, // Centered
      y: index * (nodeHeight + nodeSpacing),
    }
  })

  // Recreate edges to ensure they're connected properly
  edges.value = []
  for (let i = 0; i < nodes.value.length - 1; i++) {
    edges.value.push({
      id: `e${i}-${i + 1}`,
      source: nodes.value[i].id,
      target: nodes.value[i + 1].id,
      type: 'smoothstep',
      animated: true,
    })
  }

  // Fit viewport
  setTimeout(() => {
    fitView({ padding: 0.2, duration: 300 })
  }, 100)

  toast.success('Layout updated')
}

async function saveJourney() {
  saving.value = true

  const result = await journeyStore.updateJourney(props.journeyId, {
    nodes: nodes.value,
    edges: edges.value,
  })

  if (result.success) {
    toast.success('Journey saved!')
    originalState.value = JSON.stringify({ nodes: nodes.value, edges: edges.value })
    hasChanges.value = false
    emit('save', result.data)
  } else {
    toast.error(result.error || 'Failed to save journey')
  }

  saving.value = false
}

// Expose methods to parent
defineExpose({
  autoLayout,
  saveJourney,
  nodes,
  edges,
})
</script>

<style>
/* VueFlow custom styles are in main.css */
.vue-flow-custom {
  background-color: #000;
}
</style>
