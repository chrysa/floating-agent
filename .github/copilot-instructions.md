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

## Canonical Templates & Shared Tooling

### Makefiles

- All project Makefiles **must** extend or be derived from `Forge-Stack-Workshop/base-makefile`.
- Do not duplicate targets that already exist in the base — inherit instead.

### Pre-commit hooks

- If a required hook is missing from `chrysa/pre-commit-tools`, **open an issue** on that repo describing the hook needed before proceeding.
- In the requesting repo, open a matching issue/PR and mark it as dependent (`Depends on chrysa/pre-commit-tools#<N>`).
- Do not implement a workaround locally — wait for the hook to land in the shared repo.
