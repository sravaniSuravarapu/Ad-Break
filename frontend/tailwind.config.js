/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{ts,tsx}'],
  darkMode: 'class',
  theme: {
    extend: {
      fontFamily: {
        sans: ['"Plus Jakarta Sans"', 'Segoe UI', 'sans-serif'],
      },
      boxShadow: {
        card: '0 18px 40px rgba(12, 16, 40, 0.12)',
      },
    },
  },
  plugins: [],
}
