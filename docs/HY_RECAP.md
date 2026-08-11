# US High-Yield Bond Daily Recap

A pluggable pipeline that produces a daily recap of the US high-yield (HY) bond
market for the **previous trading session**, covering:

1. **Notable events & news** for the session.
2. **Best and worst performing HY bonds** — issuer/credit-specific, with the
   *why* behind each move.
3. **Market context** — index spreads/yields, rates, CDX, flows, new issue.
4. **What is expected for the next trading day.**

The deliverable is a Markdown file, `hy_recap_YYYY-MM-DD.md`, designed to be
generated and delivered **every weekday before 07:15 AM ET**.

## Quick start

```bash
pip install -r requirements.txt

# Preview format with bundled sample (synthetic) data
python -m hy_recap --date 2026-08-10

# Recap the previous trading day and write to output/hy_recap/
python -m hy_recap --write
```

A rendered sample lives at [`sample_recap.md`](./sample_recap.md).

## Architecture

```
hy_recap/
  models.py         Pydantic models for the recap (the data contract)
  config.py         Env-driven config; selects a backend per section
  calendar_util.py  US trading calendar (weekends + market holidays)
  sources/
    base.py         MacroSource / BondPerformanceSource / NewsSource / OutlookSource
    sample.py       Deterministic synthetic data (previews + tests)
    feeds.py        RestGatewaySource — generic JSON adapter for your feed
    registry.py     Wires config -> concrete sources
  builder.py        Composes a RecapReport from the sources
  renderer.py       Jinja2 -> Markdown
  delivery.py       Write to disk + delivery hook
  templates/        recap.md.j2
  cli.py            `python -m hy_recap`
```

The builder depends only on the four **source interfaces**, so each section can
be served independently — mix a live bond feed with a sample outlook while you
build things out.

## Connecting your licensed data feed

The issuer-level "best/worst bonds" section requires a **licensed
security-level price/spread feed** (FINRA TRACE, Bloomberg, or ICE). The
recommended integration keeps vendor SDKs and entitlements out of this repo:
stand up a small JSON gateway *you* control and point the pipeline at it.

Set the source for each section to `rest` and provide the gateway URL:

```bash
export HY_MACRO_SOURCE=rest
export HY_BOND_SOURCE=rest
export HY_NEWS_SOURCE=rest
export HY_OUTLOOK_SOURCE=rest
export HY_REST_BASE_URL=https://your-feed.internal/hy
export HY_REST_API_KEY=...        # sent as a Bearer token
python -m hy_recap --write
```

### Gateway contract

All dates are ISO `YYYY-MM-DD`. Response objects match the field names in
`hy_recap/models.py`.

| Endpoint | Returns |
|---|---|
| `GET {base}/macro?date=<d>` | `MacroSnapshot` |
| `GET {base}/performers?date=<d>&n=<k>` | `{ "gainers": [BondPerformer...], "decliners": [BondPerformer...] }` |
| `GET {base}/news?date=<d>` | `{ "items": [NewsItem...] }` |
| `GET {base}/outlook?date=<d>` | `NextSessionOutlook` |

Minimal `performers` example:

```json
{
  "gainers": [{
    "issuer": "Example Telecom", "description": "7.25% 2031",
    "sector": "Telecom", "rating": "B2/B", "direction": "gainer",
    "price": 98.4, "price_chg": 3.1, "spread_bps": 412, "spread_chg_bps": -58,
    "total_return_pct": 3.2,
    "reason": "Upgraded to BB- on deleveraging; short squeeze in the 2031s."
  }],
  "decliners": [{
    "issuer": "Example Retail", "direction": "decliner",
    "price": 71.5, "price_chg": -6.4, "spread_chg_bps": 145,
    "reason": "Guidance cut and covenant-amendment chatter."
  }]
}
```

### Vendor-direct adapters

To skip the gateway and call a vendor directly, add an adapter implementing the
relevant interface(s) from `sources/base.py` and register it in
`sources/registry.py` (`_FACTORIES`). Credentials are already read from the
environment in `config.py` (`BLOOMBERG_HOST`, `ICE_API_KEY`,
`FINRA_TRACE_API_KEY`). The `blpapi` (Bloomberg) SDK and any entitlements must
be installed on the runner — keep them off the public CI image.

## Scheduling the 07:15 ET delivery

### Option A — GitHub Actions (committed)

`.github/workflows/hy-recap.yml` runs weekdays at **10:30 UTC** (06:30 EDT /
05:30 EST — before the 07:15 ET deadline in both) and uploads the recap as a
build artifact. Configure feed selection via repo **Variables** (`HY_*_SOURCE`,
`HY_REST_BASE_URL`) and keys via repo **Secrets** (`HY_REST_API_KEY`, etc.).

> Actions' scheduled runs can start several minutes late under load. For a hard
> deadline, use Option B.

### Option B — cron / systemd timer (self-hosted, reliable)

```cron
# /etc/cron.d/hy-recap  — 06:45 America/New_York, Mon-Fri
CRON_TZ=America/New_York
45 6 * * 1-5  appuser  cd /opt/hf-scraper && /usr/bin/python -m hy_recap --write --deliver "$HY_DELIVERY_DEST" >> /var/log/hy_recap.log 2>&1
```

`CRON_TZ` (Vixie cron) pins the job to Eastern so it tracks DST automatically.

### Delivery destination

`delivery.py` writes the file and then calls a **hook** (`deliver`). Wire your
destination there — e.g. upload to Google Drive (the Drive connector),
email/SMTP, S3, or a Slack post — reading the destination from
`--deliver <DEST>` or an env var so credentials stay in the scheduler, not the
repo.

> Note: the Google Drive connector in this workspace currently needs
> re-authorization before automated uploads will work.

## Data provenance

Sample runs are explicitly flagged in the report's `data_caveats` and rendered
as a block quote at the bottom of the document — a sample-sourced recap should
never be presented as real market data. Live runs record which backend served
the issuer-level moves.

## Tests

```bash
python -m pytest tests/test_hy_recap.py -q
```
