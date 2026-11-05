// PostCSS CSS ko process karne ka tool hai jo Vite ke build pipeline mein chalta hai.
export default {
  plugins: {
    // 1. "tailwindcss": Tailwind utility classes ko actual CSS rules mein convert karta hai.
    tailwindcss: {},

    // 2. "autoprefixer": Har browser (Chrome, Safari, Firefox) ke mutabiq automatic CSS prefixes (-webkit-, -moz-) lagata hai.
    autoprefixer: {},
  },
}
