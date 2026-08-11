# Delivery schedule

**Requirement:** a fresh recap of the previous trading day's US HY market, delivered **every weekday
before 07:15 AM ET**.

## Automation

Delivery is driven by a scheduled **Routine** (Claude Code Remote trigger) that fires a fresh session
each weekday morning. That session:

1. Researches the previous trading day's US HY market (indices/OAS, rates, flows, primary, credit &
   sector news, and the forward calendar).
2. Writes `recaps/YYYY-MM-DD_US-HY-daily-recap.md` using `TEMPLATE.md`.
3. Commits and pushes the file to the delivery branch.

## Timing

- **Cron (UTC):** `30 10 * * 1-5`  → **10:30 UTC, Monday–Friday**.
- 10:30 UTC = **06:30 AM EDT** (summer) and **05:30 AM EST** (winter) — both comfortably before the
  07:15 AM ET cutoff, so the schedule holds across daylight-saving changes without edits.
- The ~45-minute buffer before 07:15 allows for research + write + push.

## Changing delivery

The default target is this project's delivery branch (a file committed to git). To change *how* the file
is delivered, adjust the Routine prompt to instead:

- **Email** the recap to the recipient, or
- Save it to **Google Drive** (attach the Drive connector to the Routine), or
- **Merge to `main`** so the dated file lands on the default branch each day.

Manage the Routine with the `list_triggers` / `update_trigger` / `delete_trigger` tools (or from the
Claude Code web UI). Fire an out-of-schedule run anytime with `fire_trigger`.
