"""
Stock prices via Alpaca Market Data API (authenticated, fast, reliable).
Crypto prices via CoinGecko (free, no key required).
No Yahoo Finance — it's rate-limited and unreliable.
"""
import httpx, asyncio, os
from typing import List, Dict

_ALPACA_KEY    = os.getenv("ALPACA_API_KEY", "")
_ALPACA_SECRET = os.getenv("ALPACA_SECRET_KEY", "")
_ALPACA_HDR    = {
    "APCA-API-KEY-ID":     _ALPACA_KEY,
    "APCA-API-SECRET-KEY": _ALPACA_SECRET,
}

# CoinGecko coin ID for each Yahoo-style ticker
_CRYPTO_ID_MAP = {
    "BTC-USD":   "bitcoin",
    "ETH-USD":   "ethereum",
    "SOL-USD":   "solana",
    "BNB-USD":   "binancecoin",
    "XRP-USD":   "ripple",
    "ADA-USD":   "cardano",
    "DOGE-USD":  "dogecoin",
    "AVAX-USD":  "avalanche-2",
    "DOT-USD":   "polkadot",
    "LINK-USD":  "chainlink",
    "MATIC-USD": "matic-network",
    "UNI-USD":   "uniswap",
    "LTC-USD":   "litecoin",
    "ATOM-USD":  "cosmos",
    "NEAR-USD":  "near",
    "SUI-USD":   "sui",
    "APT-USD":   "aptos",
    "ARB-USD":   "arbitrum",
    "OP-USD":    "optimism",
    "INJ-USD":   "injective-protocol",
    "SHIB-USD":  "shiba-inu",
    "PEPE-USD":  "pepe",
    "TON-USD":   "the-open-network",
    "TRX-USD":   "tron",
    "BCH-USD":   "bitcoin-cash",
    "HBAR-USD":  "hedera-hashgraph",
    "FIL-USD":   "filecoin",
    "ICP-USD":   "internet-computer",
    "STX-USD":   "blockstack",
    "VET-USD":   "vechain",
}

_CRYPTO_WATCHLIST = [
    "BTC-USD","ETH-USD","SOL-USD","BNB-USD","XRP-USD","ADA-USD",
    "DOGE-USD","AVAX-USD","LINK-USD","MATIC-USD","DOT-USD","UNI-USD",
    "LTC-USD","ATOM-USD","NEAR-USD","SUI-USD","APT-USD","ARB-USD",
]

_STOCK_WATCHLIST = [
    # Mega-cap core
    "AAPL","MSFT","NVDA","AMZN","GOOGL","GOOG","META","TSLA","AVGO","JPM",
    "LLY","V","UNH","XOM","MA","JNJ","COST","HD","PG","NFLX","WMT","BAC",
    "CRM","ABBV","CVX","ORCL","MRK","ACN","AMD","ADBE","KO","TMO","CSCO",
    "WFC","NOW","IBM","GE","PM","MS","INTU","AXP","ISRG","RTX","GS","CAT",
    "BKNG","SPGI","BLK","AMGN","SYK","PLD","VRTX","T","DE","UBER","MMC",
    "CB","C","BSX","ADI","SCHW","SO","AMAT","ADP","PGR","LRCX","TJX",
    "REGN","FI","MDLZ","BX","ETN","ZTS","PANW","CI","MU","SLB","HCA",
    "ITW","CME","MCO","EOG","KLAC","DHR","DUK","GD","SNPS","APH","NOC",
    "USB","WM","TT","PH","MSI","CDNS","WELL","NKE","MMM","EMR","PYPL",
    # High-interest stocks
    "PLTR","HOOD","COIN","SOFI","RIVN","NIO","LCID","F","GM","DIS",
    "SPOT","SNAP","PINS","RBLX","DKNG","APP","CRWD","SNOW","MSTR","ARM",
    "SMCI","DELL","HPQ","INTC","QCOM","MRVL","MPWR","WOLF","ON",
    # ETFs / indexes
    "SPY","QQQ","IWM","DIA","VTI","XLK","XLF","XLE","XLV","XLI",
    "XLP","XLU","XLB","XLY","XLRE","GLD","SLV","TLT","IEF","HYG",
]


async def _alpaca_batch(tickers: List[str], client: httpx.AsyncClient) -> Dict[str, Dict]:
    """Fetch one batch from Alpaca snapshots endpoint."""
    try:
        r = await client.get(
            "https://data.alpaca.markets/v2/stocks/snapshots",
            headers=_ALPACA_HDR,
            params={"symbols": ",".join(tickers), "feed": "iex"},
            timeout=20,
        )
        if r.status_code != 200:
            return {}
        data = r.json()
        if not isinstance(data, dict):
            return {}
        out = {}
        for sym, snap in data.items():
            lt    = snap.get("latestTrade") or {}
            daily = snap.get("dailyBar") or {}
            prev  = snap.get("prevDailyBar") or {}
            price = lt.get("p") or daily.get("c") or 0
            prev_c = prev.get("c") or 0
            chg    = round((price - prev_c) / prev_c * 100, 2) if prev_c else 0
            out[sym] = {
                "ticker":     sym,
                "name":       sym,
                "price":      round(float(price), 2),
                "prev_close": round(float(prev_c), 2),
                "change_pct": chg,
                "volume":     int(daily.get("v") or 0),
                "market_cap": 0,
                "avg_volume": 0,
                "52w_high":   0,
                "52w_low":    0,
            }
        return out
    except Exception:
        return {}


async def _fetch_alpaca(tickers: List[str]) -> Dict[str, Dict]:
    """Fetch Alpaca snapshots in batches of 500."""
    if not tickers:
        return {}
    async with httpx.AsyncClient(timeout=25) as client:
        batches = [tickers[i:i+500] for i in range(0, len(tickers), 500)]
        results = await asyncio.gather(*[_alpaca_batch(b, client) for b in batches],
                                       return_exceptions=True)
    out = {}
    for r in results:
        if isinstance(r, dict):
            out.update(r)
    return out


async def _fetch_coingecko(crypto_tickers: List[str]) -> Dict[str, Dict]:
    """Fetch crypto prices from CoinGecko."""
    if not crypto_tickers:
        return {}
    ids = [_CRYPTO_ID_MAP[t] for t in crypto_tickers if t in _CRYPTO_ID_MAP]
    id_to_ticker = {v: k for k, v in _CRYPTO_ID_MAP.items()}
    if not ids:
        return {}
    try:
        async with httpx.AsyncClient(timeout=15) as client:
            r = await client.get(
                "https://api.coingecko.com/api/v3/coins/markets",
                params={
                    "vs_currency": "usd",
                    "ids": ",".join(ids),
                    "order": "market_cap_desc",
                    "per_page": 250,
                    "price_change_percentage": "24h",
                },
                timeout=15,
            )
            if r.status_code != 200:
                return {}
            coins = r.json()
        out = {}
        for c in coins:
            ticker = id_to_ticker.get(c.get("id", ""))
            if not ticker:
                continue
            price = float(c.get("current_price") or 0)
            chg24 = float(c.get("price_change_percentage_24h") or 0)
            prev  = price / (1 + chg24 / 100) if price and chg24 != -100 else price
            out[ticker] = {
                "ticker":     ticker,
                "name":       c.get("name", ticker),
                "price":      price,
                "prev_close": round(prev, 6),
                "change_pct": round(chg24, 2),
                "volume":     int(c.get("total_volume") or 0),
                "market_cap": int(c.get("market_cap") or 0),
                "52w_high":   float(c.get("ath") or 0),
                "52w_low":    float(c.get("atl") or 0),
                "avg_volume": 0,
            }
        return out
    except Exception:
        return {}


async def get_prices(extra_tickers: List[str] = None) -> Dict[str, Dict]:
    """Fetch prices for watchlist + any extra signal tickers."""
    all_tickers = list(dict.fromkeys(
        _STOCK_WATCHLIST + _CRYPTO_WATCHLIST + (extra_tickers or [])
    ))
    crypto = [t for t in all_tickers if t.endswith("-USD")]
    stocks = [t for t in all_tickers if not t.endswith("-USD")]

    stock_data, crypto_data = await asyncio.gather(
        _fetch_alpaca(stocks),
        _fetch_coingecko(crypto),
    )
    return {**stock_data, **crypto_data}
