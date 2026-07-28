# Local adapters

**Role.** This package provides offline adapters backed by local machine facilities.

## Structure

- `sqlite_outbox.py` provides durable and idempotent action persistence.
- `docker_cli_monitor.py` translates bounded Docker lifecycle events.
- `eml_importer.py` imports local RFC 5322 messages without OAuth.
- `ics_importer.py` imports local ICS calendar snapshots without OAuth.
- `json_importer.py` imports local communication snapshots without OAuth.

## Should contain

- SQLite, filesystem, and operating-system implementations of application ports.

## Should not contain

- Provider credentials or remote business logic.

## Rules

- Migrations must be transactional and restart-safe.
- Database paths are injected by the composition root.
