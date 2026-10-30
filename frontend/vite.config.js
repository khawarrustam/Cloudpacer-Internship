import { defineConfig, loadEnv } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), 'VITE_')

  if (!env.VITE_DEV_HOST || !env.VITE_DEV_PORT || !env.VITE_STRICT_PORT) {
    throw new Error('Missing Vite server settings in frontend/.env')
  }

  return {
    plugins: [react()],
    server: {
      host: env.VITE_DEV_HOST,
      port: Number(env.VITE_DEV_PORT),
      strictPort: env.VITE_STRICT_PORT === 'true',
    },
  }
})
