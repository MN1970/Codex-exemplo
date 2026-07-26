# SKILL.md — git-commit-optimizer

**Version:** 1.0.0  
**Tier:** Sonnet  
**Model:** claude-3-5-sonnet-20241022  
**Status:** ✅ Operacional  
**Channels:** Bash (git), MCP  
**Created:** 2026-07-26

---

## Overview

Optimize commit history via semantic rebase—squash, reword, or drop commits to clean up messy branches before merging. Outputs a before/after ASCII tree visualization and a safe rebase script for review.

**Use this skill when:**
- The current branch has redundant, fixup, or work-in-progress commits
- You need to clean up history before a PR or merge to main
- You want to restructure commits to match semantic commit standards
- Multiple commits should be squashed into a single logical change

---

## Inputs

| Input | Type | Required | Notes |
|-------|------|----------|-------|
| Base branch | string | Yes | Branch to rebase onto (usually `main`, `develop`, or `HEAD~N`) |
| Interactive plan | JSON | Optional | Explicit list of actions: `{commit_hash: "drop"\|"squash"\|"reword"\|"keep", new_message?: string}` |
| Auto-detect | boolean | No | If true, detect fixup/squash commits by subject pattern (default: false) |

---

## Outputs

1. **ASCII tree (before)** — Visual diff of commit history
   ```
   * abc1234 (HEAD) fix: typo in README
   * def5678 chore: cleanup console logs
   * ghi9012 feat: add user auth
   |/
   * jkl3456 (main) initial commit
   ```

2. **ASCII tree (after)** — Expected state post-rebase
   ```
   * new_hash feat: add user auth
   |/
   * jkl3456 (main) initial commit
   ```

3. **Rebase script** — Executable git rebase command with actions
   ```bash
   git rebase -i main --autostash
   # pick abc1234 feat: add user auth
   # squash def5678 chore: cleanup console logs
   # squash ghi9012 fix: typo in README
   ```

4. **Dry-run report** — Validation summary: commit count delta, safety checks

---

## Prerequisites

- Current directory: git repository root
- Unstaged changes: must be clean or will be auto-stashed
- Base branch: exists and is reachable
- User has reviewed the before/after tree and approved the plan

---

## Safety & Permissions

### IMPORTANT: Force-Push Approval Required

This skill **will not push** without explicit user approval. However, **after the rebase completes**, a force-push to the remote branch will be necessary to apply the rewritten history:

```bash
git push --force-with-lease origin <branch>
```

**This action is destructive** if the remote has other contributors. The skill:
- Always outputs a dry-run first (no changes to disk)
- Requires the user to manually apply the rebase (`git rebase` command shown)
- Requires explicit approval before any `git push --force*`
- Uses `--force-with-lease` (safer than `--force`) when approved

### Conditions for approval

Force-push is approved **only if:**
1. This is a personal feature branch (not `main`, `develop`, or a shared branch)
2. No other contributors have commits on this branch since the last push
3. The user has explicitly reviewed the before/after trees
4. The user has tested the rebase locally with `git rebase` first

---

## How It Works

1. **Parse base branch** — Find merge-base between current branch and base
2. **Build action plan** — Scan commits since merge-base:
   - Auto-detect fixups (commits with `fixup!` or `squash!` prefix)
   - Apply user-provided rewording rules
   - Mark drops (e.g., debugging commits)
3. **Visualize** — Render ASCII before/after trees
4. **Generate rebase script** — Output `git rebase -i` command with actions
5. **Dry-run validation** — Check for merge conflicts, orphaned refs, etc.
6. **Await user approval** — Display full plan; do not auto-apply

---

## Example Usage

### Scenario 1: Squash fixups automatically

```
User prompt: "Clean up my feature branch, squash all fixup commits"

Skill detects:
  * abc1234 feat: add login form
  * def5678 fixup! add login form
  * ghi9012 fixup! add login form

Outputs:
  Before tree:  3 commits
  After tree:   1 commit
  Script:
    git rebase -i main --autostash
    pick abc1234 feat: add login form
    squash def5678 fixup! add login form
    squash ghi9012 fixup! add login form
```

### Scenario 2: Reword and drop

```
User prompt: "Reword the first commit to 'feat: user authentication' and drop the debug commit"

Outputs:
  Script:
    git rebase -i main --autostash
    reword abc1234 feat: add login form
    [editor opens: change to "feat: user authentication"]
    drop def5678 debug: console logs
    pick ghi9012 chore: update styles
```

### Scenario 3: Manual plan via JSON

```json
{
  "base_branch": "main",
  "actions": {
    "abc1234": "keep",
    "def5678": "squash",
    "ghi9012": "reword",
    "new_message": "chore: refactor auth module"
  }
}
```

---

## Related Skills & Tools

- **simplify** — Code review & cleanup (post-rebase)
- **review** — Full PR code review before merge
- **Bash** (`git` commands) — Execute the rebase manually
- **DesignSync** — Coordinate if rebasing affects design/artifact branches

---

## Limitations

- Does not handle rebases with **merge commits** (converted to squash)
- Cannot rebase if **submodules** are present (manual intervention required)
- Dry-run does not detect all **merge conflict scenarios** (local test advised)
- Does not reorder commits (only squash, reword, drop, keep)

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| "Unstaged changes" error | Run `git stash` first, then invoke skill; auto-stash will restore |
| Merge conflicts during rebase | Skill will pause; resolve conflicts, then `git rebase --continue` |
| Force-push rejected | Ensure no other contributors pushed since your last pull |
| Wrong commits squashed | Abort with `git rebase --abort` and restart with revised plan |

---

## Changelog

- **v1.0.0** (2026-07-26) — Initial release. Supports squash, reword, drop, keep actions; ASCII tree visualization; dry-run validation; force-push safety gate.
