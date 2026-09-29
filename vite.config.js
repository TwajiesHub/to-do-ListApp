import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

const API_URL = 'http://localhost:8000'

export default defineConfig({
  plugins: [react()],
  server: {
    proxy: { '/api': API_URL },
    // The SQLite file changes on every save. Without this, Vite reloads the page each time.
    watch: { ignored: ['**/todos.db*', '**/.venv/**', '**/api/**', '**/tests/**', '**/*.log'] },
  },
})
