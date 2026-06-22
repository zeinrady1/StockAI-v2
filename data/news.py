"""
News from two sources:
  1. Google News RSS (60+ queries, no key, broad coverage)
  2. Polygon.io news API (ticker-specific, includes sentiment scores)
Cached 2 minutes so frequent auto-refresh polls don't hammer RSS feeds.
"""
import httpx, asyncio, os, time, xml.etree.ElementTree as ET
from typing import List, Dict

_POLY_KEY = os.getenv("POLYGON_KEY", "")

_NEWS_TTL    = 2 * 60   # 2 minutes
_news_cache: List[Dict] = []
_news_ts:    float      = 0

_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/rss+xml, application/xml, text/xml, */*",
}

_MARKET_QUERIES = [
    # Macro / indices
    "S&P 500 stock market today",
    "Nasdaq Dow Jones market",
    "federal reserve interest rates economy",
    "inflation CPI GDP recession",
    "treasury yields bond market",
    "stock market news today",
    "Wall Street trading session",
    "market open premarket futures",

    # Sectors
    "technology AI semiconductor stocks",
    "energy oil gas stocks",
    "financial bank stocks earnings",
    "healthcare pharma biotech FDA",
    "consumer retail e-commerce stocks",
    "real estate REIT housing market",
    "defense aerospace military stocks",
    "utilities clean energy stocks",
    "industrials manufacturing stocks",
    "materials mining commodity stocks",
    "software cloud SaaS stocks",
    "electric vehicle EV battery stocks",
    "cybersecurity data breach stocks",
    "space satellite tech stocks",
    "genomics CRISPR biotech stocks",
    "fintech payments digital banking stocks",

    # Top individual stocks
    "NVDA Nvidia stock news",
    "AAPL Apple stock news",
    "MSFT Microsoft stock news",
    "TSLA Tesla stock news",
    "AMZN Amazon stock news",
    "META Facebook stock news",
    "GOOGL Alphabet Google stock news",
    "AMD stock news earnings",
    "PLTR Palantir stock news",
    "COIN Coinbase stock news",

    # Trading signals
    "earnings report beat miss guidance",
    "stock buyback dividend increase",
    "IPO SPAC merger acquisition deal",
    "short squeeze options unusual activity",
    "hedge fund institutional 13F filing",
    "insider buying selling SEC Form 4",
    "congress senator representative stock trade",
    "analyst upgrade downgrade price target",
    "options flow unusual call put activity",
    "dark pool large block trade",

    # Macro events
    "tariffs trade war China economy",
    "dollar index forex currency market",
    "crypto bitcoin ethereum market",
    "commodities gold silver oil price",
    "earnings season Wall Street forecast",
    "market rally selloff volatility VIX",
    "economic data jobs report employment",
    "geopolitical risk war sanctions market",
    "supply chain disruption shortage market",
    "AI artificial intelligence investment stocks",
    "federal budget debt ceiling market",
    "bank failure credit crisis market",
    "housing mortgage rates affordability",
    "pension fund sovereign wealth allocation",
]


async def get_market_news() -> List[Dict]:
    """Fetch all market news (2-minute cache so rapid polls don't hit RSS)."""
    global _news_cache, _news_ts
    if _news_cache and (time.time() - _news_ts) < _NEWS_TTL:
        return _news_cache

    articles = []
    seen     = set()

    async with httpx.AsyncClient(timeout=6, follow_redirects=True) as client:
        async def fetch_query(q: str) -> List[Dict]:
            url = f"https://news.google.com/rss/search?q={q.replace(' ','+')}&hl=en-US&gl=US&ceid=US:en"
            try:
                r = await client.get(url, headers=_HEADERS)
                if r.status_code != 200:
                    return []
                root = ET.fromstring(r.content)
                out = []
                for item in root.findall(".//item"):
                    title = item.findtext("title", "")
                    link  = item.findtext("link", "")
                    pub   = item.findtext("pubDate", "")
                    src   = item.findtext("source", "")
                    if title and title not in seen:
                        seen.add(title)
                        out.append({"title": title, "link": link,
                                    "published": pub, "source": src, "topic": q})
                return out
            except Exception:
                return []

        # Fire all queries in parallel — 6s timeout keeps total under 8s even on slow queries
        results = await asyncio.gather(*[fetch_query(q) for q in _MARKET_QUERIES],
                                       return_exceptions=True)
        for page in results:
            if isinstance(page, list):
                articles.extend(page)

    if articles:
        _news_cache = articles
        _news_ts    = time.time()
    return articles


async def _polygon_ticker_news(tickers: List[str]) -> List[Dict]:
    """Polygon news API — ticker-tagged with sentiment scores (positive/negative/neutral)."""
    if not _POLY_KEY or not tickers:
        return []
    articles = []
    seen     = set()
    # Polygon allows filtering by multiple tickers via repeated calls or comma-separated
    sem = asyncio.Semaphore(8)

    async def fetch_one(ticker: str, client: httpx.AsyncClient) -> List[Dict]:
        async with sem:
            try:
                r = await client.get(
                    "https://api.polygon.io/v2/reference/news",
                    params={"ticker": ticker, "limit": 5, "apiKey": _POLY_KEY},
                    timeout=8,
                )
                if r.status_code != 200:
                    return []
                out = []
                for a in r.json().get("results", []):
                    title = a.get("title", "")
                    if not title or title in seen:
                        continue
                    seen.add(title)
                    # Extract sentiment from insights array
                    sentiment = ""
                    for ins in (a.get("insights") or []):
                        if ins.get("ticker") == ticker:
                            sentiment = ins.get("sentiment", "")
                            break
                    out.append({
                        "ticker":    ticker,
                        "title":     title,
                        "link":      a.get("article_url", ""),
                        "published": a.get("published_utc", ""),
                        "source":    a.get("publisher", {}).get("name", ""),
                        "sentiment": sentiment,   # positive / negative / neutral
                    })
                return out
            except Exception:
                return []

    async with httpx.AsyncClient(timeout=10) as client:
        results = await asyncio.gather(*[fetch_one(t, client) for t in tickers],
                                       return_exceptions=True)
    for page in results:
        if isinstance(page, list):
            articles.extend(page)
    return articles


async def get_ticker_news(tickers: List[str]) -> List[Dict]:
    """Fetch news for tickers from Google RSS + Polygon (with sentiment)."""
    articles = []
    seen     = set()

    # Google RSS (fast, broad)
    async with httpx.AsyncClient(timeout=15, follow_redirects=True) as client:
        async def fetch_google(ticker: str) -> List[Dict]:
            url = f"https://news.google.com/rss/search?q={ticker}+stock&hl=en-US&gl=US&ceid=US:en"
            try:
                r = await client.get(url, headers=_HEADERS)
                if r.status_code != 200:
                    return []
                root = ET.fromstring(r.content)
                out = []
                for item in root.findall(".//item"):
                    title = item.findtext("title", "")
                    link  = item.findtext("link", "")
                    if title and title not in seen:
                        seen.add(title)
                        out.append({"ticker": ticker, "title": title,
                                    "link": link, "sentiment": ""})
                return out
            except Exception:
                return []

        google_results = await asyncio.gather(*[fetch_google(t) for t in tickers])
        for page in google_results:
            articles.extend(page)

    # Polygon news with sentiment (top 50 tickers only — rate conscious)
    poly_articles = await _polygon_ticker_news(tickers[:50])
    for a in poly_articles:
        if a["title"] not in seen:
            seen.add(a["title"])
            articles.append(a)

    return articles
