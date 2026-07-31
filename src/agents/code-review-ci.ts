#!/usr/bin/env ts-node
/**
 * Code Review CI Script
 *
 * Executado em GitHub Actions para analisar PRs automaticamente.
 * Lê diff e novo código, executa análise, salva relatório JSON.
 */

import fs from "fs";
import path from "path";
import { execSync } from "child_process";
import { CodeReviewerAgent, type CodeReviewInput } from "./code-reviewer";

/**
 * Obtém diff da PR
 */
function getPRDiff(): string {
  try {
    const diff = execSync("git diff origin/main...HEAD", {
      encoding: "utf-8",
    });
    return diff;
  } catch (error) {
    console.warn("⚠️ Could not get git diff, using empty diff");
    return "";
  }
}

/**
 * Obtém caminho do novo agente (se aplicável)
 */
function getNewAgentPath(): string | null {
  try {
    const files = execSync("git diff --name-only origin/main...HEAD", {
      encoding: "utf-8",
    })
      .split("\n")
      .filter(Boolean);

    const agentFiles = files.filter(
      (f) =>
        f.startsWith("src/agents/agente-") &&
        f.endsWith(".ts") &&
        fs.existsSync(f)
    );

    return agentFiles.length > 0 ? agentFiles[0] : null;
  } catch {
    return null;
  }
}

/**
 * Lê conteúdo do novo agente
 */
function readNewAgentCode(filepath: string): string {
  try {
    return fs.readFileSync(filepath, "utf-8");
  } catch {
    return "";
  }
}

/**
 * Executa análise e salva relatório
 */
async function runCodeReview(): Promise<void> {
  const startTime = Date.now();
  const outputFile = "/tmp/review-report.json";

  try {
    console.log("🔍 Starting Code Review Analysis...\n");

    // Inicializa agent
    const apiKey = process.env.ANTHROPIC_API_KEY;
    if (!apiKey) {
      throw new Error("ANTHROPIC_API_KEY not set");
    }

    const agent = new CodeReviewerAgent(apiKey);

    // Obtém dados da PR
    const prDiff = getPRDiff();
    const agentPath = getNewAgentPath();
    const newAgentCode = agentPath ? readNewAgentCode(agentPath) : "";

    // Extrai contexto de commit
    let prTitle = "";
    let prDescription = "";
    try {
      prTitle = execSync(
        'git log -1 --format="%s" origin/main...HEAD 2>/dev/null',
        { encoding: "utf-8" }
      ).trim();
      prDescription = execSync(
        'git log -1 --format="%b" origin/main...HEAD 2>/dev/null',
        { encoding: "utf-8" }
      ).trim();
    } catch {
      // Se não conseguir, continua sem contexto
    }

    console.log(`📝 PR Title: ${prTitle || "(not available)"}`);
    console.log(`📋 New Agent: ${agentPath || "None"}\n`);

    // Prepara input de análise
    const reviewInput: CodeReviewInput = {
      prDiff,
      newAgentCode,
      agentPath: agentPath || "src/agents/unknown.ts",
      prContext: {
        title: prTitle,
        description: prDescription,
        author: process.env.GITHUB_ACTOR || "unknown",
      },
    };

    // Executa review
    console.log("⏳ Running analysis with Claude Opus...\n");
    const result = await agent.reviewCode(reviewInput);

    console.log(`✅ Analysis complete\n`);
    console.log(`📊 Results:`);
    console.log(`   Score: ${result.overallScore}/100`);
    console.log(`   Findings: ${result.findings.length}`);
    console.log(`   Correctness: ${result.dimensionStats.correctness}`);
    console.log(`   Security: ${result.dimensionStats.security}`);
    console.log(`   Performance: ${result.dimensionStats.performance}`);
    console.log(`   Style: ${result.dimensionStats.style}`);
    console.log(`   Critical: ${result.severityStats.critical}`);
    console.log(`   Error: ${result.severityStats.error}`);
    console.log(`   Warning: ${result.severityStats.warning}\n`);

    // Determina ação sugerida
    let suggestedAction: "approve" | "request-changes" | "comment" = "approve";
    if (result.severityStats.critical > 0 || result.overallScore < 60) {
      suggestedAction = "request-changes";
    } else if (result.severityStats.error > 0 || result.overallScore < 80) {
      suggestedAction = "comment";
    }

    console.log(`🎯 Suggested Action: ${suggestedAction}\n`);

    // Resumo para GitHub
    console.log("SUMMARY:");
    console.log(result.summary);

    // Prepara output estruturado para GitHub Actions
    const output = {
      status: result.status,
      overallScore: result.overallScore,
      findings: result.findings,
      summary: result.summary,
      dimensionStats: result.dimensionStats,
      severityStats: result.severityStats,
      suggestedAction,
      analysisTimeMs: result.analysisTimeMs,
      timestamp: new Date().toISOString(),
    };

    // Salva relatório
    fs.writeFileSync(outputFile, JSON.stringify(output, null, 2));
    console.log(`\n💾 Report saved to ${outputFile}`);

    // GitHub Actions outputs
    if (process.env.GITHUB_OUTPUT) {
      const outputLines = [
        `status=${output.status}`,
        `score=${output.overallScore}`,
        `has-critical=${output.severityStats.critical > 0 ? "true" : "false"}`,
        `suggested-action=${output.suggestedAction}`,
      ];

      fs.appendFileSync(process.env.GITHUB_OUTPUT, outputLines.join("\n"));
    }

    // Exit code
    if (output.suggestedAction === "request-changes") {
      console.log("\n⚠️  Review requires changes before merge");
      process.exit(1);
    }

    console.log("\n✅ Code review passed!");
    process.exit(0);
  } catch (error) {
    console.error("\n❌ Code review failed:");
    console.error(error instanceof Error ? error.message : String(error));

    // Salva erro
    const errorOutput = {
      status: "failed",
      error: error instanceof Error ? error.message : String(error),
      timestamp: new Date().toISOString(),
    };

    fs.writeFileSync(
      "/tmp/review-report.json",
      JSON.stringify(errorOutput, null, 2)
    );

    process.exit(1);
  }
}

// Executa se chamado diretamente
if (import.meta.url === `file://${process.argv[1]}`) {
  runCodeReview();
}

export { runCodeReview };
