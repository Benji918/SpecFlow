<template>
  <div class="h-full flex flex-col bg-surface overflow-hidden">
    <!-- Header -->
    <div class="flex items-center justify-between mb-6 border-b border-gray-800 pb-4 px-1">
      <div>
        <h3 class="text-xl font-bold bg-gradient-to-r from-white to-gray-400 bg-clip-text text-transparent">Data Mapping</h3>
        <p class="text-[10px] text-gray-500 font-medium uppercase tracking-widest mt-0.5">Automated Intelligence Connector</p>
      </div>
      <button
        @click="$emit('close')"
        class="p-2 text-gray-400 hover:text-white rounded-lg hover:bg-gray-800 transition-colors"
      >
        <X :size="20" />
      </button>
    </div>

    <!-- Mapping List -->
    <div class="flex-1 overflow-auto space-y-6 pr-2 -mr-2">
      <div v-if="mappings.length > 0" class="space-y-6">
        <div 
          v-for="(mapping, index) in mappings" 
          :key="index"
          class="p-5 bg-black/40 border border-gray-800 rounded-2xl group transition-all hover:border-primary/40 relative backdrop-blur-sm"
        >
          <div class="flex items-center justify-between mb-4">
            <div class="flex items-center space-x-2.5">
               <div class="w-2 h-2 rounded-full shadow-[0_0_8px_rgba(191,245,73,0.5)]" :class="mapping.from ? 'bg-primary' : 'bg-gray-700'"></div>
               <span class="text-[10px] font-black uppercase text-gray-400 tracking-[0.2em]">Link #{{ index + 1 }}</span>
            </div>
            <button 
              @click="removeMapping(index)"
              class="text-gray-600 hover:text-red-400 p-1 rounded hover:bg-red-500/10 transition-all"
            >
              <Trash2 :size="14" />
            </button>
          </div>

          <div class="space-y-5">
            <!-- Source Type & Field -->
            <div class="space-y-3">
              <div class="flex items-center justify-between">
                <label class="text-[9px] text-gray-500 uppercase font-black tracking-widest">Source Configuration</label>
                <div v-if="getLiveValue(mapping.from)" class="flex items-center text-[8px] text-primary bg-primary/10 px-2 py-0.5 rounded-full border border-primary/20 max-w-[150px] animate-in fade-in slide-in-from-right-1">
                  <span class="mr-1.5 opacity-50">VAL:</span>
                  <span class="font-mono font-bold truncate">{{ truncate(getLiveValue(mapping.from), 20) }}</span>
                </div>
                <div class="flex bg-black/60 p-0.5 rounded-lg border border-gray-800 ml-auto">
                  <button 
                    @click="setSourceType(index, 'response')"
                    :class="[
                      'px-2 py-1 text-[8px] font-bold uppercase rounded-md transition-all',
                      getSourceType(mapping.from) === 'response' ? 'bg-primary text-black shadow-lg' : 'text-gray-500 hover:text-gray-300'
                    ]"
                  >
                    Response
                  </button>
                  <button 
                    @click="setSourceType(index, 'request')"
                    :class="[
                      'px-2 py-1 text-[8px] font-bold uppercase rounded-md transition-all',
                      getSourceType(mapping.from) === 'request' ? 'bg-blue-500 text-white shadow-lg' : 'text-gray-500 hover:text-gray-300'
                    ]"
                  >
                    Request
                  </button>
                </div>
              </div>

              <div class="relative group/input">
                <div class="absolute left-3 top-1/2 -translate-y-1/2 text-gray-500 group-focus-within/input:text-primary transition-colors">
                  <Database v-if="getSourceType(mapping.from) === 'response'" :size="14" />
                  <ArrowUpRight v-else :size="14" />
                </div>
                <input 
                  v-model="mapping.from"
                  class="w-full bg-black/60 border border-gray-800 rounded-xl pl-10 pr-4 py-2.5 text-xs font-mono text-primary outline-none focus:border-primary/50 focus:ring-1 focus:ring-primary/20 transition-all"
                  :placeholder="getSourceType(mapping.from) === 'response' ? 'response.data.id' : 'request.params.user_id'"
                  @input="updateEdge"
                />
              </div>

              <!-- Suggestions based on type -->
              <div v-if="availableSourceFields.length > 0" class="mt-2">
                <div v-if="getSourceType(mapping.from) === 'request' && requestFields.length > 0">
                  <div class="flex flex-wrap gap-1.5">
                    <button 
                      v-for="field in requestFields" 
                      :key="field.path"
                      @click="mapping.from = field.path; updateEdge()"
                      class="text-[9px] bg-blue-500/5 hover:bg-blue-500/20 text-blue-400 border border-blue-500/10 rounded-md px-2 py-1 transition-all flex items-center"
                    >
                      {{ field.name }}
                    </button>
                  </div>
                </div>

                <div v-if="getSourceType(mapping.from) === 'response' && responseFields.length > 0">
                  <div class="flex flex-wrap gap-1.5">
                    <button 
                      v-for="field in responseFields.slice(0, 8)" 
                      :key="field.path"
                      @click="mapping.from = field.path; updateEdge()"
                      class="text-[9px] bg-white/5 hover:bg-white/10 text-gray-400 border border-white/5 rounded-md px-2 py-1 transition-all flex items-center"
                    >
                      {{ field.path.replace('response.', '') }}
                    </button>
                  </div>
                </div>
              </div>
            </div>

            <!-- Flow Icon -->
            <div class="flex justify-center -my-3 relative">
              <div class="absolute inset-0 flex items-center justify-center">
                <div class="h-10 w-px bg-gradient-to-b from-primary/30 via-primary/50 to-blue-400/30"></div>
              </div>
              <div class="z-10 bg-surface p-1 rounded-full border border-gray-800">
                <ArrowDown :size="10" class="text-gray-600" />
              </div>
            </div>

            <!-- Target Field -->
            <div class="space-y-3">
              <div class="flex items-center justify-between">
                <label class="text-[9px] text-gray-500 uppercase font-black tracking-widest">Injection Target</label>
                <div v-if="isValidTarget(mapping.to)" class="flex items-center text-[8px] text-green-400 bg-green-400/10 px-2 py-0.5 rounded-full border border-green-400/20">
                  <Check :size="8" class="mr-1" />
                  Verified Schema
                </div>
              </div>
              
              <div class="relative group/input shadow-inner">
                <div class="absolute left-3 top-1/2 -translate-y-1/2 text-gray-500 group-focus-within/input:text-blue-400 transition-colors">
                  <Target :size="14" />
                </div>
                <input 
                  v-model="mapping.to"
                  class="w-full bg-black/60 border border-gray-800 rounded-xl pl-10 pr-4 py-2.5 text-xs font-mono text-blue-400 outline-none focus:border-blue-400/50 focus:ring-1 focus:ring-blue-400/20 transition-all"
                  placeholder="e.g. restaurant_id"
                  @input="updateEdge"
                />
              </div>

              <!-- Suggested Targets -->
              <div v-if="requiredTargetFields.length > 0" class="flex flex-wrap gap-1.5">
                <button 
                  v-for="field in requiredTargetFields" 
                  :key="field"
                  @click="mapping.to = field.includes('pathParams.') ? field : `pathParams.${field}`; updateEdge()"
                  class="text-[9px] bg-blue-500/5 hover:bg-blue-500/20 text-blue-400/70 border border-blue-500/10 rounded-md px-2 py-1 transition-all"
                >
                  {{ field.replace('pathParams.', '') }}
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <!-- Empty State -->
      <div v-else class="flex flex-col items-center justify-center py-20 text-gray-600 text-center bg-black/20 rounded-[2rem] border border-dashed border-gray-800 backdrop-blur-sm">
        <div class="relative mb-6">
          <LinkIcon :size="48" class="text-gray-800" />
          <Zap :size="20" class="absolute -top-1 -right-1 text-primary animate-pulse" />
        </div>
        <p class="text-xs font-black uppercase tracking-[0.3em] text-gray-400">No active links</p>
        <p class="text-[10px] text-gray-500 mt-4 px-12 leading-relaxed">
          Connect nodes to automatically detect and link response data to step parameters.
        </p>
      </div>

      <!-- Hints & Examples -->
      <div class="bg-blue-500/5 border border-blue-500/10 rounded-xl p-4 space-y-2">
        <div class="flex items-center text-blue-400 mb-1">
          <Info :size="12" class="mr-1.5" />
          <span class="text-[9px] font-bold uppercase tracking-widest">Mapping Guide</span>
        </div>
        <div class="grid grid-cols-2 gap-x-4 gap-y-1 text-[9px] text-gray-400 font-mono">
          <span>response.id</span> <span class="text-gray-600">→ Single value</span>
          <span>response.users[0].id</span> <span class="text-gray-600">→ List item</span>
          <span>body.menu_items</span> <span class="text-gray-600">→ Inject body</span>
          <span>body.items[0]</span> <span class="text-gray-600">→ Array index</span>
          <span>pathParams.id</span> <span class="text-gray-600">→ URL param</span>
        </div>
      </div>

      <!-- Add New Mapping -->
      <button 
        @click="addMapping"
        class="w-full py-4 bg-gradient-to-b from-white/[0.08] to-transparent hover:from-white/[0.12] border border-white/10 rounded-2xl text-[11px] text-primary font-black uppercase tracking-[0.2em] transition-all flex items-center justify-center group hover:border-primary/30"
      >
        <Plus :size="18" class="mr-2 group-hover:scale-110 transition-transform" />
        Create Intelligence Link
      </button>
    </div>

    <!-- Info Footer -->
    <div class="mt-8 p-5 bg-gradient-to-br from-primary/10 to-transparent border border-primary/10 rounded-2xl relative overflow-hidden group">
      <div class="flex items-start z-10 relative">
        <Zap :size="18" class="text-primary mr-4 shrink-0 mt-0.5 animate-pulse" />
        <div>
          <p class="text-[11px] font-black text-primary uppercase tracking-widest mb-1.5">Live Execution Engine</p>
          <p class="text-[10px] text-gray-400 leading-relaxed font-medium">
            Links automatically extract values from previous steps and inject them into subsequent execution environments.
          </p>
        </div>
      </div>
      <!-- Background Graphic -->
      <div class="absolute -right-6 -bottom-6 text-primary/[0.03] rotate-12 transition-transform group-hover:scale-110 duration-700">
        <LinkIcon :size="100" />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, computed } from 'vue'
import { X, Trash2, ArrowDown, Plus, Link as LinkIcon, Zap, Database, ArrowUpRight, Check, Target, Info } from 'lucide-vue-next'
import { useJourneyStore } from '@/stores/journey'

const props = defineProps({
  edge: {
    type: Object,
    required: true
  },
  sourceNode: {
    type: Object,
    required: true
  },
  targetNode: {
    type: Object,
    required: true
  }
})

const emit = defineEmits(['update-edge', 'close'])
const journeyStore = useJourneyStore()

const mappings = ref([])

// Helper to determine source type from path
function getSourceType(path) {
  if (!path) return 'response'
  return path.startsWith('request.') ? 'request' : 'response'
}

function setSourceType(index, type) {
  const mapping = mappings.value[index]
  if (type === 'request') {
    if (!mapping.from.startsWith('request.')) {
      mapping.from = 'request.params.'
    }
  } else {
    if (!mapping.from.startsWith('response.')) {
      mapping.from = 'response.'
    }
  }
  updateEdge()
}

// Available source fields from schema
const availableSourceFields = computed(() => {
  const fields = []

  // 1. Add request parameters
  const sourceParams = props.sourceNode?.data?.parameters || []
  sourceParams.forEach(p => {
    fields.push({ 
      name: `${p.name} (${p.in})`, 
      path: `request.params.${p.name}` 
    })
  })

  // 2. Add response fields from schema
  const responses = props.sourceNode?.data?.responses || {}
  const successCode = Object.keys(responses).find(code => code.startsWith('2'))
  const schema = responses[successCode]?.content?.['application/json']?.schema
  
  if (schema && schema.properties) {
    function extractFields(s, prefix = 'response') {
      if (!s || !s.properties) return
      Object.keys(s.properties).forEach(key => {
        const path = `${prefix}.${key}`
        fields.push({ name: key, path })
        if ((key === 'detail' || key === 'data') && s.properties[key].properties) {
          extractFields(s.properties[key], path)
        }
      })
    }
    extractFields(schema)
  }

  return fields
})

const requestFields = computed(() => availableSourceFields.value.filter(f => f.path.startsWith('request.')))
const responseFields = computed(() => availableSourceFields.value.filter(f => f.path.startsWith('response.')))

// Required target fields
const requiredTargetFields = computed(() => {
  const fields = []
  const params = props.targetNode?.data?.parameters || []
  params.filter(p => p.in === 'path').forEach(p => fields.push(`pathParams.${p.name}`))
  
  // Basic body fields
  const bodySchema = props.targetNode?.data?.requestBodySpec?.content?.['application/json']?.schema
  if (bodySchema && bodySchema.properties) {
    Object.keys(bodySchema.properties).forEach(key => {
      // Body fields can be added too if needed, but pathParams is priority
      fields.push(key)
    })
  }
  return fields
})

watch(() => props.edge, (newEdge) => {
  if (newEdge) {
    mappings.value = JSON.parse(JSON.stringify(newEdge.data?.dataMapping || []))
  }
}, { immediate: true, deep: true })

function addMapping() {
  mappings.value.push({ from: 'response.', to: '' })
  updateEdge()
}

function removeMapping(index) {
  mappings.value.splice(index, 1)
  updateEdge()
}

function updateEdge() {
  emit('update-edge', props.edge.id, { 
    data: { 
      ...props.edge.data, 
      dataMapping: [...mappings.value] 
    } 
  })
}

function getLiveValue(path) {
  if (!path) return null
  
  // Handle request parameter sources
  if (path.startsWith('request.params.')) {
    const paramKey = path.replace('request.params.', '')
    return journeyStore.sessionData[paramKey] || journeyStore.sessionData[`pathParams.${paramKey}`]
  }

  const cleanPath = path.replace('response.', '')
  
  // Try direct path first
  let val = journeyStore.sessionData[cleanPath] || journeyStore.sessionData[`pathParams.${cleanPath}`]
  
  // If no value, try looking inside common wrappers if it's a simple key
  if (val === undefined || val === null) {
     const wrappers = ['detail', 'data']
     for (const w of wrappers) {
       val = journeyStore.sessionData[`${w}.${cleanPath}`] || journeyStore.sessionData[`pathParams.${w}.${cleanPath}`]
       if (val !== undefined && val !== null) break
     }
  }

  // Fallback to generic 'id' if looking for a specific ID
  if ((val === undefined || val === null) && cleanPath.endsWith('_id')) {
    val = journeyStore.sessionData['id'] || journeyStore.sessionData['pathParams.id']
  }

  return val
}

function truncate(str, len) {
  if (!str) return ''
  const s = String(str)
  return s.length > len ? s.substring(0, len) + '...' : s
}

function isValidTarget(key) {
  return requiredTargetFields.value.includes(key)
}
</script>

<style scoped>
input::placeholder {
  color: #333;
}

::-webkit-scrollbar {
  width: 4px;
}
::-webkit-scrollbar-track {
  background: transparent;
}
::-webkit-scrollbar-thumb {
  background: #333;
  border-radius: 10px;
}
::-webkit-scrollbar-thumb:hover {
  background: #444;
}
</style>

