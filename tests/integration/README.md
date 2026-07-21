# Integration tests

**Role.** This folder verifies interactions between domain ports and concrete adapters.

## Structure

- `test_sqlite_outbox.py` covers durable action persistence and restart recovery.

## Should contain

- Tests using temporary local resources and deterministic provider fakes.

## Should not contain

- Real provider accounts, credentials, or personal data.

## Rules

- Simulate failures without network access.
- Verify recovery and idempotence across adapter re-instantiation.
