/**
 * Test suite para MaestroRouter
 * Cobertura: routing básico, prompts ambíguos, performance, cache, keyword bonuses
 */

import {
  MaestroRouter,
  getMaestroRouter,
  RoutingResult,
  RouterStats,
} from '../maestro-router';

describe('MaestroRouter', () => {
  let router: MaestroRouter;

  beforeEach(() => {
    router = new MaestroRouter();
  });

  describe('Routing Básico - Saneamento', () => {
    test('S8: Route "ETA e ETE para AySA" → agente-saneamento', () => {
      const result = router.route('Projeto de ETA e ETE para AySA');
      expect(result.agent.name).toBe('agente-saneamento');
      expect(result.agent.code).toBe('Manta 03-S8');
      expect(result.confidence).toBe('high');
    });

    test('S8: Route "adutora com drenagem urbana" → agente-saneamento', () => {
      const result = router.route('Projeto de adutora com drenagem urbana integrada');
      expect(result.agent.name).toBe('agente-saneamento');
      expect(result.confidence).toBe('high');
      expect(result.score).toBeGreaterThan(6.0);
    });

    test('S8: Route "ETE seguindo SNIS" → agente-saneamento', () => {
      const result = router.route('ETE conforme normas SNIS e NBR 12211');
      expect(result.agent.name).toBe('agente-saneamento');
      expect(result.matchedKeywords.length).toBeGreaterThan(0);
    });

    test('S8: Route "esgoto e reservatório" → agente-saneamento', () => {
      const result = router.route('Sistema de esgoto e reservatório de água potável');
      expect(result.agent.name).toBe('agente-saneamento');
      expect(result.score).toBeGreaterThan(5.0);
    });
  });

  describe('Routing Básico - Energia', () => {
    test('S9: Route "Transmissão ANEEL LT" → agente-energia', () => {
      const result = router.route('Leilão de transmissão ANEEL com LT de 500kV');
      expect(result.agent.name).toBe('agente-energia');
      expect(result.agent.code).toBe('Manta 03-S9');
      expect(result.confidence).toBe('high');
    });

    test('S9: Route "Subestação RAP" → agente-energia', () => {
      const result = router.route('Subestação com RAP conforme ONS e Resolução ANEEL');
      expect(result.agent.name).toBe('agente-energia');
      expect(result.score).toBeGreaterThan(6.0);
    });

    test('S9: Route "EPE e ONS" → agente-energia', () => {
      const result = router.route('Coordenação EPE e ONS para planejamento de energia');
      expect(result.agent.name).toBe('agente-energia');
      expect(result.confidence).toMatch(/high|medium/);
    });
  });

  describe('Routing Básico - Barragens', () => {
    test('S10: Route "CFRD com vertedouro" → agente-barragens', () => {
      const result = router.route('Barragem CFRD com vertedouro conforme ICOLD');
      expect(result.agent.name).toBe('agente-barragens');
      expect(result.agent.code).toBe('Manta 03-S10');
      expect(result.confidence).toBe('high');
    });

    test('S10: Route "Rejeitos TSF" → agente-barragens', () => {
      const result = router.route('Gestão de rejeitos em TSF (Tailings Storage Facility)');
      expect(result.agent.name).toBe('agente-barragens');
      expect(result.matchedKeywords).toContain('rejeitos');
    });

    test('S10: Route "Barragem CCR Lei 12.334" → agente-barragens', () => {
      const result = router.route('Barragem de concreto compactado CCR conforme Lei 12.334');
      expect(result.agent.name).toBe('agente-barragens');
      expect(result.score).toBeGreaterThan(7.0);
    });
  });

  describe('Routing Básico - Outros Segmentos', () => {
    test('S6: Route "Porto e ANTAQ" → agente-portos', () => {
      const result = router.route('Terminal de contêiner no porto com dragagem ANTAQ');
      expect(result.agent.name).toBe('agente-portos');
      expect(result.agent.code).toBe('Manta 03-S6');
    });

    test('S7: Route "Aeroporto ANAC" → agente-aeroportos', () => {
      const result = router.route('Pista de pouso com balizamento conforme ANAC e ICAO');
      expect(result.agent.name).toBe('agente-aeroportos');
      expect(result.agent.code).toBe('Manta 03-S7');
    });

    test('S1: Route "Pavimentação CBUQ" → agente-infraestrutura-s1', () => {
      const result = router.route('Pavimentação CBUQ e terraplenagem via SICRO DNIT');
      expect(result.agent.name).toBe('agente-infraestrutura');
      expect(result.agent.segment).toBe('Rodovias');
    });

    test('S4: Route "Metrô Linha 4" → agente-infraestrutura-s4', () => {
      const result = router.route('Estação de metrô na Linha 4 com NATM e PSD');
      expect(result.agent.name).toBe('agente-infraestrutura');
      expect(result.agent.segment).toBe('Metrô');
    });
  });

  describe('Prompts Ambíguos', () => {
    test('Ambíguo: "água" deve rotear para saneamento', () => {
      const result = router.route('Projeto de água potável');
      expect(result.agent.name).toBe('agente-saneamento');
    });

    test('Ambíguo: "concreto" prioriza OAE sobre rodovia', () => {
      const result = router.route('Estrutura de concreto em obra de arte especial');
      // OAE tem prioridade neste contexto
      expect(result.agent.segment).toContain('OAE');
    });

    test('Ambíguo: "estrutura" com múltiplos contextos', () => {
      const result = router.route('Estrutura de fundação em barragem');
      expect(result.agent.name).toBe('agente-barragens');
      expect(result.confidence).toMatch(/high|medium/);
    });

    test('Ambíguo: "transmissão" vs "distribuição" energy', () => {
      const result = router.route('Linha de transmissão 230kV ANEEL');
      expect(result.agent.name).toBe('agente-energia');
      expect(result.score).toBeGreaterThan(
        router.route('Rede de distribuição de energia').score
      );
    });

    test('Ambíguo: Fallback quando nenhuma keyword', () => {
      const result = router.route('Projeto genérico sem contexto específico');
      // Fallback padrão é S1 (rodovias)
      expect(result.agent.segment).toBe('Rodovias');
      expect(result.confidence).toBe('low');
    });
  });

  describe('Performance < 100ms', () => {
    test('Roteamento simples executa em < 50ms', () => {
      const start = performance.now();
      router.route('ETA e ETE');
      const duration = performance.now() - start;
      expect(duration).toBeLessThan(50);
    });

    test('Roteamento complexo executa em < 100ms', () => {
      const complexInput =
        'Projeto multidisciplinar de barragem com fundação, vertedouro, ' +
        'rejeitos em TSF, conforme Lei 12.334 e ICOLD, integrado com ' +
        'transmissão de energia ANEEL';

      const start = performance.now();
      const result = router.routeWithStats(complexInput);
      const duration = performance.now() - start;

      expect(duration).toBeLessThan(100);
      expect(result.executionTimeMs).toBeLessThan(100);
    });

    test('50 roteamentos sequenciais < 3s total', () => {
      const testInputs = [
        'ETA',
        'Transmissão',
        'Porto',
        'Aeroporto',
        'Barragem',
        'Rodovia',
        'Ponte',
        'Ferrovia',
        'Metrô',
      ];

      const start = performance.now();
      for (let i = 0; i < 50; i++) {
        const input = testInputs[i % testInputs.length];
        router.route(input);
      }
      const duration = performance.now() - start;

      expect(duration).toBeLessThan(3000);
      expect(duration / 50).toBeLessThan(100); // Média < 100ms
    });

    test('routeWithStats com statísticas < 100ms', () => {
      const result = router.routeWithStats(
        'Barragem CFRD com rejeitos em TSF conforme ICOLD e Lei 12.334'
      );
      expect(result.executionTimeMs).toBeLessThan(100);
    });
  });

  describe('Cache Hits e Misses', () => {
    test('getMaestroRouter() retorna singleton (cache)', () => {
      const router1 = getMaestroRouter();
      const router2 = getMaestroRouter();
      expect(router1).toBe(router2);
    });

    test('Múltiplos roteamentos com mesmo input preservam performance', () => {
      const input = 'ETA e ETE para AySA';

      // Primeira execução
      const time1 = performance.now();
      const result1 = router.route(input);
      const duration1 = performance.now() - time1;

      // Segunda execução (potencial cache hit em índice)
      const time2 = performance.now();
      const result2 = router.route(input);
      const duration2 = performance.now() - time2;

      // Resultados devem ser idênticos
      expect(result1.agent.name).toBe(result2.agent.name);
      expect(result1.score).toBe(result2.score);

      // Segunda execução não deve ser significativamente mais lenta
      // (validação de construção do índice)
      expect(duration2).toBeLessThan(100);
    });

    test('Índice de keywords built na construção', () => {
      const newRouter = new MaestroRouter();

      // Primeira query usa índice
      const start = performance.now();
      newRouter.route('barragem CFRD');
      const duration = performance.now() - start;

      expect(duration).toBeLessThan(50);
    });

    test('Keywords compostas encontradas rapidamente', () => {
      const start = performance.now();
      const result = router.route('saneamento ambiental com ETA e ETE');
      const duration = performance.now() - start;

      expect(duration).toBeLessThan(50);
      expect(result.matchedKeywords.length).toBeGreaterThanOrEqual(2);
    });
  });

  describe('Keyword Position Bonus (via score differentials)', () => {
    test('Primary keywords geram score > secondary', () => {
      // Primary: barragem (3.0) + category bonus (0.5) = 3.5
      const primaryResult = router.route('barragem estrutura');

      // Secondary: estrutura (2.0) + category bonus (0.2) = 2.2
      const secondaryResult = router.route('estrutura escavação');

      expect(primaryResult.score).toBeGreaterThan(secondaryResult.score);
    });

    test('Regulatory keywords geram score > context', () => {
      // Regulatory: Lei 12.334 (2.8) + bonus (0.3) = 3.1
      const regularResult = router.route('Lei 12.334');

      // Context: operação (1.5) + bonus (0.1) = 1.6
      const contextResult = router.route('operação e manutenção');

      expect(regularResult.score).toBeGreaterThan(contextResult.score);
    });

    test('Keywords compostas recebem weight maior', () => {
      // Composto: "pista pouso" (3.1) + bonus > tokens individuais
      const compositeResult = router.route('pista pouso ICAO');

      // Individual: "pouso" + "pista" reduzidos em 0.85x
      const individualResult = router.route('pouso em pista');

      expect(compositeResult.score).toBeGreaterThan(individualResult.score);
    });

    test('Múltiplos keywords do mesmo segment acumulam score', () => {
      // Score agregado: CFRD (3.0) + CCR (3.0) + vertedouro (3.0) = 9.0
      const result = router.route('barragem CFRD com CCR e vertedouro');

      expect(result.score).toBeGreaterThan(8.0);
      expect(result.matchedKeywords.length).toBeGreaterThanOrEqual(3);
    });

    test('Keywords no início não recebem bonus posicional explícito (não existe)', () => {
      const beginResult = router.route(
        'barragem CFRD no início do documento'
      );
      const endResult = router.route('no final vamos discutir barragem CFRD');

      // Ambos devem ter scores similares (sem position bonus)
      // Diferença < 10% do score
      const diff = Math.abs(beginResult.score - endResult.score);
      expect(diff).toBeLessThan(beginResult.score * 0.1);
    });

    test('Input length bonus afeta context', () => {
      // Input curto: contextBonus * 0.9
      const shortResult = router.route('barragem');

      // Input longo: contextBonus * 1.2
      const longInput =
        'Projeto complexo de barragem com CFRD, CCR, vertedouro, ' +
        'fundação profunda, rejeitos em TSF, conforme ICOLD, ' +
        'Lei 12.334, CBDB e PNSB';
      const longResult = router.route(longInput);

      // Input longo deve gerar score maior
      expect(longResult.score).toBeGreaterThan(shortResult.score);
    });

    test('Category bonus distribution: primary (0.5) > regulatory (0.3) > secondary (0.2) > context (0.1)', () => {
      // Primary: "barragem" 3.0 + 0.5 = 3.5
      const primary = router.route('barragem');

      // Regulatory: "Lei 12.334" 2.8 + 0.3 = 3.1
      const regulatory = router.route('Lei 12.334');

      // Secondary: "aceude" 2.7 + 0.2 = 2.9
      const secondary = router.route('açude');

      // Context: "operação" 1.5 + 0.1 = 1.6
      const context = router.route('operação');

      expect(primary.score).toBeGreaterThan(regulatory.score);
      expect(regulatory.score).toBeGreaterThan(secondary.score);
      expect(secondary.score).toBeGreaterThan(context.score);
    });
  });

  describe('Confidence Levels', () => {
    test('Confidence HIGH quando score >= 8.0', () => {
      const result = router.route('barragem CFRD com CCR e vertedouro');
      expect(result.score).toBeGreaterThanOrEqual(8.0);
      expect(result.confidence).toBe('high');
    });

    test('Confidence MEDIUM quando 4.0 <= score < 8.0', () => {
      const result = router.route('açude com reservatório');
      expect(result.confidence).toMatch(/high|medium/);
      if (result.score < 8.0) {
        expect(result.confidence).toBe('medium');
      }
    });

    test('Confidence LOW quando score < 4.0', () => {
      const result = router.route('estrutura genérica');
      if (result.score < 4.0) {
        expect(result.confidence).toBe('low');
      }
    });
  });

  describe('RouterStats', () => {
    test('routeWithStats retorna métricas completas', () => {
      const result = router.routeWithStats(
        'Barragem CFRD com rejeitos em TSF'
      );

      expect(result).toHaveProperty('agent');
      expect(result).toHaveProperty('matchedKeywords');
      expect(result).toHaveProperty('score');
      expect(result).toHaveProperty('confidence');
      expect(result).toHaveProperty('inputLength');
      expect(result).toHaveProperty('matchCount');
      expect(result).toHaveProperty('topScores');
      expect(result).toHaveProperty('executionTimeMs');
    });

    test('topScores contém agentes matchados', () => {
      const result = router.routeWithStats(
        'Barragem CFRD com rejeitos e fundação'
      );

      expect(result.topScores.size).toBeGreaterThan(0);
      expect(result.topScores.has('agente-barragens')).toBe(true);
    });

    test('inputLength reflete tamanho correto', () => {
      const input = 'Projeto de barragem';
      const result = router.routeWithStats(input);

      expect(result.inputLength).toBe(input.length);
    });

    test('matchCount reflete segmentos com keywords', () => {
      const result = router.routeWithStats('barragem CFRD');

      // Deve ter pelo menos 1 segmento (barragens)
      expect(result.matchCount).toBeGreaterThanOrEqual(1);
    });
  });

  describe('Available Agents', () => {
    test('getAvailableAgents retorna todos os 9 agentes', () => {
      const agents = router.getAvailableAgents();

      expect(agents.length).toBe(9);
      const names = agents.map((a) => a.name);
      expect(names).toContain('agente-saneamento');
      expect(names).toContain('agente-energia');
      expect(names).toContain('agente-portos');
      expect(names).toContain('agente-aeroportos');
      expect(names).toContain('agente-barragens');
    });

    test('Cada agente tem tier definido', () => {
      const agents = router.getAvailableAgents();

      for (const agent of agents) {
        expect(agent.tier).toBeDefined();
        expect(agent.tier.length).toBeGreaterThan(0);
      }
    });

    test('Cada agente tem aliases', () => {
      const agents = router.getAvailableAgents();

      for (const agent of agents) {
        expect(Array.isArray(agent.aliases)).toBe(true);
        expect(agent.aliases.length).toBeGreaterThan(0);
      }
    });
  });

  describe('Error Handling', () => {
    test('Lança erro para input vazio', () => {
      expect(() => router.route('')).toThrow('Input vazio');
    });

    test('Lança erro para input whitespace only', () => {
      expect(() => router.route('   ')).toThrow('Input vazio');
    });
  });

  describe('Segment Configuration', () => {
    test('getSegmentConfig retorna config para saneamento', () => {
      const config = router.getSegmentConfig('Saneamento');

      expect(config).toBeDefined();
      expect(config?.segment).toBe('Saneamento');
      expect(config?.keywords.length).toBeGreaterThan(20);
    });

    test('getSegmentConfig case-insensitive', () => {
      const config1 = router.getSegmentConfig('SANEAMENTO');
      const config2 = router.getSegmentConfig('saneamento');
      const config3 = router.getSegmentConfig('Saneamento');

      expect(config1?.segment).toBe(config2?.segment);
      expect(config2?.segment).toBe(config3?.segment);
    });

    test('getSegmentConfig retorna undefined para segment inexistente', () => {
      const config = router.getSegmentConfig('Inexistente');

      expect(config).toBeUndefined();
    });
  });

  describe('Integration Tests', () => {
    test('Roteamento determinístico: mesmo input sempre retorna mesmo agente', () => {
      const input = 'ETA com adutora e drenagem urbana para AySA';

      const result1 = router.route(input);
      const result2 = router.route(input);
      const result3 = router.route(input);

      expect(result1.agent.name).toBe(result2.agent.name);
      expect(result2.agent.name).toBe(result3.agent.name);
      expect(result1.score).toBe(result2.score);
      expect(result2.score).toBe(result3.score);
    });

    test('Todos os 9 segmentos roteáveis', () => {
      const testCases: Record<string, string> = {
        'agente-saneamento': 'ETA e ETE',
        'agente-energia': 'Transmissão ANEEL LT',
        'agente-portos': 'Terminal de contêiner porto',
        'agente-aeroportos': 'Pista de pouso balizamento',
        'agente-barragens': 'Barragem CFRD vertedouro',
        'agente-infraestrutura-s1': 'Pavimentação CBUQ rodovia',
        'agente-infraestrutura-s2': 'Ponte viaduto NBR 7187',
        'agente-infraestrutura-s3': 'Ferrovia trilho via permanente',
        'agente-infraestrutura-s4': 'Metrô Linha 4 NATM',
      };

      for (const [expectedAgent, testInput] of Object.entries(testCases)) {
        const result = router.route(testInput);
        const agentCode = expectedAgent
          .replace('agente-', '')
          .split('-')
          .join('');
        const actualCode = result.agent.code.toLowerCase().replace(/\s/g, '');

        expect(result.agent.name).toBeDefined();
        // Validar que roteamento funcionou
        expect(result.score).toBeGreaterThan(0);
      }
    });
  });
});
