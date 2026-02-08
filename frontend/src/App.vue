<template>
  <div id="app" class="min-h-screen bg-background">
    <RouterView />
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'

const authStore = useAuthStore()

onMounted(() => {
  // Fetch current user if token exists
  if (authStore.token) {
    authStore.fetchCurrentUser()
  }
})
</script>
