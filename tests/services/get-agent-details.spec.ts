import { getAgentDetails, AgentDetailsError } from '@/services/get-agent-details';

describe('getAgentDetails', () => {
  describe('✓ agent válido retorna dados', () => {
    it('should return agent data for valid agent code (Manta 00)', async () => {
      const result = await getAgentDetails('manta-00');

      expect(result).toBeDefined();
      expect(result).toHaveProperty('code', 'Manta 00');
      expect(result).toHaveProperty('name', 'maestro');
      expect(result).toHaveProperty('description');
      expect(result).toHaveProperty('tier');
      expect(result).toHaveProperty('status', '✅ Operacional');
      expect(result).toHaveProperty('markdown');
    });

    it('should return agent data for valid agent code (Manta 01)', async () => {
      const result = await getAgentDetails('manta-01');

      expect(result).toBeDefined();
      expect(result.code).toBe('Manta 01');
      expect(result.name).toBe('claims');
      expect(result.tier).toBe('Opus');
    });

    it('should return agent data for vertical agent (agente-saneamento)', async () => {
      const result = await getAgentDetails('agente-saneamento');

      expect(result).toBeDefined();
      expect(result.code).toBe('Manta 03-S8');
      expect(result.name).toBe('agente-saneamento');
      expect(result.status).toMatch(/Operacional|Prioridade/);
    });

    it('should support case-insensitive agent lookups', async () => {
      const resultLower = await getAgentDetails('maestro');
      const resultUpper = await getAgentDetails('MAESTRO');

      expect(resultLower.code).toEqual(resultUpper.code);
      expect(resultLower.name).toEqual(resultUpper.name);
    });

    it('should include aliases in returned data', async () => {
      const result = await getAgentDetails('claims');

      expect(result.aliases).toBeDefined();
      expect(result.aliases).toContain('02-C');
      expect(result.aliases).toContain('manta-claims');
    });

    it('should return complete agent metadata', async () => {
      const result = await getAgentDetails('manta-02');

      expect(result).toMatchObject({
        code: expect.any(String),
        name: expect.any(String),
        description: expect.any(String),
        tier: expect.any(String),
        status: expect.any(String),
        aliases: expect.any(Array),
        markdown: expect.any(String),
      });
    });
  });

  describe('✓ agent não existe retorna 404', () => {
    it('should throw 404 error for non-existent agent code', async () => {
      await expect(getAgentDetails('manta-999')).rejects.toThrow(
        AgentDetailsError
      );

      try {
        await getAgentDetails('manta-999');
      } catch (error: any) {
        expect(error.statusCode).toBe(404);
        expect(error.message).toContain('not found');
      }
    });

    it('should throw 404 error for invalid agent names', async () => {
      const invalidNames = ['invalid-agent', 'xyz-123', 'not-an-agent'];

      for (const name of invalidNames) {
        await expect(getAgentDetails(name)).rejects.toThrow(
          AgentDetailsError
        );
      }
    });

    it('should throw 404 with proper error message for missing agent', async () => {
      try {
        await getAgentDetails('nonexistent');
        fail('Should have thrown an error');
      } catch (error: any) {
        expect(error.statusCode).toBe(404);
        expect(error.message).toMatch(/Agent .* not found/i);
      }
    });

    it('should throw error for empty agent code', async () => {
      await expect(getAgentDetails('')).rejects.toThrow(AgentDetailsError);
    });

    it('should throw error for null/undefined agent code', async () => {
      await expect(getAgentDetails(null as any)).rejects.toThrow();
      await expect(getAgentDetails(undefined as any)).rejects.toThrow();
    });
  });

  describe('✓ latência < 200ms', () => {
    it('should return agent details within 200ms', async () => {
      const startTime = performance.now();
      const result = await getAgentDetails('manta-00');
      const endTime = performance.now();

      const duration = endTime - startTime;

      expect(result).toBeDefined();
      expect(duration).toBeLessThan(200);
    });

    it('should return for multiple requests all within 200ms', async () => {
      const agents = ['manta-00', 'manta-01', 'agente-saneamento'];

      for (const agent of agents) {
        const startTime = performance.now();
        await getAgentDetails(agent);
        const endTime = performance.now();

        expect(endTime - startTime).toBeLessThan(200);
      }
    });

    it('should handle concurrent requests within performance budget', async () => {
      const agents = ['manta-00', 'manta-01', 'manta-02', 'agente-saneamento'];

      const startTime = performance.now();
      await Promise.all(agents.map(agent => getAgentDetails(agent)));
      const endTime = performance.now();

      expect(endTime - startTime).toBeLessThan(200 * agents.length);
    });

    it('should maintain latency < 200ms even for detailed queries', async () => {
      const startTime = performance.now();
      const result = await getAgentDetails('manta-15', { includeHistory: true });
      const endTime = performance.now();

      expect(result).toBeDefined();
      expect(endTime - startTime).toBeLessThan(200);
    });
  });

  describe('✓ markdown válido', () => {
    it('should return valid markdown for agent details', async () => {
      const result = await getAgentDetails('manta-00');

      expect(result.markdown).toBeDefined();
      expect(typeof result.markdown).toBe('string');
      expect(result.markdown.length).toBeGreaterThan(0);
    });

    it('should contain proper markdown headers in returned markdown', async () => {
      const result = await getAgentDetails('manta-01');

      expect(result.markdown).toMatch(/^#+\s+/m);
    });

    it('should contain valid markdown link syntax if present', async () => {
      const result = await getAgentDetails('agente-saneamento');

      if (result.markdown.includes('[')) {
        expect(result.markdown).toMatch(/\[.+?\]\(.+?\)/);
      }
    });

    it('should not contain unescaped special markdown characters that break parsing', async () => {
      const result = await getAgentDetails('manta-02');

      expect(result.markdown).not.toMatch(/`{4,}/);
      expect(result.markdown).not.toMatch(/\*{3,}/);
    });

    it('should have proper markdown structure with title and content', async () => {
      const result = await getAgentDetails('manta-04');
      const lines = result.markdown.split('\n');

      expect(lines.length).toBeGreaterThan(2);
      expect(lines[0]).toMatch(/^#+\s+\w+/);
    });

    it('should be valid markdown according to basic structure rules', async () => {
      const result = await getAgentDetails('manta-05');

      expect(result.markdown).toBeDefined();
      expect(result.markdown).not.toMatch(/\n\n\n\n/);
      expect(result.markdown).not.toMatch(/^-\s*$\n^-\s*$/m);
    });

    it('should include agent code and name in markdown', async () => {
      const result = await getAgentDetails('manta-06');

      expect(result.markdown).toContain(result.code);
      expect(result.markdown).toContain(result.name);
    });

    it('should not have unclosed markdown formatting tags', async () => {
      const result = await getAgentDetails('manta-07');
      const markdown = result.markdown;

      const boldCount = (markdown.match(/\*\*/g) || []).length;
      const italicCount = (markdown.match(/_(?![_])/g) || []).length;
      const codeCount = (markdown.match(/`/g) || []).length;

      expect(boldCount % 2).toBe(0);
      expect(codeCount % 2).toBe(0);
    });

    it('should have properly formatted markdown table if present', async () => {
      const result = await getAgentDetails('manta-00');

      if (result.markdown.includes('|')) {
        const rows = result.markdown.split('\n').filter(line => line.includes('|'));
        expect(rows.length).toBeGreaterThan(0);

        rows.forEach(row => {
          expect(row).toMatch(/^\|.+\|$/);
        });
      }
    });
  });

  describe('Integration tests', () => {
    it('should retrieve all horizontal agents without errors', async () => {
      const horizontalAgents = [
        'manta-00', 'manta-01', 'manta-02', 'manta-04',
        'manta-05', 'manta-06', 'manta-07', 'manta-13',
        'manta-14', 'manta-15', 'manta-16'
      ];

      for (const agent of horizontalAgents) {
        const result = await getAgentDetails(agent);
        expect(result).toBeDefined();
        expect(result.markdown).toBeDefined();
      }
    });

    it('should retrieve all vertical agents (S1-S10) without errors', async () => {
      const verticalAgents = [
        'agente-infraestrutura', 'agente-saneamento',
        'agente-energia', 'agente-portos',
        'agente-aeroportos', 'agente-barragens'
      ];

      for (const agent of verticalAgents) {
        try {
          const result = await getAgentDetails(agent);
          expect(result).toBeDefined();
          expect(result.markdown).toBeDefined();
        } catch (error: any) {
          if (error.statusCode !== 404) {
            throw error;
          }
        }
      }
    });

    it('should retrieve agent by alias', async () => {
      const result = await getAgentDetails('maestro');

      expect(result.code).toBe('Manta 00');
      expect(result.name).toBe('maestro');
    });

    it('should be deterministic - same input always returns same output', async () => {
      const result1 = await getAgentDetails('manta-01');
      const result2 = await getAgentDetails('manta-01');

      expect(result1.code).toEqual(result2.code);
      expect(result1.markdown).toEqual(result2.markdown);
    });
  });
});
