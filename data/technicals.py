"""
Technical indicators calculated from Yahoo Finance historical OHLCV data.
Computes: RSI, MACD, Bollinger Bands, EMAs (20/50/200), Golden/Death Cross,
          Volume ratio, ATR, momentum, support/resistance levels.
In-memory cache with 1-hour TTL per ticker.

Yahoo Finance v8/chart requires a session cookie. We fetch one on first use
and refresh every 25 minutes.
"""
import httpx, asyncio, os, time
from typing import Dict, List, Optional, Tuple

_CACHE: Dict[str, Dict] = {}
_CACHE_TS: Dict[str, float] = {}
_TTL = 3600  # 1 hour

_YF_SESSION: Dict = {}   # {"cookies": {...}, "ts": float}
_YF_COOKIE_TTL = 1500    # 25 minutes

_UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"


async def _get_yahoo_cookies() -> Dict:
    """Fetch Yahoo Finance session cookies (required for v8/chart API)."""
    global _YF_SESSION
    now = time.time()
    if _YF_SESSION and now - _YF_SESSION.get("ts", 0) < _YF_COOKIE_TTL:
        return _YF_SESSION.get("cookies", {})
    try:
        async with httpx.AsyncClient(timeout=10, follow_redirects=True) as client:
            r = await client.get(
                "https://finance.yahoo.com",
                headers={
                    "User-Agent": _UA,
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                    "Accept-Language": "en-US,en;q=0.5",
                },
            )
            cookies = dict(r.cookies)
            _YF_SESSION = {"cookies": cookies, "ts": now}
            return cookies
    except Exception:
        return {}


def _yf_headers(cookies: Dict, ticker: str = "") -> Dict:
    return {
        "User-Agent": _UA,
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "en-US,en;q=0.5",
        "Referer": f"https://finance.yahoo.com/quote/{ticker}/" if ticker else "https://finance.yahoo.com/",
        "Cookie": "; ".join(f"{k}={v}" for k, v in cookies.items()),
    }


# ── Math helpers ─────────────────────────────────────────────────────────────

def _ema_series(values: List[float], period: int) -> List[float]:
    if len(values) < period:
        return []
    k = 2 / (period + 1)
    emas = [sum(values[:period]) / period]
    for v in values[period:]:
        emas.append(v * k + emas[-1] * (1 - k))
    return emas


def calc_rsi(closes: List[float], period: int = 14) -> Optional[float]:
    if len(closes) < period + 1:
        return None
    deltas = [closes[i] - closes[i-1] for i in range(1, len(closes))]
    gains  = [max(d, 0) for d in deltas]
    losses = [max(-d, 0) for d in deltas]
    avg_g  = sum(gains[:period]) / period
    avg_l  = sum(losses[:period]) / period
    for i in range(period, len(gains)):
        avg_g = (avg_g * (period - 1) + gains[i]) / period
        avg_l = (avg_l * (period - 1) + losses[i]) / period
    if avg_l == 0:
        return 100.0
    rs = avg_g / avg_l
    return round(100 - (100 / (1 + rs)), 2)


def calc_macd(closes: List[float]) -> Tuple[Optional[float], Optional[float], Optional[float]]:
    """Returns (macd_line, signal_line, histogram)."""
    if len(closes) < 35:
        return None, None, None
    ema12 = _ema_series(closes, 12)
    ema26 = _ema_series(closes, 26)
    diff  = len(ema12) - len(ema26)
    macd  = [ema12[i + diff] - ema26[i] for i in range(len(ema26))]
    if len(macd) < 9:
        return round(macd[-1], 4), None, None
    signal = _ema_series(macd, 9)
    hist   = [macd[len(macd) - len(signal) + i] - signal[i] for i in range(len(signal))]
    return round(macd[-1], 4), round(signal[-1], 4), round(hist[-1], 4)


def calc_bb(closes: List[float], period: int = 20) -> Tuple[Optional[float], Optional[float], Optional[float]]:
    """Returns (middle, upper, lower) Bollinger Bands."""
    if len(closes) < period:
        return None, None, None
    window = closes[-period:]
    sma    = sum(window) / period
    std    = (sum((x - sma) ** 2 for x in window) / period) ** 0.5
    return round(sma, 2), round(sma + 2 * std, 2), round(sma - 2 * std, 2)


def calc_atr(highs: List[float], lows: List[float], closes: List[float], period: int = 14) -> Optional[float]:
    if len(closes) < period + 1:
        return None
    trs = []
    for i in range(1, len(closes)):
        tr = max(highs[i] - lows[i], abs(highs[i] - closes[i-1]), abs(lows[i] - closes[i-1]))
        trs.append(tr)
    return round(sum(trs[-period:]) / period, 4)


def calc_ma(values: List[float], period: int) -> Optional[float]:
    if len(values) < period:
        return None
    return round(sum(values[-period:]) / period, 2)


def detect_cross(closes: List[float]) -> str:
    """Detect Golden Cross / Death Cross or trend position."""
    if len(closes) < 202:
        return "INSUFFICIENT_DATA"
    ma50      = sum(closes[-50:]) / 50
    ma200     = sum(closes[-200:]) / 200
    ma50_prev = sum(closes[-51:-1]) / 50
    ma200_prev= sum(closes[-201:-1]) / 200
    if ma50_prev <= ma200_prev and ma50 > ma200:
        return "GOLDEN_CROSS"
    if ma50_prev >= ma200_prev and ma50 < ma200:
        return "DEATH_CROSS"
    return "ABOVE_200MA" if ma50 > ma200 else "BELOW_200MA"


def detect_bb_signal(closes: List[float]) -> str:
    if len(closes) < 20:
        return "UNKNOWN"
    mid, upper, lower = calc_bb(closes)
    if upper is None:
        return "UNKNOWN"
    price = closes[-1]
    width = (upper - lower) / mid if mid else 0
    if width < 0.04:
        return "SQUEEZE"          # volatility compression — big move imminent
    if price >= upper:
        return "UPPER_BAND_TOUCH" # overbought / breakout
    if price <= lower:
        return "LOWER_BAND_TOUCH" # oversold / breakdown
    if price > mid:
        return "ABOVE_MIDLINE"
    return "BELOW_MIDLINE"


def find_support_resistance(closes: List[float], lookback: int = 60) -> Dict:
    """Simple swing high/low support-resistance levels."""
    recent = closes[-lookback:] if len(closes) >= lookback else closes
    if len(recent) < 5:
        return {}
    highs_idx = [i for i in range(1, len(recent)-1) if recent[i] >= recent[i-1] and recent[i] >= recent[i+1]]
    lows_idx  = [i for i in range(1, len(recent)-1) if recent[i] <= recent[i-1] and recent[i] <= recent[i+1]]
    resistance = round(sum(recent[i] for i in highs_idx[-3:]) / max(len(highs_idx[-3:]), 1), 2) if highs_idx else None
    support    = round(sum(recent[i] for i in lows_idx[-3:])  / max(len(lows_idx[-3:]),  1), 2) if lows_idx  else None
    return {"resistance": resistance, "support": support}


_POLY_KEY = os.getenv("POLYGON_KEY", "")


# ── Fetch + compute ───────────────────────────────────────────────────────────

async def _fetch_polygon_history(ticker: str, client: httpx.AsyncClient) -> tuple:
    """Fetch 2 years of daily OHLCV from Polygon (free tier, unlimited history)."""
    if not _POLY_KEY:
        return [], [], [], []
    from datetime import date, timedelta
    to_d   = date.today().isoformat()
    from_d = (date.today() - timedelta(days=730)).isoformat()
    url = f"https://api.polygon.io/v2/aggs/ticker/{ticker}/range/1/day/{from_d}/{to_d}"
    try:
        r = await client.get(url, params={
            "adjusted": "true", "sort": "asc", "limit": 730, "apiKey": _POLY_KEY,
        }, timeout=15)
        if r.status_code != 200:
            return [], [], [], []
        results = r.json().get("results", [])
        if not results:
            return [], [], [], []
        closes  = [b["c"] for b in results]
        highs   = [b["h"] for b in results]
        lows    = [b["l"] for b in results]
        volumes = [b["v"] for b in results]
        return closes, highs, lows, volumes
    except Exception:
        return [], [], [], []


def _compute_indicators(closes, highs, lows, volumes, ticker) -> Dict:
    """Shared computation — runs on whatever OHLCV series we got."""
    if len(closes) < 20:
        return {}
    macd, signal, hist = calc_macd(closes)
    mid_bb, up_bb, lo_bb = calc_bb(closes)
    sr = find_support_resistance(closes)
    avg_vol   = sum(volumes[-20:]) / 20 if len(volumes) >= 20 else None
    cur_vol   = volumes[-1] if volumes else None
    vol_ratio = round(cur_vol / avg_vol, 2) if avg_vol and cur_vol else None
    price     = closes[-1]
    price_1w  = closes[-5]  if len(closes) >= 5  else None
    price_1m  = closes[-21] if len(closes) >= 21 else None
    ma20  = calc_ma(closes, 20)
    ma50  = calc_ma(closes, 50)
    ma200 = calc_ma(closes, 200)
    return {
        "ticker":        ticker,
        "price":         round(price, 2),
        "rsi_14":        calc_rsi(closes),
        "rsi_signal":    _rsi_signal(calc_rsi(closes)),
        "macd":          macd,
        "macd_signal":   signal,
        "macd_histogram":hist,
        "macd_cross":    _macd_cross_signal(macd, signal, hist),
        "bb_mid":        mid_bb,
        "bb_upper":      up_bb,
        "bb_lower":      lo_bb,
        "bb_signal":     detect_bb_signal(closes),
        "bb_pct":        round((price - lo_bb) / (up_bb - lo_bb) * 100, 1) if up_bb and lo_bb else None,
        "ma_20":         ma20,
        "ma_50":         ma50,
        "ma_200":        ma200,
        "ma_cross":      detect_cross(closes),
        "above_ma20":    price > ma20  if ma20  else None,
        "above_ma50":    price > ma50  if ma50  else None,
        "above_ma200":   price > ma200 if ma200 else None,
        "atr":           calc_atr(highs, lows, closes),
        "vol_ratio":     vol_ratio,
        "vol_signal":    _vol_signal(vol_ratio),
        "momentum_1w":   round((price - price_1w) / price_1w * 100, 2) if price_1w else None,
        "momentum_1m":   round((price - price_1m) / price_1m * 100, 2) if price_1m else None,
        "support":       sr.get("support"),
        "resistance":    sr.get("resistance"),
        "pct_from_support":    round((price - sr["support"]) / sr["support"] * 100, 1) if sr.get("support") else None,
        "pct_from_resistance": round((sr["resistance"] - price) / price * 100, 1) if sr.get("resistance") else None,
    }


async def _fetch_history(ticker: str, client: httpx.AsyncClient, cookies: Dict) -> Dict:
    if ticker.endswith("-USD"):
        return {}

    # Primary: Polygon (reliable, no cookie drama)
    closes, highs, lows, volumes = await _fetch_polygon_history(ticker, client)
    if len(closes) >= 20:
        return _compute_indicators(closes, highs, lows, volumes, ticker)

    # Fallback: Yahoo Finance v8/chart with session cookie
    try:
        url = f"https://query2.finance.yahoo.com/v8/finance/chart/{ticker}"
        r   = await client.get(url, headers=_yf_headers(cookies, ticker),
                               params={"interval": "1d", "range": "2y"}, timeout=12)
        if r.status_code != 200:
            return {}
        result  = r.json().get("chart", {}).get("result", [{}])[0]
        quotes  = result.get("indicators", {}).get("quote", [{}])[0]
        closes  = [x for x in (quotes.get("close")  or []) if x is not None]
        highs   = [x for x in (quotes.get("high")   or []) if x is not None]
        lows    = [x for x in (quotes.get("low")    or []) if x is not None]
        volumes = [x for x in (quotes.get("volume") or []) if x is not None]
        return _compute_indicators(closes, highs, lows, volumes, ticker)
    except Exception:
        return {}
    except Exception:
        return {}


def _rsi_signal(rsi: Optional[float]) -> str:
    if rsi is None: return "UNKNOWN"
    if rsi < 20:    return "EXTREMELY_OVERSOLD"
    if rsi < 30:    return "OVERSOLD"
    if rsi < 40:    return "MILDLY_OVERSOLD"
    if rsi < 60:    return "NEUTRAL"
    if rsi < 70:    return "MILDLY_OVERBOUGHT"
    if rsi < 80:    return "OVERBOUGHT"
    return "EXTREMELY_OVERBOUGHT"


def _macd_cross_signal(macd, signal, hist) -> str:
    if macd is None or signal is None: return "UNKNOWN"
    if macd > signal and hist and hist > 0: return "BULLISH_CROSS"
    if macd < signal and hist and hist < 0: return "BEARISH_CROSS"
    return "NEUTRAL"


def _vol_signal(ratio: Optional[float]) -> str:
    if ratio is None:   return "UNKNOWN"
    if ratio >= 3.0:    return "EXTREME_VOLUME"
    if ratio >= 2.0:    return "VERY_HIGH_VOLUME"
    if ratio >= 1.5:    return "HIGH_VOLUME"
    if ratio >= 0.8:    return "NORMAL_VOLUME"
    return "LOW_VOLUME"


async def get_technicals(tickers: List[str]) -> Dict[str, Dict]:
    """Fetch and compute technical indicators for a list of tickers. Cached 1h."""
    now       = time.time()
    # Skip crypto — no options/technicals from Yahoo for -USD tickers
    tickers   = [t for t in tickers if not t.endswith("-USD")]
    to_fetch  = [t for t in tickers if t not in _CACHE or now - _CACHE_TS.get(t, 0) > _TTL]
    cached    = {t: _CACHE[t] for t in tickers if t in _CACHE and t not in to_fetch}

    if to_fetch:
        cookies = await _get_yahoo_cookies()
        sem     = asyncio.Semaphore(30)

        async def fetch_with_sem(ticker: str, client: httpx.AsyncClient) -> tuple:
            async with sem:
                result = await _fetch_history(ticker, client, cookies)
                return ticker, result

        async with httpx.AsyncClient(timeout=15) as client:
            results = await asyncio.gather(*[fetch_with_sem(t, client) for t in to_fetch],
                                           return_exceptions=True)

        for item in results:
            if isinstance(item, tuple):
                ticker, data = item
                if data:
                    _CACHE[ticker]    = data
                    _CACHE_TS[ticker] = now

    return {**cached, **{t: _CACHE[t] for t in to_fetch if t in _CACHE}}


def score_ticker(tech: Dict) -> Dict:
    """
    Score a ticker's technical setup from -10 to +10.
    Returns score + list of active signals.
    """
    if not tech:
        return {"score": 0, "signals": [], "grade": "F"}

    score   = 0
    signals = []

    rsi = tech.get("rsi_14")
    if rsi is not None:
        if rsi < 30:
            score += 2; signals.append(f"RSI OVERSOLD ({rsi})")
        elif rsi < 40:
            score += 1; signals.append(f"RSI mildly oversold ({rsi})")
        elif rsi > 80:
            score -= 2; signals.append(f"RSI EXTREMELY OVERBOUGHT ({rsi})")
        elif rsi > 70:
            score -= 1; signals.append(f"RSI overbought ({rsi})")

    macd_cross = tech.get("macd_cross", "")
    if macd_cross == "BULLISH_CROSS":
        score += 2; signals.append("MACD bullish crossover")
    elif macd_cross == "BEARISH_CROSS":
        score -= 2; signals.append("MACD bearish crossover")

    ma_cross = tech.get("ma_cross", "")
    if ma_cross == "GOLDEN_CROSS":
        score += 3; signals.append("GOLDEN CROSS (50MA > 200MA)")
    elif ma_cross == "DEATH_CROSS":
        score -= 3; signals.append("DEATH CROSS (50MA < 200MA)")
    elif ma_cross == "ABOVE_200MA":
        score += 1; signals.append("Above 200-day MA (bullish trend)")
    elif ma_cross == "BELOW_200MA":
        score -= 1; signals.append("Below 200-day MA (bearish trend)")

    bb_signal = tech.get("bb_signal", "")
    if bb_signal == "LOWER_BAND_TOUCH":
        score += 2; signals.append("Bollinger Band lower touch (oversold)")
    elif bb_signal == "UPPER_BAND_TOUCH":
        score -= 1; signals.append("Bollinger Band upper touch")
    elif bb_signal == "SQUEEZE":
        signals.append("BB Squeeze — big move imminent")

    vol = tech.get("vol_ratio")
    if vol and vol >= 2.0:
        score += 1; signals.append(f"High volume ({vol}x avg)")

    mom1w = tech.get("momentum_1w")
    if mom1w is not None:
        if mom1w > 5:  score += 1; signals.append(f"Strong 1-week momentum (+{mom1w}%)")
        elif mom1w < -10: score -= 1; signals.append(f"Weak 1-week momentum ({mom1w}%)")

    grade_map = [(8,"A+"), (6,"A"), (4,"B"), (2,"C"), (0,"D"), (-99,"F")]
    grade = next(g for threshold, g in grade_map if score >= threshold)

    return {"score": min(max(score, -10), 10), "signals": signals, "grade": grade}
