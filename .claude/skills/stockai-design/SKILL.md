---
name: stockai-design
description: Use this skill to generate well-branded interfaces and assets for StockAI — a dark, terminal-style AI trading dashboard — either for production or throwaway prototypes/mocks. Contains essential design guidelines, colors, type, fonts, and UI kit components for prototyping.
user-invocable: true
---

Read the `readme.md` file within this skill, and explore the other available files.

This is the StockAI design system: a near-black, monospace, power-user trading terminal. Green = gains/buy, red = losses/sell, amber = neutral/hold, everything dense and compact.

If creating visual artifacts (slides, mocks, throwaway prototypes, etc), copy assets out and create static HTML files for the user to view — link the root `styles.css` for tokens, and reuse the foundation cards in `guidelines/` and the screen in `ui_kits/dashboard/` as references. If working on production code, copy the token CSS and read the rules here to become an expert in designing with this brand.

Key files:
- `readme.md` — full design guide (content voice, visual foundations, iconography, index).
- `styles.css` → `tokens/*.css` — colors, typography (JetBrains Mono), spacing, base resets.
- `components/*` — React primitives (Button, Badge, Card, Input, Toggle, Tabs, Stat, TickerTag, IntelRow, TradeCard). Each has a `.prompt.md` with usage.
- `ui_kits/dashboard/` — the full trading-terminal screen to recreate or extend.
- `guidelines/*.card.html` — copy-pasteable specimen snippets for colors, type, spacing, brand.

If the user invokes this skill without other guidance, ask them what they want to build or design, ask a few questions (surface, density, which panels), and act as an expert designer who outputs HTML artifacts *or* production code, depending on the need. Stay faithful to the terminal aesthetic — monospace, near-black, market-semantic color, no gradients, no decorative motion, extreme density.
