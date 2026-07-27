/**
 * Shapes mirrored from `manta-backend/routers/auth.py`. Keep in sync with
 * that file's Pydantic models — it is the source of truth for the
 * `/auth/*` contract.
 */

export interface UserPublic {
  id: string
  email: string
  full_name: string
  is_active: boolean
  is_superuser: boolean
}

export interface OrgMembership {
  org_id: string
  slug: string
  name: string
  roles: string[]
}

export interface MeResponse extends UserPublic {
  active_org: OrgMembership | null
  organizations: OrgMembership[]
}

export interface TokenResponse {
  access_token: string
  refresh_token: string
  token_type: string
  expires_in: number
  org_id: string | null
  roles: string[]
}

export interface RegisterResponse {
  user: UserPublic
  organization: OrgMembership
}

export interface LoginPayload {
  email: string
  password: string
  /** Required by the backend only when the user belongs to >1 org. */
  org_id?: string
}

export interface RegisterPayload {
  email: string
  password: string
  full_name?: string
  org_name: string
}

/**
 * Shape of the 400 `detail` the backend sends from `/auth/login` when the
 * user belongs to more than one organization and `org_id` was omitted —
 * see `_multi_org_error` in `routers/auth.py`.
 */
export interface MultiOrgErrorDetail {
  message: string
  organizations: OrgMembership[]
}

export function isMultiOrgErrorDetail(
  detail: unknown,
): detail is MultiOrgErrorDetail {
  return (
    typeof detail === 'object' &&
    detail !== null &&
    Array.isArray((detail as MultiOrgErrorDetail).organizations)
  )
}
