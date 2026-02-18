import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import path from 'path'

// Production backend URL
const PROD_API_URL = 'https://backend--specflow--j29wymgjz5b5.code.run'

// https://vitejs.dev/config/
export default defineConfig(({ mode }) => ({
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

    // Production configuration
    ...(mode === 'production' && {
        base: '/',
        server: {
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
    }),

    preview: {
        allowedHosts: [
            'site--specflow-fe--j29wymgjz5b5.code.run'
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
    define: {
        'import.meta.env.VITE_API_URL': mode === 'production' ? `"${PROD_API_URL}"` : '""',
    },
}))
