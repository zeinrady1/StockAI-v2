"""
Company fundamentals via Alpha Vantage (25 free calls/day).
Fetches P/E, Forward P/E, EPS, Beta, analyst target, revenue/earnings growth,
profit margin, 52-week range, and recent earnings surprise history.

Cache strategy: 24-hour TTL per ticker. Fetches at most N uncached tickers
per call so we never burn the daily quota in one analysis run.
"""
import httpx, asyncio, os, time
from typing import Dict, List

_AV_KEY  = os.getenv("ALPHA_VANTAGE_KEY", "")
_BASE    = "https://www.alphavantage.co/query"
_CACHE:  Dict[str, Dict] = {}   # ticker → fundamentals dict
_CACHE_TS: Dict[str, float] = {}
_TTL     = 86400   # 24 hours
_MAX_FETCH_PER_CALL = 20   # stay safely within 25/day


async def _fetch_overview(ticker: str, client: httpx.AsyncClient) -> Dict:
    """Fetch OVERVIEW endpoint for one ticker."""
    try:
        r = await client.get(_BASE, params={
            "function": "OVERVIEW",
            "symbol": ticker,
            "apikey": _AV_KEY,
        }, timeout=12)
        if r.status_code != 200:
            return {}
        d = r.json()
        if not d or "Symbol" not in d:
            return {}

        def flt(v):
            try: return float(v)
            except: return None

        return {
            "ticker":             ticker,
            "name":               d.get("Name", ""),
            "sector":             d.get("Sector", ""),
            "industry":           d.get("Industry", ""),
            "pe_ratio":           flt(d.get("PERatio")),
            "forward_pe":         flt(d.get("ForwardPE")),
            "eps":                flt(d.get("EPS")),
            "beta":               flt(d.get("Beta")),
            "dividend_yield":     flt(d.get("DividendYield")),
            "analyst_target":     flt(d.get("AnalystTargetPrice")),
            "profit_margin":      flt(d.get("ProfitMargin")),
            "revenue_growth_yoy": flt(d.get("QuarterlyRevenueGrowthYOY")),
            "earnings_growth_yoy":flt(d.get("QuarterlyEarningsGrowthYOY")),
            "price_to_book":      flt(d.get("PriceToBookRatio")),
            "ev_to_ebitda":       flt(d.get("EVToEBITDA")),
            "52w_high":           flt(d.get("52WeekHigh")),
            "52w_low":            flt(d.get("52WeekLow")),
            "market_cap":         flt(d.get("MarketCapitalization")),
            "shares_outstanding": flt(d.get("SharesOutstanding")),
            "description":        (d.get("Description") or "")[:300],
        }
    except Exception:
        return {}


async def _fetch_earnings(ticker: str, client: httpx.AsyncClient) -> List[Dict]:
    """Fetch last 4 quarters of EPS vs estimate."""
    try:
        r = await client.get(_BASE, params={
            "function": "EARNINGS",
            "symbol": ticker,
            "apikey": _AV_KEY,
        }, timeout=12)
        if r.status_code != 200:
            return []
        quarters = r.json().get("quarterlyEarnings", [])[:4]
        out = []
        for q in quarters:
            def flt(v):
                try: return float(v)
                except: return None
            out.append({
                "date":       q.get("fiscalDateEnding", ""),
                "reported":   flt(q.get("reportedEPS")),
                "estimated":  flt(q.get("estimatedEPS")),
                "surprise_pct": flt(q.get("surprisePercentage")),
            })
        return out
    except Exception:
        return []


async def get_fundamentals(tickers: List[str]) -> Dict[str, Dict]:
    """
    Return fundamentals for the requested tickers.
    Hits Alpha Vantage only for uncached tickers, max _MAX_FETCH_PER_CALL per call.
    """
    if not _AV_KEY:
        return {}

    now = time.time()
    cached   = {t: _CACHE[t] for t in tickers if t in _CACHE and now - _CACHE_TS.get(t, 0) < _TTL}
    to_fetch = [t for t in tickers if t not in cached][:_MAX_FETCH_PER_CALL]

    if to_fetch:
        # Alpha Vantage rate limit: 5 req/min on free tier — throttle slightly
        async with httpx.AsyncClient(timeout=15) as client:
            for i, ticker in enumerate(to_fetch):
                if i > 0:
                    await asyncio.sleep(13)  # ~4.5 req/min to stay safe
                data = await _fetch_overview(ticker, client)
                if data:
                    _CACHE[ticker]    = data
                    _CACHE_TS[ticker] = now

    return {**cached, **{t: _CACHE[t] for t in to_fetch if t in _CACHE}}


async def get_earnings_surprises(ticker: str) -> List[Dict]:
    """Return last 4 quarters of earnings vs estimate for one ticker. Cached 24h."""
    key = f"earnings_{ticker}"
    now = time.time()
    if key in _CACHE and now - _CACHE_TS.get(key, 0) < _TTL:
        return _CACHE[key]
    if not _AV_KEY:
        return []
    async with httpx.AsyncClient(timeout=15) as client:
        data = await _fetch_earnings(ticker, client)
    if data:
        _CACHE[key]    = data
        _CACHE_TS[key] = now
    return data
