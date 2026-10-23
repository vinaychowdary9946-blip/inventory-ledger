# Architecture and decisions

## Use case

Duplicate shipment commands, concurrent operators, and overwritten stock counts make inventory hard to trust. This project records signed stock events and rebuilds quantity from history.

## Core design

An immediate write transaction reads the SKU version and balance, rejects a stale version or a negative result, then inserts one event. A globally unique command ID makes retry delivery idempotent and rejects semantic key reuse. A unique (sku, version) constraint reinforces ordering. Current state is a SUM(delta) and event count, so it can be reconstructed without a separate mutable stock table.

## Tradeoffs

Single-location integer inventory only: no reservations, transfers, monetary accounting, authentication, or external ERP integration. History is append-only through this API, but a database administrator can still edit it; this is not tamper-proof storage. Quantity is computed from events at read time; high-volume streams need snapshots or projections. Corrections append a compensating event.

## Runtime boundaries

The Python engine is the durable implementation. The browser simulation demonstrates the same domain concepts with synthetic data and an in-memory clock or event list; it is not a hosted distributed service. POST /api exposes Python behavior locally. The development server binds to loopback only and rejects foreign browser origins. It has no authentication, rate limiting, TLS, or service manager: do not expose it directly to the internet.

## Operational considerations

Keep databases on local disks and back up with SQLite's backup API or a controlled shutdown; do not copy an active database without its WAL state. Test restoration before relying on backups. Do not write credentials or personal data into example payloads. For a public deployment, place an authenticated application server behind TLS, implement request quotas, structured logs, monitoring and access controls, and exercise recovery under load. No production throughput or SLA is claimed.
