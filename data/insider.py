"""
Insider trades scraped from OpenInsider.com.
- In-memory cache (30-min TTL) so repeated calls are instant
- Pre-warmed on startup so the first "Refresh Intel" click is fast
"""
import httpx, asyncio, re, time
from typing import List, Dict
from datetime import datetime, timedelta

_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}

_BASE       = "http://openinsider.com"
_SIMPLE_URL = _BASE + "/screener?s=&cnt=200&page={page}"
_SCREENERS  = [
    (_BASE + "/screener?s=&o=&pl=&ph=&ll=100000&lh=&fd=0&td=0&tdr=&fdlyl=&fdlyh=&daysago=&xp=1&xs=0&vl=&vh=&ocl=&och=&sic1=-1&sicl=100&sich=9999&grp=0&nfl=&nfh=&nil=&nih=&nol=&noh=&v2l=&v2h=&oc2l=&oc2h=&sortcol=0&cnt=100&Action=1&page={page}", "big_buy"),
    (_BASE + "/screener?s=&o=&pl=&ph=&ll=100000&lh=&fd=0&td=0&tdr=&fdlyl=&fdlyh=&daysago=&xp=0&xs=1&vl=&vh=&ocl=&och=&sic1=-1&sicl=100&sich=9999&grp=0&nfl=&nfh=&nil=&nih=&nol=&noh=&v2l=&v2h=&oc2l=&oc2h=&sortcol=0&cnt=100&Action=1&page={page}", "big_sell"),
]

_cache:    List[Dict] = []
_cache_ts: float      = 0
_CACHE_TTL            = 5 * 60    # 5 minutes
_fetching             = False


def _clean(s: str) -> str:
    return re.sub(r'<[^>]+>', '', s).strip().replace('\n', '').replace('\t', '').replace('\r', '')


def _parse_page(html: str) -> List[Dict]:
    tbodies = re.findall(r'<tbody>(.*?)</tbody>', html, re.DOTALL)
    if len(tbodies) < 2:
        return []
    rows   = re.findall(r'<tr[^>]*>(.*?)</tr>', tbodies[1], re.DOTALL)
    trades = []
    for row in rows:
        cells = re.findall(r'<td[^>]*>(.*?)</td>', row, re.DOTALL)
        if len(cells) < 12:
            continue
        ticker_m = re.search(r'href="/([A-Za-z]{1,5})"', cells[3])
        if not ticker_m:
            continue
        ticker = ticker_m.group(1).upper()
        if len(ticker) > 5 or not ticker.isalpha():
            continue
        tt = _clean(cells[7]).strip()
        if tt.startswith('P'):
            action = 'BUY'
        elif tt.startswith('S'):
            action = 'SELL'
        else:
            continue
        try:
            price = float(_clean(cells[8]).replace('$','').replace(',','') or 0)
            qty   = abs(int(float(_clean(cells[9]).replace(',','').replace('+','') or 0)))
            val   = abs(float(_clean(cells[12]).replace('$','').replace(',','').replace('+','').lstrip('-') or 0))
        except Exception:
            price, qty, val = 0, 0, 0
        trades.append({
            "ticker":  ticker,
            "company": _clean(cells[4]),
            "insider": _clean(cells[5]),
            "role":    _clean(cells[6]),
            "transactions": [{"date": _clean(cells[2])[:10], "action": action,
                              "shares": qty, "price": round(price,2), "value": round(val,2)}],
            "filed": _clean(cells[1])[:10],
        })
    return trades


async def _fetch_url(url: str, client: httpx.AsyncClient, sem: asyncio.Semaphore) -> List[Dict]:
    async with sem:
        try:
            r = await client.get(url, headers=_HEADERS, timeout=8, follow_redirects=True)
            return _parse_page(r.text) if r.status_code == 200 else []
        except Exception:
            return []


async def _fetch_all() -> List[Dict]:
    """Fetch from OpenInsider — 20 main pages + big-buy/sell extras."""
    urls = [_SIMPLE_URL.format(page=p) for p in range(1, 21)]
    for tpl, _ in _SCREENERS:
        for p in range(1, 4):
            urls.append(tpl.format(page=p))

    sem = asyncio.Semaphore(20)
    async with httpx.AsyncClient(timeout=10, follow_redirects=True) as client:
        results = await asyncio.gather(*[_fetch_url(u, client, sem) for u in urls],
                                       return_exceptions=True)

    seen, trades = set(), []
    for result in results:
        if isinstance(result, Exception):
            continue
        for t in result:
            key = (t["ticker"], t["insider"], t.get("filed",""), t["transactions"][0]["action"])
            if key not in seen:
                seen.add(key)
                trades.append(t)

    trades.sort(key=lambda t: t.get("filed",""), reverse=True)
    return trades


async def warm_cache():
    """Pre-fetch on startup so the first user request is instant."""
    global _cache, _cache_ts
    await asyncio.sleep(5)
    if not _cache:
        _cache    = await _fetch_all()
        _cache_ts = time.time()


async def get_insider_trades(days: int = 3650, max_filings: int = 4000) -> List[Dict]:
    """Return cached insider trades, refreshing if the cache is older than 30 minutes."""
    global _cache, _cache_ts, _fetching

    if _cache and (time.time() - _cache_ts) < _CACHE_TTL:
        return _cache[:max_filings]

    if _fetching:
        await asyncio.sleep(0.3)
        return _cache[:max_filings] if _cache else []

    _fetching = True
    try:
        _cache    = await _fetch_all()
        _cache_ts = time.time()
    except Exception:
        pass
    finally:
        _fetching = False

    if days < 9999 and _cache:
        cutoff   = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
        filtered = [t for t in _cache if t.get("filed","9999") >= cutoff]
        if filtered:
            return filtered[:max_filings]

    return _cache[:max_filings]
