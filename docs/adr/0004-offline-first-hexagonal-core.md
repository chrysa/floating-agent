# ADR 0004 — Offline-first hexagonal application core

- **Date:** 2026-07-21
- **Status:** Accepted
- **Owners:** floating-agent maintainers

## Context

The existing application is a single Python process with a PySide6 overlay, an agent
loop, and concrete plugins. It starts without the remote AI aggregator by using a
stub, but mail, calendar, communications, reminders, and actions have no durable
offline model. Concrete provider clients are also reachable directly from the tool
registry, so remote writes cannot yet be governed by one confirmation and audit path.

The Debian beta must remain useful without a network connection and must not duplicate
AI routing, portfolio management, or provider-specific business applications.

## Decision

Keep the single-process PySide6 architecture and introduce explicit hexagonal
boundaries inside it:

```text
PySide6 UI
    ↓
Application services
    ↓
Offline domain core
    ↓
Provider-agnostic ports
    ↓
Local, operating-system, AI, and remote adapters
```

The domain contains connectivity states, content models, drafts, action proposals,
permissions, audit metadata, and Outbox state transitions. It performs no filesystem,
database, network, Qt, FastAPI, keyring, or provider SDK I/O.

Application services orchestrate `IntentRouter`, `ActionProposalEngine`, `SyncEngine`,
and `ConflictResolver`. Every remote mutation follows one workflow: inspectable
proposal, explicit confirmation, durable Outbox insertion, idempotent execution, and
an explicit result.

Ports define `PlatformCapabilities`, `ConnectivityMonitor`, `LocalStore`,
`LocalSearchIndex`, `Outbox`, `AuditLog`, `PermissionManifest`, `MailAdapter`,
`CalendarAdapter`, `CommunicationAdapter`, `PortfolioVisualizerAdapter`, and
`AIExecutionAdapter`. No port imports Gmail, Google Calendar, Slack, Notion, Ollama,
Qt, FastAPI, or HTTP client types.

Adapters initially include SQLite storage and search, local EML/ICS/JSON importers,
in-memory demo providers, OS/keyring integration, and wrappers around existing clients.
Remote provider writes remain disabled until they use the confirmed Outbox workflow.

## Data and security constraints

- SQLite stores cached content and Outbox records, never plaintext credentials.
- Credentials use the operating-system keyring through an adapter.
- Logs store identifiers and redacted metadata, not complete sensitive content.
- Account disconnection, credential revocation, cache removal, Outbox clearing, and
  audit-history removal are separate operations.
- Persisted personal data must be exportable in an open format.

## Consequences

- Existing plugins remain usable through compatibility adapters during migration.
- The UI can render cached content and drafts independently of provider availability.
- Provider failures degrade independently instead of collapsing the whole application.
- More interfaces and composition code are required, and SQLite migrations become a
  maintained compatibility surface.

## Alternatives rejected

- A second background daemon would add IPC and lifecycle complexity before the beta
  demonstrates a need for process isolation.
- Direct SDK calls from widgets or tools would bypass confirmation and offline recovery.
- Reimplementing AI routing locally would duplicate `ai-aggregator` responsibilities.

## Fatal hypothesis

A single-process SQLite-backed core can keep confirmed action persistence and UI
interaction responsive under the Debian beta workload.

## Kill-test

Before beta promotion, run 1,000 queued fixture actions while the overlay remains open.
The decision fails if a UI interaction blocks for more than 200 ms, an action is lost
or executed twice after a forced restart, or SQLite remains locked for more than five
seconds. A failure triggers an ADR evaluating a dedicated worker process.

## Validation gate

Proceed to remote write adapters only after automated tests prove offline startup,
draft persistence, confirmed Outbox insertion, crash recovery without duplicate
execution, and independent degraded provider states.
