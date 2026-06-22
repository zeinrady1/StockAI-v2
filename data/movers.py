"""
Market movers, trending stocks, and sentiment data from free sources.
- Yahoo Finance: 8 predefined screeners (gainers, losers, active, growth, etc.)
- Yahoo Finance Trending US
- StockTwits trending
- Fear & Greed Index (alternative.me)
"""
import httpx, asyncio
from typing import List, Dict

_YF_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
}
_ST_HEADERS  = {"User-Agent": "Mozilla/5.0"}
_FG_HEADERS  = {"User-Agent": "Mozilla/5.0"}

_SCREENER_BASE  = "https://query1.finance.yahoo.com/v1/finance/screener/predefined/saved"
_TRENDING_URL   = "https://query1.finance.yahoo.com/v1/finance/trending/US"
_STOCKTWITS_URL = "https://api.stocktwits.com/api/2/trending/symbols.json"
_FEAR_GREED_URL = "https://api.alternative.me/fng/?limit=1"

# (scrId, display label) — keep list short to avoid Yahoo Finance 429s
_SCREENERS = [
    ("day_gainers",              "Day Gainers"),
    ("day_losers",               "Day Losers"),
    ("most_actives",             "Most Active"),
    ("small_cap_gainers",        "Small Cap Gainers"),
    ("growth_technology_stocks", "Tech Growth"),
]


def _parse_screener(data: dict, label: str) -> List[Dict]:
    results = data.get("finance", {}).get("result") or []
    if not results:
        return []
    out = []
    for q in results[0].get("quotes", []):
        out.append({
            "ticker":     q.get("symbol", ""),
            "name":       q.get("shortName", q.get("symbol", "")),
            "price":      round(q.get("regularMarketPrice", 0), 2),
            "change":     round(q.get("regularMarketChange", 0), 2),
            "change_pct": round(q.get("regularMarketChangePercent", 0), 2),
            "volume":     q.get("regularMarketVolume", 0),
            "market_cap": q.get("marketCap", 0),
            "category":   label,
        })
    return out


async def get_movers() -> Dict:
    result: Dict = {
        "gainers":     [],
        "losers":      [],
        "most_active": [],
        "screeners":   {},
        "trending":    [],
        "fear_greed":  None,
    }

    async with httpx.AsyncClient(timeout=20, follow_redirects=True) as client:
        # Screeners — strictly sequential with delay to avoid Yahoo Finance 429s
        for sid, label in _SCREENERS:
            try:
                r = await client.get(_SCREENER_BASE, headers=_YF_HEADERS,
                                     params={"scrIds": sid, "count": "100",
                                             "region": "US", "lang": "en-US"})
                if r.status_code == 200:
                    stocks = _parse_screener(r.json(), label)
                    result["screeners"][sid] = {"label": label, "stocks": stocks}
                    if sid == "day_gainers":
                        result["gainers"] = stocks
                    elif sid == "day_losers":
                        result["losers"] = stocks
                    elif sid == "most_actives":
                        result["most_active"] = stocks
            except Exception:
                pass
            await asyncio.sleep(1.5)  # stay under Yahoo Finance rate limit

        # Non-YF requests — all parallel
        other_responses = await asyncio.gather(
            client.get(_TRENDING_URL, headers=_YF_HEADERS, params={"count": "50"}),
            client.get(_STOCKTWITS_URL, headers=_ST_HEADERS),
            client.get(_FEAR_GREED_URL, headers=_FG_HEADERS),
            return_exceptions=True,
        )

    # Trending (Yahoo)
    trending_resp = other_responses[0]
    if not isinstance(trending_resp, Exception) and getattr(trending_resp, 'status_code', 0) == 200:
        try:
            syms = trending_resp.json().get("finance", {}).get("result", [{}])[0].get("quotes", [])
            for s in syms:
                sym = s.get("symbol", "")
                if sym and not sym.endswith("-USD") and "=" not in sym:
                    result["trending"].append(sym)
        except Exception:
            pass

    # StockTwits
    twits_resp = other_responses[1]
    if not isinstance(twits_resp, Exception) and getattr(twits_resp, 'status_code', 0) == 200:
        try:
            for t in twits_resp.json().get("symbols", []):
                sym = t.get("symbol", "")
                if sym and not sym.endswith(".X") and sym.isalpha():
                    result["trending"].append(sym)
        except Exception:
            pass

    result["trending"] = list(dict.fromkeys(result["trending"]))

    # Fear & Greed
    fg_resp = other_responses[2]
    if not isinstance(fg_resp, Exception) and getattr(fg_resp, 'status_code', 0) == 200:
        try:
            fg = fg_resp.json().get("data", [{}])[0]
            result["fear_greed"] = {
                "score": int(fg.get("value", 50)),
                "label": fg.get("value_classification", "Neutral"),
            }
        except Exception:
            pass

    return result
