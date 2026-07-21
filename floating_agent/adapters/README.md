# Adapters

**Role.** This package implements ports using local operating-system or remote-provider facilities.

## Structure

- `local/` contains offline adapters such as SQLite persistence.

## Should contain

- Translation and I/O code behind contracts from `floating_agent.ports`.

## Should not contain

- Business lifecycle rules or Qt widgets.

## Rules

- Provider failures must remain isolated.
- Never persist plaintext credentials or log complete sensitive content.
