/**
 * Agents Module — Exportações principais
 *
 * Ponto de entrada para todos os agentes IA verticais e serviços relacionados.
 */

// Code Reviewer Agent
export { CodeReviewerAgent } from "./code-reviewer";
export type {
  AnalysisDimension,
  FindingSeverity,
  CodeFinding,
  CodeReviewInput,
  CodeReviewOutput,
} from "./code-reviewer";

// PR Integration
export { PRCodeReviewerIntegration, handleGitHubPRWebhook } from "./pr-code-reviewer-integration";
export type {
  GitHubPRPayload,
  PullRequestDiff,
  PRCodeReviewResult,
} from "./pr-code-reviewer-integration";

/**
 * Factory para criar instâncias de agentes
 */
export function createCodeReviewerAgent(apiKey?: string) {
  return new CodeReviewerAgent(apiKey || process.env.ANTHROPIC_API_KEY);
}

export function createPRReviewerIntegration(apiKey?: string) {
  return new PRCodeReviewerIntegration(apiKey || process.env.ANTHROPIC_API_KEY);
}

export default {
  CodeReviewerAgent,
  PRCodeReviewerIntegration,
  createCodeReviewerAgent,
  createPRReviewerIntegration,
};
