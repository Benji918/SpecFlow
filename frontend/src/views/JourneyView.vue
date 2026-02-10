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
      <div v-else-if="journey" class="flex-1 flex">
        <!-- Left Panel - Journey Flow -->
        <div :class="['flex-1 relative', selectedResult ? 'mr-96' : '']">
          <JourneyFlow
            ref="flowRef"
            :journey-id="journey.id"
            :initial-nodes="journey.nodes || []"
            :initial-edges="journey.edges || []"
            @node-selected="handleNodeSelected"
            @save="handleFlowSaved"
          />
        </div>

        <!-- Right Panel - Response Viewer (Slides in) -->
        <transition name="slide">
          <div
            v-if="selectedNode"
            class="w-96 border-l border-gray-800 bg-surface overflow-auto absolute right-0 top-0 bottom-0"
          >
            <div class="sticky top-0 bg-surface border-b border-gray-800 p-4 flex items-center justify-end z-10">
              <button
                @click="selectedNode = null; selectedResult = null"
                class="text-gray-400 hover:text-white"
              >
                <X :size="20" />
              </button>
            </div>
            <div class="p-4">
              <ResponsePanel
                :result="selectedResult"
                :node="selectedNode"
                @update-node="handleNodeUpdate"
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
    <transition name="slide-up">
      <div
        v-if="showRunner && journey"
        class="fixed bottom-0 left-0 right-0 bg-surface border-t border-gray-800 shadow-2xl"
        style="height: 400px; z-index: 20;"
      >
        <div class="h-full overflow-auto p-4">
          <div class="max-w-4xl mx-auto">
            <JourneyRunner
              :journey-id="journey.id"
              :nodes="journey.nodes || []"
              :edges="journey.edges || []"
              @step-start="handleStepStart"
              @step-complete="handleStepComplete"
              @execution-complete="handleExecutionComplete"
            />
          </div>
        </div>
      </div>
    </transition>
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
} from 'lucide-vue-next'
import JourneyFlow from '@/components/journey/JourneyFlow.vue'
import JourneyRunner from '@/components/journey/JourneyRunner.vue'
import ResponsePanel from '@/components/journey/ResponsePanel.vue'
import { generateEndpointMock } from '@/utils/mockGenerator'

const router = useRouter()
const route = useRoute()
const journeyStore = useJourneyStore()
const toast = useToast()

const loading = ref(true)
const showRunner = ref(false)
const selectedResult = ref(null)
const selectedNode = ref(null)
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
  // Find execution result for this node
  const result = journeyStore.executionResults.find(
    (r) => r.stepId === node.id
  )
  selectedResult.value = result || null
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
      
      // Update the flow component's nodes as well to reflect changes
      if (flowRef.value) {
        const flowNodeIndex = flowRef.value.nodes.findIndex(n => n.id === nodeId)
        if (flowNodeIndex !== -1) {
          flowRef.value.nodes[flowNodeIndex].data = {
            ...flowRef.value.nodes[flowNodeIndex].data,
            ...updates
          }
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
