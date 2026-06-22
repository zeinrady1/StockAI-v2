# StockAI — Trading Dashboard UI Kit

A high-fidelity recreation of the StockAI single-page terminal dashboard.

## Files
- `index.html` — the full dashboard view (header + 4-column grid). Self-contained, links the root `styles.css` for tokens.
- `dashboard.js` — mock data + interactions: ticker tape, live clock, accordion toggles, center tabs, AI-analysis output, the trade form, and a canvas candlestick chart.

## Layout (matches the source app)
1. **Ticker tape** — auto-scrolling marquee of indices, megacaps, crypto, commodities.
2. **Top bar** — `StockAI` wordmark + live dot, global search, and four stat readouts: Portfolio, Today P/L, Fear & Greed index, market-status clock.
3. **Column 1 (255px)** — Portfolio stat grid, Positions, Watchlist, AI Engine (Run Analysis + auto-execute toggle).
4. **Column 2 (1fr)** — tabbed center: **Chart** (candlestick + interval buttons), AI Analysis (ranked trade cards), Market, Movers, All Stocks.
5. **Column 3 (290px)** — Intel Feed: collapsible accordions for Congress Trades, Insider Trades (Form 4), Market News — each a row table.
6. **Column 4 (265px)** — TA Signals gauge + indicator readout, then the **Place Order** form (ticker, shares, buy/sell, estimate, submit).

## Interactions
- Center tabs switch panels; "Run AI Analysis" jumps to the Analysis tab.
- Intel accordions expand/collapse.
- Trade form recomputes the estimate live and shows a paper-fill toast on submit.
- Candlestick chart is drawn on a `<canvas>` and redraws on resize.

## Notes / fidelity
- The real app embeds **TradingView** widgets for the chart, market overview, and TA panel. Those are replaced here with a canvas candlestick mock and a CSS TA gauge — the visual language is preserved; live data is not.
- The source ships col 4 as a TA panel only; the **trade execution form** shown here follows the brief's layout, built from the same input/button vocabulary.
- All data is fake and static. This is a visual + interaction recreation, not production code.

## Source
Recreated from [`zeinrady1/StockAI`](https://github.com/zeinrady1/StockAI) → `static/index.html`.
