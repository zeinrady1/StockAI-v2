# StockAI

An AI-powered paper trading dashboard that monitors 13,000+ US stocks and 500 crypto assets in real time, then uses Claude to analyze insider trades, Congress disclosures, news sentiment, technicals, and macro conditions to generate trade recommendations — and optionally execute them automatically.

> **Paper trading only.** Uses Alpaca's paper trading environment. No real money is ever at risk.

## What it does

- **Live prices** — 13,000+ US equities (NYSE, NASDAQ, AMEX, OTC) + top 500 crypto, updated in real time via Alpaca and CoinGecko
- **AI analysis** — Claude Opus reads insider trades (SEC Form 4), Congress stock disclosures, market news, technical indicators (RSI, MACD, Bollinger Bands, ATR), macro regime (VIX, yield curve, dollar, breadth), and fundamental data (P/E, EPS, revenue growth) to produce ranked trade setups with confidence scores
- **Autonomous scheduler** — runs full AI analysis on a configurable interval during market hours and auto-executes trades above a confidence threshold; stop-loss monitor runs every 5 minutes
- **TradingView widgets** — interactive charts and full technical analysis panel for any ticker
- **Smart search** — search by ticker (`NVDA`), company (`Apple`), or sector (`semiconductor`, `healthcare`) with instant local results; 13,000+ asset universe loaded at startup
- **Intel feed** — live accordion panels for Congress trades, insider trades, and news articles; click any ticker to pull up its chart and TA instantly
- **Watchlist** — track custom tickers with live price/change display

## Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python 3.8+, FastAPI, uvicorn |
| AI | Claude Opus 4.8 (`claude-opus-4-8`) via Anthropic SDK |
| Trading | Alpaca Markets (paper trading API + IEX market data) |
| Crypto prices | CoinGecko (free, no key required) |
| Macro data | FRED (Federal Reserve, free) |
| Historical bars + news | Polygon.io |
| Fundamentals | Alpha Vantage |
| Sector data | NASDAQ Screener |
| Charts | TradingView Widgets (free) |
| Frontend | Vanilla JS, single-page HTML |

## Prerequisites

- Python 3.8 or higher
- A free [Alpaca paper trading account](https://alpaca.markets) (no real money needed)

## Setup

### 1. Clone the repo

```bash
git clone https://github.com/YOUR_USERNAME/StockAI.git
cd StockAI
```

### 2. Create a virtual environment

```bash
python3 -m venv venv
source venv/bin/activate        # Mac/Linux
venv\Scripts\activate           # Windows
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure API keys

```bash
cp .env.example .env
```

Open `.env` and fill in your keys (see table below).

### 5. Start the server

```bash
uvicorn main:app --host 0.0.0.0 --port 8001 --reload
```

Open [http://localhost:8001](http://localhost:8001) in your browser.

## API Keys

All keys go in `.env`. The app degrades gracefully — sources with missing keys are skipped.

| Key | Where to get it | Free tier |
|-----|----------------|-----------|
| `ANTHROPIC_API_KEY` | [console.anthropic.com](https://console.anthropic.com) | Pay per use |
| `ALPACA_API_KEY` + `ALPACA_SECRET_KEY` | [alpaca.markets](https://alpaca.markets) → Paper Trading → API Keys | Free |
| `POLYGON_KEY` | [polygon.io](https://polygon.io) | Free (historical bars + news) |
| `ALPHA_VANTAGE_KEY` | [alphavantage.co](https://www.alphavantage.co/support/#api-key) | Free (25 calls/day) |

`ANTHROPIC_API_KEY` and both Alpaca keys are required. Polygon and Alpha Vantage are optional but improve analysis quality.

## How it works

### Data pipeline (per analysis run)

1. **Insider trades** — scraped from OpenInsider (SEC Form 4 filings, last 30 days)
2. **Congress trades** — scraped from Capitol Trades (PTR filings)
3. **Market news** — 60+ Google News RSS queries + Polygon news API with sentiment scores
4. **Prices** — Alpaca IEX snapshots for stocks, CoinGecko for crypto
5. **Technicals** — Polygon daily bars → RSI, MACD, Bollinger Bands, ATR, volume z-score
6. **Macro** — FRED API for real VIX and treasury yields; Alpaca ETF proxies for SPY/QQQ/IWM/GLD/USO
7. **Fundamentals** — Alpha Vantage OVERVIEW + EARNINGS (P/E, Forward P/E, EPS, Beta, analyst target, revenue/earnings growth, profit margin)

All data is fed into a single Claude Opus prompt that returns structured JSON: market regime, top trade setups with entry/exit rationale, confidence scores, and position sizing.

### Autonomous trading

Enable via the **Auto Trade** toggle in the UI or `POST /api/scheduler/enable`. The scheduler:
- Runs full analysis every N minutes (configurable, default 60) during NYSE hours (9:30–4:00 ET)
- Auto-executes BUY orders for setups with confidence ≥ 7/10
- Allocates 5% of portfolio per trade (3% for confidence = 7)
- Checks every 5 minutes for positions down ≥ 8% and closes them (stop-loss)

### Search

The universe (13,000+ stocks + 500 crypto) is pre-loaded at startup. Search is instant from the local cache with 4-tier priority:
1. Exact ticker match
2. Ticker starts-with (A→Z)
3. Name starts-with (shorter = more exact; stocks before crypto)
4. Sector/industry match (sorted by market cap)

## Project structure

```
StockAI/
├── main.py            # FastAPI server, all API routes
├── brain.py           # Claude AI analysis prompt + response parsing
├── trader.py          # Alpaca order execution, positions, account
├── scheduler.py       # Autonomous trading loop + stop-loss monitor
├── data/
│   ├── universe.py    # Stock + crypto universe (Alpaca + CoinGecko + NASDAQ screener)
│   ├── prices.py      # Live prices (Alpaca IEX + CoinGecko)
│   ├── technicals.py  # Technical indicators (Polygon bars)
│   ├── macro.py       # Macro data (FRED + Alpaca ETF proxies)
│   ├── fundamentals.py# Fundamentals (Alpha Vantage)
│   ├── news.py        # News (Google RSS + Polygon)
│   ├── insider.py     # SEC Form 4 insider trades (OpenInsider)
│   ├── congress.py    # Congress stock trades (Capitol Trades)
│   ├── movers.py      # Market movers
│   └── options.py     # Options flow
├── static/
│   └── index.html     # Single-page frontend
├── requirements.txt
├── .env.example       # Key template
└── .env               # Your keys (never committed)
```

## Notes

- All trading is paper-only via Alpaca's sandbox. Switch to live trading requires changing the Alpaca base URL in `trader.py` — do so only if you understand the risks.
- Alpha Vantage free tier allows 25 API calls/day; the app caches fundamentals for 24 hours and fetches at most 20 tickers per analysis run.
- CoinGecko has a rate limit on the free tier; the app caches crypto prices and adds small delays between pages.
- The NASDAQ screener (sector/market cap data) is cached for 12 hours.
