import { defineStore } from 'pinia'
import { ref } from 'vue'
import apiClient from '@/api/client'

export const useSpecStore = defineStore('spec', () => {
    // State
    const specs = ref([])
    const currentSpec = ref(null)
    const loading = ref(false)
    const error = ref(null)

    // Actions
    async function fetchSpecs() {
        loading.value = true
        error.value = null

        try {
            const response = await apiClient.get('/api/specs', { timeout: 120000 })
            specs.value = response.data
            return { success: true }
        } catch (err) {
            error.value = err.response?.data?.detail || 'Failed to fetch specs'
            return { success: false, error: error.value }
        } finally {
            loading.value = false
        }
    }

    async function fetchSpec(specId) {
        loading.value = true
        error.value = null

        try {
            const response = await apiClient.get(`/api/specs/${specId}`, { timeout: 120000 })
            // console.log('Spec API response:', response.data)
            currentSpec.value = response.data
            return { success: true, data: response.data }
        } catch (err) {
            // console.error('Spec fetch error:', err)
            error.value = err.response?.data?.detail || 'Failed to fetch spec'
            return { success: false, error: error.value }
        } finally {
            loading.value = false
        }
    }

    async function uploadSpec(name, content) {
        loading.value = true
        error.value = null

        try {
            const response = await apiClient.post('/api/specs', { timeout: 120000 }, {
                name,
                content,
            })

            specs.value.unshift(response.data)
            return { success: true, data: response.data }
        } catch (err) {
            error.value = err.response?.data?.detail || 'Failed to upload spec'
            return { success: false, error: error.value }
        } finally {
            loading.value = false
        }
    }

    async function updateSpec(specId, updates) {
        loading.value = true
        error.value = null

        try {
            const response = await apiClient.patch(`/api/specs/${specId}`, { timeout: 120000 }, updates)

            // Update in list
            const index = specs.value.findIndex((s) => s.id === specId)
            if (index !== -1) {
                specs.value[index] = response.data
            }

            // Update current if it's the same
            if (currentSpec.value?.id === specId) {
                currentSpec.value = response.data
            }

            return { success: true, data: response.data }
        } catch (err) {
            error.value = err.response?.data?.detail || 'Failed to update spec'
            return { success: false, error: error.value }
        } finally {
            loading.value = false
        }
    }

    async function deleteSpec(specId) {
        loading.value = true
        error.value = null

        try {
            await apiClient.delete(`/api/specs/${specId}`, { timeout: 120000 })

            // Remove from list
            specs.value = specs.value.filter((s) => s.id !== specId)

            // Clear current if it's the same
            if (currentSpec.value?.id === specId) {
                currentSpec.value = null
            }

            return { success: true }
        } catch (err) {
            error.value = err.response?.data?.detail || 'Failed to delete spec'
            return { success: false, error: error.value }
        } finally {
            loading.value = false
        }
    }

    async function resyncSpec(specId, content) {
        loading.value = true
        error.value = null

        try {
            const response = await apiClient.put(`/api/specs/${specId}/resync`, { timeout: 120000 }, {
                content,
            })

            // Update in list
            const index = specs.value.findIndex((s) => s.id === specId)
            if (index !== -1) {
                specs.value[index] = response.data
            }

            // Update current if it's the same
            if (currentSpec.value?.id === specId) {
                currentSpec.value = response.data
            }

            return { success: true, data: response.data }
        } catch (err) {
            // Handle validation errors (422) differently
            if (err.response?.status === 422) {
                const validationErrors = err.response?.data?.detail
                if (Array.isArray(validationErrors)) {
                    // Pydantic validation errors
                    const errorMessages = validationErrors.map(e => `${e.loc.join('.')}: ${e.msg}`).join(', ')
                    error.value = `Validation error: ${errorMessages}`
                } else if (typeof validationErrors === 'string') {
                    error.value = validationErrors
                } else {
                    error.value = 'Invalid request format'
                }
            } else {
                error.value = err.response?.data?.detail || err.message || 'Failed to re-sync spec'
            }
            return { success: false, error: error.value }
        } finally {
            loading.value = false
        }
    }

    return {
        specs,
        currentSpec,
        loading,
        error,
        fetchSpecs,
        fetchSpec,
        uploadSpec,
        updateSpec,
        deleteSpec,
        resyncSpec,
    }
})
