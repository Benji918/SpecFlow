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
      @edge-update="onEdgeUpdate"
      class="vue-flow-custom"
      :node-types="nodeTypes"
      :edge-types="edgeTypes"
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
import { ref, computed, watch, markRaw, provide } from 'vue'
import { VueFlow, useVueFlow, updateEdge } from '@vue-flow/core'
import { Background } from '@vue-flow/background'
import { Controls } from '@vue-flow/controls'
import { MiniMap } from '@vue-flow/minimap'

// Import Vue Flow styles are now in <style> block
import { useJourneyStore } from '@/stores/journey'
import { useToast } from 'vue-toastification'
import { Save, GitBranch, Loader } from 'lucide-vue-next'
import EndpointNode from './EndpointNode.vue'
import MappingEdge from './MappingEdge.vue'

import { detectMappings } from '@/utils/mappingUtils'

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

const emit = defineEmits(['node-selected', 'save', 'edge-selected'])

const journeyStore = useJourneyStore()
const toast = useToast()
const { fitView, onConnect, addEdges } = useVueFlow()

// Handle new connections
// Handle new connections
onConnect((params) => {
  const sourceNode = nodes.value.find(n => n.id === params.source)
  const targetNode = nodes.value.find(n => n.id === params.target)
  
  const detectedMappings = detectMappings(sourceNode, targetNode)
  
  const edge = {
    ...params,
    id: `e-${params.source}-${params.target}-${Date.now()}`,
    type: 'mapping',
    animated: true,
    updatable: true,
    data: {
      dataMapping: detectedMappings
    }
  }
  
  // FIX: Update local ref directly so it syncs with v-model and save logic
  edges.value.push(edge)
  
  if (detectedMappings.length > 0) {
    toast.success(`Auto-mapped ${detectedMappings.length} parameters!`)
  }
})

// Handle edge updates (reconnecting)
function onEdgeUpdate({ edge, connection }) {
  // Use VueFlow's updateEdge utility to correctly handle the update
  edges.value = updateEdge(edge, connection, edges.value)
  toast.success('Connection updated, data mappings preserved')
}

// Register custom node and edge types
const nodeTypes = {
  endpoint: markRaw(EndpointNode),
}

const edgeTypes = {
  mapping: markRaw(MappingEdge),
}

const nodes = ref([...props.initialNodes])
const edges = ref(props.initialEdges.map(e => ({ ...e, updatable: true })))
const selectedNode = ref(null)
const selectedEdge = ref(null)
const hasChanges = ref(false)
const saving = ref(false)
const originalState = ref(JSON.stringify({ nodes: props.initialNodes, edges: props.initialEdges }))

// Watch for changes and track state
watch([nodes, edges], () => {
    const currentState = JSON.stringify({ nodes: nodes.value, edges: edges.value })
    hasChanges.value = currentState !== originalState.value
}, { deep: true })

// Sync from props if they change externally
watch(() => props.initialNodes, (newNodes) => {
    nodes.value = [...newNodes]
    originalState.value = JSON.stringify({ nodes: nodes.value, edges: edges.value })
}, { deep: true })

watch(() => props.initialEdges, (newEdges) => {
    // Ensure all edges are updatable when loaded
    edges.value = newEdges.map(e => ({ ...e, updatable: true }))
    originalState.value = JSON.stringify({ nodes: nodes.value, edges: edges.value })
}, { deep: true })

function onNodesChange(changes) {
  // VueFlow handles this automatically with v-model
}

function onEdgesChange(changes) {
  // VueFlow handles this automatically with v-model
}

function onNodeClick(event) {
  selectedNode.value = event.node
  selectedEdge.value = null
  emit('node-selected', event.node)
}

function onEdgeClick(event) {
  selectedEdge.value = event.edge
  selectedNode.value = null
  emit('edge-selected', event.edge)
}

// Provide edge click handler for custom edges
provide('onEdgeClick', onEdgeClick)

function autoLayout() {
  // Vertical layout with fixed spacing
  const nodeHeight = 120
  const nodeSpacing = 120
  
  // Sort nodes topologically so they follow the execution flow
  const sortedNodes = getSortedNodes(nodes.value, edges.value)
  
  // Create new array to ensure reactivity
  const newNodes = sortedNodes.map((node, index) => ({
    ...node,
    position: {
      x: 300, // Centered
      y: index * (nodeHeight + nodeSpacing),
    }
  }))
  
  nodes.value = newNodes

  // Fit viewport
  setTimeout(() => {
    fitView({ padding: 0.2, duration: 300 })
  }, 100)

  toast.success('Layout updated')
}

function clearAllMappings() {
  // 1. Clear edges data mapping
  // We map the array and ensure each edge gets a fresh reference with empty dataMapping
  edges.value = edges.value.map(edge => {
    return {
      ...edge,
      data: {
        ...edge.data,
        dataMapping: []
      }
    }
  })

  // 2. Clear nodes data (parameters values)
  // We carefully preserve data.requestBody while clearing parameter values
  nodes.value = nodes.value.map(node => {
     if (!node.data) return node
     
     const newData = { ...node.data }
     
     // Clear parameters if they exist
     if (newData.parameters) {
       newData.parameters = newData.parameters.map(p => ({
         ...p,
         value: ''
       }))
     }
     
     // Reset status for a fresh visual state
     newData.status = 'pending'
     
     // CRITICAL: We do NOT touch newData.requestBody here
     
     return {
       ...node,
       data: newData
     }
  })

  toast.success('All data links and node mappings cleared')
}

function getSortedNodes(nodesList, edgesList) {
  // 1. Build graph helpers
  const inDegree = new Map()
  const adj = new Map()
  const nodeMap = new Map()

  nodesList.forEach(node => {
    inDegree.set(node.id, 0)
    adj.set(node.id, [])
    nodeMap.set(node.id, node)
  })

  edgesList.forEach(edge => {
    // Only count edges that connect two existing nodes
    if (nodeMap.has(edge.source) && nodeMap.has(edge.target)) {
      adj.get(edge.source).push(edge.target)
      inDegree.set(edge.target, (inDegree.get(edge.target) || 0) + 1)
    }
  })

  // 2. Initialize Queue with 0 in-degree nodes
  const queue = []
  inDegree.forEach((count, id) => {
    if (count === 0) {
      queue.push(nodeMap.get(id))
    }
  })

  // Sort initial queue by Y position to respect visual order for independent start nodes
  queue.sort((a, b) => a.position.y - b.position.y)

  const sorted = []
  
  while (queue.length > 0) {
    const u = queue.shift()
    sorted.push(u)

    const neighbors = adj.get(u.id) || []
    
    // We collect newly available nodes to sort them before adding to queue
    const nextNodes = []
    neighbors.forEach(vId => {
      inDegree.set(vId, inDegree.get(vId) - 1)
      if (inDegree.get(vId) === 0) {
        nextNodes.push(nodeMap.get(vId))
      }
    })
    
    // Sort next batch by Y before adding to queue to maintain determinism
    nextNodes.sort((a, b) => a.position.y - b.position.y)
    queue.push(...nextNodes)
  }

  // 3. Fallback for cycles: if we didn't visit all nodes, append the rest sorted by Y
  if (sorted.length !== nodesList.length) {
    const visited = new Set(sorted.map(n => n.id))
    const unvisited = nodesList.filter(n => !visited.has(n.id))
    unvisited.sort((a, b) => a.position.y - b.position.y)
    return [...sorted, ...unvisited]
  }

  return sorted
}

async function saveJourney() {
  saving.value = true

  // Sort nodes based on execution flow (Topological + Y-position)
  // This ensures the backend executes them in the correct visual order
  const sortedNodes = getSortedNodes(nodes.value, edges.value)
  
  // Update local nodes ref to match sorted order
  nodes.value = sortedNodes

  const result = await journeyStore.updateJourney(props.journeyId, {
    nodes: sortedNodes,
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
  clearAllMappings,
  saveJourney,
  nodes,
  edges,
})
</script>

<style>
/* Import Vue Flow styles */
@import '@vue-flow/core/dist/style.css';
@import '@vue-flow/core/dist/theme-default.css';
@import '@vue-flow/controls/dist/style.css';
@import '@vue-flow/minimap/dist/style.css';

.vue-flow-custom {
  height: 100%;
  width: 100%;
  background: transparent;
}

/* Ensure custom edges and nodes have correct z-indexing and styling */
.vue-flow__node-endpoint {
  z-index: 10;
}

.vue-flow__edge-mapping {
  z-index: 5;
}

/* Remove default stroke override to allow custom edge animations to work */
.vue-flow__edge-path {
  stroke-width: 3px;
}
</style>
