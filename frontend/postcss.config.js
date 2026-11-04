// =============================================================================
// POSTCSS CONFIGURATION — postcss.config.js
// =============================================================================
// PostCSS ek CSS processing tool hai — bilkul jaise Babel JavaScript ke liye
// hota hai, PostCSS CSS ke liye hota hai.
//
// Jab bhi Vite aapki CSS files process karta hai (dev mode ya build), woh
// PostCSS ko beech mein lata hai. PostCSS is config file ko padh kar yeh
// decide karta hai ke CSS par kaunse "plugins" (transformations) chalane hain.
//
// Is project mein PostCSS do kaam karta hai:
//   1. Tailwind CSS → Utility classes ko actual CSS rules mein convert karna
//   2. Autoprefixer → Browser compatibility ke liye vendor prefixes add karna
//
// Processing Flow:
//   aapki .css file (index.css)
//       │
//       ▼
//   PostCSS engine
//       │
//       ├── [Plugin 1] tailwindcss  → @tailwind directives expand hoti hain
//       │                             aur scan ki gayi classes ka CSS banta hai
//       │
//       └── [Plugin 2] autoprefixer → Final CSS mein browser-specific
//                                     prefixes inject hote hain
//       │
//       ▼
//   Browser-ready final CSS bundle
//
// NOTE: Yeh file tailwind.config.js se ALAG hai.
//   - postcss.config.js → PostCSS ko batata hai ke "Tailwind ko use karo"
//   - tailwind.config.js → Tailwind ko batata hai ke "Kya scan karo, kya banao"
// =============================================================================

export default {
  plugins: {

    // -------------------------------------------------------------------------
    // PLUGIN 1: tailwindcss
    // -------------------------------------------------------------------------
    // Yeh plugin Tailwind CSS ko PostCSS pipeline mein activate karta hai.
    //
    // Kya karta hai:
    //   - index.css mein likhe "@tailwind base", "@tailwind components",
    //     "@tailwind utilities" directives ko expand karta hai
    //   - tailwind.config.js ki "content" list mein scan ki gayi files se
    //     used classes dhundh kar unka CSS generate karta hai
    //   - @layer base / @layer components / @layer utilities blocks ko
    //     sahi order mein final CSS mein inject karta hai
    //
    // Real example: Jab TodoDashboard.jsx mein "bg-blue-600 rounded-xl p-4"
    // likha hota hai, yeh plugin woh teen classes ka exact CSS rules generate
    // karke bundle mein dalta hai.
    //
    // {} matlab: tailwind.config.js se automatically settings lo (koi
    // extra options yahan pass nahi karne).
    // -------------------------------------------------------------------------
    tailwindcss: {},

    // -------------------------------------------------------------------------
    // PLUGIN 2: autoprefixer
    // -------------------------------------------------------------------------
    // Yeh plugin automatically vendor-specific CSS prefixes add karta hai
    // taake CSS maximum browsers mein correctly kaam kare.
    //
    // Kya karta hai:
    //   Aap likhte hain:          Autoprefixer bana deta hai:
    //   display: flex;        →   display: -webkit-box;
    //                             display: -ms-flexbox;
    //                             display: flex;
    //
    //   user-select: none;    →   -webkit-user-select: none;
    //                             -moz-user-select: none;
    //                             -ms-user-select: none;
    //                             user-select: none;
    //
    //   transition: all 0.2s; →   -webkit-transition: all 0.2s;
    //                             transition: all 0.2s;
    //
    // Kyun zaroori hai:
    //   Alag alag browsers (Chrome, Safari, Firefox, Edge) CSS features ko
    //   kabhi kabhi apne "experimental" prefix ke sath implement karte hain.
    //   Autoprefixer caniuse.com database se pata karta hai ke kaunse prefixes
    //   abhi bhi zaroorat hain aur automatically add kar deta hai. Aapko
    //   manually "-webkit-" waghaira likhne ki zaroorat nahi parti.
    //
    // {} matlab: Default browser support targets use karo jo package.json ki
    // "browserslist" field se ya standard defaults se aate hain.
    // -------------------------------------------------------------------------
    autoprefixer: {},
  },
}
