import os, asyncio, json
from datetime import datetime, time as dtime
from dotenv import load_dotenv
import pytz
load_dotenv()

_ET = pytz.timezone("US/Eastern")

def _is_market_open(now=None) -> bool:
    now = (now or datetime.now(_ET)).astimezone(_ET)
    if now.weekday() >= 5:
        return False
    return dtime(9, 30) <= now.time() <= dtime(16, 0)

from fastapi import FastAPI, HTTPException, Query
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
from pydantic import BaseModel
from typing import Optional, List

import brain, trader, scheduler
from data import congress, insider, news, prices, universe, movers, technicals, macro, options, fundamentals

app = FastAPI(title="StockAI")
app.mount("/static", StaticFiles(directory="static"), name="static")

_analysis_log: List[dict] = []


@app.on_event("startup")
async def startup_background():
    asyncio.create_task(insider.warm_cache())
    asyncio.create_task(congress.warm_cache())
    asyncio.create_task(scheduler.start())


# ── Static ─────────────────────────────────────────────────────────────────────

@app.get("/", response_class=HTMLResponse)
async def root():
    return FileResponse("static/index.html")


# ── Account / Portfolio ────────────────────────────────────────────────────────

@app.get("/api/account")
async def get_account():
    return trader.get_account()


@app.get("/api/positions")
async def get_positions():
    return trader.get_positions()


@app.get("/api/orders")
async def get_orders():
    return trader.get_orders()


@app.get("/api/history")
async def get_history():
    return list(reversed(_analysis_log[-50:]))


# ── Data ───────────────────────────────────────────────────────────────────────

@app.get("/api/universe")
async def get_universe_endpoint():
    return await universe.get_universe()


@app.get("/api/search")
async def search_stocks(q: str = Query("", min_length=1)):
    return await universe.search(q, limit=25)


@app.get("/api/quote/{ticker}")
async def get_quote(ticker: str):
    price_map = await prices.get_prices([ticker.upper()])
    return price_map.get(ticker.upper(), {"error": "Not found"})


@app.get("/api/movers")
async def get_movers_endpoint():
    return await movers.get_movers()


@app.get("/api/intel")
async def get_intel():
    insider_trades, congress_trades, market_news = await asyncio.gather(
        insider.get_insider_trades(),
        congress.get_congress_trades(),
        news.get_market_news(),
    )
    return {
        "insider_trades":  insider_trades,
        "congress_trades": congress_trades,
        "news":            market_news,
        "fetched_at":      datetime.now().isoformat()[:19],
    }


@app.get("/api/intel/pulse")
async def intel_pulse():
    """Lightweight heartbeat — returns cache ages so the frontend knows when to do a full refresh."""
    from data import insider as ins_mod, congress as cong_mod
    now = datetime.now()
    return {
        "market_open":   _is_market_open(now),
        "server_time":   now.isoformat()[:19],
        "insider_age":   round(now.timestamp() - ins_mod._cache_ts) if ins_mod._cache_ts else None,
        "news_age":      round(now.timestamp() - news._news_ts)     if news._news_ts    else None,
    }


# ── Trading ────────────────────────────────────────────────────────────────────

class TradeRequest(BaseModel):
    ticker: str
    side:   str
    qty:    int
    reason: Optional[str] = "Manual trade"


@app.post("/api/trade")
async def manual_trade(req: TradeRequest):
    result = trader.place_order(req.ticker, req.side, req.qty, req.reason)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result


@app.post("/api/close/{ticker}")
async def close_position(ticker: str):
    result = trader.close_position(ticker)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result


# ── Scheduler control ──────────────────────────────────────────────────────────

class SchedulerRequest(BaseModel):
    interval_minutes: Optional[int] = 60


@app.post("/api/scheduler/enable")
async def enable_scheduler(req: SchedulerRequest = SchedulerRequest()):
    scheduler.enable(req.interval_minutes)
    return scheduler.get_status()


@app.post("/api/scheduler/disable")
async def disable_scheduler():
    scheduler.disable()
    return scheduler.get_status()


@app.get("/api/scheduler/status")
async def scheduler_status():
    return scheduler.get_status()


@app.get("/api/scheduler/log")
async def scheduler_log(limit: int = 50):
    return scheduler.get_log(limit)


# ── AI Analysis ────────────────────────────────────────────────────────────────

@app.post("/api/analyze")
async def run_analysis(auto_trade: bool = False):
    from collections import Counter

    # 1. All intel in parallel
    insider_trades, congress_trades, market_news, market_movers = await asyncio.gather(
        insider.get_insider_trades(),
        congress.get_congress_trades(),
        news.get_market_news(),
        movers.get_movers(),
    )

    # 2. Rank tickers by signal count (insider weight 2, congress weight 1)
    ticker_signals = Counter()
    for t in insider_trades:
        tk = t.get("ticker", "")
        if tk and tk.isalpha() and len(tk) <= 5:
            ticker_signals[tk] += 2
    for t in congress_trades:
        tk = t.get("ticker", "")
        if tk and tk.isalpha() and len(tk) <= 5:
            ticker_signals[tk] += 1

    ranked = [tk for tk, _ in ticker_signals.most_common()]
    for tk in (market_movers.get("trending") or []):
        if tk not in ticker_signals:
            ranked.append(tk)

    # 3. All market data in parallel
    ticker_news_data, price_data, tech_data, opts_data, macro_data, fund_data = await asyncio.gather(
        news.get_ticker_news(ranked[:200]),
        prices.get_prices(ranked[:200]),
        technicals.get_technicals(ranked[:300]),
        options.get_options_flow(ranked[:100]),
        macro.get_macro(),
        fundamentals.get_fundamentals(ranked[:20]),
    )

    # 4. Portfolio state
    account           = trader.get_account()
    current_positions = trader.get_positions()
    portfolio_value   = account.get("portfolio_value", 100000)

    # 5. AI analysis
    analysis = await brain.analyze(
        insider_trades    = insider_trades,
        congress_trades   = congress_trades,
        news              = market_news,
        ticker_news       = ticker_news_data,
        prices            = price_data,
        portfolio_value   = portfolio_value,
        current_positions = current_positions,
        technicals        = tech_data,
        options_flow      = opts_data,
        macro             = macro_data,
        fundamentals      = fund_data,
    )

    # 6. Auto-execute trades (if requested and no error)
    executed = []
    if auto_trade and "error" not in analysis:
        setups = analysis.get("top_setups") or analysis.get("trades") or []
        held   = {p["ticker"] for p in current_positions}

        for rec in setups:
            conf   = rec.get("confidence", 0)
            action = (rec.get("action") or "").upper()
            ticker = (rec.get("ticker") or "").upper()

            if not ticker or conf < 7:
                continue

            if action == "BUY" and ticker not in held:
                price  = price_data.get(ticker, {}).get("price", 0)
                qty    = max(1, int(portfolio_value * (0.05 if conf >= 8 else 0.03) / price)) if price else 1
                result = trader.place_order(
                    ticker, "buy", qty,
                    reason=f"AutoTrade conf={conf}/10: "
                           + (rec.get("entry_rationale") or rec.get("reasoning") or "")[:200],
                )
                executed.append({**result, "confidence": conf, "ticker": ticker})

            elif action in ("SELL", "CLOSE") and ticker in held:
                result = trader.close_position(ticker)
                executed.append({**result, "confidence": conf, "ticker": ticker})

    # 7. Log
    log_entry = {
        "timestamp": datetime.now().isoformat()[:19],
        "analysis": analysis,
        "executed_trades": executed,
        "intel_summary": {
            "insider_trades":   len(insider_trades),
            "congress_trades":  len(congress_trades),
            "news_articles":    len(market_news),
            "tickers_analyzed": len(ranked),
        },
    }
    _analysis_log.append(log_entry)

    return {
        "analysis":  analysis,
        "intel": {
            "insider_trades":  insider_trades,
            "congress_trades": congress_trades,
            "news":            market_news + ticker_news_data,
            "prices":          price_data,
            "movers":          market_movers,
        },
        "executed":  executed,
        "timestamp": log_entry["timestamp"],
    }
