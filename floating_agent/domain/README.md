# Domain

**Role.** This package contains pure business models and rules for the offline-first
assistant. It is independent from UI, storage, networking, and provider SDKs.

## Structure

- `connectivity_state.py` defines application connectivity states.
- `calendar_event.py` defines inspectable calendar event content.
- `communication_message.py` defines inspectable communication content.
- `outbox_item.py` defines the durable remote-action record.
- `outbox_status.py` defines its lifecycle states.
- `outbox_transition.py` validates lifecycle transitions.
- `idempotency.py` derives stable action keys.

## Should contain

- Immutable models, enums, and deterministic business rules.

## Should not contain

- Qt, FastAPI, SQLite, filesystem, HTTP, keyring, or provider-specific imports.

## Rules

- Keep functions deterministic and independently testable.
- Keep one class per module.
- Adapters translate external data into these domain types.
