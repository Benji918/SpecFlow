import { defineStore } from 'pinia'
import { ref } from 'vue'
import axios from 'axios'

export const useJourneyStore = defineStore('journey', () => {
    // State
    const journeys = ref([])
    const activeJourney = ref(null)
    const executionState = ref('idle') // 'idle' | 'running' | 'paused' | 'completed'
    const executionResults = ref([])
    const sessionData = ref({})
    const loading = ref(false)
    const error = ref(null)

    // Actions
    async function fetchJourneys() {
        loading.value = true
        error.value = null

        try {
            const response = await axios.get('/api/journeys')
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
            const response = await axios.get(`/api/journeys/${journeyId}`)
            activeJourney.value = response.data
            return { success: true, data: response.data }
        } catch (err) {
            error.value = err.response?.data?.detail || 'Failed to fetch journey'
            return { success: false, error: error.value }
        } finally {
            loading.value = false
        }
    }

    async function generateJourneys(specId, strategy = 'ai') {
        loading.value = true
        error.value = null

        try {
            const response = await axios.post(
                `/api/specs/${specId}/generate-journeys`,
                { strategy }
            )

            // Add to journeys list
            journeys.value.unshift(...response.data)

            return { success: true, data: response.data }
        } catch (err) {
            error.value = err.response?.data?.detail || 'Failed to generate journeys'
            return { success: false, error: error.value }
        } finally {
            loading.value = false
        }
    }

    async function createJourney(journeyData) {
        loading.value = true
        error.value = null

        try {
            const response = await axios.post('/api/journeys', journeyData)

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
            const response = await axios.put(`/api/journeys/${journeyId}`, updates)

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
            await axios.delete(`/api/journeys/${journeyId}`)

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

        setStepStatus(stepId, 'success')
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
        fetchJourneys,
        fetchJourney,
        generateJourneys,
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
