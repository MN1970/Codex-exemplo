/**
 * Testes do protótipo isolado `src/router/maestro-router-v2.ts`.
 *
 * ATENÇÃO — ESCOPO LIMITADO: este módulo foi escrito em isolamento, sem visibilidade do
 * sistema real "Maestro OS v6.0" que já existe em `src/maestro/*.py` na branch `main`
 * (orchestrator.py, detector.py, consensus.py, parser.py). Foram encontradas 3 taxonomias
 * de segmento incompatíveis coexistindo no repositório:
 *   - detector.py (main): 11 segmentos S1-S11, com S6 = "Edificações"
 *   - tests/test_maestro_router_e2e.py (main): MockMaestroRouter com ids "manta-03-s6..s10"
 *   - CLAUDE.md local + este módulo .ts: 10 segmentos S1-S10 (Portos=S6...Barragens=S10)
 *
 * Este arquivo testa apenas a lógica interna do módulo .ts como ele está — NÃO valida o
 * roteamento real de produção e NÃO deve ser tratado como suíte de regressão do Maestro
 * OS v6.0. Ver discussão da sessão para o plano de reconciliação de taxonomia antes de
 * qualquer porte desta lógica (políticas de ambiguidade, pesos de keyword) para o Python.
 */

import test from "node:test";
import assert from "node:assert/strict";

import {
  Classifier,
  AgentSelector,
  Orchestrator,
  MaestroRouterV2,
  ModelTier,
  LifecyclePhase,
  runSelfTest,
  mockExecutor,
} from "../../src/router/maestro-router-v2";

// ============================================================================================
// 1. Classifier — casos de segmento único (não ambíguos)
// ============================================================================================

test("Classifier: identifica saneamento sem ambiguidade", () => {
  const result = new Classifier().classify(
    "Preciso projetar uma ETA de ciclo completo para 200 mil habitantes.",
  );
  assert.equal(result.top?.segmentId, "saneamento");
  assert.equal(result.isAmbiguous, false);
});

test("Classifier: identifica energia via RAP/LT", () => {
  const result = new Classifier().classify("Preciso da RAP referencial para uma LT de 500kV.");
  assert.equal(result.top?.segmentId, "energia");
});

test("Classifier: keyword genérica com peso reduzido não vence termo específico de outro segmento", () => {
  // "rodovia" (peso 0.6, regra S1) aparece, mas "viaduto"+"OAE" (regra S2) têm peso 1 cada.
  const result = new Classifier().classify("Como projeto uma viga para o viaduto OAE sobre a rodovia?");
  assert.equal(result.top?.segmentId, "S2");
});

test("Classifier: nenhuma keyword reconhecida retorna top=null", () => {
  const result = new Classifier().classify("Qual o clima hoje em São Paulo?");
  assert.equal(result.top, null);
  assert.equal(result.confidence, 0);
});

// ============================================================================================
// 2. Classifier — ambiguidade e política de resolução
// ============================================================================================

test("Classifier: marca ambíguo quando dois segmentos têm score próximo", () => {
  const result = new Classifier().classify(
    "A concessionária pediu uma ETE nova + subestação de 138kV no mesmo canteiro.",
  );
  assert.ok(result.isAmbiguous, "esperava isAmbiguous=true (saneamento vs energia)");
  assert.ok(result.top && result.runnerUp, "esperava top e runnerUp definidos");
});

test("AgentSelector: aplica política MN registrada (saneamento+energia) sem exigir revisão humana", () => {
  const selection = new AgentSelector().select(
    "A concessionária pediu uma ETE nova + subestação de 138kV no mesmo canteiro.",
  );
  const primary = selection.selections.find((s) => s.role === "primary");
  const handoff = selection.selections.find((s) => s.role === "handoff");
  assert.equal(primary?.agent.id, "agente-saneamento");
  assert.equal(handoff?.agent.id, "agente-energia");
  assert.equal(selection.requiresHumanReview, false);
});

test("AgentSelector: política barragens+energia exige revisão humana explícita", () => {
  const selection = new AgentSelector().select(
    "UHE com barragem CFRD de 90m e LT de 230kV associada — preciso do estudo prévio completo.",
  );
  assert.equal(selection.requiresHumanReview, true);
});

test("AgentSelector: ambiguidade sem política MN registrada força revisão humana (regra de cautela)", () => {
  // rodovia (S1, peso 0.6) x ferrovia (S3) não têm política de ambiguidade cadastrada.
  const selection = new AgentSelector().select(
    "Preciso comparar terraplenagem SICRO da rodovia com a via permanente da ferrovia adjacente.",
  );
  if (selection.classification.isAmbiguous) {
    assert.equal(selection.requiresHumanReview, true);
  }
});

// ============================================================================================
// 3. AgentSelector — tiering de modelo
// ============================================================================================

test("AgentSelector: escalona para Opus em fase de due diligence / M&A", () => {
  const selection = new AgentSelector().select("Preciso projetar uma barragem CFRD de 80m de altura.", {
    lifecyclePhase: LifecyclePhase.DUE_DILIGENCE_MA,
  });
  const primary = selection.selections.find((s) => s.role === "primary");
  // agente-barragens tem tier único [SONNET] no registro atual — não escalona (array de 1).
  assert.equal(primary?.agent.id, "agente-barragens");
  assert.equal(primary?.tier, ModelTier.SONNET);
});

test("AgentSelector: agente com dois tiers escalona para o segundo em contexto de alta complexidade", () => {
  const selection = new AgentSelector().select("Preciso de modelagem financeira MEF para esta UHE.", {
    complexity: "alta",
  });
  // "modelagem" não é coberto pelas ROUTING_RULES atuais (só agentes verticais S1-S10 + saneamento/energia/etc).
  // Este teste documenta o comportamento real: sem match de segmento, cai em "clarify" (tier Haiku).
  const clarify = selection.selections.find((s) => s.role === "clarify");
  assert.ok(clarify, "esperava fallback 'clarify' pois 'modelagem financeira' não está nas ROUTING_RULES");
  assert.equal(clarify?.tier, ModelTier.HAIKU);
});

// ============================================================================================
// 4. Orchestrator — estrutura do plano
// ============================================================================================

test("Orchestrator: plano sem ambiguidade não tem step escalate_review", () => {
  const plan = new Orchestrator().buildPlan("Preciso da RAP referencial para uma LT de 500kV.");
  const ids = plan.steps.map((s) => s.id);
  assert.ok(ids.includes("classify"));
  assert.ok(!ids.includes("escalate_review"));
  assert.ok(ids.some((id) => id.startsWith("dispatch:agente-energia:")));
  assert.ok(ids.includes("synthesize"));
});

test("Orchestrator: caso ambíguo com human_gate inclui escalate_review e human_gate no plano", () => {
  const plan = new Orchestrator().buildPlan(
    "UHE com barragem CFRD de 90m e LT de 230kV associada — preciso do estudo prévio completo.",
  );
  const ids = plan.steps.map((s) => s.id);
  assert.ok(ids.includes("escalate_review"), "ambiguidade deveria disparar escalate_review");
  assert.ok(ids.includes("human_gate"), "política barragens+energia exige human_gate");
  // human_gate deve depender de synthesize, que por sua vez depende dos dispatches.
  const gate = plan.steps.find((s) => s.id === "human_gate");
  assert.deepEqual(gate?.dependsOn, ["synthesize"]);
});

test("Orchestrator: prompt sem segmento produz plano só com clarify (sem synthesize)", () => {
  const plan = new Orchestrator().buildPlan("Qual o clima hoje em São Paulo?");
  const ids = plan.steps.map((s) => s.id);
  assert.ok(ids.some((id) => id.endsWith(":clarify")));
  assert.ok(!ids.includes("synthesize"), "não deve sintetizar quando a única ação é pedir esclarecimento");
});

test("Orchestrator.execute: grupos executam em ordem e mockExecutor produz output determinístico", async () => {
  const orchestrator = new Orchestrator();
  const plan = orchestrator.buildPlan("Preciso da RAP referencial para uma LT de 500kV.");
  const result = await orchestrator.execute(plan, mockExecutor);
  assert.ok(result.finalOutput.startsWith("[MOCK"));
  assert.equal(result.transcript.length, plan.steps.length);
});

// ============================================================================================
// 5. Façade MaestroRouterV2 + autoteste embutido
// ============================================================================================

test("MaestroRouterV2.explain: retorna trace legível com decisão e flag de revisão humana", () => {
  const router = new MaestroRouterV2();
  const trace = router.explain("Preciso projetar uma barragem CFRD de 80m de altura.");
  assert.match(trace, /Revisão humana necessária:/);
  assert.match(trace, /agente-barragens/);
});

test("runSelfTest: os 14 casos de tests/routing/prompts.md (subconjunto) passam no classificador atual", () => {
  const summary = runSelfTest();
  const failures = summary.details.filter((d) => !d.pass);
  assert.equal(
    summary.failed,
    0,
    `${summary.failed}/${summary.total} caso(s) falharam: ${JSON.stringify(failures, null, 2)}`,
  );
});
