import { describe, it, expect, beforeEach, afterEach, jest } from '@jest/globals';
import { createAgent, AgentInput } from '../create-agent';
import * as gitAdapter from '../../adapters/git-adapter';
import * as githubAdapter from '../../adapters/cowork-adapter';
import { AuditLog } from '../../services/audit-log';

// Mock dos adapters
jest.mock('../../adapters/git-adapter');
jest.mock('../../adapters/cowork-adapter');
jest.mock('../../services/audit-log');

describe('createAgent', () => {
  let mockGitAdapter: jest.Mocked<typeof gitAdapter>;
  let mockGithubAdapter: jest.Mocked<typeof githubAdapter>;
  let mockAuditLog: jest.Mocked<typeof AuditLog>;

  beforeEach(() => {
    jest.clearAllMocks();

    // Setup default mocks
    mockGitAdapter.createBranch = jest.fn().mockResolvedValue({
      branchName: 'feature/agente-teste-001',
      commitHash: 'abc123def456',
    });

    mockGithubAdapter.createPullRequest = jest.fn().mockResolvedValue({
      prNumber: 42,
      prUrl: 'https://github.com/manta/codex/pull/42',
      status: 'open',
    });

    mockAuditLog.log = jest.fn().mockResolvedValue({
      id: 'audit-123',
      timestamp: new Date(),
      action: 'CREATE_AGENT',
    });
  });

  // ====== TESTES DE VALIDAÇÃO SCHEMA ======
  describe('validação schema', () => {
    it('✓ deve validar agente com schema correto', async () => {
      const validInput: AgentInput = {
        code: 'Manta 03-S11',
        name: 'agente-teste',
        segment: 'Teste',
        tier: 'Sonnet',
        aliases: ['s11', 'teste'],
        keywords: [
          { keyword: 'teste', weight: 3.0, category: 'primary' },
          { keyword: 'validação', weight: 2.5, category: 'secondary' },
        ],
      };

      const result = await createAgent(validInput);

      expect(result).toBeDefined();
      expect(result.agentCode).toBe('Manta 03-S11');
      expect(result.status).toBe('success');
    });

    it('✓ deve validar campos obrigatórios', async () => {
      const incompleteInput = {
        code: 'Manta 03-S11',
        name: 'agente-teste',
        // segment faltando
        tier: 'Sonnet',
        aliases: ['s11'],
        keywords: [{ keyword: 'teste', weight: 3.0, category: 'primary' }],
      } as AgentInput;

      await expect(createAgent(incompleteInput)).rejects.toThrow(
        'Validação schema falhou: segment é obrigatório'
      );
    });

    it('✓ deve validar tipos de dados corretos', async () => {
      const invalidTypeInput = {
        code: 'Manta 03-S11',
        name: 'agente-teste',
        segment: 'Teste',
        tier: 123, // deve ser string
        aliases: ['s11'],
        keywords: [{ keyword: 'teste', weight: 3.0, category: 'primary' }],
      } as AgentInput;

      await expect(createAgent(invalidTypeInput)).rejects.toThrow(
        'Validação schema falhou: tier deve ser string'
      );
    });

    it('✓ deve validar tier com valores permitidos', async () => {
      const invalidTierInput: AgentInput = {
        code: 'Manta 03-S11',
        name: 'agente-teste',
        segment: 'Teste',
        tier: 'InvalidTier', // apenas Haiku, Sonnet, Opus permitidos
        aliases: ['s11'],
        keywords: [{ keyword: 'teste', weight: 3.0, category: 'primary' }],
      };

      await expect(createAgent(invalidTierInput)).rejects.toThrow(
        'Validação schema falhou: tier deve ser Haiku, Sonnet ou Opus'
      );
    });

    it('✓ deve validar formato de code (Manta XX-SXX)', async () => {
      const invalidCodeInput: AgentInput = {
        code: 'INVALID-CODE', // não segue padrão Manta XX-SXX
        name: 'agente-teste',
        segment: 'Teste',
        tier: 'Sonnet',
        aliases: ['s11'],
        keywords: [{ keyword: 'teste', weight: 3.0, category: 'primary' }],
      };

      await expect(createAgent(invalidCodeInput)).rejects.toThrow(
        'Validação schema falhou: code deve seguir padrão Manta XX-SXX ou Manta XX'
      );
    });

    it('✓ deve validar peso de keywords entre 0 e 5', async () => {
      const invalidWeightInput: AgentInput = {
        code: 'Manta 03-S11',
        name: 'agente-teste',
        segment: 'Teste',
        tier: 'Sonnet',
        aliases: ['s11'],
        keywords: [
          { keyword: 'teste', weight: 10.0, category: 'primary' }, // > 5
        ],
      };

      await expect(createAgent(invalidWeightInput)).rejects.toThrow(
        'Validação schema falhou: keyword weight deve estar entre 0 e 5'
      );
    });
  });

  // ====== TESTES DE GIT BRANCH ======
  describe('criação de git branch', () => {
    const validInput: AgentInput = {
      code: 'Manta 03-S11',
      name: 'agente-teste',
      segment: 'Teste',
      tier: 'Sonnet',
      aliases: ['s11'],
      keywords: [{ keyword: 'teste', weight: 3.0, category: 'primary' }],
    };

    it('✓ deve criar branch git com nome correto', async () => {
      await createAgent(validInput);

      expect(gitAdapter.createBranch).toHaveBeenCalledWith(
        expect.objectContaining({
          branchName: expect.stringMatching(/^feature\/agente-teste-\d{3}$/),
          baseBranch: 'main',
        })
      );
    });

    it('✓ deve criar commits com arquivos corretos', async () => {
      await createAgent(validInput);

      expect(gitAdapter.createBranch).toHaveBeenCalled();
      const callArgs = (gitAdapter.createBranch as jest.Mock).mock.calls[0][0];

      expect(callArgs.files).toBeDefined();
      expect(callArgs.files).toContainEqual(
        expect.objectContaining({
          path: expect.stringMatching(/\.claude\/agents\/agente-teste\.md$/),
        })
      );
    });

    it('✓ deve incluir arquivo de keywords no commit', async () => {
      await createAgent(validInput);

      const callArgs = (gitAdapter.createBranch as jest.Mock).mock.calls[0][0];

      expect(callArgs.files).toContainEqual(
        expect.objectContaining({
          path: expect.stringMatching(/agente-teste-keywords\.json$/),
        })
      );
    });

    it('✓ deve lançar erro se git branch falhar', async () => {
      (gitAdapter.createBranch as jest.Mock).mockRejectedValueOnce(
        new Error('Git branch creation failed')
      );

      await expect(createAgent(validInput)).rejects.toThrow('Git branch creation failed');
    });

    it('✓ deve committar com mensagem descriptiva', async () => {
      await createAgent(validInput);

      const callArgs = (gitAdapter.createBranch as jest.Mock).mock.calls[0][0];

      expect(callArgs.commitMessage).toContain('agente-teste');
      expect(callArgs.commitMessage).toContain('Manta 03-S11');
    });
  });

  // ====== TESTES DE PR NO GITHUB ======
  describe('abertura de PR no GitHub', () => {
    const validInput: AgentInput = {
      code: 'Manta 03-S11',
      name: 'agente-novo',
      segment: 'Novo Segmento',
      tier: 'Sonnet',
      aliases: ['s11'],
      keywords: [{ keyword: 'novo', weight: 3.0, category: 'primary' }],
    };

    it('✓ deve abrir PR após criar branch', async () => {
      await createAgent(validInput);

      expect(githubAdapter.createPullRequest).toHaveBeenCalled();
      expect(githubAdapter.createPullRequest).toHaveBeenCalledAfter(
        gitAdapter.createBranch as jest.Mock
      );
    });

    it('✓ deve incluir informações corretas no PR', async () => {
      await createAgent(validInput);

      const prArgs = (githubAdapter.createPullRequest as jest.Mock).mock.calls[0][0];

      expect(prArgs.title).toContain('agente-novo');
      expect(prArgs.title).toContain('Manta 03-S11');
      expect(prArgs.body).toContain('Novo Segmento');
      expect(prArgs.body).toContain('Keywords');
    });

    it('✓ deve usar branch name do git na PR', async () => {
      await createAgent(validInput);

      const prArgs = (githubAdapter.createPullRequest as jest.Mock).mock.calls[0][0];

      expect(prArgs.head).toMatch(/^feature\/agente-novo-\d{3}$/);
      expect(prArgs.base).toBe('main');
    });

    it('✓ deve lançar erro se PR creation falhar', async () => {
      (githubAdapter.createPullRequest as jest.Mock).mockRejectedValueOnce(
        new Error('PR creation failed')
      );

      await expect(createAgent(validInput)).rejects.toThrow('PR creation failed');
    });

    it('✓ deve retornar URL da PR no resultado', async () => {
      const result = await createAgent(validInput);

      expect(result.prUrl).toBe('https://github.com/manta/codex/pull/42');
      expect(result.prNumber).toBe(42);
    });
  });

  // ====== TESTES DE KEYWORDS VAZIAS ======
  describe('validação de keywords vazias', () => {
    it('✓ deve rejeitar array vazio de keywords', async () => {
      const noKeywordsInput: AgentInput = {
        code: 'Manta 03-S11',
        name: 'agente-teste',
        segment: 'Teste',
        tier: 'Sonnet',
        aliases: ['s11'],
        keywords: [], // vazio!
      };

      await expect(createAgent(noKeywordsInput)).rejects.toThrow(
        'Validação schema falhou: keywords não pode estar vazio'
      );
    });

    it('✓ deve rejeitar keywords undefined', async () => {
      const undefinedKeywordsInput: AgentInput = {
        code: 'Manta 03-S11',
        name: 'agente-teste',
        segment: 'Teste',
        tier: 'Sonnet',
        aliases: ['s11'],
        keywords: undefined as any,
      };

      await expect(createAgent(undefinedKeywordsInput)).rejects.toThrow(
        'Validação schema falhou: keywords é obrigatório'
      );
    });

    it('✓ deve exigir mínimo de 3 keywords', async () => {
      const tooFewKeywordsInput: AgentInput = {
        code: 'Manta 03-S11',
        name: 'agente-teste',
        segment: 'Teste',
        tier: 'Sonnet',
        aliases: ['s11'],
        keywords: [
          { keyword: 'teste', weight: 3.0, category: 'primary' },
          { keyword: 'validação', weight: 2.5, category: 'secondary' },
        ], // apenas 2
      };

      await expect(createAgent(tooFewKeywordsInput)).rejects.toThrow(
        'Validação schema falhou: mínimo de 3 keywords obrigatório'
      );
    });

    it('✓ deve rejeitar keyword com nome vazio', async () => {
      const emptyKeywordNameInput: AgentInput = {
        code: 'Manta 03-S11',
        name: 'agente-teste',
        segment: 'Teste',
        tier: 'Sonnet',
        aliases: ['s11'],
        keywords: [
          { keyword: '', weight: 3.0, category: 'primary' }, // vazio!
          { keyword: 'validação', weight: 2.5, category: 'secondary' },
          { keyword: 'teste', weight: 2.0, category: 'context' },
        ],
      };

      await expect(createAgent(emptyKeywordNameInput)).rejects.toThrow(
        'Validação schema falhou: keyword não pode ser vazio'
      );
    });

    it('✓ deve rejeitar category inválida em keywords', async () => {
      const invalidCategoryInput: AgentInput = {
        code: 'Manta 03-S11',
        name: 'agente-teste',
        segment: 'Teste',
        tier: 'Sonnet',
        aliases: ['s11'],
        keywords: [
          { keyword: 'teste', weight: 3.0, category: 'invalid' as any },
          { keyword: 'validação', weight: 2.5, category: 'secondary' },
          { keyword: 'outro', weight: 2.0, category: 'primary' },
        ],
      };

      await expect(createAgent(invalidCategoryInput)).rejects.toThrow(
        'Validação schema falhou: category deve ser primary, secondary, context ou regulatory'
      );
    });
  });

  // ====== TESTES DE AUDIT LOG ======
  describe('audit log', () => {
    const validInput: AgentInput = {
      code: 'Manta 03-S11',
      name: 'agente-auditado',
      segment: 'Teste',
      tier: 'Sonnet',
      aliases: ['s11'],
      keywords: [
        { keyword: 'teste', weight: 3.0, category: 'primary' },
        { keyword: 'auditoria', weight: 2.5, category: 'secondary' },
        { keyword: 'log', weight: 2.0, category: 'context' },
      ],
    };

    it('✓ deve registrar evento de criação no audit log', async () => {
      await createAgent(validInput);

      expect(AuditLog.log).toHaveBeenCalledWith(
        expect.objectContaining({
          action: 'CREATE_AGENT',
          agentCode: 'Manta 03-S11',
          agentName: 'agente-auditado',
        })
      );
    });

    it('✓ deve registrar keywords no audit log', async () => {
      await createAgent(validInput);

      const auditArgs = (AuditLog.log as jest.Mock).mock.calls[0][0];

      expect(auditArgs.keywordCount).toBe(3);
      expect(auditArgs.keywords).toEqual(['teste', 'auditoria', 'log']);
    });

    it('✓ deve registrar branch git criado', async () => {
      await createAgent(validInput);

      const auditArgs = (AuditLog.log as jest.Mock).mock.calls[0][0];

      expect(auditArgs.branchName).toMatch(/^feature\/agente-auditado-\d{3}$/);
    });

    it('✓ deve registrar PR aberto', async () => {
      await createAgent(validInput);

      const auditArgs = (AuditLog.log as jest.Mock).mock.calls[0][0];

      expect(auditArgs.prNumber).toBe(42);
      expect(auditArgs.prUrl).toBe('https://github.com/manta/codex/pull/42');
    });

    it('✓ deve registrar usuário que criou agente', async () => {
      await createAgent(validInput, { userId: 'mneves' });

      const auditArgs = (AuditLog.log as jest.Mock).mock.calls[0][0];

      expect(auditArgs.userId).toBe('mneves');
    });

    it('✓ deve falhar gracefully se audit log falhar', async () => {
      (AuditLog.log as jest.Mock).mockRejectedValueOnce(
        new Error('Audit log service down')
      );

      // Deve completar sem throw (fallback)
      const result = await createAgent(validInput);

      expect(result.status).toBe('success');
      expect(result.auditLogWarning).toContain('Audit log');
    });

    it('✓ deve registrar timestamp do evento', async () => {
      const beforeCreate = new Date();
      await createAgent(validInput);
      const afterCreate = new Date();

      const auditArgs = (AuditLog.log as jest.Mock).mock.calls[0][0];

      expect(auditArgs.timestamp).toBeInstanceOf(Date);
      expect(auditArgs.timestamp.getTime()).toBeGreaterThanOrEqual(beforeCreate.getTime());
      expect(auditArgs.timestamp.getTime()).toBeLessThanOrEqual(afterCreate.getTime());
    });
  });

  // ====== TESTES INTEGRADOS ======
  describe('fluxo completo integrado', () => {
    it('✓ deve executar todo o fluxo com sucesso', async () => {
      const input: AgentInput = {
        code: 'Manta 03-S12',
        name: 'agente-completo',
        segment: 'Integração Total',
        tier: 'Opus',
        aliases: ['s12', 'completo'],
        keywords: [
          { keyword: 'integração', weight: 3.0, category: 'primary' },
          { keyword: 'teste', weight: 2.8, category: 'primary' },
          { keyword: 'sucesso', weight: 2.5, category: 'secondary' },
        ],
      };

      const result = await createAgent(input);

      expect(result.status).toBe('success');
      expect(result.agentCode).toBe('Manta 03-S12');
      expect(result.agentName).toBe('agente-completo');
      expect(result.branchName).toBeDefined();
      expect(result.prNumber).toBe(42);
      expect(result.prUrl).toBeDefined();
    });

    it('✓ deve chamar funções na ordem correta', async () => {
      const input: AgentInput = {
        code: 'Manta 03-S13',
        name: 'agente-ordem',
        segment: 'Ordem',
        tier: 'Sonnet',
        aliases: ['s13'],
        keywords: [
          { keyword: 'a', weight: 3.0, category: 'primary' },
          { keyword: 'b', weight: 2.5, category: 'secondary' },
          { keyword: 'c', weight: 2.0, category: 'context' },
        ],
      };

      await createAgent(input);

      // createBranch deve ser chamado antes de createPullRequest
      const gitOrder = (gitAdapter.createBranch as jest.Mock).mock.invocationCallOrder[0];
      const prOrder = (githubAdapter.createPullRequest as jest.Mock).mock.invocationCallOrder[0];
      const auditOrder = (AuditLog.log as jest.Mock).mock.invocationCallOrder[0];

      expect(gitOrder).toBeLessThan(prOrder);
      expect(prOrder).toBeLessThan(auditOrder);
    });

    it('✓ deve ser idempotente (mesmo input, mesmo resultado)', async () => {
      const input: AgentInput = {
        code: 'Manta 03-S14',
        name: 'agente-idempotente',
        segment: 'Teste',
        tier: 'Sonnet',
        aliases: ['s14'],
        keywords: [
          { keyword: 'idem', weight: 3.0, category: 'primary' },
          { keyword: 'potente', weight: 2.5, category: 'secondary' },
          { keyword: 'test', weight: 2.0, category: 'context' },
        ],
      };

      const result1 = await createAgent(input);
      const result2 = await createAgent(input);

      expect(result1.agentCode).toBe(result2.agentCode);
      expect(result1.agentName).toBe(result2.agentName);
    });
  });
});
