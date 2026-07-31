/**
 * Exemplo de integração do CodeGenerator
 * Demonstra como usar o serviço para gerar agentes Manta
 */

import {
  CodeGenerator,
  CodeGeneratorIntent,
  validateYAMLFrontmatter,
} from "../services/code-generator";

/**
 * Exemplo 1: Gerar agente simples de saneamento
 */
async function example1_GenerateSaneamentoAgent() {
  console.log("\n=== Exemplo 1: Gerar Agente Saneamento ===\n");

  const generator = new CodeGenerator(undefined, process.cwd());

  const intent: CodeGeneratorIntent = {
    intent:
      "Criar um agente especializado em projetos de ETA, ETE e sistemas de adução. " +
      "Deve suportar cálculos de demanda, dimensionamento de tubulações e tratamento. " +
      "Integra com SNIS e normas NBR 12211-12218.",
    segment: "Saneamento",
    mantaCode: "Manta 03-S8",
    tier: "Sonnet",
    keywords: ["eta", "ete", "adutora", "saneamento", "tratamento"],
    userEmail: "mneves@mantaassociados.com",
    projectRoot: process.cwd(),
  };

  try {
    const result = await generator.generateCode(intent);

    console.log(`Status: ${result.status}`);
    console.log(`Branch: ${result.branchName}`);
    console.log(`Commit: ${result.commitHash}`);
    console.log(`Artefatos gerados: ${result.artifacts.length}`);

    if (result.errors.length > 0) {
      console.log("\nErros encontrados:");
      result.errors.forEach((err) => console.log(`  - ${err}`));
    }

    if (result.warnings.length > 0) {
      console.log("\nAvisos:");
      result.warnings.forEach((warn) => console.log(`  - ${warn}`));
    }

    console.log(`\nTempo de execução: ${result.executionTimeMs}ms`);

    // Listar artefatos
    console.log("\nArtefatos criados:");
    result.artifacts.forEach((artifact) => {
      console.log(
        `  - ${artifact.filename} (${artifact.type}) - Validado: ${artifact.validated}`
      );
      if (artifact.validationErrors) {
        artifact.validationErrors.forEach((err) =>
          console.log(`    Erro: ${err}`)
        );
      }
    });
  } catch (error) {
    console.error("Erro na geração:", error);
  }
}

/**
 * Exemplo 2: Gerar agente de energia
 */
async function example2_GenerateEnergiaAgent() {
  console.log("\n=== Exemplo 2: Gerar Agente Energia ===\n");

  const generator = new CodeGenerator(undefined, process.cwd());

  const intent: CodeGeneratorIntent = {
    intent:
      "Criar agente para projetos de transmissão, subestações e leilões de energia. " +
      "Deve integrar com ANEEL, ONS e normas do setor elétrico brasileiro.",
    segment: "Energia",
    mantaCode: "Manta 03-S9",
    tier: "Sonnet",
    keywords: ["transmissão", "aneel", "subestação", "leilão"],
    userEmail: "mneves@mantaassociados.com",
    projectRoot: process.cwd(),
  };

  try {
    const result = await generator.generateCode(intent);
    console.log(`✓ Agente criado: ${result.branchName}`);
    console.log(
      `✓ Artefatos: ${result.artifacts.map((a) => a.type).join(", ")}`
    );
  } catch (error) {
    console.error("Erro:", error);
  }
}

/**
 * Exemplo 3: Validação standalone de YAML frontmatter
 */
function example3_ValidateFrontmatter() {
  console.log("\n=== Exemplo 3: Validar YAML Frontmatter ===\n");

  // Conteúdo válido
  const validContent = `---
name: agente-saneamento
description: Especialista em ETA e ETE
tools: [Read, Bash, WebFetch, Grep]
model: sonnet
---

# Agente Saneamento

Conteúdo aqui...`;

  const validResult = validateYAMLFrontmatter(validContent);
  console.log(`Conteúdo válido: ${validResult.valid}`);
  if (!validResult.valid) {
    console.log("Erros:", validResult.errors);
  }

  // Conteúdo inválido (falta "tools")
  const invalidContent = `---
name: agente-teste
description: Test
model: sonnet
---

Conteúdo...`;

  const invalidResult = validateYAMLFrontmatter(invalidContent);
  console.log(`\nConteúdo inválido: ${!invalidResult.valid}`);
  if (!invalidResult.valid) {
    console.log("Erros:");
    invalidResult.errors.forEach((err) => console.log(`  - ${err}`));
  }
}

/**
 * Exemplo 4: Processar múltiplos intents em paralelo
 */
async function example4_ParallelGeneration() {
  console.log("\n=== Exemplo 4: Geração em Paralelo ===\n");

  const generator = new CodeGenerator(undefined, process.cwd());

  const intents: CodeGeneratorIntent[] = [
    {
      intent: "Agente para portos e terminais portuários",
      segment: "Portos",
      mantaCode: "Manta 03-S6",
    },
    {
      intent: "Agente para aeroportos e infraestrutura aérea",
      segment: "Aeroportos",
      mantaCode: "Manta 03-S7",
    },
    {
      intent: "Agente para barragens e gestão de rejeitos",
      segment: "Barragens",
      mantaCode: "Manta 03-S10",
    },
  ];

  try {
    const results = await Promise.all(
      intents.map((intent) => generator.generateCode(intent))
    );

    console.log(`✓ Todos os ${results.length} agentes foram gerados`);

    results.forEach((result, idx) => {
      const status = result.status === "success" ? "✓" : "✗";
      console.log(
        `${status} ${intents[idx].segment}: ${result.branchName} (${result.artifacts.length} artefatos)`
      );
    });
  } catch (error) {
    console.error("Erro na geração paralela:", error);
  }
}

/**
 * Exemplo 5: Tratamento de erros
 */
async function example5_ErrorHandling() {
  console.log("\n=== Exemplo 5: Tratamento de Erros ===\n");

  const generator = new CodeGenerator(undefined, process.cwd());

  // Intent mínimo
  const minimalIntent: CodeGeneratorIntent = {
    intent: "Agente teste",
    segment: "Teste",
  };

  try {
    const result = await generator.generateCode(minimalIntent);

    if (result.status === "failed") {
      console.log("✗ Geração falhou");
      console.log("Erros:");
      result.errors.forEach((err) => console.log(`  - ${err}`));
    } else if (result.status === "partial") {
      console.log("⚠ Geração parcial");
      console.log("Avisos:");
      result.warnings.forEach((warn) => console.log(`  - ${warn}`));
    } else {
      console.log("✓ Geração bem-sucedida");
    }
  } catch (error) {
    console.error("Erro inesperado:", error);
  }
}

/**
 * Exemplo 6: Auditoria de geração (conversationLog)
 */
async function example6_AuditTrail() {
  console.log("\n=== Exemplo 6: Auditoria de Geração ===\n");

  const generator = new CodeGenerator(undefined, process.cwd());

  const intent: CodeGeneratorIntent = {
    intent: "Agente para saneamento",
    segment: "Saneamento",
    userEmail: "mneves@mantaassociados.com",
  };

  try {
    const result = await generator.generateCode(intent);

    if (result.conversationLog && result.conversationLog.length > 0) {
      console.log(`Conversação com Opus: ${result.conversationLog.length} mensagens\n`);

      result.conversationLog.forEach((msg, idx) => {
        console.log(`[${idx + 1}] ${msg.role.toUpperCase()} (${msg.timestamp})`);
        const preview = msg.content.substring(0, 100).replace(/\n/g, " ");
        console.log(`    "${preview}..."\n`);
      });
    }
  } catch (error) {
    console.error("Erro:", error);
  }
}

/**
 * Função principal para executar todos os exemplos
 */
async function main() {
  console.log("╔════════════════════════════════════════════════════════════╗");
  console.log("║         Code Generator - Exemplos de Uso                   ║");
  console.log("╚════════════════════════════════════════════════════════════╝");

  // Descomente o exemplo que deseja executar:

  // await example1_GenerateSaneamentoAgent();
  // await example2_GenerateEnergiaAgent();
  example3_ValidateFrontmatter();
  // await example4_ParallelGeneration();
  // await example5_ErrorHandling();
  // await example6_AuditTrail();

  console.log(
    "\n✓ Exemplos concluídos. Modifique a função main() para executar outros exemplos.\n"
  );
}

// Executar se for arquivo principal
if (require.main === module) {
  main().catch(console.error);
}

export {
  example1_GenerateSaneamentoAgent,
  example2_GenerateEnergiaAgent,
  example3_ValidateFrontmatter,
  example4_ParallelGeneration,
  example5_ErrorHandling,
  example6_AuditTrail,
};
