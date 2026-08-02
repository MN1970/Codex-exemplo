'use strict';

/**
 * Thin Supabase client wrapper shared by the auto-registration service,
 * the webhook handler, and the A/B test service.
 *
 * Requires env vars:
 *   SUPABASE_URL
 *   SUPABASE_SERVICE_ROLE_KEY   (server-side key — never expose client-side)
 *
 * Uses @supabase/supabase-js (see package.json). Kept in one place so
 * the rest of the codebase never re-derives credentials or reaches
 * into `agents` with ad-hoc REST calls.
 */

let cachedClient = null;

function getSupabaseClient() {
  if (cachedClient) return cachedClient;

  const { createClient } = require('@supabase/supabase-js');
  const url = process.env.SUPABASE_URL;
  const key = process.env.SUPABASE_SERVICE_ROLE_KEY;

  if (!url || !key) {
    throw new Error(
      'Missing SUPABASE_URL / SUPABASE_SERVICE_ROLE_KEY env vars — see infra/agent-registry/.env.example'
    );
  }

  cachedClient = createClient(url, key, {
    auth: { persistSession: false },
  });
  return cachedClient;
}

module.exports = { getSupabaseClient };
