# Engineering research

Reviewed 2026-10-23. These references inform design decisions; the project implementation is original, not copied source code.

## Primary references

- https://martinfowler.com/eaaDev/EventSourcing.html
- https://www.sqlite.org/lang_transaction.html
- https://www.sqlite.org/wal.html

## Application to this project

An immediate write transaction reads the SKU version and balance, rejects a stale version or a negative result, then inserts one event. A globally unique command ID makes retry delivery idempotent and rejects semantic key reuse. A unique (sku, version) constraint reinforces ordering. Current state is a SUM(delta) and event count, so it can be reconstructed without a separate mutable stock table.

## What this does not establish

Using an established pattern does not establish novelty, production readiness, or measured business impact. Tests validate bounded scenarios, not every operating condition. All examples are synthetic. The browser implementation and Python implementation run in different environments and are documented separately.
