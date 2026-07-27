import { defineConfig, mergeConfig } from 'vitest/config'
import viteConfig from './vite.config'

// Kept separate from vite.config.ts (rather than adding a `test` block
// there) so `vite.config.ts` doesn't need a `vitest/config` type
// dependency just to build the app.
export default mergeConfig(
  viteConfig,
  defineConfig({
    test: {
      environment: 'jsdom',
      setupFiles: ['./src/test/setup.ts'],
      css: false,
    },
  }),
)
