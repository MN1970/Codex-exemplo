'use strict';

/**
 * Classificador determinístico de janela viável de execução para fases de
 * obra de faseamento de tráfego (MOT) em trevos/interseções rodoviárias.
 *
 * Todas as decisões são tomadas por regras fixas (A-H), sem heurística ou
 * julgamento livre. O objeto de retorno inclui `motivos` para rastreabilidade
 * e auditoria (ex.: aluci-guard / laudos técnicos).
 */

/**
 * Converte letra de LOS ('A'..'F') em ordem numérica (1..6), onde maior é pior.
 * @param {string} letra
 * @returns {number}
 */
function ordemLos(letra) {
  const tabela = { A: 1, B: 2, C: 3, D: 4, E: 5, F: 6 };
  const chave = String(letra || '').trim().toUpperCase();
  const ordem = tabela[chave];
  if (ordem === undefined) {
    throw new Error(`LOS inválido: "${letra}" (esperado 'A'..'F')`);
  }
  return ordem;
}

/**
 * Classifica a janela viável de execução para uma fase de MOT.
 *
 * @param {Object} faseInput
 * @param {number} faseInput.vc_projetado - relação V/C projetada (0-2).
 * @param {string} faseInput.los_resultante - LOS resultante da fase ('A'..'F').
 * @param {string} faseInput.los_atual - LOS atual (antes da fase, 'A'..'F').
 * @param {string[]} faseInput.restricao_contratual_periodo - períodos com restrição contratual (ex.: ['feriado','safra']).
 * @param {boolean} faseInput.atividade_critica - true se fundação/lançamento de vigas/demolição sobre pista.
 * @param {number} faseInput.duracao_dias - duração da fase em dias.
 * @param {number} faseInput.folga_total_dias - folga total disponível no cronograma (dias).
 * @param {boolean} faseInput.sazonalidade_pico - true se o período avaliado é pico sazonal/turístico.
 * @param {boolean} [faseInput.rota_alternativa_aprovada] - true se há rota alternativa aprovada (para bloqueio total).
 * @param {boolean} [faseInput.solicita_bloqueio_total] - true se a opção avaliada é bloqueio total sem faseamento (Regra H).
 *
 * @returns {{janela: string|null, exigeTmpAprofundado: boolean, degradacaoLos: boolean, motivos: string[], erros: string[]}}
 */
function classificarJanela(faseInput) {
  const {
    vc_projetado,
    los_resultante,
    los_atual,
    restricao_contratual_periodo = [],
    atividade_critica = false,
    duracao_dias,
    folga_total_dias,
    sazonalidade_pico = false,
    rota_alternativa_aprovada = false,
    solicita_bloqueio_total = false,
  } = faseInput;

  const motivos = [];
  const erros = [];

  const ordemResultante = ordemLos(los_resultante);
  const ordemAtual = ordemLos(los_atual);
  const degradacaoLos = ordemResultante > ordemAtual;

  motivos.push(
    `LOS atual='${los_atual}' (ordem ${ordemAtual}) -> LOS resultante='${los_resultante}' (ordem ${ordemResultante}); ` +
      `degradacaoLos=${degradacaoLos}.`
  );

  // Regra C: sinalização de TMP aprofundado (não bloqueia a fase por si só).
  const exigeTmpAprofundado = vc_projetado > 0.8;
  if (exigeTmpAprofundado) {
    motivos.push(
      `Regra C: vc_projetado=${vc_projetado} > 0.80 -> exige_tmp_aprofundado=true (sinalização, não bloqueia a fase).`
    );
  }

  const haRestricaoContratual =
    Array.isArray(restricao_contratual_periodo) && restricao_contratual_periodo.length > 0;

  // Regra H: bloqueio total sem faseamento — avaliada apenas quando solicitada
  // explicitamente como opção (não é o fluxo padrão de janela por fase).
  if (solicita_bloqueio_total) {
    const folgaSuficiente = folga_total_dias >= duracao_dias;
    if (rota_alternativa_aprovada && folgaSuficiente) {
      motivos.push(
        `Regra H: rota_alternativa_aprovada=true E folga_total_dias(${folga_total_dias}) >= duracao_dias(${duracao_dias}) ` +
          `-> opção 'bloqueio_total_sem_faseamento' viável.`
      );
      return {
        janela: 'bloqueio_total_sem_faseamento',
        exigeTmpAprofundado,
        degradacaoLos,
        motivos,
        erros,
      };
    }
    if (!rota_alternativa_aprovada) {
      erros.push(
        "Regra H: 'bloqueio_total_sem_faseamento' rejeitado — rota_alternativa_aprovada=false. " +
          'É necessária rota alternativa aprovada para interditar totalmente sem faseamento.'
      );
    }
    if (!folgaSuficiente) {
      erros.push(
        `Regra H: 'bloqueio_total_sem_faseamento' rejeitado — folga_total_dias(${folga_total_dias}) < duracao_dias(${duracao_dias}). ` +
          'Folga de cronograma insuficiente para absorver a interdição total.'
      );
    }
    erros.push(
      "Opção 'bloqueio_total_sem_faseamento' não pode ser adotada nestas condições — redesenho do faseamento é necessário " +
        '(reavaliar sequenciamento de fases / negociar rota alternativa / recuperar folga de cronograma).'
    );
    return {
      janela: null,
      exigeTmpAprofundado,
      degradacaoLos,
      motivos,
      erros,
    };
  }

  // Regra A: atividade crítica (risco estrutural) sempre prevalece, independente de V/C ou LOS.
  if (atividade_critica === true) {
    motivos.push(
      "Regra A: atividade_critica=true (fundação/lançamento de vigas/demolição sobre pista) -> " +
        "janela 'noturna_ou_fds_interdicao_total' obrigatória, independente de V/C ou LOS (risco estrutural, não de capacidade)."
    );
    return {
      janela: 'noturna_ou_fds_interdicao_total',
      exigeTmpAprofundado,
      degradacaoLos,
      motivos,
      erros,
    };
  }

  // Regra D: diurna_vale — exige LOS resultante <= D, sem degradação, V/C <= 0.80 e sem restrição contratual.
  const condicaoLosBase = ordemResultante <= ordemLos('D') && !degradacaoLos;
  if (condicaoLosBase && vc_projetado <= 0.8 && !haRestricaoContratual) {
    motivos.push(
      `Regra D: LOS resultante ('${los_resultante}') <= 'D', sem degradação, vc_projetado=${vc_projetado} <= 0.80 e ` +
        'sem restrição contratual para o período -> janela \'diurna_vale\' permitida.'
    );
    return {
      janela: 'diurna_vale',
      exigeTmpAprofundado,
      degradacaoLos,
      motivos,
      erros,
    };
  }

  // Regra E: diurna_pico — mesmas condições de LOS/degradação de D, mas tolera vc_projetado > 0.80
  // (nesse caso fica condicionada ao flag exigeTmpAprofundado, já calculado acima).
  if (condicaoLosBase && !haRestricaoContratual) {
    motivos.push(
      `Regra E: LOS resultante ('${los_resultante}') <= 'D', sem degradação e sem restrição contratual, mas ` +
        `vc_projetado=${vc_projetado} > 0.80 -> janela 'diurna_pico' condicionada a exige_tmp_aprofundado=${exigeTmpAprofundado}.`
    );
    return {
      janela: 'diurna_pico',
      exigeTmpAprofundado,
      degradacaoLos,
      motivos,
      erros,
    };
  }

  // Regra F: noturna preferencial quando vc_projetado > 0.80 (mesmo fora de pico) — ou atividade_critica,
  // já tratada na Regra A. Aplica-se tipicamente quando a janela diurna não é viável por LOS/degradação.
  if (exigeTmpAprofundado) {
    motivos.push(
      `Regra F: vc_projetado=${vc_projetado} > 0.80 e condições de LOS/degradação não permitem janela diurna ` +
        "(LOS resultante fora do limite 'D' e/ou degradacaoLos=true) -> janela 'noturna' preferencial."
    );
    return {
      janela: 'noturna',
      exigeTmpAprofundado,
      degradacaoLos,
      motivos,
      erros,
    };
  }

  // Regra G: fim_de_semana só viável se !sazonalidade_pico e sem restrição contratual para o período;
  // senão, tratar como pico (mesma regra de vc_projetado > 0.80 -> TMP aprofundado).
  if (!sazonalidade_pico && !haRestricaoContratual) {
    motivos.push(
      'Regra G: sazonalidade_pico=false e sem restrição contratual para o período -> janela ' +
        "'fim_de_semana' viável."
    );
    return {
      janela: 'fim_de_semana',
      exigeTmpAprofundado,
      degradacaoLos,
      motivos,
      erros,
    };
  }
  if (sazonalidade_pico || haRestricaoContratual) {
    motivos.push(
      'Regra G: sazonalidade_pico=true ou há restrição contratual para o período -> período tratado como pico ' +
        `(mesma regra de vc_projetado > 0.80 -> exige_tmp_aprofundado=${exigeTmpAprofundado}).`
    );
  }

  // Fallback determinístico: degradação de LOS presente, mas fora das condições explícitas de A/D/E/F/G
  // (ex.: vc_projetado <= 0.80, não crítica, LOS ainda dentro do limite, porém com degradação em relação ao
  // cenário atual). As regras A-H não cobrem literalmente esta combinação; por precaução operacional,
  // trata-se como janela 'noturna', priorizando segurança/capacidade sobre custo de janela.
  motivos.push(
    'Fallback determinístico: nenhuma das regras A, D, E, F ou G foi satisfeita explicitamente ' +
      `(ex.: degradacaoLos=${degradacaoLos} sem enquadramento em D/E, e vc_projetado=${vc_projetado} <= 0.80 sem ` +
      "enquadramento em F) -> por precaução, janela 'noturna' é adotada até redesenho/reavaliação específica."
  );
  return {
    janela: 'noturna',
    exigeTmpAprofundado,
    degradacaoLos,
    motivos,
    erros,
  };
}

module.exports = { classificarJanela, ordemLos };

// ---------------------------------------------------------------------------
// TESTES (assert nativo do Node — sem framework externo)
// Executar com: node engine/mot/window-classifier.js
// ---------------------------------------------------------------------------
if (require.main === module) {
  const assert = require('assert');

  // Caso 1 — Parclo km230,5 (OAE/passagem inferior): atividade_critica=true.
  // Esperado: Regra A prevalece sempre, independente de V/C (0.55, folgado) ou LOS (estável em 'C').
  {
    const input = {
      vc_projetado: 0.55,
      los_resultante: 'C',
      los_atual: 'C',
      restricao_contratual_periodo: [],
      atividade_critica: true,
      duracao_dias: 300,
      folga_total_dias: 0,
      sazonalidade_pico: false,
      rota_alternativa_aprovada: false,
    };
    const resultado = classificarJanela(input);
    assert.strictEqual(
      resultado.janela,
      'noturna_ou_fds_interdicao_total',
      'Caso Parclo km230,5: atividade crítica (OAE) deve forçar interdição total noturna/FDS (Regra A).'
    );
    assert.strictEqual(resultado.degradacaoLos, false, 'Caso Parclo km230,5: LOS C->C não é degradação.');
    assert.strictEqual(resultado.exigeTmpAprofundado, false, 'Caso Parclo km230,5: vc=0.55 não exige TMP aprofundado.');
    assert.strictEqual(resultado.erros.length, 0, 'Caso Parclo km230,5: não deve haver erros.');
    console.log('OK - Caso 1 (Parclo km230,5 / OAE, Regra A):', resultado.janela);
  }

  // Caso 2 — Diamante km282 (sem OAE crítica confirmada): vc=0.72 (<=0.80), LOS C (pior que B) -> degradação.
  // A Regra E exige explicitamente "mesmas condições de D" (LOS resultante <= 'D' E !degradacao) para permitir
  // diurna_pico, tolerando apenas o V/C > 0.80 em relação a D. Como aqui HÁ degradação de LOS (B->C), tanto D
  // quanto E ficam bloqueados pela condição de degradação — mesmo com V/C confortável e LOS ainda dentro do
  // limite 'D'. A Regra F também não se aplica (vc=0.72 <= 0.80 e atividade_critica=false). Restando apenas a
  // Regra G, que é avaliada de forma independente de LOS/degradação (ela só verifica sazonalidade_pico e
  // restrição contratual do período): como sazonalidade_pico=false e restricao_contratual_periodo=[] (sem
  // restrição), a janela 'fim_de_semana' é literalmente viável pela Regra G — é o único enquadramento que
  // resta para esta fase, já que a degradação de LOS bloqueia apenas as janelas diurnas (D/E), não a de FDS.
  {
    const input = {
      vc_projetado: 0.72,
      los_resultante: 'C',
      los_atual: 'B',
      restricao_contratual_periodo: [],
      atividade_critica: false,
      duracao_dias: 120,
      folga_total_dias: 15,
      sazonalidade_pico: false,
      rota_alternativa_aprovada: false,
    };
    const resultado = classificarJanela(input);
    assert.strictEqual(resultado.degradacaoLos, true, 'Caso Diamante km282: LOS B->C é degradação.');
    assert.strictEqual(
      resultado.janela,
      'fim_de_semana',
      "Caso Diamante km282: degradação de LOS bloqueia D/E (diurnas), F não se aplica (vc<=0.80, não crítica) -> " +
        "Regra G avalia isoladamente sazonalidade_pico/restrição e libera 'fim_de_semana'."
    );
    assert.strictEqual(resultado.exigeTmpAprofundado, false, 'Caso Diamante km282: vc=0.72 não exige TMP aprofundado.');
    console.log('OK - Caso 2 (Diamante km282, degradação bloqueia D/E, Regra G libera fim_de_semana):', resultado.janela);
  }

  // Caso 3 — vc=0.95 (>0.80), LOS resultante E (pior que C) -> degradação e fora do limite 'D'.
  // Esperado: exigeTmpAprofundado=true (Regra C), degradacaoLos=true, janela='noturna' (Regra F).
  {
    const input = {
      vc_projetado: 0.95,
      los_resultante: 'E',
      los_atual: 'C',
      restricao_contratual_periodo: [],
      atividade_critica: false,
      duracao_dias: 60,
      folga_total_dias: 10,
      sazonalidade_pico: false,
      rota_alternativa_aprovada: false,
    };
    const resultado = classificarJanela(input);
    assert.strictEqual(resultado.exigeTmpAprofundado, true, 'Caso 3: vc=0.95 > 0.80 exige TMP aprofundado.');
    assert.strictEqual(resultado.degradacaoLos, true, 'Caso 3: LOS C->E é degradação.');
    assert.strictEqual(resultado.janela, 'noturna', "Caso 3: vc>0.80 fora de LOS aceitável -> janela 'noturna' (Regra F).");
    console.log('OK - Caso 3 (vc=0.95, LOS E, Regra F):', resultado.janela);
  }

  // Caso 4 — bloqueio total solicitado, mas rota_alternativa_aprovada=false e folga insuficiente.
  // Esperado: array de erros não vazio, rejeitando 'bloqueio_total_sem_faseamento' (Regra H).
  {
    const input = {
      vc_projetado: 0.4,
      los_resultante: 'B',
      los_atual: 'B',
      restricao_contratual_periodo: [],
      atividade_critica: false,
      duracao_dias: 90,
      folga_total_dias: 10,
      sazonalidade_pico: false,
      rota_alternativa_aprovada: false,
      solicita_bloqueio_total: true,
    };
    const resultado = classificarJanela(input);
    assert.ok(
      Array.isArray(resultado.erros) && resultado.erros.length > 0,
      'Caso 4: deve retornar array de erros não vazio ao rejeitar bloqueio total sem faseamento.'
    );
    assert.notStrictEqual(
      resultado.janela,
      'bloqueio_total_sem_faseamento',
      'Caso 4: bloqueio total não pode ser aceito sem rota alternativa aprovada e folga suficiente.'
    );
    console.log('OK - Caso 4 (bloqueio total rejeitado, Regra H):', resultado.erros);
  }

  console.log('\nTodos os testes passaram.');
}
