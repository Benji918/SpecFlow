<template>
  <div class="min-h-screen bg-background">
    <!-- Header -->
    <header class="border-b border-gray-800 bg-surface/50 backdrop-blur-lg sticky top-0 z-10">
      <div class="max-w-full px-4 py-4">
        <div class="flex items-center justify-between">
          <div class="flex items-center space-x-4">
            <button 
              @click="router.push(`/spec/${journey?.spec_id}`)" 
              class="text-gray-400 hover:text-white"
              title="Back to Spec Details"
            >
              <ArrowLeft :size="24" />
            </button>
            <div class="group relative">
              <div v-if="!isEditingName" @click="startEditingName" class="cursor-pointer hover:bg-white/5 p-1 rounded -ml-1 flex items-center">
                <h1 class="text-2xl font-bold">{{ journey?.name || 'Journey' }}</h1>
                <Edit2 :size="16" class="ml-2 text-gray-600 opacity-0 group-hover:opacity-100 transition-opacity" />
              </div>
              <input
                v-else
                ref="nameInputRef"
                v-model="editedName"
                @blur="saveName"
                @keyup.enter="saveName"
                @keyup.esc="cancelEditName"
                type="text"
                class="bg-black border border-gray-700 rounded px-2 py-1 text-2xl font-bold text-white outline-none focus:border-primary w-full min-w-[300px]"
              />
              <p v-if="nameError" class="text-xs text-red-500 absolute top-full left-0 mt-1 whitespace-nowrap">{{ nameError }}</p>
              
              <p v-if="journey" class="text-sm text-gray-400 mt-1">
                {{ journey.nodes?.length || 0 }} steps
              </p>
            </div>
          </div>
          <div class="flex items-center space-x-3">
            <button
              @click="showAddStep = true"
              class="btn-primary text-sm py-2 px-4 shadow-lg shadow-primary/10 hover:shadow-primary/20"
              title="Add a new step to the journey"
            >
              <Plus :size="16" class="inline mr-2" />
              Add Step
            </button>
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
                :nodes="journey.nodes"
                @update-node="handleNodeUpdate"
                @select-edge="handleEdgeSelected"
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

    <!-- Add Step Modal -->
    <div v-if="showAddStep" class="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm p-4">
      <div class="bg-surface border border-gray-800 rounded-xl w-full max-w-4xl max-h-[85vh] flex flex-col shadow-2xl relative">
        <!-- Modal Header -->
        <div class="flex items-center justify-between p-6 border-b border-gray-800">
          <div>
            <h2 class="text-xl font-bold flex items-center">
              <Plus :size="24" class="mr-2 text-primary" />
              Add Step to Journey
            </h2>
            <p class="text-sm text-gray-400 mt-1">Select an endpoint to append to the flow</p>
          </div>
          <button @click="showAddStep = false" class="p-2 hover:bg-gray-800 rounded-lg text-gray-400 hover:text-white transition-colors">
            <X :size="20" />
          </button>
        </div>

        <!-- Filters & Search -->
        <div class="p-4 border-b border-gray-800 bg-surface/50 backdrop-blur flex flex-col md:flex-row gap-4 items-center">
          <div class="relative flex-1 w-full">
            <Search :size="16" class="absolute left-3 top-1/2 -translate-y-1/2 text-gray-500" />
            <input 
              v-model="searchQuery"
              type="text"
              placeholder="Search endpoints..."
              class="w-full bg-black/40 border border-gray-800 rounded-xl pl-10 pr-4 py-2 text-sm outline-none focus:border-primary/50 transition-all placeholder:text-gray-600"
              autoFocus
            />
          </div>
          <div class="flex items-center space-x-2">
            <button 
              v-for="m in filterableMethods" 
              :key="m"
              @click="toggleMethodFilter(m)"
              :class="[
                'px-3 py-1.5 rounded-lg text-[10px] font-black tracking-wider uppercase transition-all border',
                selectedMethods.includes(m) 
                  ? getMethodColor(m) + ' border-transparent'
                  : 'border-transparent hover:border-gray-700 text-gray-500 bg-gray-800/20'
              ]"
            >
              {{ m }}
            </button>
          </div>
        </div>

        <!-- Endpoints List -->
        <div class="flex-1 overflow-y-auto p-4 custom-scrollbar">
          <div v-if="filteredEndpoints.length === 0" class="flex flex-col items-center justify-center h-40 text-gray-500">
            <Search :size="32" class="mb-2 opacity-50" />
            <p class="text-sm">No matching endpoints found</p>
          </div>

          <div v-else class="grid grid-cols-1 gap-3">
             <div
                v-for="endpoint in filteredEndpoints"
                :key="`${endpoint.method}-${endpoint.path}`"
                class="flex items-center justify-between p-4 bg-black/20 border border-gray-800 rounded-xl hover:bg-gray-800/40 hover:border-primary/30 transition-all group"
              >
                <div class="flex items-center space-x-4 overflow-hidden">
                  <span
                    :class="[
                      'shrink-0 w-16 text-center py-1.5 rounded-lg font-mono text-[10px] font-black tracking-widest border border-current/20',
                      getMethodColor(endpoint.method)
                    ]"
                  >
                    {{ endpoint.method }}
                  </span>
                  
                  <div class="min-w-0">
                    <div class="font-mono text-sm font-bold text-gray-200 truncate group-hover:text-primary transition-colors">
                      {{ endpoint.path }}
                    </div>
                    <div class="text-xs text-gray-500 truncate mt-0.5">
                      {{ endpoint.summary || endpoint.operation_id }}
                    </div>
                  </div>
                </div>

                <div class="flex items-center pl-4">
                  <!-- Check if already exists in flow -->
                  <div v-if="flowRef?.nodes.some(n => n.data.path === endpoint.path && n.data.method === endpoint.method)" 
                       class="text-xs text-gray-500 flex items-center px-3 py-1.5 bg-gray-800/50 rounded-lg border border-gray-700">
                    <Check :size="14" class="mr-1.5" />
                    Added
                  </div>
                  <button 
                    v-else
                    @click="handleAddNode(endpoint)"
                    class="btn-primary py-1.5 px-4 text-xs shadow-none hover:shadow-lg hover:scale-105 active:scale-95 flex items-center"
                  >
                    <Plus :size="14" class="mr-1.5" />
                    Add
                  </button>
                </div>
              </div>
          </div>
        </div>
      </div>
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
  Plus,
  Search,
  Check,
  Edit2,
} from 'lucide-vue-next'
import { useSpecStore } from '@/stores/spec'
import JourneyFlow from '@/components/journey/JourneyFlow.vue'
import JourneyRunner from '@/components/journey/JourneyRunner.vue'
import ResponsePanel from '@/components/journey/ResponsePanel.vue'
import MappingPanel from '@/components/journey/MappingPanel.vue'
import { generateEndpointMock } from '@/utils/mockGenerator'

const router = useRouter()
const route = useRoute()
const journeyStore = useJourneyStore()
const specStore = useSpecStore()
const toast = useToast()

const loading = ref(true)
const showRunner = ref(false)
const showAddStep = ref(false)
const selectedResult = ref(null)
const selectedNode = ref(null)
const selectedEdge = ref(null)
const flowRef = ref(null)

// Add Step Modal State
const searchQuery = ref('')
const selectedMethods = ref([])
const filterableMethods = ['GET', 'POST', 'PUT', 'DELETE', 'PATCH']

const journey = computed(() => journeyStore.activeJourney)
const spec = computed(() => specStore.currentSpec)

const filteredEndpoints = computed(() => {
  if (!spec.value?.endpoints) return []
  
  return spec.value.endpoints.filter(endpoint => {
    // Search query filter
    const matchesSearch = !searchQuery.value || 
      endpoint.path.toLowerCase().includes(searchQuery.value.toLowerCase()) ||
      (endpoint.summary && endpoint.summary.toLowerCase().includes(searchQuery.value.toLowerCase())) ||
      (endpoint.operation_id && endpoint.operation_id.toLowerCase().includes(searchQuery.value.toLowerCase()))
    
    // Method filter
    const matchesMethod = selectedMethods.value.length === 0 || 
      selectedMethods.value.includes(endpoint.method.toUpperCase())
    
    
    return matchesSearch && matchesMethod
  })
})

// Journey Name Editing
const isEditingName = ref(false)
const editedName = ref('')
const nameInputRef = ref(null)
const nameError = ref('')

function startEditingName() {
  if (!journey.value) return
  editedName.value = journey.value.name
  isEditingName.value = true
  nameError.value = ''
  // Focus input on next tick
  setTimeout(() => {
    nameInputRef.value?.focus()
  }, 0)
}

function cancelEditName() {
  isEditingName.value = false
  nameError.value = ''
}

async function saveName() {
  if (!isEditingName.value) return
  
  const newName = editedName.value.trim()
  if (!newName) {
    nameError.value = 'Name cannot be empty'
    return
  }
  
  if (newName === journey.value.name) {
    cancelEditName()
    return
  }

  // Frontend Validation for XSS/SQL Injection
  // Basic patterns - comprehensive validation should be on backend too
  const xssPattern = /<[^>]*>|javascript:|on\w+=/i
  const sqlPattern = /(\b(select|update|delete|insert|drop|alter)\b.*\b(from|table|into)\b)|(--)/i
  
  if (xssPattern.test(newName)) {
    nameError.value = 'Invalid characters detected (XSS)'
    return
  }
  
  if (sqlPattern.test(newName)) {
    nameError.value = 'Invalid characters detected (SQL Injection)'
    return
  }

  // Save
  const result = await journeyStore.updateJourney(journey.value.id, { name: newName })
  
  if (result.success) {
    toast.success('Journey name updated')
    isEditingName.value = false
  } else {
    toast.error(result.error || 'Failed to update name')
    cancelEditName()
  }
}


onMounted(async () => {
  await fetchJourney()
})

async function fetchJourney() {
  loading.value = true
  const result = await journeyStore.fetchJourney(route.params.id)
  if (!result.success) {
    toast.error('Failed to load journey')
  } else {
    // Load the spec as well for "Add Step" functionality
    const specResult = await specStore.fetchSpec(result.data.spec_id)
    if (!specResult.success) {
      console.warn('Failed to load specification:', specResult.error)
    }
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
  if (journeyStore.activeJourney) {
    const nodeIndex = journeyStore.activeJourney.nodes.findIndex(n => n.id === nodeId)
    if (nodeIndex !== -1) {
      // Create a fresh object for the node to ensure Vue triggers reactivity
      const node = journeyStore.activeJourney.nodes[nodeIndex]
      journeyStore.activeJourney.nodes[nodeIndex] = {
        ...node,
        data: {
          ...node.data,
          ...updates
        }
      }
      
      // Also update selectedNode if it's the one being modified
      if (selectedNode.value && selectedNode.value.id === nodeId) {
        selectedNode.value = journeyStore.activeJourney.nodes[nodeIndex]
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
    const status = message.status
    const executionId = message.executionId
    const totalSteps = message.totalSteps || 0
    const completedSteps = message.completedSteps || 0
    const failedSteps = message.failedSteps || 0
    const failedStepDetails = message.failedStepDetails || []
    
    if (status === 'failed') {
      // Show detailed error message
      const firstFailed = failedStepDetails[0]
      if (firstFailed) {
        const stepName = firstFailed.stepName || firstFailed.stepId
        const errorMsg = firstFailed.error ? `: ${firstFailed.error}` : ` (HTTP ${firstFailed.statusCode})`
        toast.error(`Journey failed at "${stepName}"${errorMsg}`)
      } else {
        toast.error(`Journey execution failed - ${failedSteps} of ${totalSteps} steps failed`)
      }
    } else if (status === 'completed') {
      toast.success(`Journey executed successfully! (${completedSteps} steps)`)
    } else {
      toast.info(`Journey execution ${status}`)
    }
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
    // Generate mock data regardless if it exists - user wants fresh data on click
    const mock = generateEndpointMock(node.data)
    const updates = {}
    
    if (mock.body) {
      updates.requestBody = mock.body
    }
    
    // Also prefill params
    if (mock.params && node.data.parameters) {
      const updatedParams = node.data.parameters.map(p => {
        return { ...p, value: mock.params[p.name] || '' }
      })
      
      updates.parameters = updatedParams
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

function toggleMethodFilter(method) {
  const index = selectedMethods.value.indexOf(method)
  if (index === -1) {
    selectedMethods.value.push(method)
  } else {
    selectedMethods.value.splice(index, 1)
  }
}

function getMethodColor(method) {
  const colors = {
    GET: 'bg-blue-500/20 text-blue-400',
    POST: 'bg-green-500/20 text-green-400',
    PUT: 'bg-yellow-500/20 text-yellow-400',
    DELETE: 'bg-red-500/20 text-red-400',
    PATCH: 'bg-purple-500/20 text-purple-400',
  }
  return colors[method] || 'bg-gray-500/20 text-gray-400'
}

function handleAddNode(endpoint) {
  if (!flowRef.value) return

  // Check for duplicates
  const existingNodes = flowRef.value.nodes
  const duplicate = existingNodes.find(n => 
    n.data.path === endpoint.path && 
    n.data.method === endpoint.method
  )

  if (duplicate) {
    toast.warning(`Endpoint ${endpoint.method} ${endpoint.path} already exists in this journey.`)
    return
  }

  // Determine position (below the last node)
  const lastNode = existingNodes.length > 0 ? existingNodes[existingNodes.length - 1] : null
  const x = lastNode ? lastNode.position.x : 250
  const y = lastNode ? lastNode.position.y + 200 : 100

  // Create new node
  const newNode = {
    id: `node-${Date.now()}`,
    type: 'endpoint',
    position: { x, y },
    data: {
      ...JSON.parse(JSON.stringify(endpoint)),
      status: 'pending' // Default status
    }
  }

  // Add to flow
  flowRef.value.nodes.push(newNode)
  toast.success('Step added')
  // Don't close modal immediately to allow adding multiple? 
  // User asked "ability to added endpoints or nodes", implies maybe single or multiple.
  // "x buttton beside the node check" probably means close modal or remove filter.
  // I'll close the modal for better UX unless they ctrl+click (not easy to implement).
  showAddStep.value = false
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
