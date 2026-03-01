<template>
  <div class="flex flex-col h-full bg-black/40 border border-gray-800 rounded-xl overflow-hidden backdrop-blur-md transition-all">
    <!-- Header -->
    <div class="px-4 py-3 bg-white/5 border-b border-gray-800 flex items-center justify-between">
      <div class="flex items-center space-x-2">
        <label class="p-1.5 bg-primary/10 rounded-lg">
          <Globe :size="14" class="text-primary" />
        </label>
        <div>
          <h3 class="text-[10px] font-black uppercase tracking-[0.2em] text-gray-400 leading-none">Tunnel Proxy</h3>
          <p class="text-[9px] text-gray-600 font-bold mt-1 uppercase">{{ tunnels.length > 0 ? 'Active' : 'Standby' }}</p>
        </div>
      </div>
      
      <div class="flex items-center space-x-2">
        <button 
          @click="closeAllTunnels"
          class="flex items-center space-x-1.5 px-2 py-1 bg-red-500/10 hover:bg-red-500/20 text-red-500 rounded-md transition-all border border-red-500/20 group/kill"
          title="Reset Ngrok Infrastructure (Kill all processes)"
        >
          <X :size="10" class="group-hover/kill:rotate-90 transition-transform" />
          <span class="text-[8px] font-black uppercase tracking-widest">Reset All</span>
        </button>
        <button 
          @click="loadTunnels" 
          class="p-1.5 hover:bg-white/5 rounded-md transition-all text-gray-500 hover:text-white"
          title="Refresh Tunnels"
        >
          <RotateCcw :size="12" :class="{ 'animate-spin': loading }" />
        </button>
        <div 
          :class="[
            'w-2 h-2 rounded-full shadow-[0_0_8px]',
            tunnels.length > 0 ? 'bg-green-500 shadow-green-500/50' : 'bg-gray-700 shadow-transparent'
          ]"
        ></div>
      </div>
    </div>

    <!-- Scrollable Content Area -->
    <div class="flex-1 overflow-auto custom-scrollbar p-4 space-y-4">
      <!-- Setup Configuration Tip -->
      <div class="p-3 bg-primary/5 rounded-lg border border-primary/10 flex items-start space-x-3 mb-4">
        <ShieldAlert :size="16" class="text-primary/60 mt-0.5 shrink-0" />
        <div class="space-y-1">
          <p class="text-[10px] text-gray-300 font-black uppercase tracking-widest">Configuration Required</p>
          <p class="text-[9px] text-gray-500 font-medium leading-tight">
            To prevent blocked requests, ensure your target application permits the <span class="text-primary font-bold">ngrok domain</span> in its <span class="text-white">CORS settings</span> and <span class="text-white">Allowed Hosts</span> configuration.
          </p>
        </div>
      </div>

      <!-- Create Tunnel Form (Compact) -->
      <div class="space-y-3">
        <div class="flex items-center space-x-2 transition-all duration-300">
          <div class="flex-1 relative group">
            <span class="absolute left-3 top-1/2 -translate-y-1/2 text-[10px] font-bold text-gray-600 group-focus-within:text-primary transition-colors">PORT</span>
            <input
              v-model="localPort"
              type="number"
              class="w-full bg-black/40 border border-gray-800 rounded-lg px-3 py-2 text-xs text-white pl-12 focus:ring-1 focus:ring-primary/30 focus:border-primary/50 transition-all outline-none"
              min="1"
              max="65535"
            />
          </div>
          <select
            v-model="protocol"
            class="bg-black/40 border border-gray-800 rounded-lg px-2 py-2 text-xs text-white focus:ring-1 focus:ring-primary/30 focus:border-primary/50 transition-all outline-none appearance-none cursor-pointer"
          >
            <option value="http">HTTP</option>
            <option value="https">HTTPS</option>
          </select>
        </div>
        
        <button
          @click="createTunnel"
          :disabled="creatingTunnel"
          class="w-full py-2.5 rounded-lg bg-primary hover:bg-primary-dark disabled:opacity-30 disabled:grayscale text-black font-black text-[10px] uppercase tracking-widest transition-all flex items-center justify-center hover:shadow-[0_0_20px_rgba(191,245,73,0.3)] active:scale-95"
        >
          <Loader v-if="creatingTunnel" :size="14" class="mr-2 animate-spin" />
          <Zap v-else :size="14" class="mr-2 fill-current" />
          {{ creatingTunnel ? 'Deploying...' : 'Fire up tunnel' }}
        </button>
      </div>

      <!-- Active Tunnels List -->
      <div v-if="tunnels.length > 0" class="space-y-3">
        <div class="flex items-center justify-between">
          <h4 class="text-[9px] font-black uppercase text-gray-600 tracking-widest">Active Tunnels</h4>
          <span class="text-[9px] px-1.5 py-0.5 rounded-full bg-primary/10 text-primary font-bold">{{ tunnels.length }}</span>
        </div>
        
        <div v-for="tunnel in tunnels" :key="tunnel.name" class="group bg-white/[0.03] rounded-xl border border-white/5 hover:border-primary/20 transition-all duration-300 p-3 relative overflow-hidden">
          <!-- Background Glow on Hover -->
          <div class="absolute inset-0 bg-primary/5 opacity-0 group-hover:opacity-100 transition-opacity"></div>
          
          <div class="relative z-10">
            <div class="flex items-center justify-between mb-2">
              <div class="flex items-center space-x-2">
                <span class="text-[10px] font-bold text-gray-300">{{ tunnel.name }}</span>
                <span class="text-[8px] px-1.5 py-0.5 rounded bg-black/40 text-primary font-black uppercase border border-primary/20">
                  {{ tunnel.proto }}
                </span>
              </div>
              <div class="flex items-center space-x-1 opacity-0 group-hover:opacity-100 transition-opacity translate-x-2 group-hover:translate-x-0 transition-transform">
                <button
                  @click="copyToClipboard(tunnel.public_url)"
                  class="p-1.5 hover:bg-white/10 rounded-lg text-gray-500 hover:text-white transition-colors"
                  title="Copy URL"
                >
                  <Copy :size="12" />
                </button>
                <button
                  @click="closeTunnel(tunnel.name)"
                  class="p-1.5 hover:bg-red-500/20 rounded-lg text-gray-600 hover:text-red-400 transition-colors"
                  title="Close tunnel"
                >
                  <X :size="12" />
                </button>
              </div>
            </div>

            <div class="space-y-2">
              <div class="bg-black/60 rounded-lg px-2 py-1.5 flex items-center justify-between group/url">
                <code class="text-[10px] font-mono text-primary/80 truncate pr-4">{{ tunnel.public_url }}</code>
                <button 
                  @click="$emit('use-as-base-url', tunnel.public_url)"
                  class="text-[9px] font-black uppercase text-gray-500 hover:text-primary whitespace-nowrap transition-colors flex items-center"
                >
                  Apply <ChevronRight :size="10" class="ml-1" />
                </button>
              </div>
              
              <div class="flex items-center justify-between text-[8px] font-bold uppercase tracking-widest text-gray-600 px-1">
                <div class="flex items-center">
                  <span class="w-1 h-1 rounded-full bg-gray-600 mr-2"></span>
                  Local: {{ tunnel.addr }}
                </div>
                <div class="flex items-center">
                  <span class="w-1 h-1 rounded-full bg-gray-600 mr-2"></span>
                  Region: {{ tunnel.region }}
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- No Tunnels Message -->
      <div v-else class="flex flex-col items-center justify-center py-10 text-center space-y-3 opacity-40">
        <div class="p-4 bg-white/5 rounded-full border border-white/5">
          <Globe :size="32" class="text-gray-500" />
        </div>
        <div>
          <p class="text-[10px] font-black uppercase tracking-widest text-gray-500">
            {{ isDisabled ? 'Proxy Disabled' : 'Infrastructure Empty' }}
          </p>
          <p v-if="isDisabled" class="text-[8px] text-gray-700 mt-1 max-w-[150px] mx-auto">
            Enable NGROK_ENABLED in your backend .env to use proxying
          </p>
          <p v-else class="text-[8px] text-gray-700 mt-1">Deploy a tunnel to proxy local traffic</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useToast } from 'vue-toastification'
import { Globe, Loader, Copy, X, Zap, RotateCcw, ChevronRight, ShieldAlert } from 'lucide-vue-next'
import client from '@/api/client'

const toast = useToast()
const tunnels = ref([])
const localPort = ref(8000)
const protocol = ref('http')
const creatingTunnel = ref(false)
const loading = ref(false)
const isDisabled = ref(false)

const emit = defineEmits(['use-as-base-url'])

// Load active tunnels on mount
onMounted(async () => {
  await loadTunnels()
})

// Load active tunnels
async function loadTunnels() {
  loading.value = true
  try {
    const response = await client.get('/api/ngrok/tunnels')
    if (response.data.success) {
      tunnels.value = response.data.tunnels
      isDisabled.value = response.data.message?.includes('disabled') || false
    }
  } catch (error) {
    console.error('Failed to load tunnels:', error)
    toast.error('Failed to load active tunnels')
  } finally {
    loading.value = false
  }
}

// Create new tunnel
async function createTunnel() {
  if (!localPort.value || localPort.value < 1 || localPort.value > 65535) {
    toast.error('Please enter a valid port number')
    return
  }

  creatingTunnel.value = true

  try {
    const response = await client.post('/api/ngrok/create-tunnel', {
      local_port: localPort.value,
      protocol: protocol.value
    })

    if (response.data.success) {
      const message = response.data.message || 'Tunnel created successfully'
      toast.success(message)
      await loadTunnels()
    }
  } catch (error) {
    console.error('Failed to create tunnel:', error)
    const errorMessage = error.response?.data?.detail || 'Failed to create tunnel'
    toast.error(errorMessage)
  } finally {
    creatingTunnel.value = false
  }
}

// Close tunnel
async function closeTunnel(tunnelName) {
  try {
    const response = await client.delete(`/api/ngrok/tunnels/${tunnelName}`)
    if (response.data.success) {
      toast.success('Tunnel closed successfully')
      await loadTunnels()
    }
  } catch (error) {
    console.error('Failed to close tunnel:', error)
    toast.error(error.response?.data?.detail || 'Failed to close tunnel')
  }
}

// Close all tunnels
async function closeAllTunnels() {
  if (!confirm('Are you sure you want to stop all tunnels and reset the ngrok binary? This will kill any dangling ngrok processes.')) return
  
  try {
    const response = await client.delete('/api/ngrok/tunnels')
    if (response.data.success) {
      toast.success('Ngrok infrastructure reset successfully')
      await loadTunnels()
    }
  } catch (error) {
    console.error('Failed to reset infrastructure:', error)
    if (error.response?.status === 429) {
      toast.info('Infrastructure is busy. Please wait a few seconds.')
    } else {
      toast.error(error.response?.data?.detail || 'Failed to reset infrastructure')
    }
  }
}

// Copy to clipboard
function copyToClipboard(text) {
  navigator.clipboard.writeText(text)
    .then(() => {
      toast.success('URL copied to clipboard')
    })
    .catch(() => {
      toast.error('Failed to copy URL')
    })
}
</script>

<style scoped>
.custom-scrollbar::-webkit-scrollbar {
  width: 4px;
}
.custom-scrollbar::-webkit-scrollbar-track {
  background: transparent;
}
.custom-scrollbar::-webkit-scrollbar-thumb {
  background: rgba(255, 255, 255, 0.05);
  border-radius: 10px;
}
.custom-scrollbar::-webkit-scrollbar-thumb:hover {
  background: rgba(255, 255, 255, 0.1);
}
</style>

