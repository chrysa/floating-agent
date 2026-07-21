# Architecture decision records

**Role.** This folder records structural decisions for floating-agent that require
explicit hypotheses, validation gates, and reversal criteria.

## Structure

- `0004-offline-first-hexagonal-core.md` defines the Debian beta architecture.

## Should contain

- Decisions that change architecture, external dependencies, public contracts, or
  persisted data models.

## Should not contain

- Implementation notes or user guides; place those in the relevant documentation
  section instead.

## Rules

- Keep records in English and number them consistently with `DECISIONS.md`.
- Every record must include one fatal hypothesis, a measurable kill-test, and a
  validation gate.
- Accepted records are immutable; supersede them with a new record.
