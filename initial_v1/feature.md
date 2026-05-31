# Feature: Dynamic Portfolio and Technical Analysis Dashboard

## Overview

This feature delivers a single, easy-to-use dashboard for a private investor to monitor and analyze a personal stock portfolio. The dashboard should make it fast to understand portfolio health, open any stock for deeper review, and explore price behavior with common visual indicators.

The initial release focuses on speed and clarity for day-to-day use. The user should be able to move from portfolio summary to detailed stock view in seconds, without complex workflows.

## Background

The current portfolio source file includes 116 holdings and serves as the baseline for the first version of the dashboard.

For this release, the scope is intentionally narrow to reduce risk and accelerate delivery:

- Portfolio scope is all 116 rows in the current source file.
- Ticker support is US-only in MVP.
- Stocks with missing snapshot prices are shown as unavailable instead of being auto-filled.
- Default chart history window is 1 year.

This scope supports a practical first release while leaving room to expand international symbol support and richer data handling in later phases.

## Feature Details

### Primary user

Individual retail investor managing a medium-to-large personal portfolio who needs fast visual insights and low-friction analysis.

### User goals

- See overall portfolio status at a glance.
- Open any included stock quickly for deeper inspection.
- Understand trend and momentum using familiar chart overlays.
- Keep the experience responsive even with a large watchlist.

### In-scope capabilities for v1

- Portfolio-level summary area with key KPI style metrics, including total portfolio value.
- Fast stock lookup and selection across all in-scope holdings.
- Single-stock interactive chart view with 1-year default history.
- Toggleable technical overlays for common analysis workflows, including moving averages, Bollinger Bands, Fibonacci retracement, and RSI.
- Clear unavailable state for holdings that have missing snapshot values.

### Out of scope for v1

- International ticker support beyond the agreed US-only scope.
- Authentication and user account management.
- Exporting reports or files from the dashboard.

### Success signals

- User can open and inspect any in-scope stock quickly.
- Portfolio summary and single-stock charting both work reliably in one flow.
- Missing data states are understandable and non-blocking.
- The experience remains responsive with the full 116-row portfolio.

## References

- Portfolio source snapshot: [Porfelis20260221.csv](../source-files/Porfelis20260221.csv)
