/** @type {import('tailwindcss').Config} */
export default {
  // "content": Tailwind kin files ko scan kare taake used CSS classes dhund sake.
  // Sirf woh classes final CSS mein aayengi jo in files mein use ho rahi hain.
  content: [
    './index.html',
    './src/**/*.{js,ts,jsx,tsx}',
  ],

  // "theme": Colors, fonts, spacing waghera customize karne ke liye.
  theme: {
    // "extend": Tailwind ke default styles ko rakhte hue naye styles add karta hai.
    extend: {},
  },

  // "plugins": Extra Tailwind plugins yahan add hote hain (e.g. forms, typography).
  plugins: [],
}
