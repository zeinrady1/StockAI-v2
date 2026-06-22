"""
Macro market signals: VIX, yield curve, dollar, gold, oil, market breadth.
- VIX + Treasury yields: FRED API (Federal Reserve, free, 1-day lag)
- Market ETF proxies: Alpaca Market Data API (real-time)
"""
import httpx, asyncio, os
from typing import Dict, Optional

_ALPACA_KEY    = os.getenv("ALPACA_API_KEY", "")
_ALPACA_SECRET = os.getenv("ALPACA_SECRET_KEY", "")
_ALPACA_HDR    = {
    "APCA-API-KEY-ID":     _ALPACA_KEY,
    "APCA-API-SECRET-KEY": _ALPACA_SECRET,
}

# Alpaca ETF tickers used as macro proxies
_ETF_MAP = {
    "SPY":  "sp500",
    "QQQ":  "nasdaq100",
    "IWM":  "russell2000",
    "GLD":  "gold",
    "USO":  "oil",
    "UUP":  "dollar",
    "TLT":  "bonds_long",
    "IEF":  "bonds_10y",
    "UVXY": "vix_proxy",
    "VXX":  "vix_alt",
}

# FRED series IDs
_FRED = {
    "VIXCLS": "vix",
    "DGS10":  "yield_10y",
    "DGS2":   "yield_2y",
}


async def _fetch_fred(series_id: str, client: httpx.AsyncClient) -> Optional[float]:
    """Fetch latest data point from FRED CSV feed."""
    try:
        r = await client.get(
            f"https://fred.stlouisfed.org/graph/fredgraph.csv?id={series_id}",
            timeout=10,
        )
        if r.status_code != 200:
            return None
        lines = [l.strip() for l in r.text.strip().splitlines() if l.strip()]
        for line in reversed(lines[1:]):   # skip header, newest-first
            parts = line.split(",")
            if len(parts) == 2 and parts[1].strip() not in (".", ""):
                return float(parts[1].strip())
        return None
    except Exception:
        return None


async def _fetch_etf_prices(client: httpx.AsyncClient) -> Dict[str, Dict]:
    """Fetch Alpaca snapshots for macro ETF proxies."""
    try:
        r = await client.get(
            "https://data.alpaca.markets/v2/stocks/snapshots",
            headers=_ALPACA_HDR,
            params={"symbols": ",".join(_ETF_MAP.keys()), "feed": "iex"},
            timeout=15,
        )
        if r.status_code != 200:
            return {}
        data = r.json()
        out = {}
        for sym, snap in data.items():
            key = _ETF_MAP.get(sym)
            if not key:
                continue
            lt    = snap.get("latestTrade") or {}
            daily = snap.get("dailyBar") or {}
            prev  = snap.get("prevDailyBar") or {}
            price  = lt.get("p") or daily.get("c") or 0
            prev_c = prev.get("c") or 0
            chg    = round((price - prev_c) / prev_c * 100, 2) if prev_c else 0
            out[key] = {"price": round(float(price), 2), "change_pct": chg}
        return out
    except Exception:
        return {}


async def get_macro() -> Dict:
    async with httpx.AsyncClient(timeout=12) as client:
        fred_tasks = {k: _fetch_fred(k, client) for k in _FRED}
        etf_task   = _fetch_etf_prices(client)

        fred_vals, etf_data = await asyncio.gather(
            asyncio.gather(*[fred_tasks[k] for k in _FRED]),
            etf_task,
        )

    fred = {_FRED[k]: v for k, v in zip(_FRED.keys(), fred_vals)}
    raw  = {**etf_data}

    result = {"raw": {**raw, **{k: {"price": v, "change_pct": 0} for k, v in fred.items() if v}}}

    # ── VIX ──────────────────────────────────────────────────────────────────
    vix = fred.get("vix")
    if not vix:   # fall back to UVXY proxy (rough)
        uvxy = etf_data.get("vix_proxy", {}).get("price")
        vix  = round(uvxy * 0.85, 2) if uvxy else None

    if vix:
        if vix > 40:   regime = "EXTREME_FEAR"
        elif vix > 30: regime = "HIGH_FEAR"
        elif vix > 20: regime = "ELEVATED"
        elif vix > 15: regime = "NORMAL"
        else:          regime = "COMPLACENCY"
        result["vix"]        = round(vix, 2)
        result["vix_regime"] = regime
        result["vix_signal"] = (
            "BUY_SIGNAL — extreme fear historically marks bottoms" if vix > 35
            else "CAUTION — elevated volatility" if vix > 25
            else "NEUTRAL" if vix > 15
            else "CAUTION — complacency, market may be overextended"
        )

    # ── Yield curve ──────────────────────────────────────────────────────────
    y10 = fred.get("yield_10y")
    y2  = fred.get("yield_2y")
    if y10 and y2:
        spread = round(y10 - y2, 3)
        result["yield_10y"]           = y10
        result["yield_2y"]            = y2
        result["yield_curve_spread"]  = spread
        result["yield_curve_signal"]  = (
            "INVERTED — recession risk elevated (2s10s negative)" if spread < 0
            else "FLATTENING — watch closely" if spread < 0.5
            else "NORMAL — healthy economy signal"
        )

    # ── Gold ─────────────────────────────────────────────────────────────────
    gold = raw.get("gold", {})
    if gold.get("price"):
        result["gold"]        = gold["price"]
        result["gold_change"] = gold["change_pct"]

    # ── Oil ──────────────────────────────────────────────────────────────────
    oil = raw.get("oil", {})
    if oil.get("price"):
        result["oil"]        = oil["price"]
        result["oil_change"] = oil["change_pct"]

    # ── Dollar ───────────────────────────────────────────────────────────────
    uup = raw.get("dollar", {})
    if uup.get("price"):
        result["dollar_index"] = uup["price"]
        dchg = uup.get("change_pct", 0)
        result["dollar_signal"] = (
            "STRONG DOLLAR — headwind for commodities and international stocks"
            if dchg > 0.3
            else "WEAK DOLLAR — tailwind for commodities and emerging markets"
            if dchg < -0.3
            else "NEUTRAL"
        )

    # ── Market breadth ───────────────────────────────────────────────────────
    sp    = raw.get("sp500",      {}).get("change_pct")
    ndx   = raw.get("nasdaq100",  {}).get("change_pct")
    rut   = raw.get("russell2000",{}).get("change_pct")
    if sp is not None:
        result["market_breadth"] = {
            "sp500_chg":   sp,
            "nasdaq_chg":  ndx,
            "russell_chg": rut,
            "risk_on":     (sp > 0 and ndx is not None and ndx > 0 and rut is not None and rut > 0),
            "signal": (
                "RISK-ON — all major indices green" if sp > 0 and ndx and ndx > 0
                else "MIXED" if sp > 0
                else "RISK-OFF — market selling off"
            ),
        }

    # ── Overall macro regime ─────────────────────────────────────────────────
    signals = []
    if vix and vix > 30:           signals.append("HIGH_VIX")
    if vix and vix < 15:           signals.append("LOW_VIX_COMPLACENCY")
    if y10 and y2 and y10 - y2 < 0: signals.append("INVERTED_YIELD_CURVE")
    if sp and sp < -1:             signals.append("MARKET_SELLOFF")
    if sp and sp > 1:              signals.append("MARKET_RALLY")

    if "HIGH_VIX" in signals and "MARKET_SELLOFF" in signals:
        regime = "RISK_OFF_PANIC"
    elif "MARKET_RALLY" in signals and "LOW_VIX_COMPLACENCY" not in signals:
        regime = "RISK_ON_HEALTHY"
    elif "INVERTED_YIELD_CURVE" in signals:
        regime = "LATE_CYCLE_CAUTION"
    elif not signals:
        regime = "NEUTRAL"
    else:
        regime = "MIXED"

    result["macro_regime"]  = regime
    result["macro_signals"] = signals
    return result
