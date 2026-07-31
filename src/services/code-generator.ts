/**
 * Code Generator — Serviço de geração de código para agentes Manta
 * Versão: 1.0.0
 *
 * Responsabilidades:
 * - Recebe um intent (descrição em linguagem natural do agente a criar)
 * - Usa Claude Opus em conversação multi-turn para gerar código
 * - Valida YAML frontmatter obrigatório no output
 * - Cria branch feature/* com arquivos gerados
 * - Retorna filePath e metadados dos artefatos criados
 *
 * Tipos de artefatos gerados:
 * 1. Agent .md (com YAML frontmatter + markdown)
 * 2. Test cases (.test.ts)
 * 3. Documentation (.md)
 * 4. Keywords JSON
 */

import Anthropic from "@anthropic-ai/sdk";
import { execSync } from "child_process";
import { writeFileSync, mkdirSync, existsSync } from "fs";
import { join } from "path";
import { randomBytes } from "crypto";

// ============================================================================
// TIPOS E INTERFACES
// ============================================================================

/**
 * Input para o gerador de código
 */
export interface CodeGeneratorIntent {
  /** Descrição do agente a ser criado */
  intent: string;

  /** Segmento vertical (ex: "Saneamento", "Energia", "Portos") */
  segment: string;

  /** Código Manta (ex: "Manta 03-S8") */
  mantaCode?: string;

  /** Tier do modelo (Haiku, Sonnet, Opus) */
  tier?: "Haiku" | "Sonnet" | "Opus";

  /** Aliases/keywords iniciais */
  keywords?: string[];

  /** Email do usuário que está gerando */
  userEmail?: string;

  /** Diretório raiz do projeto */
  projectRoot?: string;
}

/**
 * Esquema de frontmatter YAML esperado nos outputs
 */
export interface AgentFrontmatter {
  name: string;
  description: string;
  tools: string[];
  model: "haiku" | "sonnet" | "opus";
}

/**
 * Artefato individual gerado
 */
export interface GeneratedArtifact {
  /** Nome do arquivo */
  filename: string;

  /** Caminho relativo ao repo */
  filepath: string;

  /** Conteúdo completo do arquivo */
  content: string;

  /** Tipo de artefato */
  type: "agent-md" | "test-cases" | "documentation" | "keywords-json";

  /** Validade do YAML frontmatter (se aplicável) */
  validated: boolean;

  /** Erros de validação (se houver) */
  validationErrors?: string[];
}

/**
 * Output completo do gerador
 */
export interface CodeGeneratorOutput {
  /** Status da geração */
  status: "success" | "partial" | "failed";

  /** Artefatos gerados */
  artifacts: GeneratedArtifact[];

  /** Caminhos dos arquivos criados */
  createdFiles: string[];

  /** Branch feature/* criado */
  branchName: string;

  /** Commit hash */
  commitHash: string;

  /** Erros encontrados durante geração */
  errors: string[];

  /** Avisos (validações que passaram mas têm restrições) */
  warnings: string[];

  /** Tempo total de execução (ms) */
  executionTimeMs: number;

  /** Conversação completa com Claude Opus (para auditoria) */
  conversationLog?: ConversationMessage[];
}

/**
 * Mensagem de conversação para auditoria
 */
export interface ConversationMessage {
  role: "user" | "assistant";
  content: string;
  timestamp: Date;
}

/**
 * Contexto interno de geração
 */
interface GenerationContext {
  intent: CodeGeneratorIntent;
  conversationHistory: ConversationMessage[];
  artifacts: GeneratedArtifact[];
  errors: string[];
  warnings: string[];
  startTime: number;
  branchName: string;
}

// ============================================================================
// CÓDIGO GENERATOR SERVICE
// ============================================================================

export class CodeGenerator {
  private client: Anthropic;
  private projectRoot: string;

  /**
   * Inicializa o gerador de código
   */
  constructor(apiKey?: string, projectRoot?: string) {
    this.client = new Anthropic({
      apiKey: apiKey || process.env.ANTHROPIC_API_KEY,
    });
    this.projectRoot = projectRoot || process.cwd();
  }

  /**
   * Função principal: gera código baseado em um intent
   *
   * @param intent - Descrição do agente a ser criado
   * @returns Resultado com artefatos, branch, commits
   */
  async generateCode(intent: CodeGeneratorIntent): Promise<CodeGeneratorOutput> {
    const startTime = Date.now();
    const context: GenerationContext = {
      intent,
      conversationHistory: [],
      artifacts: [],
      errors: [],
      warnings: [],
      startTime,
      branchName: this.generateBranchName(intent),
    };

    try {
      // Fase 1: Planejamento (Opus determina estrutura)
      await this.planGeneration(context);

      // Fase 2: Geração iterativa de artefatos
      await this.generateArtifacts(context);

      // Fase 3: Validação de schemas
      this.validateAllArtifacts(context);

      // Fase 4: Criação de branch e commits
      const commitHash = await this.createFeatureBranch(context);

      return {
        status: context.errors.length === 0 ? "success" : "partial",
        artifacts: context.artifacts,
        createdFiles: context.artifacts.map((a) => a.filepath),
        branchName: context.branchName,
        commitHash,
        errors: context.errors,
        warnings: context.warnings,
        executionTimeMs: Date.now() - startTime,
        conversationLog: context.conversationHistory,
      };
    } catch (error) {
      context.errors.push(
        `Erro crítico: ${error instanceof Error ? error.message : String(error)}`
      );

      return {
        status: "failed",
        artifacts: context.artifacts,
        createdFiles: context.artifacts.map((a) => a.filepath),
        branchName: context.branchName,
        commitHash: "",
        errors: context.errors,
        warnings: context.warnings,
        executionTimeMs: Date.now() - startTime,
      };
    }
  }

  /**
   * Fase 1: Planejamento com Claude Opus
   * Determina estrutura inicial, tipo de agente, dependências
   */
  private async planGeneration(context: GenerationContext): Promise<void> {
    const systemPrompt = `Tu es Claude Opus, especialista em arquitetura de agentes IA.
Estou criando um novo agente Manta. Tu vais:
1. Analisar o intent
2. Sugerir código + testes + documentação
3. Garantir que TODOS os outputs tenham YAML frontmatter válido
4. Retornar código TypeScript/Markdown pronto para uso

IMPORTANTE:
- Agent .md DEVE ter frontmatter YAML válido (name, description, tools, model)
- Todos os outputs DEVEM estar prontos para commitar sem edição
- Use backticks triplos para blocos de código`;

    const userPrompt = `Crie um agente Manta baseado neste intent:

INTENT: ${context.intent.intent}
SEGMENTO: ${context.intent.segment}
TIER: ${context.intent.tier || "Sonnet"}
CÓDIGO: ${context.intent.mantaCode || "Auto-assign"}

Retorne estruturado assim:

## Agent Markdown
\`\`\`markdown
---
name: agente-name
description: ...
tools: [...]
model: sonnet
---

# Agente Name
...
\`\`\`

## Test Cases
\`\`\`typescript
import { describe, it, expect } from '@jest/globals';

describe('Agent Name', () => {
  // test cases
});
\`\`\`

## Documentation
\`\`\`markdown
# Documentação do Agente Name
...
\`\`\`

## Keywords JSON
\`\`\`json
{
  "keywords": [...]
}
\`\`\``;

    const messages: Anthropic.MessageParam[] = [
      { role: "user", content: userPrompt },
    ];

    // Registra mensagem do usuário
    context.conversationHistory.push({
      role: "user",
      content: userPrompt,
      timestamp: new Date(),
    });

    // Chama Claude Opus
    const response = await this.client.messages.create({
      model: "claude-opus-4-1-20250805",
      max_tokens: 4000,
      system: systemPrompt,
      messages,
    });

    const assistantMessage =
      response.content[0].type === "text" ? response.content[0].text : "";

    // Registra resposta do assistant
    context.conversationHistory.push({
      role: "assistant",
      content: assistantMessage,
      timestamp: new Date(),
    });

    // Parse dos artefatos na resposta
    this.parseOpusResponse(assistantMessage, context);
  }

  /**
   * Fase 2: Geração iterativa de detalhes
   * Se necessário, faz perguntas de follow-up ao Opus
   */
  private async generateArtifacts(context: GenerationContext): Promise<void> {
    // Se a primeira resposta gerou todos os artefatos, não precisa de iteração
    if (context.artifacts.length >= 3) {
      return;
    }

    // Caso contrário, pede mais detalhes
    const missingArtifacts = this.identifyMissingArtifacts(context);

    if (missingArtifacts.length === 0) {
      return;
    }

    const followUpPrompt = `Os artefatos gerados foram: ${context.artifacts.map((a) => a.type).join(", ")}
Faltam: ${missingArtifacts.join(", ")}

Por favor, gere os artefatos faltantes mantendo o mesmo padrão e estrutura.`;

    const messages: Anthropic.MessageParam[] = [
      ...context.conversationHistory.map((msg) => ({
        role: msg.role as "user" | "assistant",
        content: msg.content,
      })),
      { role: "user", content: followUpPrompt },
    ];

    context.conversationHistory.push({
      role: "user",
      content: followUpPrompt,
      timestamp: new Date(),
    });

    const response = await this.client.messages.create({
      model: "claude-opus-4-1-20250805",
      max_tokens: 3000,
      system:
        "Continua gerando os artefatos faltantes com mesma qualidade e estrutura.",
      messages,
    });

    const assistantMessage =
      response.content[0].type === "text" ? response.content[0].text : "";

    context.conversationHistory.push({
      role: "assistant",
      content: assistantMessage,
      timestamp: new Date(),
    });

    this.parseOpusResponse(assistantMessage, context);
  }

  /**
   * Extrai artefatos da resposta Opus (markdown com blocos de código)
   */
  private parseOpusResponse(
    response: string,
    context: GenerationContext
  ): void {
    // Padrão: ## Tipo \n ```language \n conteúdo \n ```
    const codeBlockPattern =
      /## (Agent Markdown|Test Cases|Documentation|Keywords JSON)\s*\n```(?:markdown|typescript|json)?\s*\n([\s\S]*?)\n```/gi;

    let match;
    while ((match = codeBlockPattern.exec(response)) !== null) {
      const type = match[1].toLowerCase().trim();
      const content = match[2];

      let artifactType: GeneratedArtifact["type"];
      let filename: string;

      switch (type) {
        case "agent markdown":
          artifactType = "agent-md";
          filename = `${this.extractAgentName(content)}.md`;
          break;
        case "test cases":
          artifactType = "test-cases";
          filename = `${this.extractAgentName(content)}.test.ts`;
          break;
        case "documentation":
          artifactType = "documentation";
          filename = `${this.extractAgentName(content)}-documentation.md`;
          break;
        case "keywords json":
          artifactType = "keywords-json";
          filename = `${this.extractAgentName(content)}-keywords.json`;
          break;
        default:
          continue;
      }

      const filepath = this.buildFilepath(filename, artifactType);

      context.artifacts.push({
        filename,
        filepath,
        content,
        type: artifactType,
        validated: false,
      });
    }
  }

  /**
   * Valida YAML frontmatter obrigatório
   */
  private validateAllArtifacts(context: GenerationContext): void {
    for (const artifact of context.artifacts) {
      if (artifact.type === "agent-md") {
        const validationErrors = this.validateFrontmatter(artifact.content);
        if (validationErrors.length > 0) {
          artifact.validationErrors = validationErrors;
          artifact.validated = false;
          context.errors.push(
            `Validação falhou em ${artifact.filename}: ${validationErrors.join("; ")}`
          );
        } else {
          artifact.validated = true;
        }
      } else {
        // Outros tipos: validação básica de sintaxe
        artifact.validated = this.validateSyntax(artifact);
      }
    }
  }

  /**
   * Valida YAML frontmatter de arquivo agent .md
   */
  private validateFrontmatter(content: string): string[] {
    const errors: string[] = [];

    // Deve começar com ---
    if (!content.startsWith("---")) {
      errors.push("Arquivo deve começar com --- (YAML frontmatter)");
      return errors;
    }

    // Extrai frontmatter
    const frontmatterMatch = content.match(/^---\s*\n([\s\S]*?)\n---/);
    if (!frontmatterMatch) {
      errors.push("Frontmatter YAML não encontrado ou mal formado");
      return errors;
    }

    const frontmatterStr = frontmatterMatch[1];

    // Parse YAML simples (sem dependência externa)
    const frontmatter: Record<string, unknown> = {};
    for (const line of frontmatterStr.split("\n")) {
      if (!line.trim() || line.startsWith("#")) continue;

      const [key, ...valueParts] = line.split(":");
      if (!key) continue;

      const value = valueParts.join(":").trim();

      if (key.trim() === "tools") {
        // Parse array [tool1, tool2]
        const arrayMatch = value.match(/\[(.*?)\]/);
        frontmatter[key.trim()] = arrayMatch
          ? arrayMatch[1].split(",").map((t) => t.trim())
          : [];
      } else if (value === "true" || value === "false") {
        frontmatter[key.trim()] = value === "true";
      } else {
        frontmatter[key.trim()] = value;
      }
    }

    // Validação de campos obrigatórios
    const requiredFields = ["name", "description", "tools", "model"];
    for (const field of requiredFields) {
      if (!(field in frontmatter)) {
        errors.push(`Campo obrigatório ausente: ${field}`);
      }
    }

    // Validação de tipos
    if (
      frontmatter["name"] &&
      typeof frontmatter["name"] !== "string"
    ) {
      errors.push("Campo 'name' deve ser string");
    }

    if (
      frontmatter["tools"] &&
      !Array.isArray(frontmatter["tools"])
    ) {
      errors.push("Campo 'tools' deve ser array");
    }

    if (
      frontmatter["model"] &&
      !["haiku", "sonnet", "opus"].includes(String(frontmatter["model"]))
    ) {
      errors.push("Campo 'model' deve ser: haiku, sonnet ou opus");
    }

    return errors;
  }

  /**
   * Validação básica de sintaxe TypeScript/JSON
   */
  private validateSyntax(artifact: GeneratedArtifact): boolean {
    try {
      if (artifact.type === "test-cases") {
        // Valida que é TypeScript válido (check mínimo)
        if (
          !artifact.content.includes("describe") ||
          !artifact.content.includes("test")
        ) {
          artifact.validationErrors = [
            "Test file deve conter describe() e test()",
          ];
          return false;
        }
      } else if (artifact.type === "keywords-json") {
        // Valida JSON
        JSON.parse(artifact.content);
      }
      return true;
    } catch (error) {
      artifact.validationErrors = [
        `Erro de sintaxe: ${error instanceof Error ? error.message : String(error)}`,
      ];
      return false;
    }
  }

  /**
   * Cria branch feature/* e faz commits dos artefatos
   */
  private async createFeatureBranch(context: GenerationContext): Promise<string> {
    try {
      // Cria diretório .claude/agents se não existir
      const agentsDir = join(
        this.projectRoot,
        ".claude",
        "agents"
      );
      if (!existsSync(agentsDir)) {
        mkdirSync(agentsDir, { recursive: true });
      }

      // Escreve arquivos no disco
      for (const artifact of context.artifacts) {
        const fullPath = join(this.projectRoot, artifact.filepath);
        const dir = fullPath.substring(0, fullPath.lastIndexOf("/"));

        if (!existsSync(dir)) {
          mkdirSync(dir, { recursive: true });
        }

        writeFileSync(fullPath, artifact.content, "utf-8");
      }

      // Executa comandos git
      const agentName = this.extractAgentName(
        context.artifacts[0]?.content || ""
      );

      // 1. Cria branch
      execSync(`git checkout -b ${context.branchName}`, {
        cwd: this.projectRoot,
        stdio: "pipe",
      });

      // 2. Adiciona arquivos
      for (const artifact of context.artifacts) {
        execSync(`git add ${artifact.filepath}`, {
          cwd: this.projectRoot,
          stdio: "pipe",
        });
      }

      // 3. Cria commit
      const commitMessage = `feat: add ${agentName} agent

Generated by CodeGenerator service
Agent segment: ${context.intent.segment}
Intent: ${context.intent.intent.substring(0, 50)}...`;

      const commitHashOutput = execSync(
        `git commit -m "${commitMessage.replace(/"/g, '\\"')}"`,
        {
          cwd: this.projectRoot,
          stdio: "pipe",
          encoding: "utf-8",
        }
      );

      // Extrai hash do commit
      const hashMatch = commitHashOutput.match(/\[[\w/]+ ([a-f0-9]+)\]/);
      const commitHash = hashMatch ? hashMatch[1] : "unknown";

      return commitHash;
    } catch (error) {
      context.errors.push(
        `Erro ao criar branch/commit: ${error instanceof Error ? error.message : String(error)}`
      );
      throw error;
    }
  }

  /**
   * Gera nome único para branch feature/*
   */
  private generateBranchName(intent: CodeGeneratorIntent): string {
    const agentName = intent.intent
      .toLowerCase()
      .replace(/\s+/g, "-")
      .replace(/[^a-z0-9-]/g, "")
      .substring(0, 30);

    const shortHash = randomBytes(3).toString("hex");
    return `feature/agente-${agentName}-${shortHash}`;
  }

  /**
   * Extrai nome do agente a partir do conteúdo gerado
   */
  private extractAgentName(content: string): string {
    // Tenta extrair de frontmatter YAML
    const nameMatch = content.match(/name:\s*(['"]?)([^'"\n]+)\1/);
    if (nameMatch) {
      return nameMatch[2].toLowerCase().replace(/\s+/g, "-");
    }

    // Fallback: tenta extrair de # heading
    const headingMatch = content.match(/^#\s+(.+?)$/m);
    if (headingMatch) {
      return headingMatch[1].toLowerCase().replace(/\s+/g, "-");
    }

    return "agente-unknown";
  }

  /**
   * Constrói caminho do arquivo no repositório
   */
  private buildFilepath(
    filename: string,
    type: GeneratedArtifact["type"]
  ): string {
    switch (type) {
      case "agent-md":
        return `.claude/agents/${filename}`;
      case "test-cases":
        return `src/services/__tests__/${filename}`;
      case "documentation":
        return `docs/${filename}`;
      case "keywords-json":
        return `.claude/agents/${filename}`;
      default:
        return `src/${filename}`;
    }
  }

  /**
   * Identifica quais artefatos faltam
   */
  private identifyMissingArtifacts(context: GenerationContext): string[] {
    const generated = new Set(context.artifacts.map((a) => a.type));
    const required = [
      "agent-md",
      "test-cases",
      "documentation",
      "keywords-json",
    ];

    return required.filter((type) => !generated.has(type as any));
  }
}

// ============================================================================
// FACTORY FUNCTIONS
// ============================================================================

/**
 * Cria instância do gerador com configurações padrão
 */
export function createCodeGenerator(
  projectRoot?: string
): CodeGenerator {
  return new CodeGenerator(undefined, projectRoot);
}

/**
 * Função auxiliar para validação standalone de frontmatter
 */
export function validateYAMLFrontmatter(content: string): {
  valid: boolean;
  errors: string[];
} {
  const generator = new CodeGenerator();
  const errors = (generator as any).validateFrontmatter(content);
  return {
    valid: errors.length === 0,
    errors,
  };
}
