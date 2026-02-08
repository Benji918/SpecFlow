/** @type {import('tailwindcss').Config} */
export default {
    content: [
        "./index.html",
        "./src/**/*.{vue,js,ts,jsx,tsx}",
    ],
    darkMode: 'class',
    theme: {
        extend: {
            colors: {
                // SpecFlow Brand Colors (from branding.json)
                primary: '#BFF549',      // Vibrant Lime/Green
                accent: '#BFF549',       // Same as primary
                background: '#000000',   // Pure Black
                surface: '#121212',      // Dark Grey for cards
                secondary: '#282828',    // Secondary button background
                link: '#99A1AF',         // Link color
            },
            fontFamily: {
                sans: ['Inter', 'system-ui', 'Helvetica Neue', 'Helvetica', 'Arial', 'sans-serif'],
            },
            fontSize: {
                'h1': '96px',
                'h2': '48px',
                'body': '24px',
            },
            borderRadius: {
                'full-brand': '9999px',  // Fully rounded buttons
            },
            boxShadow: {
                'glow': 'rgba(191, 245, 73, 0.6) 0px 0px 60px -15px',  // Primary glow
                'secondary': 'rgba(0, 0, 0, 0.1) 0px 10px 15px -3px, rgba(0, 0, 0, 0.1) 0px 4px 6px -4px',
            },
        },
    },
    plugins: [],
}
