/**
 * Types for the agent registry (`GET /agents`) and its Server-Sent
 * Events invocation contract (`POST /agents/{slug}/invoke`) — mirrors
 * `manta-backend/routers/agents.py`.
 */
export type AgentAxis = 'horizontal' | 'vertical' | 'lifecycle'
export type AgentStatus = 'operacional' | 'parcial' | 'planejado'

export interface Agent {
  code: string
  slug: string
  name: string
  aliases: string[]
  tier: string
  status: AgentStatus
  axis: AgentAxis
}

/** Payload for `event: meta` — the first SSE frame of an invocation. */
export interface InvokeMeta {
  session_id: string
  agent_slug: string
  agent_code: string
}

/** Payload for `event: done` — the last SSE frame of an invocation. */
export interface InvokeDone {
  session_id: string
  full_response: string
}

/** A persisted prompt/response pair, as returned by `GET /agents/{slug}/sessions`. */
export interface AgentSession {
  id: string
  agent_code: string
  agent_slug: string
  prompt: string
  response: string
  user_email: string | null
  created_at: string
}
