# Local adapters

**Role.** This package provides offline adapters backed by local machine facilities.

## Structure

- `sqlite_outbox.py` provides durable and idempotent action persistence.

## Should contain

- SQLite, filesystem, and operating-system implementations of application ports.

## Should not contain

- Provider credentials or remote business logic.

## Rules

- Migrations must be transactional and restart-safe.
- Database paths are injected by the composition root.
