// =============================================================================
// ESLINT CONFIGURATION — eslint.config.js (Flat Config Format)
// =============================================================================
// ESLint kya hai?
//   ESLint JavaScript aur React code ke liye ek "Static Code Analysis" tool hai.
//   Yeh aapka code run (execute) kiye baghair scan karta hai aur syntax errors,
//   bugs, missing dependencies, unused variables, aur best-practice violations
//   ko pehle hi pakar leta hai.
//
// Is file ka maqsad:
//   Vite + React projects mein modern ESLint 9+ flat config use karta hai.
//   Yeh file ESLint ko batati hai ke:
//     1. Kaunse folders ignore karne hain (e.g., 'dist', 'node_modules')
//     2. Browser & Node.js globals (window, document, process) ko recognize karo
//     3. React Hooks ke rules (useEffect dependencies, etc.) check karo
//     4. Vite HMR (Fast Refresh) standards enforce karo
// =============================================================================

import js from '@eslint/js'
import globals from 'globals'
import reactHooks from 'eslint-plugin-react-hooks'
import reactRefresh from 'eslint-plugin-react-refresh'

export default [
  // 1. Files aur folders jinhe linting se ignore karna hai
  { ignores: ['dist', 'node_modules'] },

  // 2. Main configuration for JS & JSX files
  {
    files: ['**/*.{js,jsx}'],
    languageOptions: {
      ecmaVersion: 2020,
      globals: {
        ...globals.browser,
        ...globals.node, // Allows process.cwd(), process.env in Vite & config files
      },
      parserOptions: {
        ecmaVersion: 'latest',
        ecmaFeatures: { jsx: true },
        sourceType: 'module',
      },
    },
    plugins: {
      'react-hooks': reactHooks,
      'react-refresh': reactRefresh,
    },
    rules: {
      // Standard JavaScript recommended rules (syntax checks, unreachable code, etc.)
      ...js.configs.recommended.rules,

      // React Hooks rules (Hook calling order aur dependency array verify karta hai)
      ...reactHooks.configs.recommended.rules,

      // Unused variables ki warning (e.g. imported but unused variables)
      'no-unused-vars': [
        'warn',
        {
          vars: 'all',
          args: 'after-used',
          ignoreRestSiblings: true,
          varsIgnorePattern: '^[A-Z_]',
        },
      ],

      // Fast refresh rule: components ke sath helper exports ko handle karta hai
      'react-refresh/only-export-components': [
        'warn',
        { allowConstantExport: true },
      ],
    },
  },
]
