'use strict';

/**
 * MOTOR DE MATCHING DE PRECEDENTES — MOT (Faseamento de Tráfego) em trevos
 * e interseções.
 *
 * Adaptado do padrão da skill Manta `sicro-similaridade` (motor híbrido
 * BM25 + TF-IDF usado lá para comparar composições de custo). Aqui o mesmo
 * padrão híbrido é reaproveitado para comparar CASOS de faseamento de
 * tráfego (precedentes reais) contra um caso novo, sem nenhuma dependência
 * externa — BM25 e TF-IDF/cosseno são implementados do zero neste arquivo.
 *
 * Uso: node engine/mot/matching-engine.js
 */

// ---------------------------------------------------------------------------
// 1. BASE DE PRECEDENTES (hardcode — 8 casos reais)
// ---------------------------------------------------------------------------

const BASE_PRECEDENTES = [
  {
    id: 'caso_01',
    tipologia: 'trevo_parclo',
    subtipo: 'Parclo com rotatória',
    elemento_critico: 'OAE (passagem inferior)',
    restricao_contorno: 'rotatórias nos dois lados, 9 ramos',
    num_fases: 2,
  },
  {
    id: 'caso_02',
    tipologia: 'trevo_trombeta',
    subtipo: 'Trombeta Pista Leste',
    elemento_critico: 'OAE (vão único 30m)',
    restricao_contorno: 'laço R=35m, rampa acentuada',
    num_fases: null,
  },
  {
    id: 'caso_03',
    tipologia: 'trevo_diamante',
    subtipo: 'Diamante com rotatória',
    elemento_critico: 'viaduto 162m ligando rotatórias',
    restricao_contorno: '6 ramos, 2 rotatórias',
    num_fases: null,
  },
  {
    id: 'caso_04',
    tipologia: 'trevo_diamante',
    subtipo: 'Diamante sem rotatória',
    elemento_critico: 'OAE pequena 195m² (divergente na fonte)',
    restricao_contorno: '5 ramos, sem núcleo circular confirmado',
    num_fases: null,
  },
  {
    id: 'caso_05',
    tipologia: 'duplicacao',
    subtipo: 'Duplicação com Canteiro Central',
    elemento_critico: 'Canteiro Central',
    restricao_contorno: '3 frentes simultâneas',
    num_fases: 2,
  },
  {
    id: 'caso_06',
    tipologia: 'duplicacao',
    subtipo: 'Duplicação Total 4 faixas com Canteiro Central',
    elemento_critico: 'Canteiro Central',
    restricao_contorno: '4 faixas totais, Pare/Siga na fase 2',
    num_fases: 3,
  },
  {
    id: 'caso_07',
    tipologia: 'duplicacao',
    subtipo: 'Duplicação (2+1) com New Jersey',
    elemento_critico: 'Barreira New Jersey',
    restricao_contorno: 'seção 2+1',
    num_fases: 2,
  },
  {
    id: 'caso_08',
    tipologia: 'duplicacao',
    subtipo: 'Duplicação Total 4 faixas com New Jersey',
    elemento_critico: 'Barreira New Jersey',
    restricao_contorno: 'desvio bidirecional único, sem sinaleiro',
    num_fases: 1,
  },
];

// ---------------------------------------------------------------------------
// Utilidades de tokenização
// ---------------------------------------------------------------------------

/**
 * Tokeniza texto: lowercase + split por espaço/pontuação, removendo tokens
 * vazios. Simples de propósito (sem stemming/stopwords) — adequado ao
 * vocabulário técnico curto usado aqui.
 */
function tokenize(text) {
  if (text === null || text === undefined) return [];
  return String(text)
    .toLowerCase()
    .split(/[^a-z0-9à-ÿ]+/i)
    .map((t) => t.trim())
    .filter((t) => t.length > 0);
}

/** Monta o "documento textual" de um caso a partir dos campos textuais relevantes. */
function documentoDoCaso(caso) {
  return [caso.subtipo, caso.elemento_critico, caso.restricao_contorno]
    .filter(Boolean)
    .join(' ');
}

// ---------------------------------------------------------------------------
// 2. FILTRO DURO
// ---------------------------------------------------------------------------

/**
 * Filtra a base pela igualdade exata de `tipologia`. Se nenhum candidato
 * restar, retorna a base inteira inalterada e marca fallback=true (o
 * chamador deve então aplicar a penalidade de fallback no score final).
 */
function filtroDuro(casoNovo, base) {
  const filtrados = base.filter((c) => c.tipologia === casoNovo.tipologia);
  if (filtrados.length === 0) {
    return { candidatos: base.slice(), fallback: true };
  }
  return { candidatos: filtrados, fallback: false };
}

// ---------------------------------------------------------------------------
// 3. BM25 (k1=1.5, b=0.75)
// ---------------------------------------------------------------------------

/**
 * BM25 clássico (Robertson/Sparck-Jones), calculado sobre `documentos`
 * (array de strings) para a `query` (string). Retorna array de scores
 * normalizados 0-1 (dividindo pelo score máximo obtido no conjunto; se
 * todos os scores forem 0, retorna 0 para todos).
 */
function bm25(query, documentos) {
  const k1 = 1.5;
  const b = 0.75;

  const queryTokens = tokenize(query);
  const docsTokens = documentos.map(tokenize);
  const N = docsTokens.length;

  if (N === 0) return [];

  const docLens = docsTokens.map((toks) => toks.length);
  const avgdl = docLens.reduce((a, l) => a + l, 0) / N || 1;

  // document frequency por termo
  const df = new Map();
  for (const toks of docsTokens) {
    const seen = new Set(toks);
    for (const term of seen) {
      df.set(term, (df.get(term) || 0) + 1);
    }
  }

  function idf(term) {
    const n = df.get(term) || 0;
    // variante BM25 com piso em 0 (evita idf negativo "explodir" scores)
    const val = Math.log((N - n + 0.5) / (n + 0.5) + 1);
    return val;
  }

  const rawScores = docsTokens.map((toks, i) => {
    const tf = new Map();
    for (const term of toks) {
      tf.set(term, (tf.get(term) || 0) + 1);
    }
    const dl = docLens[i];
    let score = 0;
    for (const qterm of queryTokens) {
      const f = tf.get(qterm) || 0;
      if (f === 0) continue;
      const numerator = f * (k1 + 1);
      const denominator = f + k1 * (1 - b + b * (dl / avgdl));
      score += idf(qterm) * (numerator / denominator);
    }
    return score;
  });

  const max = Math.max(...rawScores, 0);
  if (max <= 0) return rawScores.map(() => 0);
  return rawScores.map((s) => s / max);
}

// ---------------------------------------------------------------------------
// 4. TF-IDF vetorial + similaridade de cosseno
// ---------------------------------------------------------------------------

/**
 * TF-IDF + cosseno entre `query` e cada documento de `documentos`. Constrói
 * o vocabulário a partir de query + documentos, vetoriza cada um com peso
 * tf*idf (idf = log(N/df), N = nº de documentos, incluindo a query como um
 * "documento" adicional para o cálculo de idf) e retorna a similaridade de
 * cosseno (0-1; termos negativos não ocorrem pois tf/idf >= 0).
 */
function tfidfCosine(query, documentos) {
  const queryTokens = tokenize(query);
  const docsTokens = documentos.map(tokenize);

  const allDocsForIdf = [queryTokens, ...docsTokens];
  const N = allDocsForIdf.length;

  const df = new Map();
  for (const toks of allDocsForIdf) {
    const seen = new Set(toks);
    for (const term of seen) {
      df.set(term, (df.get(term) || 0) + 1);
    }
  }

  function idf(term) {
    const n = df.get(term) || 0;
    if (n === 0) return 0;
    return Math.log(N / n) + 1; // +1 evita idf=0 para termos presentes em todos os docs
  }

  function vetorTfIdf(tokens) {
    const tf = new Map();
    for (const term of tokens) {
      tf.set(term, (tf.get(term) || 0) + 1);
    }
    const vec = new Map();
    for (const [term, freq] of tf.entries()) {
      const tfNorm = freq / tokens.length;
      vec.set(term, tfNorm * idf(term));
    }
    return vec;
  }

  function cosseno(vecA, vecB) {
    let dot = 0;
    let normA = 0;
    let normB = 0;
    for (const v of vecA.values()) normA += v * v;
    for (const v of vecB.values()) normB += v * v;
    for (const [term, va] of vecA.entries()) {
      const vb = vecB.get(term);
      if (vb) dot += va * vb;
    }
    if (normA === 0 || normB === 0) return 0;
    return dot / (Math.sqrt(normA) * Math.sqrt(normB));
  }

  const queryVec = vetorTfIdf(queryTokens);
  return docsTokens.map((toks) => {
    if (toks.length === 0) return 0;
    const docVec = vetorTfIdf(toks);
    const sim = cosseno(queryVec, docVec);
    // cosseno com pesos tf*idf >=0 já cai em [0,1]; clamp defensivo.
    return Math.max(0, Math.min(1, sim));
  });
}

// ---------------------------------------------------------------------------
// 5. SCORE ESTRUTURADO (campos categóricos/numéricos)
// ---------------------------------------------------------------------------

/** Similaridade textual simples (Jaccard sobre tokens) entre dois campos de texto. */
function similaridadeTextoSimples(a, b) {
  const ta = new Set(tokenize(a));
  const tb = new Set(tokenize(b));
  if (ta.size === 0 && tb.size === 0) return 1; // ambos vazios = "iguais" (nulos)
  if (ta.size === 0 || tb.size === 0) return 0;
  let intersecao = 0;
  for (const t of ta) {
    if (tb.has(t)) intersecao++;
  }
  const uniao = new Set([...ta, ...tb]).size;
  return uniao === 0 ? 0 : intersecao / uniao;
}

/**
 * Diferença normalizada de num_fases. Se qualquer um dos dois lados for
 * null/undefined, trata a similaridade desse componente como 0 (não há
 * informação suficiente para afirmar semelhança).
 */
function similaridadeNumFases(a, b) {
  if (a === null || a === undefined || b === null || b === undefined) return 0;
  const diff = Math.abs(a - b);
  const maxFases = 5; // faixa observada na base (1 a 3), com folga
  return Math.max(0, 1 - diff / maxFases);
}

/**
 * Score estruturado entre o caso novo e um candidato:
 *   - elemento_critico: peso 0.45 (similaridade textual)
 *   - restricao_contorno: peso 0.35 (similaridade textual)
 *   - num_fases: peso 0.20 (diferença normalizada; null em qualquer lado -> 0)
 * Retorna valor em [0,1].
 */
function scoreEstruturado(casoNovo, candidato) {
  const simElemento = similaridadeTextoSimples(
    casoNovo.elemento_critico,
    candidato.elemento_critico
  );
  const simRestricao = similaridadeTextoSimples(
    casoNovo.restricao_contorno,
    candidato.restricao_contorno
  );
  const simFases = similaridadeNumFases(casoNovo.num_fases, candidato.num_fases);

  return simElemento * 0.45 + simRestricao * 0.35 + simFases * 0.2;
}

// ---------------------------------------------------------------------------
// 6. PIPELINE COMPLETO
// ---------------------------------------------------------------------------

function classificarConfianca(score) {
  if (score >= 0.8) return 'alta';
  if (score >= 0.6) return 'media';
  return 'baixa';
}

/**
 * Pipeline completo de matching:
 *   1. filtroDuro (tipologia)
 *   2. score_texto = bm25*0.5 + tfidf*0.5  (sobre subtipo+elemento_critico+restricao_contorno)
 *   3. score_final (MODO PRODUÇÃO, com embedding real):
 *        score_final = score_texto*0.30 + scoreEstruturado*0.40 + scoreVetorial*0.30
 *      Este arquivo NÃO tem acesso a um serviço de embeddings, então
 *      scoreVetorial não existe aqui. Em vez de fingir um componente
 *      vetorial com peso 0, os dois pesos restantes (texto e estruturado)
 *      são RENORMALIZADOS proporcionalmente para somarem 1.0:
 *        score_final = score_texto*(0.30/0.70) + scoreEstruturado*(0.40/0.70)
 *      ou seja, score_texto*(3/7) + scoreEstruturado*(4/7).
 *   4. penalidade de fallback: se o filtro duro não achou nada da mesma
 *      tipologia (fallback=true), multiplica o score final por 0.10.
 *   5. ordena decrescente e retorna os topN.
 */
function buscarPrecedente(casoNovo, { topN = 3 } = {}) {
  const { candidatos, fallback } = filtroDuro(casoNovo, BASE_PRECEDENTES);

  const queryTexto = documentoDoCaso(casoNovo);
  const documentosTexto = candidatos.map(documentoDoCaso);

  const bm25Scores = bm25(queryTexto, documentosTexto);
  const tfidfScores = tfidfCosine(queryTexto, documentosTexto);

  // Pesos de produção (com embedding vetorial real):
  const PESO_TEXTO_PROD = 0.3;
  const PESO_ESTRUTURADO_PROD = 0.4;
  // const PESO_VETORIAL_PROD = 0.30; // indisponível nesta implementação standalone

  // Renormalização sem o componente vetorial (soma dos dois pesos restantes = 0.70):
  const somaPesosDisponiveis = PESO_TEXTO_PROD + PESO_ESTRUTURADO_PROD; // 0.70
  const pesoTextoRenorm = PESO_TEXTO_PROD / somaPesosDisponiveis; // 3/7
  const pesoEstruturadoRenorm = PESO_ESTRUTURADO_PROD / somaPesosDisponiveis; // 4/7

  const resultados = candidatos.map((candidato, i) => {
    const scoreBm25 = bm25Scores[i];
    const scoreTfidf = tfidfScores[i];
    const scoreTexto = scoreBm25 * 0.5 + scoreTfidf * 0.5;
    const scoreEstrut = scoreEstruturado(casoNovo, candidato);

    let scoreFinal =
      scoreTexto * pesoTextoRenorm + scoreEstrut * pesoEstruturadoRenorm;

    if (fallback) {
      scoreFinal *= 0.1;
    }

    return {
      id: candidato.id,
      subtipo: candidato.subtipo,
      scoreFinal,
      similaridadePct: Math.round(scoreFinal * 1000) / 10, // 1 casa decimal, em %
      componentes: {
        bm25: scoreBm25,
        tfidf: scoreTfidf,
        estruturado: scoreEstrut,
      },
      classificacaoConfianca: classificarConfianca(scoreFinal),
    };
  });

  resultados.sort((a, b) => b.scoreFinal - a.scoreFinal);

  return {
    fallback,
    resultados: resultados.slice(0, topN),
  };
}

// ---------------------------------------------------------------------------
// 7. BLOCO DE TESTE
// ---------------------------------------------------------------------------

function _runSelfTest() {
  const casoNovoHipotetico = {
    tipologia: 'trevo_diamante',
    subtipo: 'Diamante em desnível com anel viário',
    elemento_critico: 'viaduto central ligando dois anéis',
    restricao_contorno: 'múltiplos ramos, núcleo circular duplo',
    num_fases: 2,
  };

  const { fallback, resultados } = buscarPrecedente(casoNovoHipotetico, { topN: 3 });

  console.log('=== MOT — Motor de Matching de Precedentes ===');
  console.log('Caso novo:', JSON.stringify(casoNovoHipotetico, null, 2));
  console.log('Fallback (tipologia não encontrada na base)?', fallback);
  console.log('\nTop resultados:');
  for (const r of resultados) {
    console.log(
      `  [${r.id}] ${r.subtipo} — score=${r.scoreFinal.toFixed(4)} ` +
        `(${r.similaridadePct}%) — confiança=${r.classificacaoConfianca} — ` +
        `bm25=${r.componentes.bm25.toFixed(3)} tfidf=${r.componentes.tfidf.toFixed(3)} ` +
        `estrut=${r.componentes.estruturado.toFixed(3)}`
    );
  }

  const top1 = resultados[0];
  console.assert(
    top1 && top1.id === 'caso_03',
    `ASSERT FALHOU: esperado top-1 = caso_03, obtido = ${top1 && top1.id}`
  );
  if (top1 && top1.id === 'caso_03') {
    console.log('\n[OK] Assert passou: top-1 é caso_03, como esperado.');
  } else {
    throw new Error(
      `Assert falhou: esperado top-1 = caso_03, obtido = ${top1 && top1.id}`
    );
  }
}

if (require.main === module) {
  _runSelfTest();
}

module.exports = {
  BASE_PRECEDENTES,
  tokenize,
  filtroDuro,
  bm25,
  tfidfCosine,
  scoreEstruturado,
  buscarPrecedente,
};
