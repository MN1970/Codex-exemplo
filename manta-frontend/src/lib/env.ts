/**
 * Centralized access to Vite env vars. Add new `VITE_*` vars here rather
 * than reading `import.meta.env` ad-hoc across the codebase.
 */
export const env = {
  apiBaseUrl: import.meta.env.VITE_API_BASE_URL ?? '/api',
  appName: import.meta.env.VITE_APP_NAME ?? 'Manta Frontend',
  isDev: import.meta.env.DEV,
  isProd: import.meta.env.PROD,
} as const
