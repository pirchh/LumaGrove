/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{ts,tsx}'],
  theme: {
    extend: {
      fontFamily: {
        sans: ['Inter', 'ui-sans-serif', 'system-ui', 'sans-serif'],
        serif: ['Georgia', 'ui-serif', 'serif'],
      },
      colors: {
        soil: '#17130f',
        moss: '#8fa36b',
        leaf: '#b7c88b',
        cream: '#f5f0e6',
        bark: '#443327',
      },
    },
  },
  plugins: [],
};
