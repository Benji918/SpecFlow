<template>
  <div class="h-full flex flex-col bg-surface">
    <!-- Header -->
    <div class="flex items-center justify-between mb-4 border-b border-gray-800 pb-4">
      <div>
        <h3 class="text-lg font-semibold">Data Mapping</h3>
        <p class="text-xs text-gray-500 font-mono">Configure data flow between steps</p>
      </div>
      <button
        @click="$emit('close')"
        class="p-2 text-gray-400 hover:text-white rounded hover:bg-gray-800"
      >
        <X :size="20" />
      </button>
    </div>

    <!-- Mapping List -->
    <div class="flex-1 overflow-auto space-y-4">
      <div v-if="mappings.length > 0" class="space-y-4">
        <div 
          v-for="(mapping, index) in mappings" 
          :key="index"
          class="p-4 bg-black/40 border border-gray-800 rounded-xl group transition-all hover:border-primary/30 relative"
        >
          <div class="flex items-center justify-between mb-3">
            <div class="flex items-center space-x-2">
               <div class="w-1.5 h-1.5 rounded-full bg-primary/60"></div>
               <span class="text-[10px] font-black uppercase text-gray-500 tracking-widest">Link #{{ index + 1 }}</span>
            </div>
            <button 
              @click="removeMapping(index)"
              class="text-gray-600 hover:text-red-500 transition-colors"
            >
              <Trash2 :size="12" />
            </button>
          </div>

          <div class="space-y-4">
            <!-- Source Field -->
            <div>
              <div class="flex items-center justify-between mb-1.5">
                <label class="text-[10px] text-gray-400 uppercase font-bold tracking-wider">Source Response Path</label>
                <div v-if="getLiveValue(mapping.from)" class="flex items-center text-[9px] text-primary/80 bg-primary/10 px-1.5 py-0.5 rounded border border-primary/20 max-w-[150px] truncate">
                  <Database :size="8" class="mr-1" />
                  {{ truncate(getLiveValue(mapping.from), 20) }}
                </div>
              </div>
              
              <div class="relative">
                <input 
                  v-model="mapping.from"
                  class="w-full bg-black/60 border border-gray-800 rounded-lg px-3 py-2 text-xs font-mono text-primary outline-none focus:border-primary/50 transition-all"
                  placeholder="response.id"
                  @input="updateEdge"
                />
                
                <!-- Suggestions -->
                <div v-if="availableSourceFields.length > 0" class="mt-1 flex flex-wrap gap-1">
                  <button 
                    v-for="field in availableSourceFields.slice(0, 5)" 
                    :key="field.path"
                    @click="mapping.from = field.path; updateEdge()"
                    class="text-[9px] bg-white/5 hover:bg-white/10 text-gray-500 border border-white/5 rounded px-1.5 py-0.5 transition-colors"
                  >
                    {{ field.path.replace('response.', '') }}
                  </button>
                </div>
              </div>
            </div>

            <div class="flex justify-center -my-1">
              <div class="h-6 w-px bg-gradient-to-b from-primary/50 to-blue-400/50"></div>
            </div>

            <!-- Target Field -->
            <div>
              <div class="flex items-center justify-between mb-1.5">
                <label class="text-[10px] text-gray-400 uppercase font-bold tracking-wider">Target Parameter Key</label>
                <span v-if="isValidTarget(mapping.to)" class="text-[8px] text-blue-300/60 uppercase font-bold">Matches Schema</span>
              </div>
              
              <div class="relative">
                <input 
                  v-model="mapping.to"
                  class="w-full bg-black/60 border border-gray-800 rounded-lg px-3 py-2 text-xs font-mono text-blue-400 outline-none focus:border-primary/50 transition-all"
                  placeholder="restaurant_id"
                  @input="updateEdge"
                />

                <!-- Suggestions -->
                <div v-if="requiredTargetFields.length > 0" class="mt-1 flex flex-wrap gap-1">
                  <button 
                    v-for="field in requiredTargetFields" 
                    :key="field"
                    @click="mapping.to = field; updateEdge()"
                    class="text-[9px] bg-blue-500/5 hover:bg-blue-500/20 text-blue-400/70 border border-blue-500/10 rounded px-1.5 py-0.5 transition-colors"
                  >
                    {{ field }}
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <div v-else class="flex flex-col items-center justify-center py-16 text-gray-600 text-center bg-black/20 rounded-2xl border border-dashed border-gray-800">
        <LinkIcon :size="40" class="mb-3 opacity-10" />
        <p class="text-xs font-bold uppercase tracking-widest text-gray-500">No active links</p>
        <p class="text-[10px] opacity-60 mt-2 px-12">Connect nodes to automatically detect and link response data to step parameters.</p>
      </div>

      <!-- Add New Mapping -->
      <button 
        @click="addMapping"
        class="w-full py-3 bg-white/5 hover:bg-white/10 border border-white/5 rounded-xl text-xs text-gray-400 font-bold uppercase tracking-wider transition-all flex items-center justify-center hover:text-white"
      >
        <Plus :size="16" class="mr-2" />
        Create New Link
      </button>
    </div>

    <!-- Live Execution Status -->
    <div class="mt-6 p-4 bg-primary/5 border border-primary/10 rounded-xl relative overflow-hidden">
      <div class="flex items-start z-10 relative">
        <Zap :size="16" class="text-primary mr-3 shrink-0 mt-0.5" />
        <div>
          <p class="text-[11px] font-black text-primary uppercase tracking-wider mb-1">Live Execution Engine</p>
          <p class="text-[10px] text-gray-400 leading-relaxed">
            Mappers automatically extract values from previous responses and inject them into the next step's execution environment. Changes here take effect on the next run.
          </p>
        </div>
      </div>
      <div class="absolute -right-4 -bottom-4 opacity-[0.03]">
        <LinkIcon :size="80" />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, computed } from 'vue'
import { X, Trash2, ArrowDown, Plus, Info, Link as LinkIcon, Zap, Database } from 'lucide-vue-next'
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

// Available source fields from schema
const availableSourceFields = computed(() => {
  const fields = []
  const responses = props.sourceNode?.data?.responses || {}
  const successCode = Object.keys(responses).find(code => code.startsWith('2'))
  const schema = responses[successCode]?.content?.['application/json']?.schema
  
  if (!schema || !schema.properties) return fields

  if (schema.properties.detail?.properties) {
    Object.keys(schema.properties.detail.properties).forEach(key => {
      fields.push({ name: key, path: `response.detail.${key}` })
    })
  } else if (schema.properties.data?.properties) {
    Object.keys(schema.properties.data.properties).forEach(key => {
      fields.push({ name: key, path: `response.data.${key}` })
    })
  } else {
    Object.keys(schema.properties).forEach(key => {
      fields.push({ name: key, path: `response.${key}` })
    })
  }
  return fields
})

// Required target fields
const requiredTargetFields = computed(() => {
  const fields = []
  const params = props.targetNode?.data?.parameters || []
  params.filter(p => p.in === 'path').forEach(p => fields.push(p.name))
  
  // Basic body fields
  const bodySchema = props.targetNode?.data?.requestBodySpec?.content?.['application/json']?.schema
  if (bodySchema && bodySchema.properties) {
    Object.keys(bodySchema.properties).forEach(key => {
      if (key.toLowerCase().includes('id') || key.toLowerCase().includes('pk')) {
         fields.push(key)
      }
    })
  }
  return fields
})

watch(() => props.edge, (newEdge) => {
  if (newEdge) {
    // Force a deep copy to ensure we don't mutate props directly and maintain reactivity
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
  // Emit with a fresh data object to ensure reactivity in VueFlow and MappingEdge
  emit('update-edge', props.edge.id, { 
    data: { 
      ...props.edge.data, 
      dataMapping: [...mappings.value] 
    } 
  })
}

function getLiveValue(path) {
  if (!path) return null
  // In a real scenario, we would parse the path against the last result of the source node
  // For now, let's check global sessionData as a fallback
  const cleanPath = path.replace('response.', '')
  return journeyStore.sessionData[cleanPath] || journeyStore.sessionData[`pathParams.${cleanPath}`]
}

function isValidTarget(key) {
  return requiredTargetFields.value.includes(key)
}

function truncate(str, len) {
  if (!str) return ''
  const s = String(str)
  return s.length > len ? s.substring(0, len) + '...' : s
}
</script>

<style scoped>
input::placeholder {
  color: #333;
}
</style>
