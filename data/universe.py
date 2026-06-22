"""
Complete market universe:
  - US equities (13,000+ tradable): Alpaca asset list (NYSE, NASDAQ, AMEX, OTC)
    enriched with sector/industry/market_cap from NASDAQ screener
  - Top 500 crypto: CoinGecko markets API
Cached 4 hours for equities, 2 hours for crypto, 12 hours for sector data.
"""
import httpx, asyncio, os, time
from typing import List, Dict

_ALPACA_KEY    = os.getenv("ALPACA_API_KEY", "")
_ALPACA_SECRET = os.getenv("ALPACA_SECRET_KEY", "")
_ALPACA_HDR    = {
    "APCA-API-KEY-ID":     _ALPACA_KEY,
    "APCA-API-SECRET-KEY": _ALPACA_SECRET,
}

_STOCK_TTL  = 4  * 3600
_CRYPTO_TTL = 2  * 3600
_SECTOR_TTL = 12 * 3600

_stock_cache:  List[Dict] = []
_crypto_cache: List[Dict] = []
_sector_map:   Dict       = {}   # ticker → {sector, industry, market_cap}
_stock_ts:  float = 0
_crypto_ts: float = 0
_sector_ts: float = 0


async def _fetch_nasdaq_sectors() -> Dict:
    """Fetch sector, industry, and market_cap for all US-listed stocks from NASDAQ screener."""
    try:
        async with httpx.AsyncClient(timeout=20) as client:
            r = await client.get(
                "https://api.nasdaq.com/api/screener/stocks",
                params={"tableonly": "true", "offset": "0", "download": "true"},
                headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"},
                timeout=20,
            )
            if r.status_code != 200:
                return {}
            rows = r.json().get("data", {}).get("rows") or []
            out: Dict = {}
            for row in rows:
                sym = (row.get("symbol") or "").strip().upper()
                if not sym:
                    continue
                mc_raw = (row.get("marketCap") or "").replace(",", "").replace("$", "").strip()
                try:
                    mc = int(float(mc_raw)) if mc_raw else 0
                except ValueError:
                    mc = 0
                out[sym] = {
                    "sector":     row.get("sector", "") or "",
                    "industry":   row.get("industry", "") or "",
                    "market_cap": mc,
                }
            return out
    except Exception:
        return {}


async def _ensure_sectors():
    global _sector_map, _sector_ts
    if _sector_map and (time.time() - _sector_ts) < _SECTOR_TTL:
        return
    data = await _fetch_nasdaq_sectors()
    if data:
        _sector_map = data
        _sector_ts  = time.time()


async def _fetch_alpaca_assets() -> List[Dict]:
    """Fetch all active tradable US equities from Alpaca."""
    try:
        async with httpx.AsyncClient(timeout=30) as client:
            r = await client.get(
                "https://paper-api.alpaca.markets/v2/assets",
                headers=_ALPACA_HDR,
                params={"status": "active", "asset_class": "us_equity"},
                timeout=30,
            )
            if r.status_code != 200:
                return []
            assets = r.json()
            if not isinstance(assets, list):
                return []

        out = []
        for a in assets:
            sym = (a.get("symbol") or "").strip().upper()
            if not sym or "/" in sym or len(sym) > 6:
                continue
            out.append({
                "ticker":     sym,
                "name":       a.get("name", sym),
                "exchange":   a.get("exchange", ""),
                "sector":     "",
                "industry":   "",
                "country":    "US",
                "market_cap": 0,
                "price":      0,
                "change_pct": 0,
                "type":       "stock",
                "tradable":   a.get("tradable", False),
            })
        return sorted(out, key=lambda x: x["ticker"])
    except Exception:
        return []


async def _fetch_coingecko_universe() -> List[Dict]:
    """Fetch top 250 crypto by market cap from CoinGecko."""
    try:
        all_coins = []
        async with httpx.AsyncClient(timeout=20) as client:
            for page in (1, 2):
                r = await client.get(
                    "https://api.coingecko.com/api/v3/coins/markets",
                    params={
                        "vs_currency": "usd",
                        "order": "market_cap_desc",
                        "per_page": 250,
                        "page": page,
                        "sparkline": False,
                    },
                    timeout=15,
                )
                if r.status_code == 200:
                    all_coins.extend(r.json())
                await asyncio.sleep(0.5)   # respect CoinGecko rate limit

        out = []
        for c in all_coins:
            sym = (c.get("symbol") or "").upper()
            if not sym:
                continue
            ticker = f"{sym}-USD"
            out.append({
                "ticker":      ticker,
                "name":        c.get("name", sym),
                "exchange":    "CRYPTO",
                "sector":      "Cryptocurrency",
                "industry":    c.get("id", ""),
                "country":     "",
                "market_cap":  int(c.get("market_cap") or 0),
                "price":       float(c.get("current_price") or 0),
                "change_pct":  round(float(c.get("price_change_percentage_24h") or 0), 2),
                "type":        "crypto",
                "coingecko_id": c.get("id", ""),
                "tradable":    True,
            })
        return out
    except Exception:
        return []


async def _ensure_stocks():
    global _stock_cache, _stock_ts
    if _stock_cache and (time.time() - _stock_ts) < _STOCK_TTL:
        return
    stocks, _ = await asyncio.gather(_fetch_alpaca_assets(), _ensure_sectors())
    if stocks:
        for s in stocks:
            info = _sector_map.get(s["ticker"])
            if info:
                s["sector"]     = info["sector"]
                s["industry"]   = info["industry"]
                s["market_cap"] = info["market_cap"]
        _stock_cache = stocks
        _stock_ts    = time.time()


async def _ensure_crypto():
    global _crypto_cache, _crypto_ts
    if _crypto_cache and (time.time() - _crypto_ts) < _CRYPTO_TTL:
        return
    crypto = await _fetch_coingecko_universe()
    if crypto:
        _crypto_cache = crypto
        _crypto_ts    = time.time()


async def get_universe(force_refresh: bool = False) -> List[Dict]:
    """Return all stocks + crypto combined."""
    if force_refresh:
        global _stock_ts, _crypto_ts
        _stock_ts = _crypto_ts = 0
    await asyncio.gather(_ensure_stocks(), _ensure_crypto())
    return _stock_cache + _crypto_cache


async def search(query: str, limit: int = 25) -> List[Dict]:
    """Search stocks and crypto by ticker or name. Results ordered:
    exact match → ticker starts-with (alpha) → name starts-with (alpha) → name contains (alpha).
    """
    await asyncio.gather(_ensure_stocks(), _ensure_crypto())
    q = query.strip().upper()
    if not q:
        return []

    # Only tradable stocks + all crypto
    items = [s for s in _stock_cache + _crypto_cache
             if s.get("tradable") or s.get("type") == "crypto"]

    def norm(ticker: str) -> str:
        return ticker[:-4] if ticker.endswith("-USD") else ticker

    exact        = [s for s in items if norm(s["ticker"]) == q or s["ticker"] == q]
    starts       = sorted(
                     [s for s in items if norm(s["ticker"]).startswith(q) and s not in exact],
                     key=lambda s: norm(s["ticker"]))
    def _name_key(s):
        is_crypto = 1 if s.get("type") == "crypto" else 0
        return (is_crypto, len(s["name"]), s["name"])

    name_starts  = sorted(
                     [s for s in items if s["name"].upper().startswith(q)
                      and s not in exact and s not in starts],
                     key=_name_key)
    name_contains= sorted(
                     [s for s in items if q in s["name"].upper()
                      and s not in exact and s not in starts and s not in name_starts],
                     key=lambda s: (s.get("type") == "crypto",
                                    s["name"].upper().index(q), len(s["name"]), s["name"]))

    # Sector/industry match — top stocks in that sector by market cap desc
    # Normalize spaces so "healthcare" matches "Health Care", "realEstate" matches "Real Estate"
    ql     = query.strip().lower()
    ql_ns  = ql.replace(" ", "")   # query with no spaces

    def _sector_hit(s) -> bool:
        sec = (s.get("sector")   or "").lower().replace(" ", "")
        ind = (s.get("industry") or "").lower().replace(" ", "")
        return ql_ns in sec or ql_ns in ind

    seen_ids = {id(s) for s in exact + starts + name_starts}
    sector_match = sorted(
        [s for s in items if id(s) not in seen_ids and _sector_hit(s)],
        key=lambda s: -(s.get("market_cap") or 0),
    )
    # name_contains excludes everything above
    seen_ids2 = seen_ids | {id(s) for s in sector_match}
    name_contains_final = [s for s in name_contains if id(s) not in seen_ids2]

    return (exact + starts + name_starts + sector_match + name_contains_final)[:limit]
