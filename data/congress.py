"""
Congress trading — House PTR (2015–present) + Senate STOCK Act.

Strategy:
- Real-time (/api/intel): serve cache immediately + fetch only RECENT PDFs (last 60 days)
- Background warmup: fetches all historical PDFs and adds them to disk cache
- Disk cache (congress_cache.json) persists across restarts
"""
import httpx, pdfplumber, io, re, zipfile, asyncio, json, os
from typing import List, Dict, Tuple, Set
from datetime import datetime, timedelta

_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
}

_HOUSE_FD_ZIP  = "https://disclosures-clerk.house.gov/public_disc/financial-pdfs/{year}FD.zip"
_HOUSE_PTR_PDF = "https://disclosures-clerk.house.gov/public_disc/ptr-pdfs/{year}/{doc_id}.pdf"
_SENATE_JSON   = ("https://senate-stock-watcher-data.s3-us-west-2.amazonaws.com/"
                  "aggregate/all_transactions.json")

_CACHE_FILE    = os.path.join(os.path.dirname(__file__), "congress_cache.json")
_START_YEAR    = 2015
_BATCH_SIZE    = 30

# Background warmup state
_warming    = False
_warm_done  = False


# ─── DISK CACHE ───────────────────────────────────────────────────────────────

def _load_cache() -> Dict:
    if os.path.exists(_CACHE_FILE):
        try:
            with open(_CACHE_FILE) as f:
                raw = json.load(f)
            return {
                "fetched": set(raw.get("fetched", [])),
                "trades":  raw.get("trades", []),
            }
        except Exception:
            pass
    return {"fetched": set(), "trades": []}


def _save_cache(fetched: Set[str], trades: List[Dict]):
    try:
        with open(_CACHE_FILE, "w") as f:
            json.dump({"fetched": list(fetched), "trades": trades}, f)
    except Exception:
        pass


# ─── PDF PARSER ───────────────────────────────────────────────────────────────

def _parse_ptr_pdf(pdf_bytes: bytes, name: str, filed: str, state: str) -> List[Dict]:
    try:
        pdf = pdfplumber.open(io.BytesIO(pdf_bytes))
        full_text = " ".join(page.extract_text() or "" for page in pdf.pages)
        full_text = re.sub(r"\s+", " ", full_text)
    except Exception:
        return []

    events = []
    for m in re.finditer(r"\b([SP])\s+(\d{2}/\d{2}/\d{4})\s+\d{2}/\d{2}/\d{4}", full_text):
        events.append({"pos": m.start(), "type": "action",
                        "action": m.group(1), "date": m.group(2)})
    for m in re.finditer(r"\(([A-Z]{1,5})\)\s*\[ST\]", full_text):
        events.append({"pos": m.start(), "type": "ticker", "ticker": m.group(1)})
    for m in re.finditer(r"\$([\d,]+)\s*[-–]\s*\$([\d,]+)", full_text):
        events.append({"pos": m.start(), "type": "amount", "amount": m.group(0)})

    events.sort(key=lambda x: x["pos"])

    trades, last_action, last_date, last_amount = [], None, None, None
    for e in events:
        if e["type"] == "action":
            last_action = "Purchase" if e["action"] == "P" else "Sale"
            last_date = e["date"]
            last_amount = None
        elif e["type"] == "amount":
            last_amount = e["amount"]
        elif e["type"] == "ticker" and last_action:
            trades.append({
                "trader": name, "chamber": "House", "ticker": e["ticker"],
                "action": last_action, "amount": last_amount or "",
                "date": last_date or "", "filed": filed, "state": state,
            })
            last_action = None
    return trades


async def _fetch_one_ptr(rec: Dict, client: httpx.AsyncClient,
                          sem: asyncio.Semaphore) -> List[Dict]:
    async with sem:
        url = _HOUSE_PTR_PDF.format(year=rec["year"], doc_id=rec["doc_id"])
        try:
            r = await client.get(url, headers=_HEADERS, timeout=15)
            if r.status_code != 200:
                return []
            return _parse_ptr_pdf(r.content, rec["name"], rec["filed"], rec["state"])
        except Exception:
            return []


# ─── INDEX FETCHER ────────────────────────────────────────────────────────────

async def _get_doc_ids_for_years(years: List[int],
                                  client: httpx.AsyncClient) -> List[Dict]:
    doc_ids: List[Dict] = []

    async def fetch_year(yr: int):
        try:
            r = await client.get(_HOUSE_FD_ZIP.format(year=yr),
                                 headers=_HEADERS, timeout=30)
            if r.status_code != 200:
                return
            z = zipfile.ZipFile(io.BytesIO(r.content))
            txt = next((n for n in z.namelist() if n.endswith(".txt")), None)
            if not txt:
                return
            lines = z.read(txt).decode("utf-8", errors="ignore").splitlines()
            for line in lines[1:]:
                parts = line.split("\t")
                if len(parts) < 9:
                    continue
                prefix, last, first, _, filing_type, state, _fy, filed, doc_id = parts[:9]
                if filing_type.strip() != "P":
                    continue
                doc_ids.append({
                    "doc_id": doc_id.strip(),
                    "name":   f"{prefix.strip()} {first.strip()} {last.strip()}".strip(),
                    "filed":  filed.strip(),
                    "state":  state.strip(),
                    "year":   str(yr),
                })
        except Exception:
            pass

    await asyncio.gather(*[fetch_year(yr) for yr in years])
    return doc_ids


def _filed_iso(filed: str) -> str:
    try:
        return datetime.strptime(filed, "%m/%d/%Y").strftime("%Y-%m-%d")
    except Exception:
        return filed[:10]


# ─── SENATE ───────────────────────────────────────────────────────────────────

async def _get_senate_trades(client: httpx.AsyncClient) -> List[Dict]:
    try:
        r = await client.get(_SENATE_JSON, headers=_HEADERS, timeout=30)
        if r.status_code != 200:
            return []
        data = r.json()
    except Exception:
        return []

    trades = []
    for senator in data:
        name = senator.get("senator", "")
        for tx in senator.get("transactions", []):
            tx_date = tx.get("transaction_date") or tx.get("disclosure_date") or ""
            try:
                iso = (datetime.strptime(tx_date, "%m/%d/%Y").strftime("%Y-%m-%d")
                       if "/" in tx_date else tx_date[:10])
            except Exception:
                iso = tx_date[:10]
            ticker = (tx.get("ticker") or "").strip().upper()
            if not ticker or not ticker.isalpha() or len(ticker) > 5:
                continue
            tx_type = tx.get("type", "")
            if "purchase" in tx_type.lower():
                action = "Purchase"
            elif "sale" in tx_type.lower():
                action = "Sale"
            else:
                continue
            trades.append({
                "trader": name, "chamber": "Senate", "ticker": ticker,
                "action": action, "amount": tx.get("amount", ""),
                "date": iso, "filed": tx.get("disclosure_date", iso),
                "state": tx.get("state", ""),
            })
    return trades


# ─── BACKGROUND WARMUP ────────────────────────────────────────────────────────

async def warm_cache():
    """
    Download all historical House PTR PDFs (2015–present) gradually in the background.
    Uses low concurrency (3) and yields between batches so real-time requests are
    never starved. Waits 30s after startup before beginning.
    """
    global _warming, _warm_done
    if _warming or _warm_done:
        return
    _warming = True

    await asyncio.sleep(30)   # let server fully start and serve initial requests

    cache      = _load_cache()
    known_ids  = cache["fetched"]
    all_trades = list(cache["trades"])

    current_year = datetime.now().year
    years = list(range(_START_YEAR, current_year + 1))

    async with httpx.AsyncClient(timeout=20, follow_redirects=True) as client:
        all_docs = await _get_doc_ids_for_years(years, client)
        new_docs = [d for d in all_docs if d["doc_id"] not in known_ids]

        sem = asyncio.Semaphore(3)   # gentle — don't compete with real-time requests
        new_ids: Set[str] = set()

        for i in range(0, len(new_docs), _BATCH_SIZE):
            batch   = new_docs[i:i + _BATCH_SIZE]
            results = await asyncio.gather(
                *[_fetch_one_ptr(d, client, sem) for d in batch],
                return_exceptions=True,
            )
            for rec, result in zip(batch, results):
                if isinstance(result, list):
                    all_trades.extend(result)
                    new_ids.add(rec["doc_id"])
            # Save incrementally + yield to event loop between batches
            if new_ids:
                _save_cache(known_ids | new_ids, all_trades)
            await asyncio.sleep(0.1)

    _warming = False
    _warm_done = True


# ─── FAST REAL-TIME (used by /api/intel) ─────────────────────────────────────

async def get_congress_trades(days: int = 3650) -> List[Dict]:
    """
    Fast path: return disk cache immediately + fetch only PDFs from the last 60 days.
    Full historical cache is built by warm_cache() running in the background.
    """
    cache      = _load_cache()
    known_ids  = cache["fetched"]
    all_trades = list(cache["trades"])

    cutoff = datetime.now() - timedelta(days=60)
    current_year = datetime.now().year
    years_to_check = list({current_year, current_year - 1})

    async with httpx.AsyncClient(timeout=20, follow_redirects=True) as client:
        senate_task = _get_senate_trades(client)

        # Only fetch recent PDFs not yet cached
        all_docs = await _get_doc_ids_for_years(years_to_check, client)
        recent_new = [
            d for d in all_docs
            if d["doc_id"] not in known_ids
            and _filed_iso(d["filed"]) >= cutoff.strftime("%Y-%m-%d")
        ]

        sem = asyncio.Semaphore(20)
        house_results, senate_trades = await asyncio.gather(
            asyncio.gather(*[_fetch_one_ptr(d, client, sem) for d in recent_new],
                           return_exceptions=True),
            senate_task,
        )

    new_ids   = set()
    new_trades: List[Dict] = []
    for rec, result in zip(recent_new, house_results):
        if isinstance(result, list):
            new_trades.extend(result)
            new_ids.add(rec["doc_id"])

    if new_ids:
        _save_cache(known_ids | new_ids, all_trades + new_trades)
        all_trades.extend(new_trades)

    all_trades.extend(senate_trades)

    # Apply days filter
    if days < 99999:
        cutoff_str = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
        filtered = [t for t in all_trades
                    if _filed_iso(t.get("filed") or t.get("date") or "") >= cutoff_str]
        if filtered:
            all_trades = filtered

    def _sort_key(t: Dict) -> str:
        return _filed_iso(t.get("filed") or t.get("date") or "")

    all_trades.sort(key=_sort_key, reverse=True)
    return all_trades
