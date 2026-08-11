# US High Yield Bond Market — Daily Recap

**Delivery:** Tuesday, August 11, 2026 (before 07:15 AM EST)
**Session covered:** Monday, August 10, 2026
**Prepared:** Pre-market

---

## 1. Snapshot

| Metric | Level | Day-over-day |
|---|---|---|
| ICE BofA US HY OAS | ~264–271 bps | Tighter |
| ICE BofA US HY yield-to-worst | ~7.0–7.1% | Slightly lower |
| UST 10Y yield | ~4.64–4.65% | ~Flat (down ~9 bps on the week) |
| UST 30Y yield | ~5.25% | +~5 bps |
| WTI crude | ~$77/bbl | Softer (‑9% on the week) |
| HY fund flows | Positive | Largest weekly inflow in >1 month |
| Tone | Risk-on / grind tighter | Constructive |

> **Data note:** Level readings are triangulated from public commentary and index sources; they are close-of-day approximations, not terminal marks. See §5 on data provenance.

---

## 2. Most Notable Events / News

- **Dovish rate repricing dominated the tape.** Following Friday's (Aug 7) weaker-than-expected July employment report, the market pared its expectations for a hawkish Fed and leaned further into cuts. Lower/steady front-end and belly Treasury yields created a hospitable backdrop for credit risk. The next FOMC decision is **September 16**; the July CPI print (Aug 12) is the near-term swing factor (see §4).
- **Primary market roared back on the reopen.** The high-grade market saw its busiest issuance day in about seven months (~19 IG issuers Monday — utilities, overseas banks, Tyson Foods among them), with dealers pointing to ~$40bn of expected supply for the week after ~$80bn last week (third-heaviest of 2026). Heavy IG supply typically pulls HY syndicate desks along; issuers rushed to print ahead of Wednesday's CPI.
- **Technicals turned supportive.** HY retail fund flows flipped to their largest inflow in over a month, and the prior stretch of outflows continued to decelerate. Combined with solid Q2 earnings, this underpinned a modest grind tighter in spreads.
- **Spreads remain historically rich.** HY OAS in the mid-260s to ~270 bps sits near multi-year tights (vs. ~233 bps June 2007, ~259 bps early 2025), leaving limited cushion and keeping the market sensitive to any macro or idiosyncratic shock.

---

## 3. Best & Worst Performing HY Bonds (company/credit-specific)

> **Important — data access limitation:** Security-level ("best/worst bond of the day") performance requires TRACE prints and/or a Bloomberg/ICE terminal, which are **not accessible from this environment**. To avoid publishing fabricated prices, the section below reports the *supportable* cohort- and sector-level dispersion, and flags the exact terminal pulls needed to populate named winners/losers. **Do not treat any single security as confirmed until sourced from TRACE/BBG.** See §6 for the one-line fix to make this section fully security-specific each morning.

**Cohort dispersion (directional, from public commentary):**

- **Outperformers — lower-quality / higher-beta.** With yields repricing dovishly and flows positive, the **CCC and B tier** typically led on days like this ("reach for yield"). Recent data shows BB–CCC spread compression as investors move down in quality; ex-distressed CCCs have been notably stronger, i.e., the rally is broad but concentrated away from the genuinely stressed names.
- **Sector tailwind — Energy.** Energy is ~10% of the HY index and has been a leading absolute contributor in recent months; note, however, WTI softened toward ~$77 on the week, so the energy tailwind was **fading** rather than accelerating into Monday — watch for underperformance if crude keeps sliding.
- **Underperformers — distressed / secularly-challenged.** Weakness continues to concentrate in the **distressed bucket**. Rating agencies (Moody's, S&P) flag **legacy media, consumer/retail, and healthcare services** as elevated downgrade/default risk. Distressed exchanges have made up ~45–54% of defaults over 2023–2025, so idiosyncratic haircut/maturity-extension headlines remain the primary source of large single-name drawdowns.

**To be filled from terminal each morning (template):**

| Rank | Issuer | Coupon / Maturity | Δ Price | Δ Spread | Driver |
|---|---|---|---|---|---|
| Top gainer | *[TRACE pull]* | | | | *earnings beat / upgrade / M&A / tender* |
| Top decliner | *[TRACE pull]* | | | | *downgrade / guidance cut / distressed headline* |

---

## 4. What's Expected — Next Trading Day (Tuesday, Aug 11) & Week Ahead

- **Positioning day into CPI.** Tuesday is largely a set-up session ahead of the marquee event: **July CPI, Wednesday Aug 12, 8:30 AM ET.** Expect HY to trade with a firm-but-cautious tone, with new-issue desks likely to keep pushing deals out the door before the print. A benign CPI would validate the dovish repricing and support a further grind tighter; a hot CPI is the main downside risk given how little spread cushion exists.
- **Primary calendar.** With IG at its busiest since January and dealers guiding to ~$40bn for the week, expect an active HY new-issue slate on any constructive open — refinancings and opportunistic prints ahead of CPI.
- **Rest of week catalysts:** **PPI Thursday Aug 13 (8:30 ET)**, **Retail Sales Friday Aug 14 (8:30 ET)** and **UMich preliminary sentiment Friday (10:00 ET)**. FOMC is not until **Sept 16**, so data — not the Fed — drives the week.
- **Watch items:** (1) crude — further softness pressures the energy cohort; (2) any distressed/idiosyncratic single-name headlines in media/retail/healthcare; (3) whether HY inflows persist, confirming the technical bid.

---

## 5. Data Provenance & Caveats

- Figures are **triangulated from public market commentary and index references**, cross-checked across multiple sources. They are **approximate close-of-day levels**, not official terminal marks.
- Several primary financial data domains (FRED, TradingEconomics, issuer commentary sites) were **blocked by this environment's network egress proxy**, so some values are given as ranges.
- **No individual security prices are asserted** in §3 because security-level TRACE/Bloomberg data was not reachable. Cohort/sector commentary is directional.

## 6. Recommended fix to make §3 fully security-specific

To deliver named best/worst bonds each morning, wire in one of:
- **FINRA TRACE** end-of-day HY prints (most-active + biggest price movers), or
- **Bloomberg/ICE** terminal exports (`SRCH` / index constituent day P&L), or
- a market-data vendor API (e.g., ICE, S&P/Markit) for HY constituent daily returns.

Then the §3 template auto-populates the top gainer/decliner rows with issuer, CUSIP, price/spread change, and a one-line driver.

---

## Sources

- [August 10, 2026 — Bond Buyer](https://www.bondbuyer.com/digital-edition/august-10-2026)
- [US High-Grade Bond Market Sees the Most Issuers Since January — Bloomberg](https://www.bloomberg.com/news/articles/2026-08-10/us-high-grade-bond-market-sees-the-most-issuers-since-january)
- [ICE BofA US High Yield Index Effective Yield — FRED](https://fred.stlouisfed.org/series/BAMLH0A0HYM2EY)
- [HY Credit Spread (OAS) — Convex](https://convextrade.com/metrics/bamlh0a0hym2)
- [US 10 Year Treasury Note Yield — TradingEconomics](https://tradingeconomics.com/united-states/government-bond-yield)
- [2026 Corporate Credit Outlook — Charles Schwab](https://www.schwab.com/learn/story/corporate-bond-outlook)
- [High-Yield Defaults: Canary in the Coal Mine? — Charles Schwab](https://www.schwab.com/learn/story/high-yield-defaults-canary-coal-mine)
- [Weekly Market Commentary, Aug 10 2026 — Clearbrook](https://www.clearbrookglobal.com/weekly-market-commentary-august-10-2026/)
- [CPI Release Schedule — BLS / CPI Inflation Calculator](https://cpiinflationcalculator.com/cpi-release-schedule/)
- [US Economic Calendar — Econoday](https://us.econoday.com/)

*Recap prepared for internal use. Not investment advice. Verify all levels against a terminal before trading.*
