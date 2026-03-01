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
          title="Clear all manual tunnels"
        >
          <X :size="10" class="group-hover/kill:rotate-90 transition-transform" />
          <span class="text-[8px] font-black uppercase tracking-widest">Clear All</span>
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
      
      <!-- Instructions for Manual Tunnel -->
      <div class="p-3 bg-primary/5 rounded-lg border border-primary/10 flex items-start space-x-3 mb-4">
        <Terminal :size="16" class="text-primary/60 mt-0.5 shrink-0" />
        <div class="space-y-2">
          <p class="text-[10px] text-gray-300 font-black uppercase tracking-widest">Manual Setup Instructions</p>
          <div class="text-[9px] text-gray-500 font-medium leading-tight space-y-2">
            <p>To connect your <span class="text-white">locally running backend</span> to the app, follow these steps:</p>
            <ol class="list-decimal list-inside space-y-1 ml-1 opacity-80">
              <li>Open a <span class="text-primary">terminal</span> on your machine.</li>
              <li>Ensure your backend is running on <span class="bg-black/40 px-1 py-0.5 rounded">your port</span> (e.g., 8000).</li>
              <li>Run: <code class="bg-black/60 px-1.5 py-0.5 rounded text-primary">ngrok http &lt;your-port&gt;</code></li>
              <li>Copy the <span class="font-bold underline">Forwarding URL</span> (starts with https://).</li>
              <li>Paste onto the input below and click <span class="font-bold text-white italic underline">Register Tunnel</span>.</li>
            </ol>
          </div>
        </div>
      </div>

      <!-- Add Manual Tunnel Form -->
      <div class="space-y-3 mb-4">
        <div class="flex items-center space-x-2">
          <div class="flex-1 relative group">
            <span class="absolute left-3 top-1/2 -translate-y-1/2 text-[10px] font-bold text-gray-600 group-focus-within:text-primary transition-colors">URL</span>
            <input
              v-model="manualTunnelUrl"
              type="url"
              placeholder="https://xxxx-xxxx-xxxx.ngrok-free.app"
              class="w-full bg-black/40 border border-gray-800 rounded-lg px-3 py-2 text-xs text-white pl-12 focus:ring-1 focus:ring-primary/30 focus:border-primary/50 transition-all outline-none"
              @keyup.enter="addManualTunnel"
            />
          </div>
          <button
            @click="addManualTunnel"
            :disabled="!manualTunnelUrl || registering"
            class="px-3 py-2 bg-primary hover:bg-primary-dark disabled:opacity-30 disabled:grayscale text-black font-black text-[10px] uppercase tracking-widest rounded-lg transition-all flex items-center justify-center hover:shadow-[0_0_15px_rgba(191,245,73,0.2)]"
          >
            <Loader v-if="registering" :size="14" class="animate-spin" />
            <span v-else>Register Tunnel</span>
          </button>
        </div>
      </div>

      <!-- Active Tunnels List -->
      <div v-if="tunnels.length > 0" class="space-y-3">
        <div class="flex items-center justify-between">
          <h4 class="text-[9px] font-black uppercase text-gray-600 tracking-widest">Active Manual Tunnels</h4>
          <span class="text-[9px] px-1.5 py-0.5 rounded-full bg-primary/10 text-primary font-bold">{{ tunnels.length }}</span>
        </div>
        
        <div v-for="tunnel in tunnels" :key="tunnel.public_url" class="group bg-white/[0.03] rounded-xl border border-white/5 hover:border-primary/20 transition-all duration-300 p-3 relative overflow-hidden">
          <div class="absolute inset-0 bg-primary/5 opacity-0 group-hover:opacity-100 transition-opacity"></div>
          
          <div class="relative z-10">
            <div class="flex items-center justify-between mb-2">
              <div class="flex items-center space-x-2">
                <span class="text-[10px] font-bold text-gray-300">{{ tunnel.name }}</span>
                <span class="text-[8px] px-1.5 py-0.5 rounded bg-black/40 text-primary font-black uppercase border border-primary/20">
                  {{ tunnel.proto }}
                </span>
              </div>
              <div class="flex items-center space-x-1 opacity-0 group-hover:opacity-100 transition-opacity translate-x-1 group-hover:translate-x-0 transition-transform">
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
                  title="Remove tunnel"
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
                  <span class="w-1 h-1 rounded-full bg-green-500 mr-1.5 animate-pulse"></span>
                  Status: REAL-TIME
                </div>
                <div class="flex items-center">
                  <span class="w-1 h-1 rounded-full bg-yellow-600 mr-1.5"></span>
                  MANUAL
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- No Tunnels Message -->
      <div v-else class="flex flex-col items-center justify-center py-10 text-center space-y-3 opacity-40">
        <div class="p-4 bg-white/5 rounded-full border border-white/10">
          <Terminal :size="32" class="text-gray-500" />
        </div>
        <div>
          <p class="text-[10px] font-black uppercase tracking-widest text-gray-500">Waitng for Input</p>
          <p class="text-[8px] text-gray-700 mt-1">Please register a manual ngrok URL followng the steps above</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useToast } from 'vue-toastification'
import { Globe, Loader, Copy, X, RotateCcw, ChevronRight, Terminal } from 'lucide-vue-next'
import client from '@/api/client'

const toast = useToast()
const tunnels = ref([])
const manualTunnelUrl = ref('')
const loading = ref(false)
const registering = ref(false)

const emit = defineEmits(['use-as-base-url'])

// Load active tunnels on mount
onMounted(async () => {
  await loadTunnels()
})

// Load tunnels from backend (syncs with database/redis)
async function loadTunnels() {
  loading.value = true
  try {
    const response = await client.get('/api/ngrok/tunnels')
    if (response.data.success) {
      tunnels.value = response.data.tunnels
    }
  } catch (error) {
    console.error('Failed to load tunnels:', error)
    toast.error('Failed to sync tunnels from server')
  } finally {
    loading.value = false
  }
}

// Add manual tunnel
async function addManualTunnel() {
  const url = manualTunnelUrl.value.trim()
  if (!url) {
    toast.error('Please enter an ngrok Forwarding URL')
    return
  }

  if (!url.startsWith('http')) {
    toast.error('URL must start with http:// or https://')
    return
  }

  registering.value = true
  try {
    const response = await client.post('/api/ngrok/add-manual-tunnel', {
      public_url: url,
      local_port: 8000,
      protocol: 'http'
    })

    if (response.data.success) {
      toast.success('Tunnel registered successfully')
      manualTunnelUrl.value = ''
      await loadTunnels()
    }
  } catch (error) {
    console.error('Failed to add manual tunnel:', error)
    toast.error(error.response?.data?.detail || 'Registration failed')
  } finally {
    registering.value = false
  }
}

// Close/Remove specific tunnel
async function closeTunnel(tunnelName) {
  try {
    const response = await client.delete(`/api/ngrok/tunnels/${tunnelName}`)
    if (response.data.success) {
      toast.success('Tunnel removed')
      await loadTunnels()
    }
  } catch (error) {
    console.error('Failed to remove tunnel:', error)
    toast.error('Failed to remove tunnel from sync')
  }
}

// Close all tunnels
async function closeAllTunnels() {
  if (tunnels.value.length === 0) return
  if (!confirm('Are you sure you want to clear all manual tunnels?')) return
  
  try {
    const response = await client.delete('/api/ngrok/tunnels')
    if (response.data.success) {
      toast.success('All tunnels cleared')
      tunnels.value = []
    }
  } catch (error) {
    console.error('Failed to clear tunnels:', error)
    toast.error('Failed to clear registered tunnels')
  }
}

// Copy to clipboard
function copyToClipboard(text) {
  navigator.clipboard.writeText(text)
    .then(() => {
      toast.success('URL copied')
    })
    .catch(() => {
      toast.error('Failed to copy')
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
