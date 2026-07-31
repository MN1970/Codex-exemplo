import * as nodegit from 'nodegit';

/**
 * Interface para resposta estruturada do adapter
 */
export interface AdapterResponse<T> {
  success: boolean;
  data?: T;
  error?: {
    code: string;
    message: string;
    details?: string;
  };
  timestamp: string;
}

/**
 * Interface para estado do repositório Git
 */
export interface GitState {
  repoPath: string;
  currentBranch: string;
  headHash: string;
  isDirty: boolean;
  unstagedFiles: string[];
  stagedFiles: string[];
  unmergedPaths: string[];
  remoteUrl?: string;
  remoteUrls?: {
    fetch: string;
    push: string;
  };
}

/**
 * Interface para resultado de create_branch
 */
export interface CreateBranchResult {
  branchName: string;
  commitHash: string;
  created: boolean;
  checkedOut: boolean;
}

/**
 * Interface para resultado de create_commit
 */
export interface CreateCommitResult {
  commitHash: string;
  message: string;
  author: {
    name: string;
    email: string;
  };
  timestamp: number;
  filesChanged: number;
}

/**
 * Interface para resultado de create_pull_request
 */
export interface CreatePullRequestResult {
  number?: number;
  url?: string;
  title: string;
  baseBranch: string;
  headBranch: string;
  status: 'created' | 'pending' | 'draft';
  message: string;
}

/**
 * Classe para operações Git com nodegit
 */
class GitAdapter {
  private repoPath: string;
  private repo: nodegit.Repository | null = null;

  constructor(repoPath: string) {
    this.repoPath = repoPath;
  }

  /**
   * Abre o repositório Git
   */
  private async openRepository(): Promise<nodegit.Repository> {
    if (this.repo) {
      return this.repo;
    }
    try {
      this.repo = await nodegit.Repository.open(this.repoPath);
      return this.repo;
    } catch (error) {
      throw new Error(
        `Failed to open repository at ${this.repoPath}: ${
          error instanceof Error ? error.message : String(error)
        }`
      );
    }
  }

  /**
   * Obtém o estado atual do repositório Git
   */
  async getGitState(): Promise<AdapterResponse<GitState>> {
    try {
      const repo = await this.openRepository();
      const head = await repo.getHeadCommit();
      const currentBranch = await repo.getCurrentBranch();
      const statuses = await repo.getStatus();

      const unstagedFiles: string[] = [];
      const stagedFiles: string[] = [];
      const unmergedPaths: string[] = [];

      statuses.forEach((file, path) => {
        if (file & nodegit.Status.STATUS.WT_MODIFIED ||
            file & nodegit.Status.STATUS.WT_NEW ||
            file & nodegit.Status.STATUS.WT_DELETED) {
          unstagedFiles.push(path);
        }
        if (file & nodegit.Status.STATUS.INDEX_MODIFIED ||
            file & nodegit.Status.STATUS.INDEX_NEW ||
            file & nodegit.Status.STATUS.INDEX_DELETED) {
          stagedFiles.push(path);
        }
        if (file & nodegit.Status.STATUS.CONFLICTED) {
          unmergedPaths.push(path);
        }
      });

      // Obter remote URL
      let remoteUrl: string | undefined;
      let remoteUrls: { fetch: string; push: string } | undefined;
      try {
        const remote = await repo.getRemote('origin');
        remoteUrl = remote.url();
        remoteUrls = {
          fetch: remote.url(),
          push: remote.url(),
        };
      } catch {
        // Remote não configurado
      }

      const gitState: GitState = {
        repoPath: this.repoPath,
        currentBranch: currentBranch.shorthand(),
        headHash: head.sha(),
        isDirty: unstagedFiles.length > 0 || stagedFiles.length > 0,
        unstagedFiles,
        stagedFiles,
        unmergedPaths,
        remoteUrl,
        remoteUrls,
      };

      return {
        success: true,
        data: gitState,
        timestamp: new Date().toISOString(),
      };
    } catch (error) {
      return {
        success: false,
        error: {
          code: 'GIT_STATE_ERROR',
          message: 'Failed to get Git state',
          details: error instanceof Error ? error.message : String(error),
        },
        timestamp: new Date().toISOString(),
      };
    }
  }

  /**
   * Cria uma nova branch
   */
  async createBranch(
    branchName: string,
    fromCommitHash?: string
  ): Promise<AdapterResponse<CreateBranchResult>> {
    try {
      if (!branchName || branchName.trim().length === 0) {
        return {
          success: false,
          error: {
            code: 'INVALID_BRANCH_NAME',
            message: 'Branch name cannot be empty',
          },
          timestamp: new Date().toISOString(),
        };
      }

      const repo = await this.openRepository();
      let targetCommit: nodegit.Commit;

      if (fromCommitHash) {
        try {
          targetCommit = await repo.getCommit(fromCommitHash);
        } catch {
          return {
            success: false,
            error: {
              code: 'INVALID_COMMIT_HASH',
              message: `Commit hash not found: ${fromCommitHash}`,
            },
            timestamp: new Date().toISOString(),
          };
        }
      } else {
        targetCommit = await repo.getHeadCommit();
      }

      // Verificar se branch já existe
      try {
        await repo.getBranch(branchName);
        return {
          success: false,
          error: {
            code: 'BRANCH_EXISTS',
            message: `Branch already exists: ${branchName}`,
          },
          timestamp: new Date().toISOString(),
        };
      } catch {
        // Branch não existe, pode criar
      }

      // Criar a branch
      const newBranch = await repo.createBranch(branchName, targetCommit);

      // Tentar fazer checkout (pode falhar se houver mudanças não commitadas)
      let checkedOut = false;
      try {
        await nodegit.Checkout.tree(repo, targetCommit, {
          checkoutStrategy: nodegit.Checkout.STRATEGY.SAFE,
        });
        await repo.setHead(newBranch.target());
        checkedOut = true;
      } catch {
        // Checkout falhou, mas branch foi criada
        checkedOut = false;
      }

      const result: CreateBranchResult = {
        branchName: newBranch.shorthand(),
        commitHash: targetCommit.sha(),
        created: true,
        checkedOut,
      };

      return {
        success: true,
        data: result,
        timestamp: new Date().toISOString(),
      };
    } catch (error) {
      return {
        success: false,
        error: {
          code: 'CREATE_BRANCH_ERROR',
          message: 'Failed to create branch',
          details: error instanceof Error ? error.message : String(error),
        },
        timestamp: new Date().toISOString(),
      };
    }
  }

  /**
   * Cria um commit
   */
  async createCommit(
    message: string,
    author?: { name: string; email: string },
    filePaths?: string[]
  ): Promise<AdapterResponse<CreateCommitResult>> {
    try {
      if (!message || message.trim().length === 0) {
        return {
          success: false,
          error: {
            code: 'INVALID_MESSAGE',
            message: 'Commit message cannot be empty',
          },
          timestamp: new Date().toISOString(),
        };
      }

      const repo = await this.openRepository();
      const index = await repo.refreshIndex();

      // Adicionar arquivos específicos ao staging area
      if (filePaths && filePaths.length > 0) {
        await index.addByPath(...filePaths);
      } else {
        // Adicionar todos os arquivos modificados
        await index.addAll();
      }

      // Escrever o index
      await index.write();

      // Obter HEAD
      const headCommit = await repo.getHeadCommit();

      // Criar signature (autor)
      const signature = author
        ? nodegit.Signature.create(author.name, author.email, Date.now() / 1000, 0)
        : nodegit.Signature.create('Codex Hub', 'codex@manta.local', Date.now() / 1000, 0);

      // Criar o commit
      const parentCommits = headCommit ? [headCommit] : [];
      const treeId = await index.writeTree();
      const tree = await repo.getTree(treeId);

      const commitHash = await repo.createCommit(
        'HEAD',
        signature,
        signature,
        message,
        tree,
        parentCommits.length > 0 ? parentCommits : undefined
      );

      // Obter informações do commit criado
      const newCommit = await repo.getCommit(commitHash);

      const result: CreateCommitResult = {
        commitHash: newCommit.sha(),
        message: newCommit.message().trim(),
        author: {
          name: newCommit.author().name(),
          email: newCommit.author().email(),
        },
        timestamp: newCommit.timeMs() / 1000,
        filesChanged: filePaths?.length || 0,
      };

      return {
        success: true,
        data: result,
        timestamp: new Date().toISOString(),
      };
    } catch (error) {
      return {
        success: false,
        error: {
          code: 'CREATE_COMMIT_ERROR',
          message: 'Failed to create commit',
          details: error instanceof Error ? error.message : String(error),
        },
        timestamp: new Date().toISOString(),
      };
    }
  }

  /**
   * Cria um pull request (requer integração com GitHub API)
   */
  async createPullRequest(
    title: string,
    baseBranch: string,
    headBranch: string,
    description?: string,
    githubToken?: string
  ): Promise<AdapterResponse<CreatePullRequestResult>> {
    try {
      if (!title || title.trim().length === 0) {
        return {
          success: false,
          error: {
            code: 'INVALID_TITLE',
            message: 'PR title cannot be empty',
          },
          timestamp: new Date().toISOString(),
        };
      }

      if (!baseBranch || !headBranch) {
        return {
          success: false,
          error: {
            code: 'INVALID_BRANCHES',
            message: 'Both base and head branches are required',
          },
          timestamp: new Date().toISOString(),
        };
      }

      const repo = await this.openRepository();

      // Verificar se as branches existem
      try {
        await repo.getBranch(baseBranch);
        await repo.getBranch(headBranch);
      } catch (error) {
        return {
          success: false,
          error: {
            code: 'BRANCH_NOT_FOUND',
            message: `One or more branches not found`,
            details: error instanceof Error ? error.message : String(error),
          },
          timestamp: new Date().toISOString(),
        };
      }

      // Obter URL do remote
      let remoteUrl: string | undefined;
      try {
        const remote = await repo.getRemote('origin');
        remoteUrl = remote.url();
      } catch {
        // Remote não configurado
      }

      if (!remoteUrl || !githubToken) {
        // Retornar resultado pendente se não houver credenciais
        const result: CreatePullRequestResult = {
          title,
          baseBranch,
          headBranch,
          status: 'pending',
          message:
            'GitHub token not provided. PR creation requires GitHub API integration.',
        };

        return {
          success: true,
          data: result,
          timestamp: new Date().toISOString(),
        };
      }

      // Extrair owner/repo de remoteUrl
      const repoMatch = remoteUrl.match(/github\.com[:/]([^/]+)\/(.+?)(\.git)?$/);
      if (!repoMatch) {
        return {
          success: false,
          error: {
            code: 'INVALID_REMOTE_URL',
            message: 'Could not parse GitHub repository URL',
            details: `Remote URL: ${remoteUrl}`,
          },
          timestamp: new Date().toISOString(),
        };
      }

      const [, owner, repo_name] = repoMatch;
      const repoNameClean = repo_name.replace(/\.git$/, '');

      // Criar PR via GitHub API
      try {
        const response = await fetch(`https://api.github.com/repos/${owner}/${repoNameClean}/pulls`, {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${githubToken}`,
            'Accept': 'application/vnd.github.v3+json',
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            title,
            body: description || '',
            base: baseBranch,
            head: headBranch,
            draft: false,
          }),
        });

        if (!response.ok) {
          const errorData = await response.json() as { message?: string };
          return {
            success: false,
            error: {
              code: 'GITHUB_API_ERROR',
              message: 'Failed to create pull request via GitHub API',
              details: errorData.message || `HTTP ${response.status}`,
            },
            timestamp: new Date().toISOString(),
          };
        }

        const prData = await response.json() as { number?: number; html_url?: string };
        const result: CreatePullRequestResult = {
          number: prData.number,
          url: prData.html_url,
          title,
          baseBranch,
          headBranch,
          status: 'created',
          message: `Pull request created successfully`,
        };

        return {
          success: true,
          data: result,
          timestamp: new Date().toISOString(),
        };
      } catch (error) {
        return {
          success: false,
          error: {
            code: 'PR_CREATION_ERROR',
            message: 'Failed to create pull request',
            details: error instanceof Error ? error.message : String(error),
          },
          timestamp: new Date().toISOString(),
        };
      }
    } catch (error) {
      return {
        success: false,
        error: {
          code: 'CREATE_PR_ERROR',
          message: 'Failed to process pull request creation',
          details: error instanceof Error ? error.message : String(error),
        },
        timestamp: new Date().toISOString(),
      };
    }
  }
}

/**
 * Funções exportadas para uso direto
 */

/**
 * Obtém o estado do repositório Git
 */
export async function get_git_state(
  repoPath: string = '.'
): Promise<AdapterResponse<GitState>> {
  const adapter = new GitAdapter(repoPath);
  return adapter.getGitState();
}

/**
 * Cria uma nova branch
 */
export async function create_branch(
  repoPath: string,
  branchName: string,
  fromCommitHash?: string
): Promise<AdapterResponse<CreateBranchResult>> {
  const adapter = new GitAdapter(repoPath);
  return adapter.createBranch(branchName, fromCommitHash);
}

/**
 * Cria um commit
 */
export async function create_commit(
  repoPath: string,
  message: string,
  author?: { name: string; email: string },
  filePaths?: string[]
): Promise<AdapterResponse<CreateCommitResult>> {
  const adapter = new GitAdapter(repoPath);
  return adapter.createCommit(message, author, filePaths);
}

/**
 * Cria um pull request
 */
export async function create_pull_request(
  repoPath: string,
  title: string,
  baseBranch: string,
  headBranch: string,
  description?: string,
  githubToken?: string
): Promise<AdapterResponse<CreatePullRequestResult>> {
  const adapter = new GitAdapter(repoPath);
  return adapter.createPullRequest(title, baseBranch, headBranch, description, githubToken);
}
