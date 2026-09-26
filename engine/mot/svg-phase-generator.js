'use strict';

/**
 * engine/mot/svg-phase-generator.js
 *
 * Motor de faseamento de tráfego (MOT) — Manta Associados.
 * Gera uma planta esquemática SVG de UMA fase de obra de faseamento de
 * tráfego, a partir de uma descrição geométrica simplificada (polilinhas
 * de eixos/faixas, dispositivos de sinalização e setas de fluxo).
 *
 * Sem dependências externas (Node.js puro).
 */

const fs = require('fs');

// ---------------------------------------------------------------------------
// Paleta Manta
// ---------------------------------------------------------------------------

const CORES = {
  liberada: '#10B981', // verde
  interditada: '#9CA3AF', // cinza
  desvio_provisorio: '#BF4D19', // âmbar/terracota Manta
  eixoInativo: '#D1D5DB',
  texto: '#1F2933',
  seloFundo: '#FFFFFF',
  seloBorda: '#1F2933',
  dispositivo: '#1F2933',
  pmvFundo: '#1F2933',
  pmvTexto: '#FFFFFF',
};

const FONT_FAMILY = 'Yantramanav, Arial, sans-serif';

// ---------------------------------------------------------------------------
// Helpers geométricos
// ---------------------------------------------------------------------------

function pontosParaAtributoSvg(pontos) {
  return pontos.map(([x, y]) => `${formatNum(x)},${formatNum(y)}`).join(' ');
}

function formatNum(n) {
  // Evita notação científica e corta casas decimais desnecessárias.
  return Number(n.toFixed(3)).toString();
}

function escapeXml(str) {
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&apos;');
}

/**
 * Coleta todos os pontos (x,y) presentes na descrição da fase, para
 * calcular o bounding box e, a partir dele, o viewBox com margem.
 */
function coletarTodosOsPontos(fase) {
  const pontos = [];

  (fase.eixos || []).forEach((eixo) => {
    (eixo.pontos || []).forEach((p) => pontos.push(p));
  });

  (fase.faixas || []).forEach((faixa) => {
    (faixa.pontos || []).forEach((p) => pontos.push(p));
  });

  (fase.dispositivos || []).forEach((d) => {
    if (d.posicao) pontos.push(d.posicao);
  });

  (fase.setasFluxo || []).forEach((s) => {
    if (s.inicio) pontos.push(s.inicio);
    if (s.fim) pontos.push(s.fim);
  });

  return pontos;
}

function calcularViewBox(pontos, margem) {
  if (!pontos.length) {
    // fallback razoável se a fase vier vazia
    return { minX: 0, minY: 0, largura: 400, altura: 300 };
  }

  let minX = Infinity;
  let minY = Infinity;
  let maxX = -Infinity;
  let maxY = -Infinity;

  pontos.forEach(([x, y]) => {
    if (x < minX) minX = x;
    if (y < minY) minY = y;
    if (x > maxX) maxX = x;
    if (y > maxY) maxY = y;
  });

  minX -= margem;
  minY -= margem;
  maxX += margem;
  maxY += margem;

  return {
    minX,
    minY,
    largura: maxX - minX,
    altura: maxY - minY,
  };
}

// ---------------------------------------------------------------------------
// Desenho de elementos
// ---------------------------------------------------------------------------

function corPorEstado(estado) {
  return CORES[estado] || CORES.interditada;
}

function desenharEixo(eixo) {
  const cor = eixo.ativo ? CORES.liberada : CORES.eixoInativo;
  const tracejado = eixo.ativo ? '' : ' stroke-dasharray="6,5"';
  const nome = eixo.nome ? `<title>${escapeXml(eixo.nome)}</title>` : '';
  return (
    `<polyline points="${pontosParaAtributoSvg(eixo.pontos)}" ` +
    `fill="none" stroke="${cor}" stroke-width="1.5" stroke-linecap="round" ` +
    `stroke-linejoin="round"${tracejado} opacity="0.6">${nome}</polyline>`
  );
}

function desenharFaixa(faixa) {
  const cor = corPorEstado(faixa.estado);
  const tracejado =
    faixa.estado === 'desvio_provisorio' ? ' stroke-dasharray="10,6"' : '';
  const nome = faixa.nome ? `<title>${escapeXml(faixa.nome)}</title>` : '';
  return (
    `<polyline points="${pontosParaAtributoSvg(faixa.pontos)}" ` +
    `fill="none" stroke="${cor}" stroke-width="5" stroke-linecap="round" ` +
    `stroke-linejoin="round"${tracejado}>${nome}</polyline>`
  );
}

function desenharDispositivo(disp) {
  const [x, y] = disp.posicao;
  const label = disp.label
    ? `<text x="${formatNum(x)}" y="${formatNum(
        y + 14
      )}" font-family="${FONT_FAMILY}" font-size="8" fill="${
        CORES.texto
      }" text-anchor="middle">${escapeXml(disp.label)}</text>`
    : '';

  let simbolo = '';

  switch (disp.tipo) {
    case 'cone': {
      // círculo pequeno laranja com contorno
      simbolo =
        `<circle cx="${formatNum(x)}" cy="${formatNum(y)}" r="2.5" ` +
        `fill="#F97316" stroke="${CORES.dispositivo}" stroke-width="0.5" />`;
      break;
    }
    case 'new_jersey': {
      // retângulo alongado (barreira rígida)
      const largura = 10;
      const altura = 2.5;
      simbolo =
        `<rect x="${formatNum(x - largura / 2)}" y="${formatNum(
          y - altura / 2
        )}" width="${largura}" height="${altura}" fill="${CORES.eixoInativo}" ` +
        `stroke="${CORES.dispositivo}" stroke-width="0.6" />`;
      break;
    }
    case 'placa': {
      // triângulo (placa de advertência)
      const r = 4;
      const p1 = [x, y - r];
      const p2 = [x - r, y + r];
      const p3 = [x + r, y + r];
      simbolo =
        `<polygon points="${pontosParaAtributoSvg([p1, p2, p3])}" ` +
        `fill="#FBBF24" stroke="${CORES.dispositivo}" stroke-width="0.6" />`;
      break;
    }
    case 'pmv': {
      // retângulo escuro com texto "PMV"
      const largura = 14;
      const altura = 8;
      simbolo =
        `<rect x="${formatNum(x - largura / 2)}" y="${formatNum(
          y - altura / 2
        )}" width="${largura}" height="${altura}" rx="1" fill="${
          CORES.pmvFundo
        }" stroke="${CORES.dispositivo}" stroke-width="0.6" />` +
        `<text x="${formatNum(x)}" y="${formatNum(
          y + 2.5
        )}" font-family="${FONT_FAMILY}" font-size="5" fill="${
          CORES.pmvTexto
        }" text-anchor="middle" font-weight="bold">PMV</text>`;
      break;
    }
    default: {
      simbolo = `<circle cx="${formatNum(x)}" cy="${formatNum(
        y
      )}" r="2.5" fill="${CORES.dispositivo}" />`;
    }
  }

  return `<g class="dispositivo-${escapeXml(disp.tipo)}">${simbolo}${label}</g>`;
}

function desenharSetaFluxo(seta) {
  const [x1, y1] = seta.inicio;
  const [x2, y2] = seta.fim;
  return (
    `<line x1="${formatNum(x1)}" y1="${formatNum(y1)}" x2="${formatNum(
      x2
    )}" y2="${formatNum(y2)}" stroke="#2563EB" stroke-width="1.8" ` +
    `marker-end="url(#seta-fluxo)" />`
  );
}

function desenharSelo(selo, viewBox) {
  if (!selo) return '';

  const largura = 150;
  const altura = 70;
  const margemSelo = 8;
  const x = viewBox.minX + viewBox.largura - largura - margemSelo;
  const y = viewBox.minY + viewBox.altura - altura - margemSelo;

  const linhas = [
    selo.km !== undefined ? `km ${escapeXml(String(selo.km))}` : null,
    selo.dataInicio || selo.dataFim
      ? `${escapeXml(selo.dataInicio || '?')} a ${escapeXml(
          selo.dataFim || '?'
        )}`
      : null,
    selo.janela ? `Janela: ${escapeXml(selo.janela)}` : null,
  ].filter(Boolean);

  const textos = linhas
    .map(
      (linha, i) =>
        `<text x="${formatNum(x + 8)}" y="${formatNum(
          y + 16 + i * 14
        )}" font-family="${FONT_FAMILY}" font-size="9" fill="${CORES.texto}">${linha}</text>`
    )
    .join('');

  return (
    `<g class="selo">` +
    `<rect x="${formatNum(x)}" y="${formatNum(y)}" width="${largura}" height="${altura}" ` +
    `fill="${CORES.seloFundo}" stroke="${CORES.seloBorda}" stroke-width="1" rx="2" />` +
    textos +
    `</g>`
  );
}

// ---------------------------------------------------------------------------
// Função principal
// ---------------------------------------------------------------------------

/**
 * Gera a planta esquemática SVG de uma fase de obra de faseamento de
 * tráfego.
 *
 * @param {Object} fase
 * @param {number} fase.numeroFase
 * @param {string} fase.nomeFase
 * @param {Array} fase.eixos
 * @param {Array} fase.faixas
 * @param {Array} fase.dispositivos
 * @param {Array} fase.setasFluxo
 * @param {Object} fase.selo
 * @returns {string} SVG completo (string)
 */
function gerarPlantaFase(fase) {
  if (!fase || typeof fase !== 'object') {
    throw new Error('gerarPlantaFase: parâmetro "fase" é obrigatório.');
  }

  const MARGEM = 40;
  const todosOsPontos = coletarTodosOsPontos(fase);
  const viewBox = calcularViewBox(todosOsPontos, MARGEM);

  const eixosSvg = (fase.eixos || []).map(desenharEixo).join('\n    ');
  const faixasSvg = (fase.faixas || []).map(desenharFaixa).join('\n    ');
  const dispositivosSvg = (fase.dispositivos || [])
    .map(desenharDispositivo)
    .join('\n    ');
  const setasSvg = (fase.setasFluxo || []).map(desenharSetaFluxo).join('\n    ');
  const seloSvg = desenharSelo(fase.selo, viewBox);

  const titulo = `Fase ${fase.numeroFase !== undefined ? fase.numeroFase : ''} — ${
    fase.nomeFase || ''
  }`;

  const svg = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="${formatNum(
    viewBox.minX
  )} ${formatNum(viewBox.minY)} ${formatNum(viewBox.largura)} ${formatNum(
    viewBox.altura
  )}" font-family="${FONT_FAMILY}">
  <title>${escapeXml(titulo)}</title>
  <defs>
    <marker id="seta-fluxo" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto" markerUnits="strokeWidth">
      <path d="M0,0 L6,3 L0,6 Z" fill="#2563EB" />
    </marker>
  </defs>
  <rect x="${formatNum(viewBox.minX)}" y="${formatNum(
    viewBox.minY
  )}" width="${formatNum(viewBox.largura)}" height="${formatNum(
    viewBox.altura
  )}" fill="#FFFFFF" />
  <text x="${formatNum(viewBox.minX + 8)}" y="${formatNum(
    viewBox.minY + 16
  )}" font-family="${FONT_FAMILY}" font-size="12" font-weight="bold" fill="${
    CORES.texto
  }">${escapeXml(titulo)}</text>
  <g class="eixos">
    ${eixosSvg}
  </g>
  <g class="faixas">
    ${faixasSvg}
  </g>
  <g class="setas-fluxo">
    ${setasSvg}
  </g>
  <g class="dispositivos">
    ${dispositivosSvg}
  </g>
  ${seloSvg}
</svg>
`;

  return svg;
}

module.exports = { gerarPlantaFase };

// ---------------------------------------------------------------------------
// Exemplo de uso (dados fictícios plausíveis)
//
// Geometria baseada em um Parclo com rotatória: os ramos periféricos
// (loops/direcionais) permanecem liberados ao tráfego durante a obra,
// enquanto o núcleo/rotatória central está em desvio provisório (faixa
// de contorno temporária em torno do canteiro).
// ---------------------------------------------------------------------------

if (require.main === module) {
  const faseExemplo = {
    numeroFase: 2,
    nomeFase: 'Execução do núcleo da rotatória — desvio provisório',
    eixos: [
      {
        nome: 'Eixo principal — Rodovia SP-XXX (sentido Norte)',
        pontos: [
          [0, 100],
          [150, 100],
          [260, 90],
        ],
        ativo: true,
      },
      {
        nome: 'Eixo principal — Rodovia SP-XXX (sentido Sul)',
        pontos: [
          [700, 320],
          [560, 320],
          [440, 310],
        ],
        ativo: true,
      },
    ],
    faixas: [
      {
        nome: 'Ramo direcional NE (loop 1) — liberado',
        pontos: [
          [260, 90],
          [340, 60],
          [430, 70],
          [480, 120],
        ],
        estado: 'liberada',
      },
      {
        nome: 'Ramo direcional SE (loop 2) — liberado',
        pontos: [
          [480, 190],
          [520, 250],
          [500, 300],
          [440, 310],
        ],
        estado: 'liberada',
      },
      {
        nome: 'Ramo direcional SO (loop 3) — liberado',
        pontos: [
          [220, 300],
          [180, 260],
          [200, 200],
          [260, 170],
        ],
        estado: 'liberada',
      },
      {
        nome: 'Ramo direcional NO (loop 4) — interditado',
        pontos: [
          [220, 110],
          [180, 150],
          [190, 190],
        ],
        estado: 'interditada',
      },
      {
        nome: 'Contorno provisório do núcleo (rotatória)',
        pontos: [
          [300, 130],
          [380, 110],
          [420, 150],
          [420, 210],
          [380, 250],
          [300, 250],
          [260, 210],
          [260, 150],
          [300, 130],
        ],
        estado: 'desvio_provisorio',
      },
    ],
    dispositivos: [
      { tipo: 'new_jersey', posicao: [280, 120], label: 'NJ-01' },
      { tipo: 'new_jersey', posicao: [400, 120] },
      { tipo: 'new_jersey', posicao: [400, 240] },
      { tipo: 'new_jersey', posicao: [280, 240] },
      { tipo: 'cone', posicao: [320, 135] },
      { tipo: 'cone', posicao: [340, 130] },
      { tipo: 'cone', posicao: [360, 132] },
      { tipo: 'placa', posicao: [230, 95], label: 'Obra' },
      { tipo: 'placa', posicao: [470, 130], label: 'Desvio' },
      { tipo: 'pmv', posicao: [150, 130], label: 'PMV' },
    ],
    setasFluxo: [
      { inicio: [10, 100], fim: [140, 100] },
      { inicio: [690, 320], fim: [570, 320] },
      { inicio: [270, 95], fim: [335, 65] },
      { inicio: [485, 195], fim: [505, 245] },
      { inicio: [215, 295], fim: [185, 265] },
    ],
    selo: {
      km: '12+350',
      dataInicio: '2026-10-01',
      dataFim: '2026-11-15',
      janela: 'Diurna — 08h às 17h',
    },
  };

  const svgGerado = gerarPlantaFase(faseExemplo);
  fs.writeFileSync('/tmp/exemplo-fase.svg', svgGerado, 'utf8');
  console.log('SVG de exemplo gravado em /tmp/exemplo-fase.svg');
}
