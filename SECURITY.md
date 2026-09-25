# SECURITY — floating-agent

> Tags: FACT / INFERENCE / UNKNOWN. Secrets are never copied here — only their nature and
> location. No HIGH/CRITICAL finding requiring code change was identified during this
> docs-only pass.

## Secret management (FACT)

- `secret_store.py::SecretStore` resolves named secrets **OS keychain (keyring) first, then
  environment variable** of the same name. Design guarantee: "no plaintext secrets on disk".
- Keychain read tolerates a missing backend (`KeyringError` → `None`), enabling headless/CI.
- Secrets referenced (names only): `AI_AGGREGATOR_URL`, `NOTION_API_KEY`, `NOTION_TASKS_DB_ID`,
  `CALENDAR_ACCESS_TOKEN`, `GMAIL_ACCESS_TOKEN`.
- **No hardcoded secrets found** in `floating_agent/` or `tests/` (pattern scan negative).

## Agent safety controls (FACT — `agent/loop.py`)

- Tools flagged `requires_confirmation=True` (e.g. writes) are **denied by default** and run
  only when an explicit confirmation callback approves them. A model tool-call alone cannot
  trigger a real write.
- The loop is bounded by `MAX_STEPS`; unknown tool names return an error rather than executing.

## Network exposure (FACT)

- Optional FastAPI layer binds `127.0.0.1:34001` only; CORS restricted to
  `http://localhost:5173`, credentials off, methods `GET`/`POST`. Documented as "never exposed
  externally".
- Notion client pins API version `2022-06-28`; HTTPS endpoints for all external calls.

## Logging posture (FACT — README "Security")

- AI calls logged as provider + timestamp, **no content**.
- OAuth tokens stated as never logged.

## Repo hygiene / guardrails (FACT)

- Dedicated CI: `secret-scan.yml`, `quality-gate-check.yml`, `pre-commit.yml`, `sonar.yml`,
  `mutation-testing.yml`.
- Local hookify guards: block dangerous `rm`, block `.env` edits, block lockfile edits.

## Open items / to verify (UNKNOWN)

- Whether `ReminderStore` persists to disk (and if so, its contents' sensitivity) — no
  persistence layer was observed in read modules.
- OAuth flow implementation details for calendar/messaging tokens (refresh, storage lifetime).
- Runtime confirmation-callback wiring in the overlay (that a callback is actually installed for
  sensitive tools at runtime).

No HIGH/CRITICAL finding is asserted; the above are verification gaps, not confirmed
vulnerabilities.
