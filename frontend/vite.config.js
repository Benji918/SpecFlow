import { defineConfig, loadEnv } from 'vite'
import vue from '@vitejs/plugin-vue'
import path from 'path'

// https://vitejs.dev/config/
export default defineConfig(({ mode }) => {
    // Load env file based on `mode` in the current working directory.
    // Set the third parameter to '' to load all envs regardless of the `VITE_` prefix.
    const env = loadEnv(mode, process.cwd(), '')
    
    // Production backend URL from env or fallback
    const PROD_API_URL = env.VITE_API_URL || 'https://backend--specflow-be--j29wymgjz5b5.code.run'
    const allowedHosts = env.ALLOWED_HOSTS ? env.ALLOWED_HOSTS.split(',').map(h => h.trim()) : []

    return {
        plugins: [vue()],
        resolve: {
            alias: {
                '@': path.resolve(__dirname, './src'),
            },
        },
        server: {
            port: 5173,
            proxy: {
                '/api': {
                    target: 'http://127.0.0.1:8000',
                    changeOrigin: true,
                },
                '/ws': {
                    target: 'ws://127.0.0.1:8000',
                    ws: true,
                },
            },
        },

        // Build configuration for optimal caching
        build: {
            // Use content hashing for better long-term caching
            rollupOptions: {
                output: {
                    assetFileNames: (assetInfo) => {
                        // Add content hash to JS and CSS files
                        if (assetInfo.name?.endsWith('.js') || assetInfo.name?.endsWith('.css')) {
                            return 'assets/[name]-[hash][extname]'
                        }
                        return 'assets/[name]-[hash][extname]'
                    },
                },
            },
        },

        // Preview configuration for testing production build locally
        preview: {
            allowedHosts: allowedHosts.length > 0 ? allowedHosts : [
                'site--specflow-fe--j29wymgjz5b5.code.run',
                'specflow.pro'
            ],
            proxy: {
                '/api': {
                    target: PROD_API_URL,
                    changeOrigin: true,
                    secure: true,
                },
                '/ws': {
                    target: PROD_API_URL,
                    ws: true,
                },
            },
        },

        // Expose API URL to the app via environment variable
        // In production, the app will make direct calls to the backend
        define: {
            'import.meta.env.VITE_API_URL': mode === 'production' ? `"${PROD_API_URL}"` : '""',
        },
    }
})
