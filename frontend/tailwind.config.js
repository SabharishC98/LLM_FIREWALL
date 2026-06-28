/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  safelist: [
    {
      pattern: /bg-luma-(000|100|300|500|700|900|FFF)(\/[0-9]+)?/,
    },
    {
      pattern: /text-luma-(000|100|300|500|700|900|FFF)/,
    },
    {
      pattern: /border-luma-(000|100|300|500|700|900|FFF)/,
    },
    'text-accent-gold',
    'bg-accent-gold',
    'border-accent-gold'
  ],
  theme: {
    extend: {
      gridTemplateColumns: {
        '24': 'repeat(24, minmax(0, 1fr))',
      },
      colors: {
        luma: {
          '000': '#000000',
          100: '#111111',
          300: '#333333',
          500: '#666666',
          700: '#AAAAAA',
          900: '#E0E0E0',
          'FFF': '#FFFFFF',
        },
        'accent-gold': '#D4B89E',
        // Clean, stark semantic colors for the dashboard (Old Money Palette)
        firewall: {
          red: '#9B4444', // Muted Oxblood
          green: '#4A7C59', // Sage/Hunter
          yellow: '#C89F3C', // Old Gold
          blue: '#456B7D', // Slate Blue
          purple: '#6B5B95', // Dusty Plum
        },
      },
      fontFamily: {
        sans: ['Manrope', 'system-ui', '-apple-system', 'sans-serif'],
        mono: ['Manrope', 'monospace'],
      },
      animation: {
        'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'flicker': 'flicker 0.15s infinite',
        'slide-in': 'slide-in 0.3s ease-out',
        'fade-in': 'fade-in 0.5s ease-out',
      },
      keyframes: {
        'flicker': {
          '0%': { opacity: '0.9' },
          '50%': { opacity: '0.85' },
          '100%': { opacity: '1' },
        },
        'slide-in': {
          '0%': { transform: 'translateX(100%)', opacity: '0' },
          '100%': { transform: 'translateX(0)', opacity: '1' },
        },
        'fade-in': {
          '0%': { opacity: '0', transform: 'translateY(10px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
      },
    },
  },
  plugins: [],
}
