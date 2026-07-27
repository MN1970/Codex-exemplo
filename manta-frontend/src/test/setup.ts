import { cleanup } from '@testing-library/react'
import { afterEach } from 'vitest'
import '@testing-library/jest-dom/vitest'

// `globals: false` in vitest.config.ts means `afterEach` isn't a global,
// so @testing-library/react's own auto-cleanup (which only registers
// itself when it detects a global `afterEach`) never kicks in — without
// this, every test's rendered DOM piles up on top of the previous one.
afterEach(() => {
  cleanup()
})
