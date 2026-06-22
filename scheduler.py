"""
Autonomous trading scheduler.
  - Runs full AI analysis every N minutes during NYSE market hours
  - Auto-executes trades with confidence >= 7/10
  - Monitors stop losses every 5 minutes — closes positions down >= 8%
  - Logs every action with timestamp
"""
import asyncio, logging
from datetime import datetime, time as dtime
from typing import List, Dict
import pytz

_ET           = pytz.timezone("US/Eastern")
_STOP_LOSS    = 8.0    # Close if position falls this % below entry
_MIN_CONF     = 7      # Only auto-trade if confidence >= this
_MAX_POS_PCT  = 0.05   # Max 5% of portfolio per position
_FALLBACK_QTY = 1      # If price unknown, buy 1 share

_enabled:  bool      = False
_interval: int       = 60   # minutes between analysis runs
_log:      List[Dict] = []   # last 200 entries, newest last
_status:   Dict       = {
    "enabled": False,
    "next_run": None,
    "last_run": None,
    "last_regime": None,
    "total_auto_trades": 0,
    "total_stop_losses": 0,
}


# ── Public controls ───────────────────────────────────────────────────────────

def enable(interval_minutes: int = 60):
    global _enabled, _interval
    _enabled  = True
    _interval = max(15, interval_minutes)
    _status["enabled"] = True
    _log_event("SCHEDULER_ON", f"Auto-trading enabled — running every {_interval} min during market hours")


def disable():
    global _enabled
    _enabled = False
    _status["enabled"] = False
    _log_event("SCHEDULER_OFF", "Auto-trading disabled")


def get_status() -> Dict:
    return {**_status, "log_count": len(_log), "stop_loss_pct": _STOP_LOSS, "min_confidence": _MIN_CONF}


def get_log(limit: int = 50) -> List[Dict]:
    return list(reversed(_log[-limit:]))


# ── Internal helpers ──────────────────────────────────────────────────────────

def _log_event(event_type: str, msg: str, extra: Dict = None):
    entry = {"time": datetime.now().isoformat()[:19], "type": event_type, "msg": msg}
    if extra:
        entry.update(extra)
    _log.append(entry)
    if len(_log) > 200:
        del _log[:50]
    logging.info(f"[scheduler] {event_type}: {msg}")


def _is_market_open() -> bool:
    now = datetime.now(_ET)
    if now.weekday() >= 5:
        return False
    return dtime(9, 30) <= now.time() <= dtime(16, 0)


def _compute_qty(price: float, portfolio_value: float, confidence: int) -> int:
    """Position size: 5% for conf>=8, 3% for conf=7. Never less than 1 share."""
    pct   = _MAX_POS_PCT if confidence >= 8 else 0.03
    alloc = portfolio_value * pct
    if price and price > 0:
        return max(1, int(alloc / price))
    return _FALLBACK_QTY


# ── Stop-loss monitor — runs every 5 min ─────────────────────────────────────

async def _stop_loss_loop():
    import trader
    while True:
        try:
            if _enabled and _is_market_open():
                positions = trader.get_positions()
                for pos in positions:
                    pct = pos.get("unrealized_pl_pct", 0)
                    tk  = pos["ticker"]
                    if pct <= -_STOP_LOSS:
                        result = trader.close_position(tk)
                        _status["total_stop_losses"] += 1
                        _log_event(
                            "STOP_LOSS_TRIGGERED",
                            f"Closed {tk} — position down {pct:.1f}% (limit -{_STOP_LOSS}%)",
                            {"ticker": tk, "pct": pct, "result": result},
                        )
        except Exception as e:
            _log_event("STOP_LOSS_ERROR", str(e))
        await asyncio.sleep(300)   # 5-minute check interval


# ── Full analysis + trade loop ────────────────────────────────────────────────

async def _analysis_loop():
    import trader as trader_mod, brain
    from data import congress, insider, news as news_mod, prices as prices_mod
    from data import movers, technicals as tech_mod, macro as macro_mod, options as opt_mod, fundamentals as fund_mod
    from collections import Counter

    while True:
        if not _enabled:
            await asyncio.sleep(60)
            continue

        if not _is_market_open():
            now = datetime.now(_ET)
            _status["next_run"] = "Market closed — will run at next 9:30 AM ET open"
            await asyncio.sleep(300)
            continue

        # ── Run analysis ──────────────────────────────────────────────────────
        _log_event("ANALYSIS_START", "Running full AI analysis...")
        _status["last_run"] = datetime.now().isoformat()[:19]

        try:
            # Gather intel
            insider_trades, congress_trades, market_news, market_movers = await asyncio.gather(
                insider.get_insider_trades(),
                congress.get_congress_trades(),
                news_mod.get_market_news(),
                movers.get_movers(),
            )

            # Build ranked signal tickers
            tc = Counter()
            for t in insider_trades:
                tk = t.get("ticker","")
                if tk and tk.isalpha() and len(tk) <= 5:
                    tc[tk] += 2
            for t in congress_trades:
                tk = t.get("ticker","")
                if tk and tk.isalpha() and len(tk) <= 5:
                    tc[tk] += 1
            ranked = [tk for tk, _ in tc.most_common()]
            for tk in (market_movers.get("trending") or []):
                if tk not in tc:
                    ranked.append(tk)

            ticker_news_data, price_data, tech_data, opts_data, macro_data, fund_data = await asyncio.gather(
                news_mod.get_ticker_news(ranked[:200]),
                prices_mod.get_prices(ranked[:200]),
                tech_mod.get_technicals(ranked[:300]),
                opt_mod.get_options_flow(ranked[:100]),
                macro_mod.get_macro(),
                fund_mod.get_fundamentals(ranked[:20]),
            )

            account           = trader_mod.get_account()
            current_positions = trader_mod.get_positions()
            portfolio_value   = account.get("portfolio_value", 100000)

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

            _status["last_regime"] = analysis.get("market_regime", "?")

            if "error" in analysis:
                _log_event("ANALYSIS_ERROR", analysis["error"])
            else:
                _log_event(
                    "ANALYSIS_DONE",
                    f"Regime: {analysis.get('market_regime','?')} | "
                    f"Outlook: {analysis.get('market_outlook','?')} | "
                    f"Cash rec: {analysis.get('cash_allocation_pct','?')}%",
                )

                # ── Execute high-confidence trades ────────────────────────────
                setups = analysis.get("top_setups") or analysis.get("trades") or []
                executed_count = 0

                for rec in setups:
                    conf   = rec.get("confidence", 0)
                    action = (rec.get("action") or "").upper()
                    ticker = (rec.get("ticker") or "").upper()

                    if not ticker or conf < _MIN_CONF:
                        continue

                    # Don't open a position we already hold
                    held_tickers = {p["ticker"] for p in current_positions}

                    if action == "BUY" and ticker not in held_tickers:
                        price = price_data.get(ticker, {}).get("price", 0)
                        qty   = _compute_qty(price, portfolio_value, conf)
                        if qty <= 0:
                            continue
                        reason = (
                            f"AutoTrade conf={conf}/10: "
                            + (rec.get("entry_rationale") or rec.get("reasoning") or "")[:200]
                        )
                        result = trader_mod.place_order(ticker, "buy", qty, reason)
                        _status["total_auto_trades"] += 1
                        executed_count += 1
                        _log_event(
                            "AUTO_BUY",
                            f"BUY {qty}x {ticker} @ ~${price:.2f} | conf {conf}/10",
                            {"ticker": ticker, "qty": qty, "price": price,
                             "confidence": conf,
                             "setup": rec.get("setup_type",""),
                             "catalyst": rec.get("catalyst",""),
                             "stop_loss_pct": rec.get("stop_loss_pct", _STOP_LOSS),
                             "target_pct": rec.get("target_pct", 0),
                             "result": result},
                        )

                    elif action in ("SELL", "CLOSE") and ticker in held_tickers:
                        result = trader_mod.close_position(ticker)
                        _status["total_auto_trades"] += 1
                        executed_count += 1
                        _log_event(
                            "AUTO_SELL",
                            f"SELL/CLOSE {ticker} | conf {conf}/10",
                            {"ticker": ticker, "confidence": conf, "result": result},
                        )

                _log_event(
                    "CYCLE_COMPLETE",
                    f"Executed {executed_count} trade(s) — next run in {_interval} min",
                )

        except Exception as e:
            _log_event("CYCLE_ERROR", str(e))

        _status["next_run"] = f"In {_interval} minutes"
        await asyncio.sleep(_interval * 60)


# ── Start both loops (called from main.py startup) ────────────────────────────

async def start():
    asyncio.create_task(_stop_loss_loop())
    asyncio.create_task(_analysis_loop())
