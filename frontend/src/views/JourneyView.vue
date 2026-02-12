<template>
  <div class="min-h-screen bg-background">
    <!-- Header -->
    <header class="border-b border-gray-800 bg-surface/50 backdrop-blur-lg sticky top-0 z-10">
      <div class="max-w-full px-4 py-4">
        <div class="flex items-center justify-between">
          <div class="flex items-center space-x-4">
            <button @click="router.push('/dashboard')" class="text-gray-400 hover:text-white">
              <ArrowLeft :size="24" />
            </button>
            <div>
              <h1 class="text-2xl font-bold">{{ journey?.name || 'Journey' }}</h1>
              <p v-if="journey" class="text-sm text-gray-400">
                {{ journey.nodes?.length || 0 }} steps
              </p>
            </div>
          </div>
          <div class="flex items-center space-x-3">
            <button
              @click="prefillAllMockData"
              class="btn-secondary text-sm py-2 px-4"
              title="Generate mock data for all steps"
            >
              <Sparkles :size="16" class="inline mr-2" />
              Prefill All
            </button>
            <button
              @click="clearAllMappings"
              class="btn-secondary text-sm py-2 px-4 hover:bg-red-500/10 hover:text-red-400"
              title="Clear all mappings and prefilled data"
            >
              <Link2Off :size="16" class="inline mr-2" />
              Clear Mappings
            </button>
            <button
              @click="showRunner = !showRunner"
              :class="[
                'btn-secondary text-sm py-2 px-4',
                showRunner && 'bg-primary/20 text-primary',
              ]"
            >
              <PlayCircle :size="16" class="inline mr-2" />
              {{ showRunner ? 'Hide' : 'Show' }} Runner
            </button>
            <button
              @click="handleDeleteJourney"
              class="btn-secondary text-sm py-2 px-4 hover:bg-red-500/20 hover:text-red-500"
            >
              <Trash2 :size="16" class="inline mr-2" />
              Delete
            </button>
          </div>
        </div>
      </div>
    </header>

    <main class="h-[calc(100vh-73px)] flex">
      <!-- Loading State -->
      <div v-if="loading" class="flex-1 flex items-center justify-center">
        <Loader :size="48" class="animate-spin text-primary" />
      </div>

      <!-- Main Content -->
      <div v-else-if="journey" class="flex-1 flex relative">
        <!-- Left Panel - Journey Flow -->
        <div :class="['flex-1 relative', (selectedNode || selectedEdge) ? 'mr-96' : '']">
          <JourneyFlow
            ref="flowRef"
            :journey-id="journey.id"
            :initial-nodes="journey.nodes || []"
            :initial-edges="journey.edges || []"
            @node-selected="handleNodeSelected"
            @edge-selected="handleEdgeSelected"
            @save="handleFlowSaved"
          />
        </div>

        <!-- Right Panel - Slide in -->
        <transition name="slide">
          <div
            v-if="selectedNode || selectedEdge"
            class="w-96 border-l border-gray-800 bg-surface overflow-auto absolute right-0 top-0 bottom-0 z-20"
          >
            <div class="p-4">
              <!-- Node Info -->
              <ResponsePanel
                v-if="selectedNode"
                :result="selectedResult"
                :node="selectedNode"
                :edges="journey.edges"
                @update-node="handleNodeUpdate"
                @close="selectedNode = null; selectedResult = null"
              />

              <!-- Edge Info -->
              <MappingPanel
                v-if="selectedEdge"
                :edge="selectedEdge"
                :source-node="journey.nodes.find(n => n.id === selectedEdge.source)"
                :target-node="journey.nodes.find(n => n.id === selectedEdge.target)"
                @update-edge="handleEdgeUpdate"
                @close="selectedEdge = null"
              />
            </div>
          </div>
        </transition>
      </div>

      <!-- Error State -->
      <div v-else class="flex-1 flex items-center justify-center">
        <div class="text-center">
          <AlertCircle :size="48" class="mx-auto text-red-500 mb-4" />
          <p class="text-gray-400">Failed to load journey</p>
          <button @click="router.back()" class="btn-secondary mt-4">
            Go Back
          </button>
        </div>
      </div>
    </main>

    <!-- Bottom Panel - Runner (Slides up) -->
    <div v-if="journey">
      <div v-show="showRunner" class="fixed inset-0 z-[15]" @click="showRunner = false"></div>
      
      <transition name="slide-up">
        <div
          v-show="showRunner"
          class="fixed bottom-0 left-0 right-0 bg-surface border-t border-gray-800 shadow-[0_-10px_40px_rgba(0,0,0,0.5)] z-20"
          style="height: 320px;"
          @click.stop
        >
          <div class="h-full p-4">
            <div class="max-w-[1400px] mx-auto h-full">
              <JourneyRunner
                :journey-id="journey.id"
                :nodes="journey.nodes || []"
                :edges="journey.edges || []"
                @step-start="handleStepStart"
                @step-complete="handleStepComplete"
                @execution-complete="handleExecutionComplete"
                @close="showRunner = false"
              />
            </div>
          </div>
        </div>
      </transition>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useJourneyStore } from '@/stores/journey'
import { useToast } from 'vue-toastification'
import {
  ArrowLeft,
  PlayCircle,
  Trash2,
  Loader,
  AlertCircle,
  X,
  Sparkles,
  Link2Off,
} from 'lucide-vue-next'
import JourneyFlow from '@/components/journey/JourneyFlow.vue'
import JourneyRunner from '@/components/journey/JourneyRunner.vue'
import ResponsePanel from '@/components/journey/ResponsePanel.vue'
import MappingPanel from '@/components/journey/MappingPanel.vue'
import { generateEndpointMock } from '@/utils/mockGenerator'

const router = useRouter()
const route = useRoute()
const journeyStore = useJourneyStore()
const toast = useToast()

const loading = ref(true)
const showRunner = ref(false)
const selectedResult = ref(null)
const selectedNode = ref(null)
const selectedEdge = ref(null)
const flowRef = ref(null)

const journey = computed(() => journeyStore.activeJourney)

onMounted(async () => {
  await fetchJourney()
})

async function fetchJourney() {
  loading.value = true
  const result = await journeyStore.fetchJourney(route.params.id)
  if (!result.success) {
    toast.error('Failed to load journey')
  }
  loading.value = false
}

function handleNodeSelected(node) {
  selectedNode.value = node
  selectedEdge.value = null
  // Find execution result for this node
  const result = journeyStore.executionResults.find(
    (r) => r.stepId === node.id
  )
  selectedResult.value = result || null
}

function handleEdgeSelected(edge) {
  selectedEdge.value = edge
  selectedNode.value = null
  selectedResult.value = null
}

function handleNodeUpdate(nodeId, updates) {
  if (journey.value) {
    const nodeIndex = journey.value.nodes.findIndex(n => n.id === nodeId)
    if (nodeIndex !== -1) {
      // Deep merge updates into node.data
      journey.value.nodes[nodeIndex].data = {
        ...journey.value.nodes[nodeIndex].data,
        ...updates
      }
      
      // Sync with flow component
      if (flowRef.value) {
        const flowNode = flowRef.value.nodes.find(n => n.id === nodeId)
        if (flowNode) {
          flowNode.data = { ...flowNode.data, ...updates }
        }
      }
    }
  }
}

function handleEdgeUpdate(edgeId, updates) {
  if (journey.value) {
    const edgeIndex = journey.value.edges.findIndex(e => e.id === edgeId)
    if (edgeIndex !== -1) {
      journey.value.edges[edgeIndex] = {
        ...journey.value.edges[edgeIndex],
        ...updates
      }

      // Sync with flow component
      if (flowRef.value) {
        const flowEdge = flowRef.value.edges.find(e => e.id === edgeId)
        if (flowEdge) {
          Object.assign(flowEdge, updates)
        }
      }
    }
  }
}

function handleStepStart(stepId) {
  // Update node status in the flow
  if (journey.value) {
    const node = journey.value.nodes.find((n) => n.id === stepId)
    if (node) {
      node.data.status = 'running'
    }
  }
}

function handleStepComplete(result) {
  // Update node status
  if (journey.value) {
    const node = journey.value.nodes.find((n) => n.id === result.stepId)
    if (node) {
      if (result.error || result.statusCode >= 400) {
        node.data.status = 'error'
      } else {
        node.data.status = 'success'
      }
    }
  }

  // Show result if this node is selected
  if (selectedResult.value?.stepId === result.stepId) {
    selectedResult.value = result
  }
}

function handleExecutionComplete(message) {
  if (message) {
    toast.success('Journey execution completed!')
  }
}

function handleFlowSaved(data) {
  // Flow saved successfully
  journeyStore.activeJourney = data
}

function prefillAllMockData() {
  if (!journey.value?.nodes) return
  
  let updatedCount = 0
  journey.value.nodes.forEach(node => {
    // Generate mock data if schema is present
    const mock = generateEndpointMock(node.data)
    const updates = {}
    
    if (mock.body && !node.data.requestBody) {
      updates.requestBody = mock.body
    }
    
    // Also prefill params if empty
    if (mock.params && node.data.parameters) {
      const updatedParams = node.data.parameters.map(p => {
        if (!p.value) {
          return { ...p, value: mock.params[p.name] || '' }
        }
        return p
      })
      
      // Check if anything actually changed in params
      const hasParamChanges = JSON.stringify(updatedParams) !== JSON.stringify(node.data.parameters)
      if (hasParamChanges) {
        updates.parameters = updatedParams
      }
    }
    
    if (Object.keys(updates).length > 0) {
      handleNodeUpdate(node.id, updates)
      updatedCount++
    }
  })
  
  if (updatedCount > 0) {
    toast.success(`Prefilled ${updatedCount} steps with mock data. Don't forget to save!`)
  } else {
    toast.info('No steps needed prefilling.')
  }
}

async function clearAllMappings() {
  if (!confirm('Clear all data links and node mappings? This will also save the journey.')) return
  
  if (flowRef.value) {
    // 1. Call the component method to update local state
    flowRef.value.clearAllMappings()
    
    // 2. Sync the cleared state back to the store immediately
    if (journey.value) {
      journey.value.nodes = [...flowRef.value.nodes]
      journey.value.edges = [...flowRef.value.edges]
    }
    
    // 3. Persist to backend immediately
    await flowRef.value.saveJourney()
    
    // 4. Reset UI and execution state
    selectedNode.value = null
    selectedEdge.value = null
    selectedResult.value = null
    journeyStore.resetExecution()
  }
}

async function handleDeleteJourney() {
  if (!confirm('Delete this journey? This action cannot be undone.')) {
    return
  }

  const result = await journeyStore.deleteJourney(route.params.id)
  if (result.success) {
    toast.success('Journey deleted')
    router.back()
  } else {
    toast.error(result.error)
  }
}
</script>

<style scoped>
/* Slide transition for right panel */
.slide-enter-active,
.slide-leave-active {
  transition: all 0.3s ease;
}

.slide-enter-from {
  transform: translateX(100%);
}

.slide-leave-to {
  transform: translateX(100%);
}

/* Slide up transition for bottom panel */
.slide-up-enter-active,
.slide-up-leave-active {
  transition: all 0.3s ease;
}

.slide-up-enter-from {
  transform: translateY(100%);
}

.slide-up-leave-to {
  transform: translateY(100%);
}
</style>
