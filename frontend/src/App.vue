<script setup>
import { onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'

const authStore = useAuthStore()

onMounted(() => {
  authStore.fetchCurrentUser()
})
</script>

<template>
  <div id="app" class="min-h-screen bg-background">
    <RouterView v-slot="{ Component }">
      <KeepAlive :include="['Dashboard', 'SpecDetail']">
        <component :is="Component" />
      </KeepAlive>
    </RouterView>
  </div>
</template>

