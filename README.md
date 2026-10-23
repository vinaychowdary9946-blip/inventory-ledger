# Inventory Ledger

Duplicate shipment commands, concurrent operators, and overwritten stock counts make inventory hard to trust. This project records signed stock events and rebuilds quantity from history.

Independent engineering project built around realistic failure scenarios. Examples use synthetic data; no customer deployment or commercial impact is claimed.

**[Live interactive demo](https://vinaychowdary9946-blip.github.io/demos/inventory-ledger/)** · [Architecture](docs/ARCHITECTURE.md) · [API guide](docs/API.md) · [Verification](docs/VERIFICATION.md)

## What it does

Append-only application writes; per-SKU versions; idempotent command IDs; negative-stock rejection; transactional concurrency checks; compensating events; JSON event export.

## Run locally

Requires Python 3.10+; no pip installation, paid service, or API key is required. From this repository directory:

```sh
python ledger.py adjust --command receipt-001 --sku SENSOR-01 --delta 20 --version 0 --reason receipt
python ledger.py adjust --command shipment-001 --sku SENSOR-01 --delta -7 --version 1 --reason shipment
python ledger.py state --sku SENSOR-01
python ledger.py events
python -m unittest discover -s tests -v
python server.py
```

Open http://127.0.0.1:8000 for the browser simulation. The local server also exposes POST /api for the actual Python engine; see [API examples](docs/API.md). The visual simulation is deliberately separate from the backend and keeps its data in browser memory. Reloading clears it. SQLite files persist local API and CLI data across restarts.

## Repository map

- `ledger.py` — domain implementation and CLI
- `server.py` — loopback development server and JSON API
- `web/` — interactive browser simulation, no dependencies
- `tests/` — domain, concurrency, and HTTP tests
- `examples/` — reproducible inputs
- `docs/` — architecture, API contracts, research, validation, and operations

## Engineering boundaries

Single-location integer inventory only: no reservations, transfers, monetary accounting, authentication, or external ERP integration. History is append-only through this API, but a database administrator can still edit it; this is not tamper-proof storage. Quantity is computed from events at read time; high-volume streams need snapshots or projections. Corrections append a compensating event.

## Development

Run tests from the repository root. GitHub Actions is configured for Python 3.10, 3.12, and 3.13 on Linux and Windows. Local validation and hosted CI results are reported separately in the verification guide.

MIT license. Contributions should include a reproducible failing scenario and a regression test.
