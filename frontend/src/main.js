import { createApp } from 'vue'
import { createPinia } from 'pinia'
import Toast from 'vue-toastification'
import 'vue-toastification/dist/index.css'

import App from './App.vue'
import router from './router'
import apiClient from './api/client'
import './assets/main.css'

// Create app
const app = createApp(App)

// Add global properties
app.config.globalProperties.$api = apiClient

// Use plugins
app.use(createPinia())
app.use(router)
app.use(Toast, {
    position: 'top-right',
    timeout: 3000,
    closeOnClick: true,
    pauseOnFocusLoss: true,
    pauseOnHover: true,
    draggable: true,
    draggablePercent: 0.6,
    showCloseButtonOnHover: false,
    hideProgressBar: false,
    closeButton: 'button',
    icon: true,
    rtl: false,
    transition: 'Vue-Toastification__fade',
    maxToasts: 5,
    newestOnTop: true,
})

// Mount app
app.mount('#app')
