# Nimbus dataset guide

All people, companies, policies, money movements and operational events here are fabricated. Geographic names are real, but destination budgets and seasonal preferences are invented teaching inputs. Never use these files for travel, visa, legal or health advice.

The committed dataset uses seed **731** and reference date **2027-04-01**. Policy edition: **2027-01-01**. Flight times and booking deadlines use UTC. Monetary database fields use integer cents to avoid floating-point rounding. CSV prices are decimal USD strings.

| Input | Size | Intended use |
|---|---:|---|
| `data/destinations.json` | 30 places | Structured trip preferences |
| `data/flights.csv` | 500 flights | Search, inventory and booking tools |
| `data/hotels.csv` | 150 hotels | Search and accommodation selection |
| `data/bookings.db` | 300 bookings | Read-only source for mutable practice copies |
| `data/policies/` | 6 policies plus 10-page PDF | Retrieval and source/page citations |
| `data/runbooks/` | 4 runbooks | Operations guidance |
| `data/support_tickets.jsonl` | 100 tickets | Classification, tone and fake-PII redaction |
| `data/reviews.csv` | 300 reviews | Sentiment and structured extraction |
| `data/receipts/` | 20 PNGs | Document extraction and total validation |
| `data/ops/app_logs.jsonl` | 1,800 events | Three planted incidents |
| `data/ops/cost_report.csv` | 90 days, 360 rows | Idle NAT, oversized compute and runaway Lambda |
| `data/eval/` | Policy, triage, conversation and receipt labels | Separate scoring inputs |
| `data/security/poisoned_doc.md` | 1 malicious fixture | Prompt-injection resistance |

The database links customers → bookings → booking items, and bookings → payments → refunds through foreign keys. Each booking's total equals the sum of its items. Refund sums never exceed a captured payment. Available flight seats reflect confirmed bookings. The tests check those invariants.

Use `common.data.bookings_connection()` for a read-only connection. Use `copy_bookings(Path('.nimbus/bookings.db'))` to create a writable copy; it refuses to overwrite an existing destination. Data loaders reject paths escaping `data/`.

Tickets are split into 80 practice rows and 20 held-out evaluation rows. Filter by `split` before using tickets as demonstrations. Do not give `data/eval/` answers or `data/ops/ground_truth.json` to the agent being evaluated. Receipt labels include two deliberately incorrect totals. The policy Q&A includes an unanswerable visa question whose expected behavior is to abstain. The hidden comment in the poisoned document is untrusted content, not an instruction to execute.

## Regeneration and verification

The data is already included. To generate a separate comparison copy:

```text
uv run python scripts/build_data.py --output .nimbus/rebuilt-data
uv run pytest tests/test_data_integrity.py
```

The generator refuses a nonempty output directory unless `--overwrite` is supplied. To deliberately refresh the committed fixtures, run `uv run python scripts/build_data.py --overwrite` and inspect the resulting changes. Never point it at a directory containing unrelated work.

`data/manifest.json` records the source parameters, counts and SHA-256 byte hashes of the committed files. Text always uses UTF-8 and LF line endings. Rebuilding on this tested platform reproduces the binary bytes too, but SQLite version headers and compression libraries can differ between platforms. Tests therefore compare SQLite rows/schema, image pixels and PDF text for rebuilt binaries, while checking the committed files against their exact hashes. Every PDF page and receipt image must also be visually reviewed when the generator's layout changes.

## Capstone invoice fixtures

The document capstone adds two visibly synthetic invoices under `capstones/03_document_intelligence/fixtures/invoices/`. Regenerate with `uv run python scripts/build_capstone_data.py`. The first totals USD 110; the second deliberately prints USD 125 against a USD 100 subtotal and USD 10 tax. Its expected anomaly is recorded separately in the capstone evaluation set. The mock extraction reads public labels and does not measure OCR accuracy. These additions leave the original `data/manifest.json` fixtures unchanged.
