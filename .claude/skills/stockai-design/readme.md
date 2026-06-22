# StockAI Design System

A dark, terminal-style design system for **StockAI** — an AI-powered paper-trading dashboard that monitors 13,000+ US stocks and 500 crypto assets, then uses Claude to analyze insider trades, Congress disclosures, news sentiment, technicals, and macro conditions into ranked trade setups.

This system captures the product's power-user aesthetic: near-black surfaces, monospace everything, market-semantic green/red/amber, and extreme density. It is **not** consumer UI — it is a Bloomberg-terminal-for-Claude.

## Sources

Built by reading the real product code. Explore these to build higher-fidelity designs:

- **GitHub:** [`zeinrady1/StockAI`](https://github.com/zeinrady1/StockAI) — the full app. The entire frontend is one file: [`static/index.html`](https://github.com/zeinrady1/StockAI/blob/main/static/index.html) (vanilla JS + CSS; the `:root` block is the source of truth for the palette). The Python backend (`brain.py`, `trader.py`, `scheduler.py`, `data/*`) documents the data model: insider/congress/news intel, technicals, macro regime, AI trade setups.
- A copy of the source frontend is kept at [`_source/stockai-index.html`](./_source/stockai-index.html) for reference.

> The reader is **not** assumed to have access to these — they are recorded so you can go deeper if you do.

---

## CONTENT FUNDAMENTALS

**Voice:** terse, numeric, trader shorthand. Labels are abbreviated and uppercased — `P/L`, `F&G INDEX`, `BUYING POWER`, `RSI (14)`, `MACD`. Microcopy favors the fewest characters that stay unambiguous.

**Casing:** Tiny labels and eyebrows are `UPPERCASE` with tracked-out letter-spacing. Values, tickers, and headlines are mixed-case. Tickers are always uppercase (`NVDA`, `BTC-USD`).

**Person:** Effectively impersonal — the UI addresses the *market*, not the user. No "you"/"I" in chrome. The AI engine speaks in rationale form: declarative, evidence-led ("Pullback to the 50-day with bullish insider flow…"), never chatty.

**Numbers are the content.** Prices, percentages, share counts, confidence scores (`8/10`), dollar ranges (`$1M–5M`). Signed and colored: `+2.40%` green, `−1.8%` red. Compact dollar formatting: `$104K`, `$42.1M`.

**Emoji / glyphs:** A small set of emoji act as section markers (🇺🇸 Congress, 📊 Insider, 📰 News, ⚡ refresh, ▶ run). Unicode triangles `▲ ▼` and dots `●` are used as status/direction indicators. No decorative emoji elsewhere.

**Vibe:** Live, fast, slightly clinical. A glowing green dot signals "live." Status badges (`Paper`, `Opus 4.8`) sit quietly in card titles. Nothing celebratory — gains and losses are stated, not editorialized.

**Examples**
- Buttons: `▶ Run AI Analysis`, `⚡ Refresh Intel`, `Buy 25 NVDA`, `Close`
- Labels: `TOTAL VALUE`, `TODAY P/L`, `BUYING POWER`, `TA SIGNALS — NVDA`
- Intel row: `NVDA Purchase · N. Pelosi (CA) · $1M–5M · Jun 18`
- AI rationale: `Overbought into resistance with a notable Congressional sale this week.`

---

## VISUAL FOUNDATIONS

**Color.** Near-black canvas `--bg #060910`. Surfaces step up in tiny increments — tape `#070b12`, raised chrome `#0d1117`, card `#111827`, input field `#0d1420`. Market semantics carry all the meaning: **green `#00e676`** = gains / buy / live, **red `#ff4444`** = losses / sell / stop-loss, **amber `#fbbf24`** = neutral / hold / tickers-in-context, **blue `#3b82f6`** = news / info / technical signals, **purple `#a78bfa`** = AI / model. Text is a 3-tier grey ramp (`#e8edf5` → `#8b98ae` → `#4b5568`). Semantic fills are translucent washes (`rgba(0,230,118,0.12)`) with a matching 25%-alpha border.

**Type.** Monospace throughout — the single strongest brand signal. The source uses the OS mono stack (`SF Mono`/`Cascadia Code`/`Menlo`); this system prepends **JetBrains Mono** (webfont) so specimens render identically everywhere *(substitution — see Caveats)*. The scale is deliberately tiny: 7px micro-labels → 8px card titles → 9–11px body → 12px values → 14px emphasis → 15px wordmark. Weight **800** is the workhorse for tickers, values, and the logo.

**Spacing & density.** Everything is compact: spacing steps run 2–14px, card padding is ~10px, grid gaps 4–8px. This is a power-user tool — whitespace is rationed.

**Backgrounds.** Flat near-black. **No gradients** (except one functional red→amber→green TA gauge bar), no imagery, no textures, no illustrations. The only "image" is the candlestick chart itself.

**Borders.** A single 1px hairline does almost all the work — `--border #1a2332` for dividers and card edges, `--border2 #243044` for inputs and stronger separators. Accents use a **3px left border** (open accordion, trade-card action keying).

**Corner radii.** Gentle: 4px chips → 5px wells → 6px inputs → 7px primary buttons → 8px cards/search → 20px pills.

**Cards.** Dark `#111827` fill, 1px `--border`, 8px radius, ~10px padding. **No drop shadows** on cards — depth comes from the surface-step palette, not elevation. The only shadows in the system are dropdown menus (`0 8px 32px rgba(0,0,0,0.5)`) and the green glow on the live dot / primary buttons.

**Shadows / glow.** Minimal. Live dots and primary buttons get a green glow (`0 0 6–12px rgba(0,230,118,…)`). Dropdowns get a deep soft shadow. That's it.

**Animation.** Restrained and functional: a continuous ticker-tape marquee, a `spin` keyframe for loading spinners, 0.1–0.2s transitions on tabs/toggles/hovers. No bounces, no parallax, no decorative motion.

**Hover states.** Rows get a faint green wash (`rgba(0,230,118,0.04)`) and bleed ~4px into the gutter. Ghost buttons brighten their border and text to green. Primary buttons brighten and intensify their glow.

**Press / active states.** Active tab = green text + green underline. Active interval/TA buttons = green border + green text. Toggles flip grey→amber and slide the knob. No shrink/scale on press.

**Transparency & blur.** Used sparingly — translucent semantic washes for chips/pills, and `isTransparent` TradingView widgets so the dark canvas shows through. No backdrop-blur glass.

**Layout rules.** A fixed full-height shell: ticker tape + top bar are fixed; the body is a 4-column CSS grid (`255px / 1fr / 290px / 265px`) that fills the viewport with independently-scrolling panels. Ultra-thin 4px scrollbars. `overflow:hidden` on the body — the app never scrolls as a whole.

**Imagery vibe.** None to speak of — this is a data UI. The "imagery" is green/red candlesticks on near-black. Cool, high-contrast, clinical.

---

## ICONOGRAPHY

StockAI ships **no icon font, no SVG sprite, and no logo file.** Iconography is entirely **Unicode/emoji glyphs** rendered inline at the system font size:

- **Emoji as section markers:** 🇺🇸 Congress Trades · 📊 Insider Trades · 📰 Market News · ⚡ Refresh/Auto · ▶ Run · 🔍 Search.
- **Geometric Unicode for status/direction:** `▲`/`▼` up/down, `●` live/signal dots, `▼` accordion chevrons, `◷` loading.
- **The wordmark is text:** `Stock` in green + `AI` in white, weight 800, monospace — paired with a glowing live dot. There is no separate logomark.

When extending the system, prefer this same approach (Unicode glyphs colored with the semantic palette) for fidelity. If a true icon set is needed, substitute a **thin-stroke** CDN set (e.g. Lucide) to match the lightweight terminal feel, and flag the substitution. See the **Brand** cards in the Design System tab for the wordmark and glyph inventory.

---

## INDEX

**Foundations**
- `styles.css` — global entry point (imports only). Consumers link this one file.
- `tokens/colors.css` — surfaces, borders, market semantics, text tiers, washes, glow.
- `tokens/typography.css` — mono family (+ JetBrains Mono webfont), size scale, weights, tracking.
- `tokens/spacing.css` — spacing steps, radii, the 4-column layout widths, control sizing.
- `tokens/base.css` — resets, thin scrollbars, semantic text utilities.
- `guidelines/*.card.html` — foundation specimen cards (Colors, Type, Spacing, Brand).

**Components** (`window.StockAIDesignSystem_ed0dbf.*`)
- `components/core/` — **Button**, **Badge**, **Card**
- `components/forms/` — **Input**, **Toggle**
- `components/navigation/` — **Tabs**
- `components/data/` — **Stat**, **TickerTag**, **IntelRow**, **TradeCard**

**UI kit**
- `ui_kits/dashboard/` — the full StockAI trading terminal (`index.html` + `dashboard.js`).

**Other**
- `_source/stockai-index.html` — reference copy of the original frontend.
- `SKILL.md` — Agent-Skills manifest for using this system in Claude Code.

---

## Caveats
- **Font substitution:** the product uses the OS monospace stack only. This system standardizes on **JetBrains Mono** (Google Fonts) as the closest free webfont. Swap in your licensed faces if you have them.
- **No brand assets to copy:** the app has no logo/illustration/image files — the wordmark is pure text and icons are glyphs. Nothing was copied into an `assets/` folder because nothing exists to copy.
- **TradingView widgets** (chart, market overview, TA panel) are live third-party embeds in the source; the UI kit replaces them with a canvas candlestick mock + CSS TA gauge.
