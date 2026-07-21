# Domain tests

**Role.** This folder verifies pure offline-first business models and rules.

## Structure

- `test_idempotency.py` verifies stable action identity.
- `test_outbox.py` verifies model invariants and lifecycle transitions.

## Should contain

- Fast deterministic tests that require no filesystem, network, database, or Qt event loop.

## Should not contain

- Adapter or UI integration tests; place those in their dedicated test areas.

## Rules

- Test public behavior and invalid transitions explicitly.
