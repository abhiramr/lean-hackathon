/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,jsx}'],
  theme: {
    extend: {
      colors: {
        void: '#06080d',
        abyss: '#0a0e17',
        slate: { 850: '#1a2234', 950: '#0d1321' },
        proof: { ok: '#22c55e', fail: '#ef4444', pending: '#eab308' },
        cyan: { 450: '#22d3ee' },
      },
      fontFamily: {
        mono: ['JetBrains Mono', 'Fira Code', 'monospace'],
        display: ['Outfit', 'system-ui', 'sans-serif'],
        body: ['DM Sans', 'system-ui', 'sans-serif'],
      },
      animation: {
        'fade-in': 'fadeIn 0.4s ease forwards',
        'slide-up': 'slideUp 0.5s cubic-bezier(0.4,0,0.2,1) forwards',
        'pulse-glow': 'pulseGlow 2s ease-in-out infinite',
        'scan': 'scan 3s linear infinite',
      },
      keyframes: {
        fadeIn: { from: { opacity: 0 }, to: { opacity: 1 } },
        slideUp: { from: { opacity: 0, transform: 'translateY(12px)' }, to: { opacity: 1, transform: 'translateY(0)' } },
        pulseGlow: { '0%,100%': { boxShadow: '0 0 0 0 rgba(34,211,238,0)' }, '50%': { boxShadow: '0 0 20px 4px rgba(34,211,238,0.15)' } },
        scan: { from: { transform: 'translateY(-100%)' }, to: { transform: 'translateY(100%)' } },
      },
    },
  },
  plugins: [],
};
