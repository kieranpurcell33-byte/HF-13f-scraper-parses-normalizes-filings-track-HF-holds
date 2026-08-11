# US HY Bond Market — Daily Recap

An automated, weekday recap of the US high-yield (HY) bond market for the **previous trading day**.

## What each recap covers

1. **Snapshot** — HY index return, OAS/spread level, effective yield, and the key rate move.
2. **Most notable events / news** — macro prints, primary-market activity, flows, and credit headlines.
3. **Best & worst performing credits** — company/credit-specific themes and watch-list names.
4. **Best & worst performing sectors** — macro attribution for the session.
5. **What to expect next trading day** — HY-specific setup, macro events, and geopolitical risks.

## Delivery schedule

- **Every weekday, before 07:15 AM ET.**
- Recaps are written to `recaps/YYYY-MM-DD_US-HY-daily-recap.md`, where the date is the **delivery
  date** (the morning after the session being recapped).
- Automated delivery is driven by a scheduled Routine (see `SCHEDULE.md`) that fires ~06:30 AM ET
  (10:30 UTC) each weekday — comfortably before the 07:15 AM ET cutoff in both EST and EDT.

## Data sources

Public/aggregated sources are used for levels and narrative:

- **ICE BofA US High Yield indices** (OAS, effective yield) via FRED (`BAMLH0A0HYM2`, `BAMLH0A0HYM2EY`)
  and aggregators.
- **Bloomberg HY 2% Issuer-Capped Index** returns/spreads via manager commentaries (e.g., Nuveen weekly).
- **US Treasury yields** via Trading Economics / Federal Reserve H.15.
- **Financial press** (Bloomberg, Yahoo Finance, sector commentaries) for credit and macro headlines.
- **Economic calendar** (CPI/PPI/NFP) for the forward-looking section.

## Important limitation (please read)

Precise **issuer-level, single-day total-return league tables** for individual HY bonds require a
market-data terminal (Bloomberg / ICE / TRACE). A web-only automated process cannot reliably produce a
verified bond-by-bond daily ranking. Accordingly, the "best & worst credits" section is presented as
**credit themes and watch-list names** grounded in sourced reporting, and is explicitly labeled as such.

To upgrade to true issuer-level daily rankings, wire in one of:

- A **Bloomberg** (BQL/BLPAPI), **ICE Data Services**, or **FINRA TRACE** feed, or
- A vendor API (e.g., a bond analytics provider) with entitlements for HY constituent-level pricing.

Once a feed is available, populate section 3 from actual constituent total returns for the session.

## Not investment advice

These recaps are informational/directional only. Verify all levels against your own market-data terminal
before making any trading decision.
