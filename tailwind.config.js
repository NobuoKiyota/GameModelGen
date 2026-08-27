/** @type {import('tailwindcss').Config} */
export default {
  content: [
    './index.html',
    './src/**/*.{js,ts,jsx,tsx}',
  ],
  theme: {
    extend: {
      colors: {
        darkBg: '#0f1117',
        darkPanel: '#161922',
        darkCard: '#1f2432',
        darkBorder: '#2e364a',
        accentGold: '#e5b842',
        accentGoldHover: '#cfa132',
      }
    },
  },
  plugins: [],
}