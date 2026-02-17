import { defineStore } from 'pinia'
import { ref } from 'vue'
import apiClient from '@/api/client'
// import { useWebSocketJourneyGeneration } from '@/composables/useWebSocketJourneyGeneration'

export const useJourneyStore = defineStore('journey', () => {
    // State
    const journeys = ref([])
    const activeJourney = ref(null)
    const executionState = ref('idle') // 'idle' | 'running' | 'paused' | 'completed'
    const executionResults = ref([])
    const sessionData = ref({})
    const loading = ref(false)
    const error = ref(null)
    const runnerConfig = ref({
        baseUrl: 'https://api.example.com',
        initialSessionData: '',
    })

    // Actions
    async function fetchJourneys() {
        loading.value = true
        error.value = null

        try {
            const response = await apiClient.get('/api/journeys')
            journeys.value = response.data
            return { success: true }
        } catch (err) {
            error.value = err.response?.data?.detail || 'Failed to fetch journeys'
            return { success: false, error: error.value }
        } finally {
            loading.value = false
        }
    }

    async function fetchJourney(journeyId) {
        loading.value = true
        error.value = null

        try {
            const response = await apiClient.get(`/api/journeys/${journeyId}`)
            activeJourney.value = response.data
            return { success: true, data: response.data }
        } catch (err) {
            error.value = err.response?.data?.detail || 'Failed to fetch journey'
            return { success: false, error: error.value }
        } finally {
            loading.value = false
        }
    }

    // async function generateJourneys(specId, strategy = 'ai') {

    //     loading.value = true
    //     error.value = null

    //     const { generateJourneys: wsGenerate } = useWebSocketJourneyGeneration()

    //     try {
    //     const result = await wsGenerate(specId, strategy)
        
    //     // Add to journeys list
    //     journeys.value.unshift(...result)
        
    //     return { success: true, data: result }
    //     } catch (err) {
    //     error.value = err.message || 'Failed to generate journeys'
    //     return { success: false, error: error.value }
    //     } finally {
    //     loading.value = false
    //     }

        // loading.value = true
        // error.value = null

        // try {
        //     const response = await apiClient.post(
        //         `/api/specs/${specId}/generate-journeys`,
        //         { strategy },
        //         options
        //     )

        //     // Add to journeys list
        //     journeys.value.unshift(...response.data)

        //     return { success: true, data: response.data }
        // } catch (err) {
        //     error.value = err.response?.data?.detail || 'Failed to generate journeys'
        //     return { success: false, error: error.value }
        // } finally {
        //     loading.value = false
        // }
    // }

    async function createJourney(journeyData) {
        loading.value = true
        error.value = null

        try {
            const response = await apiClient.post('/api/journeys', journeyData)

            journeys.value.unshift(response.data)
            return { success: true, data: response.data }
        } catch (err) {
            error.value = err.response?.data?.detail || 'Failed to create journey'
            return { success: false, error: error.value }
        } finally {
            loading.value = false
        }
    }

    async function updateJourney(journeyId, updates) {
        loading.value = true
        error.value = null

        try {
            const response = await apiClient.put(`/api/journeys/${journeyId}`, updates)

            // Update in list
            const index = journeys.value.findIndex((j) => j.id === journeyId)
            if (index !== -1) {
                journeys.value[index] = response.data
            }

            // Update active if it's the same
            if (activeJourney.value?.id === journeyId) {
                activeJourney.value = response.data
            }

            return { success: true, data: response.data }
        } catch (err) {
            error.value = err.response?.data?.detail || 'Failed to update journey'
            return { success: false, error: error.value }
        } finally {
            loading.value = false
        }
    }

    async function deleteJourney(journeyId) {
        loading.value = true
        error.value = null

        try {
            await apiClient.delete(`/api/journeys/${journeyId}`)

            // Remove from list
            journeys.value = journeys.value.filter((j) => j.id !== journeyId)

            // Clear active if it's the same
            if (activeJourney.value?.id === journeyId) {
                activeJourney.value = null
            }

            return { success: true }
        } catch (err) {
            error.value = err.response?.data?.detail || 'Failed to delete journey'
            return { success: false, error: error.value }
        } finally {
            loading.value = false
        }
    }

    function setStepStatus(stepId, status) {
        if (!activeJourney.value) return

        const node = activeJourney.value.nodes.find((n) => n.id === stepId)
        if (node) {
            node.data.status = status
        }
    }

    function saveStepResult(stepId, result) {
        const existingIndex = executionResults.value.findIndex(
            (r) => r.stepId === stepId
        )

        if (existingIndex !== -1) {
            executionResults.value[existingIndex] = result
        } else {
            executionResults.value.push(result)
        }

        // --- SYNC SESSION DATA FOR LIVE PREVIEWS ---
        // Ensure we have active journey data to map edges
        let currentJourney = activeJourney.value
        if (!currentJourney) {
            // Fallback: search across all loaded journeys
            currentJourney = journeys.value.find(j => j.nodes && j.nodes.some(n => n.id === stepId))
        }

        if (currentJourney && result.responseBody) {
            const edges = currentJourney.edges || []
            const relevantEdges = edges.filter(e => e.source === stepId)

            const newSessionUpdates = {}

            // 1. Process explicit mappings
            relevantEdges.forEach(edge => {
                const mappings = edge.data?.dataMapping || []
                mappings.forEach(m => {
                    let value = null
                    if (m.from?.startsWith('request.params.')) {
                        const key = m.from.replace('request.params.', '')
                        value = result.request?.params?.[key]
                    } else if (m.from?.startsWith('response.')) {
                        const path = m.from.replace('response.', '')
                        value = getNestedValue(result.responseBody, path)
                    }

                    if (value !== null && value !== undefined) {
                        newSessionUpdates[m.to] = value
                    }
                })
            })

            // 2. Smart extraction (IDs and common fields) - help fallback logic
            if (typeof result.responseBody === 'object' && result.responseBody !== null) {
                const idKeys = ['id', 'uuid', 'pk', 'restaurant_id', 'order_id', 'user_id', 'token', 'access_token']

                const extractIds = (obj) => {
                    if (!obj || typeof obj !== 'object') return
                    Object.entries(obj).forEach(([k, v]) => {
                        if (idKeys.includes(k) && (typeof v === 'string' || typeof v === 'number')) {
                            newSessionUpdates[k] = v
                            // Also map to pathParams context for flexibility
                            newSessionUpdates[`pathParams.${k}`] = v
                        }
                        if (['detail', 'data'].includes(k) && typeof v === 'object') {
                            extractIds(v)
                        }
                    })
                }
                extractIds(result.responseBody)
            }

            if (Object.keys(newSessionUpdates).length > 0) {
                updateSessionData(newSessionUpdates)
            }
        }

        setStepStatus(stepId, 'success')
    }

    // Helper for store
    function getNestedValue(obj, path) {
        if (!path) return obj
        const keys = path.split('.')
        let value = obj
        for (const key of keys) {
            if (value && typeof value === 'object') {
                value = value[key]
                // Try wrappers if first lookup fails
                if (value === undefined && keys.indexOf(key) === 0) {
                    value = (obj.data && obj.data[key]) || (obj.detail && obj.detail[key])
                }
            } else {
                return null
            }
        }
        return value
    }

    function saveStepError(stepId, error) {
        executionResults.value.push({
            stepId,
            error: error.message || String(error),
            statusCode: 0,
        })

        setStepStatus(stepId, 'error')
    }

    function updateSessionData(newData) {
        sessionData.value = {
            ...sessionData.value,
            ...newData,
        }
    }

    function resetExecution() {
        executionState.value = 'idle'
        executionResults.value = []
        sessionData.value = {}

        // Reset all node statuses
        if (activeJourney.value) {
            activeJourney.value.nodes.forEach((node) => {
                node.data.status = 'pending'
            })
        }
    }

    function getJourney(journeyId) {
        return journeys.value.find((j) => j.id === journeyId)
    }

    return {
        journeys,
        activeJourney,
        executionState,
        executionResults,
        sessionData,
        loading,
        error,
        runnerConfig,
        fetchJourneys,
        fetchJourney,
        // generateJourneys,
        createJourney,
        updateJourney,
        deleteJourney,
        setStepStatus,
        saveStepResult,
        saveStepError,
        updateSessionData,
        resetExecution,
        getJourney,
    }
})
