# US High‑Yield Bond Market — Daily Recap

**Recap for trading day:** Monday, August 10, 2026
**Prepared for delivery:** Tuesday, August 11, 2026 (pre‑07:15 ET)

> **Read‑me on the numbers.** Precise index levels below are drawn from public, free sources and should be treated as *directional* — free feeds lag, round, and sometimes disagree (e.g., ICE BofA HY OAS was quoted at ~281 bps on 7/27 and ~271 bps on 8/6 by different providers). Where a figure could not be cleanly verified it is given as a range and flagged. See **Data & methodology** at the end. This desk does not currently have a licensed market‑data feed (ICE/Bloomberg/TRACE), which is the gating item for true CUSIP‑level "best/worst bond of the day" reporting — see the note in Section 2.

---

## 1) Market at a glance — Monday, Aug 10

| Metric | Level (approx.) | Day / recent move | Read |
|---|---|---|---|
| ICE BofA US HY OAS | ~265–275 bps area | Tighter on the week | Risk‑on; spreads grinding tighter with the dovish rate repricing |
| ICE BofA US HY yield (effective) | ~7.0% area | Lower with rates | Carry still the story; all‑in yields off recent highs |
| 10Y UST yield | ~4.6–4.7% | ~Flat on the day | Held after Friday's rally |
| 30Y UST yield | ~5.25% | +~5 bps | Long end lagged the front‑end rally |
| Tone | Firm / risk‑on | — | HY bid; heavy IG supply cleared well |

*Directional; verify against a licensed feed before external use.*

**One‑line summary:** HY traded with a firm, risk‑on tone to start the week, riding the dovish repricing that followed Friday's weak jobs report, even as the primary market's focus stayed on a record burst of investment‑grade supply and the Street positioned ahead of Wednesday's CPI.

---

## 2) Most notable events & news

**1. Friday's jobs shock is still driving the tape.** The July employment report (released Fri 8/7) was a sharp downside miss — roughly **+22k payrolls vs. ~+75k expected**, unemployment up to **4.3%** (highest since Oct 2021), with prior months revised lower. That flipped rate expectations decisively dovish and set the risk‑on backdrop HY carried into Monday.

**2. Rate‑cut pricing surged.** Following the miss, futures moved to price a **~90% probability of a 25 bp September cut** (CME FedWatch), a meaningful dovish swing from the higher‑for‑longer/possible‑hike posture priced pre‑report. Lower yields + falling vol = a hospitable window for credit.

**3. Record primary — but in IG, not HY.** Monday saw **19 high‑grade issuers** come to market, the most in ~7 months, as borrowers (utilities, overseas banks, Tyson Foods among them) front‑ran the week's inflation data. The takeaway for HY: the new‑issue window is wide open and demand is deep; expect the HY calendar to lean on it into the fall (names like Brink's and Fertitta Entertainment have been flagged in the pipeline).

**4. Macro cross‑current: US–Japan FX intervention.** Markets were also watching the first coordinated US–Japan currency intervention in nearly three decades to support the yen — a notable risk event to keep on the radar for cross‑asset spillover, though HY impact Monday was limited.

**5. The structural caution underneath the rally.** Even with spreads tight, the year's credit narrative — CDX HY at multi‑month wides earlier in the summer, credit‑vs‑equity divergence, rising fallen‑angel risk, and the earlier defaults of **First Brands** and **Tricolor** reigniting "market access can vanish fast" concerns — remains the bear case. Quality dispersion (BB over CCC) is the prevailing professional posture.

### On "best & worst individual HY bonds of the day"
Reliable, CUSIP‑level daily winners/losers require a licensed data feed (TRACE prints / ICE or Bloomberg index constituents). Those sources are **not accessible from this environment's free/public tooling**, and fabricating specific bond prints would be worse than useless in a financial deliverable — so this section is reported at the level that *is* verifiable: the credit‑specific news flow that drives idiosyncratic moves.

- **Where the pain is (context, not a Monday print):** the stressed cohort remains concentrated in **legacy media, healthcare services, and bricks‑and‑mortar retail**, plus recent distressed situations (**First Brands, Tricolor**). These are the names most exposed to the "sentiment turns → access disappears" dynamic.
- **Where the bid is:** higher‑quality **BB** paper and shorter spread‑duration credits benefited most from the dovish rate move.

> **To deliver true daily best/worst‑bond attribution going forward, this desk needs a market‑data source wired in** (see Section 5). That is the single highest‑value upgrade to this product.

---

## 3) What's expected — Tuesday, Aug 11 (and the week)

- **Tone:** Constructive but two‑sided into the data. HY likely stays bid on the dovish backdrop, but expect **positioning/de‑risking around CPI** rather than fresh conviction.
- **The main event — Wednesday 8/12, 8:30 ET: July CPI.** Consensus looks for headline **~3.4% YoY** and core around **+0.2% m/m (~2.5% YoY)** — which would be among the softer core readings of the year. This print is the swing factor: a soft number validates the ~90% September‑cut pricing and should let HY spreads grind tighter / new issue accelerate; a hot number reopens the higher‑for‑longer debate and is the clearest near‑term risk to the rally. **PPI later in the week** is the confirm/deny.
- **Primary market:** the IG deluge should continue; watch for HY issuers opportunistically tapping the open window ahead of the data.
- **What to watch on the screens:** front‑end UST direction, CDX HY vs. equities (does the divergence keep narrowing?), and fund‑flow signals (HY flows had been improving).

---

## 4) Bottom line

A risk‑on HY session Monday, powered by a dovish rate repricing off Friday's weak jobs data, with the spotlight on record IG supply. The market is coiled ahead of Wednesday's CPI, which will decide whether the tightening bias extends or the summer's credit‑caution narrative reasserts. Underlying dispersion — up‑in‑quality, distressed pockets in media/healthcare/retail — remains the story beneath the index.

---

## 5) Data & methodology

**Verifiable this cycle (public sources):** the jobs‑report miss and its rate‑market impact, the ~90% Sept‑cut pricing, Monday's record IG issuance count, the CPI calendar/consensus, and the broad spread/yield ranges.

**Not verifiable from free tooling (reported directionally or omitted):** exact same‑day HY OAS/yield closes, and CUSIP‑level individual‑bond performance. FRED and several commentary sites were blocked by this environment's network egress proxy this cycle; index snapshots were reconstructed from multiple secondary sources that did not fully agree, hence the ranges.

**To make this a fully accurate daily product, wire in one data source** (in rough order of value):
1. **ICE BofA HY index** levels/returns (OAS, yield, daily total return) — for the top‑line snapshot.
2. **TRACE / a HY index constituent feed** (Bloomberg, ICE, or a broker runs sheet) — for real best/worst‑bond attribution.
3. **A ratings/news feed** (Moody's/S&P/Fitch actions, Octus/LCD for primary) — for the credit‑specific "why."

### Sources
- [US High‑Grade Bond Market Sees the Most Issuers Since January — Bloomberg](https://www.bloomberg.com/news/articles/2026-08-10/us-high-grade-bond-market-sees-the-most-issuers-since-january)
- [Odds the Fed will hike in September tumble following big July jobs miss — CNBC](https://www.cnbc.com/2026/08/07/odds-the-fed-hikes-in-september-tumble-following-big-july-jobs-miss.html)
- [Jobs report July 2026 — CNBC](https://www.cnbc.com/2026/08/07/jobs-report-july-2026.html)
- [US CPI Prep (12th August) — FinancialJuice](https://features.financialjuice.com/2026/08/10/us-cpi-prep-12th-august-2/)
- [Consumer Price Index News Release schedule — BLS](https://www.bls.gov/news.release/cpi.htm)
- [ICE BofA US High Yield OAS (BAMLH0A0HYM2) — FRED](https://fred.stlouisfed.org/series/BAMLH0A0HYM2) *(egress‑blocked this cycle)*
- [HY Credit Spread (OAS) 271 bps, Aug 6 2026 — Convex](https://convextrade.com/metrics/bamlh0a0hym2)
- [2026 Taxable Fixed Income Mid‑Year Outlook — Charles Schwab](https://www.schwab.com/learn/story/fixed-income-outlook)
- [CDX: Credit Spreads Are Flashing A Warning — RIA](https://realinvestmentadvice.com/resources/blog/cdx-credit-spreads-are-flashing-a-warning/)
- [Junk‑bond credit spreads 2026 — ECM Source](https://ecmsource.com/junk-bond-credit-spreads-2026-corporate-debt/)
- [Americas Primary Market 2026 Outlook — Octus](https://octus.com/resources/articles/americas-primary-market-2026-outlook/)

*Generated by Claude Code. Numbers are directional pending a licensed market‑data feed; verify before any external or investment use.*
