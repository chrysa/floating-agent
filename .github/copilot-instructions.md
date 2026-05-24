# floating-agent — GitHub Copilot Instructions

## Mandatory Workflow

1. Read `.github/instructions/*.instructions.md` when present.
2. Read `CLAUDE.md` for repository context.
3. Follow repository-local conventions before writing code.

## Project Context

**Stack:** Python daemon (`daemon/`) · Electron + Node.js UI (`electron/`, `ui/`)
**Purpose:** Floating multi-OS AI assistant — keyboard-triggered overlay providing AI assistance across any application.

## Engineering Rules

- Write in English: code, comments, docs, issues, PRs and commits.
- Keep changes minimal and aligned with the existing style.
- Do not add unrelated refactors or speculative improvements.
- Prefer make targets when available instead of invoking tooling ad hoc.
- Never commit secrets, credentials or environment-specific values.

## Automation & Industrialization (NON-NEGOTIABLE)

- Projects must be **maximally automated and industrialized**.
- Every repetitive task must be covered by one of: CI/CD pipeline, Makefile target, pre-commit hook, GitHub Actions workflow, or a bot/script.
- Required automation baseline for any project:
  - **CI/CD**: automated lint, type-check, tests, build on every push/PR.
  - **Formatting**: auto-applied via pre-commit or CI (no manual `ruff`/`prettier` runs).
  - **Releases**: automated versioning and changelog generation (e.g. `cliff`, `semantic-release`).
  - **Dependency updates**: automated via Dependabot or Renovate.
  - **Secret scanning**: automated on every commit (pre-commit hook + CI step).
- When proposing or implementing a feature, always include the automation layer (tests, CI step, Makefile target) — not just the code.
- Any manual step that could be automated is considered **technical debt** and must be tracked.

## Canonical Templates & Shared Tooling

### Makefiles

- All project Makefiles **must** extend or be derived from `Forge-Stack-Workshop/base-makefile`.
- Do not duplicate targets that already exist in the base — inherit instead.

### Pre-commit hooks

- If a required hook is missing from `chrysa/pre-commit-tools`, **open an issue** on that repo describing the hook needed before proceeding.
- In the requesting repo, open a matching issue/PR and mark it as dependent (`Depends on chrysa/pre-commit-tools#<N>`).
- Do not implement a workaround locally — wait for the hook to land in the shared repo.

## Claude Interoperability

- This repository is also prepared for Claude Code via `.claude/` and `CLAUDE.md`.
- Claude skills are available under `.claude/skills/` for relevant tasks.
- If a task has repository instructions, those instructions override generic defaults.

## Quality Thresholds

- Max function length: 50 lines when practical.
- Max file length: 500 lines when practical.
- Max cyclomatic complexity: 10.
- Lint warnings target: 0.
