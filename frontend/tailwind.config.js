// =============================================================================
// TAILWIND CSS CONFIGURATION — tailwind.config.js
// =============================================================================
// Yeh file Tailwind CSS framework ko batati hai ke:
//   1. Kaunsi project files mein Tailwind classes dhundo (content scanning)
//   2. Design system mein kya customize karna hai (theme.extend)
//   3. Koi third-party Tailwind plugin use karna hai ya nahi (plugins)
//
// Yeh file DIRECTLY Tailwind ke liye hai, PostCSS ke liye nahi.
// PostCSS ke liye postcss.config.js alag file hai.
//
// Kaise kaam karta hai (Build Time):
//   Jab "npm run build" ya "npm run dev" chalao, Vite PostCSS ko trigger karta
//   hai, PostCSS tailwind plugin ko chalata hai, aur Tailwind ye config file
//   read karke final CSS generate karta hai.
// =============================================================================

/** @type {import('tailwindcss').Config} */
export default {

  // ---------------------------------------------------------------------------
  // CONTENT — Tree Shaking (Unused Classes Ko Remove Karna)
  // ---------------------------------------------------------------------------
  // Tailwind by default hazaron CSS classes generate karna janta hai (bg-red-500,
  // flex, p-4, text-xl, etc.) lekin SABI classes bundle mein nahi dali jaati.
  // Tailwind sirf woh classes bundle mein dalta hai jo aapke code mein ACTUALLY
  // use ho rahi hain.
  //
  // Yeh "content" array batata hai ke Tailwind kin files ko SCAN kare.
  // Tailwind in files mein string patterns dhundhta hai jaise "bg-blue-500",
  // "rounded-xl", "flex", "p-4" etc.
  //
  // Hamare project mein:
  //   - index.html         → Root HTML template (Vite ka entry point)
  //   - src/**/*.{js,...}  → Tamam React components (.jsx), utility files (.js)
  //                          "**" matlab koi bhi subfolder (nested bhi)
  //                          "{js,ts,jsx,tsx}" matlab in 4 extensions wali files
  //
  // Real-life example: Agar sirf TodoDashboard.jsx mein "bg-blue-600" likha hai
  // aur baaki kisi file mein nahi, toh sirf us ek class ka CSS bundle mein
  // aayega. Isse final CSS ~5KB tak chhi ho sakti hai, warna 3MB+ hoti.
  // ---------------------------------------------------------------------------
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],

  // ---------------------------------------------------------------------------
  // THEME — Design System Customization
  // ---------------------------------------------------------------------------
  // "theme" aapke poore design system ko control karta hai:
  // colors, fonts, spacing, border-radius, breakpoints, shadows, etc.
  //
  // "theme.extend" ka matlab: Tailwind ke default values RAKHTE hue naye
  // values ADD karo. Agar sirf "theme: {}" likhte (without extend), toh
  // Tailwind ke sare defaults override ho jaate.
  //
  // Hamare project mein custom CSS variables index.css mein :root par define
  // hain (--primary, --bg-main, etc.) aur components mein bg-[var(--primary)]
  // syntax se directly use hoti hain. Isliye abhi theme.extend khali hai.
  //
  // Future extension examples:
  //   extend: {
  //     colors: {
  //       brand: { DEFAULT: '#3157d5', hover: '#2547bd' },  // Brand colors
  //       danger: '#b94343',
  //     },
  //     fontFamily: {
  //       sans: ['Manrope', 'system-ui', 'sans-serif'],      // Default font
  //     },
  //     borderRadius: {
  //       '2xl': '1rem',
  //       '3xl': '1.5rem',
  //     },
  //     animation: {
  //       'slide-up': 'rise 0.2s ease-out both',
  //       'toast-in': 'toast-in 0.22s ease-out both',
  //     },
  //   }
  // ---------------------------------------------------------------------------
  theme: {
    extend: {},
  },

  // ---------------------------------------------------------------------------
  // PLUGINS — Third-Party Tailwind Extensions
  // ---------------------------------------------------------------------------
  // Tailwind ke official aur community plugins yahan register hote hain.
  // Plugin install karne ke baad yahan add karo taake Tailwind unhe load kare.
  //
  // Popular plugins:
  //   require('@tailwindcss/forms')       → Input, select, checkbox ko better
  //                                         default styling deta hai
  //   require('@tailwindcss/typography')  → .prose class milti hai jo
  //                                         markdown/blog content style karta hai
  //   require('@tailwindcss/line-clamp')  → Text ko N lines par clamp karta hai
  //   require('@tailwindcss/aspect-ratio')→ Image/video aspect ratios control
  //
  // Hamare project mein custom CSS index.css mein @layer components ke zariye
  // likhi gayi hai, isliye abhi koi external plugin zaroorat nahi.
  // ---------------------------------------------------------------------------
  plugins: [],
}
