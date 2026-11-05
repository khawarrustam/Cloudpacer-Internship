// "import" doosri package se code is file mein lata hai.
// "js" ESLint ke standard JavaScript rules ka short naam hai.
import js from '@eslint/js'

// "globals" browser aur Node ke built-in names ki list deta hai.
// Examples: window, document, console aur process.
import globals from 'globals'

// Yeh plugin useState, useEffect aur doosre React Hooks ke rules check karta hai.
import reactHooks from 'eslint-plugin-react-hooks'

// "export default" is configuration ko ESLint ke liye available karta hai.
// Array ke andar har object ESLint configuration ka ek section hai.
export default [
  {
    // "ignores" batata hai ke kin folders ko ESLint ne check nahi karna.
    // dist generated build hai aur node_modules installed packages hain.
    ignores: ['dist', 'node_modules'],
  },
  {
    // "files" batata hai ke yeh rules kin files par apply honge.
    // ** = har folder, * = har filename, {js,jsx} = JS aur JSX extensions.
    files: ['**/*.{js,jsx}'],

    // "languageOptions" JavaScript ko samajhne ke options rakhta hai.
    languageOptions: {
      // "latest" ESLint ko modern JavaScript syntax allow karne ko kehta hai.
      ecmaVersion: 'latest',

      // "module" import aur export syntax ko allow karta hai.
      sourceType: 'module',

      // "jsx: true" ESLint ko React ka HTML jaisa JSX syntax samjhata hai.
      parserOptions: { ecmaFeatures: { jsx: true } },

      // "..." spread operator dono global-name lists ko ek object mein milata hai.
      // browser mein window/document aur Node mein process jaise names milte hain.
      globals: { ...globals.browser, ...globals.node },
    },

    // "plugins" ESLint mein extra checking abilities add karta hai.
    plugins: {
      // Left side rule prefix hai; right side imported plugin hai.
      'react-hooks': reactHooks,
    },

    // "rules" decide karta hai ke ESLint ko kya check karna hai.
    rules: {
      // JavaScript ke recommended rules ko spread karke yahan add karta hai.
      ...js.configs.recommended.rules,

      // React Hooks ke recommended rules ko bhi add karta hai.
      ...reactHooks.configs.recommended.rules,

      // Unused variable milne par build fail nahi hota, sirf warning aati hai.
      // "argsIgnorePattern: '^_'" ka matlab _ se shuru argument ignore hoga.
      'no-unused-vars': ['warn', { argsIgnorePattern: '^_' }],
    },
  },
]
