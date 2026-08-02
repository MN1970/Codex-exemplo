'use strict';

/**
 * agent_service_example.js — Exemplo de agente Manta em Node.js
 * ================================================================
 *
 * Serviço HTTP minimalista (sem framework, apenas `http` nativo — troque
 * por Express/Fastify em produção) que representa um agente Manta
 * implementado em Node.js (ex.: integração Slack, skill em TypeScript,
 * conector SharePoint) recebendo um handoff do Maestro (Python, ver
 * instrumentation/python/maestro_routing_example.py -> dispatch_remote_http).
 *
 * Fluxo instrumentado:
 *   1. Extrai o contexto W3C (traceparent) dos headers da requisição
 *      recebida do Maestro -> o `agent.dispatch` span aqui criado é FILHO
 *      do `maestro.route` span do lado Python, no MESMO trace.
 *   2. Cria o agent span (`agent.dispatch`) e, dentro dele, skill spans
 *      (`skill.<nome>`).
 *   3. Expõe queue depth (fila de requisições em processamento) para o
 *      gauge `manta.agent.queue_depth`.
 *
 * Rodar:
 *   cd observability
 *   npm install
 *   node instrumentation/nodejs/agent_service_example.js
 *
 * Testar (simula o handoff do Maestro; troque o traceparent por um trace_id
 * real gerado pelo maestro_routing_example.py se quiser ver o link no Jaeger):
 *
 *   curl -X POST http://localhost:8090/agents/manta-03-s8/invoke \
 *     -H 'Content-Type: application/json' \
 *     -H 'traceparent: 00-4bf92f3577b34da6a3ce929d0e0e4736-00f067aa0ba902b7-01' \
 *     -d '{"query": "Analisar edital de saneamento AySA"}'
 */

const http = require('http');
const { configureTelemetry } = require('./otel-setup');

const AGENT_ID = process.env.MANTA_AGENT_ID || 'manta-03-s8';
const SEGMENT = process.env.MANTA_SEGMENT || 'saneamento';
const PORT = Number(process.env.PORT || 8090);

const telemetry = configureTelemetry('agente-saneamento-node', {
  agentId: AGENT_ID,
  environment: process.env.MANTA_ENV || 'local',
});

// Fila simulada de requisições em processamento — alimenta
// manta.agent.queue_depth (gauge observável lido a cada export cycle).
let inFlight = 0;
telemetry.registerQueueDepthProvider(AGENT_ID, () => inFlight);

async function runSkill(skillName, agentId, workFn) {
  return telemetry.skillSpan(skillName, agentId, async (span) => {
    const result = await workFn(span);
    return result;
  });
}

async function handleInvoke(query) {
  return telemetry.agentSpan(
    AGENT_ID,
    async (span) => {
      span.setAttribute('manta.query', String(query).slice(0, 200));

      await runSkill('ler-edital', AGENT_ID, async () => {
        await sleep(60); // simula extração de PDF
      });

      await runSkill('aluci-guard', AGENT_ID, async () => {
        await sleep(15); // simula auditoria de referências normativas
      });

      return {
        agent_id: AGENT_ID,
        segment: SEGMENT,
        result: `[${AGENT_ID}] parecer técnico (node.js) gerado para: ${String(query).slice(0, 60)}`,
      };
    },
    { segment: SEGMENT },
  );
}

function sleep(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

const server = http.createServer((req, res) => {
  if (req.method !== 'POST' || !req.url.startsWith(`/agents/${AGENT_ID}/invoke`)) {
    res.writeHead(404, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify({ error: 'not_found' }));
    return;
  }

  let body = '';
  req.on('data', (chunk) => {
    body += chunk;
  });

  req.on('end', () => {
    inFlight += 1;

    // Extrai o traceparent/tracestate/baggage recebido do Maestro e faz
    // com que TODO o processamento abaixo rode dentro daquele contexto —
    // por isso o handleInvoke() precisa estar dentro deste callback.
    telemetry.runWithExtractedContext(req.headers, async () => {
      try {
        const payload = JSON.parse(body || '{}');
        const result = await handleInvoke(payload.query);
        res.writeHead(200, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify(result));
      } catch (err) {
        res.writeHead(500, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify({ error: String(err.message || err) }));
      } finally {
        inFlight -= 1;
      }
    });
  });
});

server.listen(PORT, () => {
  console.log(
    `[${AGENT_ID}] agente Node.js escutando em http://localhost:${PORT} ` +
      `(POST /agents/${AGENT_ID}/invoke)`,
  );
});

process.on('SIGTERM', async () => {
  const { shutdownTelemetry } = require('./otel-setup');
  await shutdownTelemetry();
  server.close(() => process.exit(0));
});
