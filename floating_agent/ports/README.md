# Ports

**Role.** This package defines provider-agnostic contracts consumed by application services.

## Structure

- `outbox.py` defines durable action persistence operations.

## Should contain

- Protocols expressed with floating-agent domain types.

## Should not contain

- SQLite, Qt, FastAPI, HTTP, keyring, or provider SDK imports.

## Rules

- Keep one protocol per module.
- Adapters implement ports; domain code never imports adapters.
