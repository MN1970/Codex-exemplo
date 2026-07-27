/**
 * Shared, cross-cutting types live here. Domain-specific types (e.g. tied
 * to a single API resource) can instead live next to their `api/*.ts` file.
 */
export interface ApiError {
  message: string
  status: number
}
