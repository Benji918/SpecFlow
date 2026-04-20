<template>
  <div class="card">
    <h2 class="text-2xl font-semibold mb-4">Upload OpenAPI Specification</h2>

    <!-- Drag and Drop Area -->
    <div
      @drop.prevent="handleDrop"
      @dragover.prevent="dragOver = true"
      @dragleave.prevent="dragOver = false"
      :class="[
        'border-2 border-dashed rounded-lg p-8 text-center transition-all cursor-pointer',
        dragOver
          ? 'border-primary bg-primary/10'
          : 'border-gray-700 hover:border-gray-600',
      ]"
      @click="$refs.fileInput.click()"
    >
      <input
        ref="fileInput"
        type="file"
        accept=".json,.yaml,.yml"
        @change="handleFileSelect"
        class="hidden"
      />

      <div class="space-y-4">
        <!-- Upload Icon -->
        <div class="flex justify-center">
          <Upload :size="48" class="text-gray-400" />
        </div>

        <!-- Instructions -->
        <div>
          <p class="text-lg font-medium mb-2">
            {{ dragOver ? 'Drop your file here' : 'Drop your OpenAPI spec here' }}
          </p>
          <p class="text-sm text-gray-400">
            or click to browse for a file
          </p>
          <p class="text-xs text-gray-500 mt-2">
            Supports JSON and YAML formats
          </p>

          <div class="pt-4 border-t border-gray-800/50 mt-4">
            <button
              type="button"
              @click.stop="handleUseSample"
              :disabled="loadingSample || uploading"
              class="group relative inline-flex items-center px-4 py-2 text-sm font-medium text-primary hover:text-white transition-all duration-300 rounded-full border border-primary/20 hover:border-primary/50 bg-primary/5 hover:bg-primary/10 overflow-hidden"
            >
              <div v-if="loadingSample" class="mr-2 animate-spin">
                <Loader2 :size="16" />
              </div>
              <Sparkles v-else :size="16" class="mr-2 group-hover:rotate-12 transition-transform" />
              <span>{{ loadingSample ? 'Loading Sample...' : 'Try with sample data' }}</span>
              
              <!-- Subtle glow effect on hover -->
              <div class="absolute inset-0 -translate-x-full group-hover:translate-x-full transition-transform duration-1000 bg-gradient-to-r from-transparent via-white/10 to-transparent"></div>
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Selected File Info -->
    <div v-if="selectedFile" class="mt-4 p-4 bg-surface rounded-lg">
      <div class="flex items-center justify-between">
        <div class="flex items-center space-x-3">
          <FileText :size="20" class="text-primary" />
          <div>
            <p class="font-medium">{{ selectedFile.name }}</p>
            <p class="text-sm text-gray-400">
              {{ formatFileSize(selectedFile.size) }}
            </p>
          </div>
        </div>
        <button
          @click="selectedFile = null"
          class="text-gray-400 hover:text-red-500 transition-colors"
        >
          <X :size="20" />
        </button>
      </div>
    </div>

    <!-- Name Input -->
    <div v-if="selectedFile" class="mt-4">
      <label for="spec-name" class="block text-sm font-medium mb-2">
        Specification Name
      </label>
      <input
        id="spec-name"
        v-model="specName"
        type="text"
        required
        class="input-field w-full"
        placeholder="My API Specification"
      />
    </div>

    <!-- Validation Error -->
    <div v-if="validationError" class="mt-4 p-4 bg-red-500/10 border border-red-500 rounded-lg">
      <div class="flex items-start space-x-2">
        <AlertCircle :size="20" class="text-red-500 mt-0.5" />
        <div>
          <p class="font-medium text-red-500">Validation Error</p>
          <p class="text-sm text-red-400 mt-1">{{ validationError }}</p>
        </div>
      </div>
    </div>

    <!-- Progress Bar -->
    <div v-if="uploading" class="mt-4">
      <div class="flex items-center justify-between mb-2">
        <span class="text-sm font-medium">Uploading...</span>
        <span class="text-sm text-gray-400">{{ uploadProgress }}%</span>
      </div>
      <div class="w-full h-2 bg-gray-800 rounded-full overflow-hidden">
        <div
          class="h-full bg-primary transition-all duration-300"
          :style="{ width: uploadProgress + '%' }"
        ></div>
      </div>
    </div>

    <!-- Action Buttons -->
    <div v-if="selectedFile" class="mt-6 flex space-x-3">
      <button
        @click="handleUpload"
        :disabled="uploading || !specName.trim()"
        class="btn-primary flex-1"
      >
        <span v-if="!uploading">Upload Specification</span>
        <span v-else>Uploading...</span>
      </button>
      <button
        @click="cancel"
        :disabled="uploading"
        class="btn-secondary"
      >
        Cancel
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useSpecStore } from '@/stores/spec'
import { useToast } from 'vue-toastification'
import { Upload, FileText, X, AlertCircle, Sparkles, Loader2 } from 'lucide-vue-next'
import { load } from 'js-yaml'

const router = useRouter()
const specStore = useSpecStore()
const toast = useToast()

const dragOver = ref(false)
const selectedFile = ref(null)
const specName = ref('')
const uploading = ref(false)
const uploadProgress = ref(0)
const validationError = ref(null)
const loadingSample = ref(false)

function handleDrop(event) {
  dragOver.value = false
  const files = event.dataTransfer.files
  if (files.length > 0) {
    processFile(files[0])
  }
}

function handleFileSelect(event) {
  const files = event.target.files
  if (files.length > 0) {
    processFile(files[0])
  }
}

function processFile(file) {
  // Check file type
  const validExtensions = ['.json', '.yaml', '.yml']
  const fileExtension = file.name.substring(file.name.lastIndexOf('.')).toLowerCase()
  
  if (!validExtensions.includes(fileExtension)) {
    toast.error('Invalid file type. Please upload a JSON or YAML file.')
    return
  }

  selectedFile.value = file
  specName.value = file.name.replace(/\.(json|yaml|yml)$/, '')
  validationError.value = null
}

async function handleUseSample() {
  if (loadingSample.value || uploading.value) return
  
  loadingSample.value = true
  validationError.value = null
  
  try {
    // Fetch from local public assets
    const response = await fetch('/mini-assessment-api.yaml')
    if (!response.ok) throw new Error('Failed to fetch sample data')
    
    const blob = await response.blob()
    
    // Create a File object from the blob
    const file = new File([blob], 'mini-assessment-api.yaml', { 
      type: 'text/yaml' 
    })
    
    processFile(file)
    toast.info('Sample data loaded! You can now review and upload it.')
    
  } catch (error) {
    console.error('Error fetching sample data:', error)
    toast.error('Could not load sample data. Please try uploading your own spec.')
    validationError.value = 'Failed to load sample data from local assets.'
  } finally {
    loadingSample.value = false
  }
}

async function handleUpload() {
  if (!selectedFile.value || !specName.value.trim()) return

  uploading.value = true
  uploadProgress.value = 0
  validationError.value = null

  // Check for duplicate spec name
  const trimmedName = specName.value.trim()
  const existingSpec = specStore.specs.find(
    (s) => s.name.toLowerCase() === trimmedName.toLowerCase()
  )
  if (existingSpec) {
    validationError.value = `A specification with the name "${trimmedName}" already exists. Please choose a different name.`
    uploading.value = false
    toast.error('Specification name must be unique')
    return
  }

  try {
    // Read file content
    const content = await readFileContent(selectedFile.value)
    
    // Simulate progress
    uploadProgress.value = 30

    // Parse content (JSON or YAML)
    let specContent
    try {
      if (selectedFile.value.name.endsWith('.json')) {
        specContent = JSON.parse(content)
      } else {
        // For YAML, we'll use js-yaml
        specContent = load(content)
      }
    } catch (parseError) {
      throw new Error('Invalid file format: ' + parseError.message)
    }

    uploadProgress.value = 50

    // Validate OpenAPI spec (Basic check)
    if (!specContent.openapi && !specContent.swagger) {
      validationError.value = 'Missing openapi or swagger version'
      uploading.value = false
      uploadProgress.value = 0
      toast.error('Invalid OpenAPI specification')
      return
    }
    
    // Optional: You could do more checks here, but let backend handle strict validation
    validationError.value = null

    uploadProgress.value = 70

    // Upload to backend
    const result = await specStore.uploadSpec(specName.value.trim(), specContent)

    uploadProgress.value = 100

    if (result.success) {
      toast.success('Specification uploaded successfully!')
      setTimeout(() => {
        router.push(`/spec/${result.data.id}`)
      }, 500)
    } else {
      validationError.value = result.error
      toast.error(result.error)
    }
  } catch (error) {
    validationError.value = error.message
    toast.error('Upload failed: ' + error.message)
  } finally {
    uploading.value = false
    uploadProgress.value = 0
  }
}

function readFileContent(file) {
  return new Promise((resolve, reject) => {
    const reader = new FileReader()
    reader.onload = (e) => resolve(e.target.result)
    reader.onerror = (e) => reject(e)
    reader.readAsText(file)
  })
}

function formatFileSize(bytes) {
  if (bytes === 0) return '0 Bytes'
  const k = 1024
  const sizes = ['Bytes', 'KB', 'MB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i]
}

function cancel() {
  selectedFile.value = null
  specName.value = ''
  validationError.value = null
}
</script>
