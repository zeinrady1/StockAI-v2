"""
Options flow analysis from Yahoo Finance — put/call ratio, IV, unusual activity.
No API key required.
"""
import httpx, asyncio, math
from typing import Dict, List, Optional

_HEADERS = {"User-Agent": "Mozilla/5.0", "Accept": "application/json"}


async def _fetch_options_chain(ticker: str, client: httpx.AsyncClient) -> Dict:
    """Fetch the nearest-expiry options chain from Yahoo Finance."""
    url = f"https://query2.finance.yahoo.com/v7/finance/options/{ticker}"
    try:
        r = await client.get(url, headers=_HEADERS, timeout=10)
        if r.status_code != 200:
            return {}
        data   = r.json().get("optionChain", {}).get("result", [{}])
        if not data:
            return {}
        chain  = data[0]
        calls  = chain.get("options", [{}])[0].get("calls", [])
        puts   = chain.get("options", [{}])[0].get("puts",  [])
        price  = chain.get("quote", {}).get("regularMarketPrice", 0)
        return {"calls": calls, "puts": puts, "price": price}
    except Exception:
        return {}


def _analyze_chain(chain: Dict) -> Dict:
    if not chain:
        return {}

    calls = chain.get("calls", [])
    puts  = chain.get("puts",  [])
    price = chain.get("price", 0)

    call_vol = sum(c.get("volume", 0) or 0 for c in calls)
    put_vol  = sum(p.get("volume", 0) or 0 for p in puts)
    call_oi  = sum(c.get("openInterest", 0) or 0 for c in calls)
    put_oi   = sum(p.get("openInterest", 0) or 0 for p in puts)

    pc_ratio = round(put_vol / call_vol, 3) if call_vol > 0 else None
    pc_oi    = round(put_oi  / call_oi,  3) if call_oi  > 0 else None

    # Unusual options: volume > 3× open interest (fresh positioning)
    unusual_calls = [
        c for c in calls
        if (c.get("volume") or 0) > 3 * max(c.get("openInterest") or 1, 1)
        and (c.get("volume") or 0) > 500
    ]
    unusual_puts = [
        p for p in puts
        if (p.get("volume") or 0) > 3 * max(p.get("openInterest") or 1, 1)
        and (p.get("volume") or 0) > 500
    ]

    # Average IV across ATM options (±10% of current price)
    atm_ivs = []
    for opt in calls + puts:
        strike = opt.get("strike", 0)
        iv     = opt.get("impliedVolatility", 0) or 0
        if price and abs(strike - price) / price < 0.10 and iv > 0:
            atm_ivs.append(iv)
    avg_iv = round(sum(atm_ivs) / len(atm_ivs) * 100, 1) if atm_ivs else None

    # P/C ratio signal
    if pc_ratio is not None:
        if pc_ratio > 1.5:   pc_signal = "EXTREME_FEAR — heavy put buying, contrarian bullish"
        elif pc_ratio > 1.0: pc_signal = "BEARISH_BIAS — more puts than calls"
        elif pc_ratio > 0.7: pc_signal = "NEUTRAL"
        elif pc_ratio > 0.4: pc_signal = "BULLISH_BIAS — call buying dominant"
        else:                pc_signal = "EXTREME_GREED — heavy call buying"
    else:
        pc_signal = "UNKNOWN"

    return {
        "call_volume":     call_vol,
        "put_volume":      put_vol,
        "pc_ratio":        pc_ratio,
        "pc_oi_ratio":     pc_oi,
        "pc_signal":       pc_signal,
        "avg_iv_pct":      avg_iv,
        "unusual_calls":   len(unusual_calls),
        "unusual_puts":    len(unusual_puts),
        "unusual_signal": (
            "STRONG BUY SIGNAL — unusual call sweep" if len(unusual_calls) >= 3
            else "UNUSUAL CALL ACTIVITY" if len(unusual_calls) >= 1
            else "STRONG SELL SIGNAL — unusual put sweep" if len(unusual_puts) >= 3
            else "UNUSUAL PUT ACTIVITY" if len(unusual_puts) >= 1
            else "NORMAL"
        ),
        "top_unusual_calls": [
            {"strike": c.get("strike"), "expiry": c.get("expiration"),
             "volume": c.get("volume"), "oi": c.get("openInterest"),
             "iv": round((c.get("impliedVolatility") or 0)*100, 1)}
            for c in sorted(unusual_calls, key=lambda x: x.get("volume",0), reverse=True)[:3]
        ],
        "top_unusual_puts": [
            {"strike": p.get("strike"), "expiry": p.get("expiration"),
             "volume": p.get("volume"), "oi": p.get("openInterest"),
             "iv": round((p.get("impliedVolatility") or 0)*100, 1)}
            for p in sorted(unusual_puts, key=lambda x: x.get("volume",0), reverse=True)[:3]
        ],
    }


async def get_options_flow(tickers: List[str]) -> Dict[str, Dict]:
    """Analyze options flow for a list of tickers. Returns dict keyed by ticker."""
    sem = asyncio.Semaphore(20)

    async def fetch_one(ticker: str, client: httpx.AsyncClient) -> tuple:
        async with sem:
            chain = await _fetch_options_chain(ticker, client)
            return ticker, _analyze_chain(chain)

    async with httpx.AsyncClient(timeout=12) as client:
        results = await asyncio.gather(
            *[fetch_one(t, client) for t in tickers],
            return_exceptions=True,
        )

    return {ticker: data for item in results
            if isinstance(item, tuple)
            for ticker, data in [item] if data}


async def get_market_put_call() -> Dict:
    """SPY and QQQ put/call ratios as a market-wide sentiment gauge."""
    data = await get_options_flow(["SPY", "QQQ"])
    return {
        "spy": data.get("SPY", {}),
        "qqq": data.get("QQQ", {}),
        "market_sentiment": _market_sentiment(data),
    }


def _market_sentiment(data: Dict) -> str:
    spy_pc = (data.get("SPY") or {}).get("pc_ratio")
    qqq_pc = (data.get("QQQ") or {}).get("pc_ratio")
    if spy_pc is None and qqq_pc is None:
        return "UNKNOWN"
    avg = sum(x for x in [spy_pc, qqq_pc] if x is not None) / sum(1 for x in [spy_pc, qqq_pc] if x is not None)
    if avg > 1.3:   return "EXTREME_FEAR — market-wide put hedging, contrarian bullish"
    if avg > 1.0:   return "FEARFUL — defensive positioning"
    if avg > 0.7:   return "NEUTRAL"
    if avg > 0.5:   return "GREEDY — call buying dominant"
    return "EXTREME_GREED — dangerous complacency"
