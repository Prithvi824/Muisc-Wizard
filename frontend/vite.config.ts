import { resolve } from 'path'
import { defineConfig, loadEnv } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'

export default defineConfig(({ mode }) => {
  // Load environment variables from the repo root (one level up from /frontend)
  const env = loadEnv(mode, resolve(__dirname, '..'))

  return {
    plugins: [react(), tailwindcss()],
    server: {
      allowedHosts: [env.VITE_ALLOWED_HOST],
      host: '0.0.0.0',
      port: 3000,
      cors: true
    },
    define: Object.fromEntries(
      Object.entries(env).map(([key, val]) => [
        `import.meta.env.${key}`,
        JSON.stringify(val)
      ])
    )
  }
})
