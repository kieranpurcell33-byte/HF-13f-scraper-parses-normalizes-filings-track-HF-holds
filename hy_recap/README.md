# `hy_recap` — US High Yield Daily Recap

Generates a pre-market recap of the prior US high-yield session — notable
events, best/worst credit-specific bond moves, and the next-day outlook —
rendered as Markdown into `reports/YYYY-MM-DD_US_HY_Daily_Recap.md`.

The pipeline is built around one rule: **it never fabricates.** Any figure it
cannot source is left blank and the gap is recorded as an explicit warning in
the report's *Data Provenance* section. A missing number is reported as missing.

---

## Quick start

```bash
pip install -r hy_recap/requirements.txt

# Previous business day, live feeds, write to ./reports
export FRED_API_KEY=xxxxxxxx            # free: https://fred.stlouisfed.org/docs/api/api_key.html
python -m hy_recap

# Backfill a specific session, supplying the editorial narrative
python -m hy_recap --session-date 2026-08-10 --delivery-date 2026-08-11 \
                   --narrative hy_recap/sample_narrative.json
```

## What comes from where

| Section | Source | Notes |
|---|---|---|
| HY OAS, HY yield, UST 10Y/30Y, WTI | **FRED** (`FRED_API_KEY`) | `sources/fred.py`. Day-over-day change computed from the two latest prints. |
| UST 10Y/30Y fallback | **US Treasury FiscalData** (public) | `sources/treasury.py`. Fills gaps if FRED is down. |
| Best/worst named bonds | **FINRA TRACE** (`FINRA_API_CLIENT_ID/SECRET`) | `sources/trace.py`. Populates only if the dataset carries per-CUSIP price/spread changes; otherwise the section renders a template. |
| Notable events / outlook | **Editorial / LLM** (`--narrative`) | Not inferable from price feeds — supplied as JSON (see `sample_narrative.json`). |

### On security-level movers (the honest bit)

Naming the single best/worst bond of the day with real prices needs an
entitled **TRACE** data product or a commercial feed (**ICE**, **S&P/Markit**,
**Bloomberg**). The free FINRA API surfaces breadth/volume summaries, not
per-CUSIP daily returns. Plug a vendor in by implementing one method
(`fetch_movers`) against `sources/base.SecurityMoversSource` — the generator and
report format need no changes.

### Editorial level overrides

For days a live feed is unreachable (or to pin a triangulated level), a
narrative JSON may include a `levels` array. These **fill only gaps** the live
sources didn't cover, and their use is flagged in the report as
"editor-supplied … not live terminal marks." See `sample_narrative.json`.

---

## Automation — delivering every weekday before 07:15 AM ET

Two mechanisms, complementary:

### 1. GitHub Actions (in-repo, deterministic) — `.github/workflows/hy-recap.yml`

Runs 10:15 UTC Mon–Fri (≈05:15–06:15 ET across DST), builds the data-driven
report from FRED/Treasury/TRACE and commits it to `reports/`. Configure repo
**Secrets**: `FRED_API_KEY`, and optionally `FINRA_API_CLIENT_ID` /
`FINRA_API_CLIENT_SECRET`. Active once this workflow is on the default branch.

> Note: GitHub's scheduled runs can lag under load; the 10:15 UTC slot leaves a
> buffer before 07:15 ET. Also handles DST automatically since it's pinned to UTC.

### 2. Scheduled Claude session (full narrative) — recommended for the news/outlook

The events and outlook need research + synthesis a plain cron can't do. Run a
weekday-morning Claude session (a Routine / scheduled trigger) that:

1. researches the prior session's HY news and forward calendar,
2. writes a `narrative.json` (events, outlook, sources, and — if feeds are down —
   `levels`),
3. runs `python -m hy_recap --narrative narrative.json --email`, and
4. commits the report.

Example cron for ~06:45 ET (10:45 UTC): `45 10 * * 1-5`.

## Email delivery

Both automations email the recap when the `--email` flag is passed and SMTP
secrets are configured (see `delivery.py`). Delivery is self-contained SMTP — no
external connector required:

| Var | Meaning |
|---|---|
| `SMTP_HOST` | e.g. `smtp.gmail.com` |
| `SMTP_PORT` | `587` (STARTTLS, default) or `465` (with `SMTP_USE_SSL=1`) |
| `SMTP_USER` / `SMTP_PASSWORD` | login (use an app password for Gmail) |
| `EMAIL_FROM` | from address (defaults to `SMTP_USER`) |
| `EMAIL_TO` | comma-separated recipients (required to send) |

If any required var is missing, delivery is skipped with a logged reason — it
never breaks report generation. The email is multipart: a rendered HTML body
plus a plain-text (raw Markdown) fallback.

```bash
python -m hy_recap --narrative narrative.json --email
```

---

## Tests

```bash
python -m pytest tests/test_hy_recap.py -q
```

All tests are hermetic (no network) — sources are faked — and assert the
non-fabrication behavior explicitly.
