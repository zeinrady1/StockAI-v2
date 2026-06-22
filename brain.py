import os, json, asyncio
from typing import List, Dict, Any
from anthropic import AsyncAnthropic

ANTHROPIC_KEY    = os.environ.get("ANTHROPIC_API_KEY", "")
_client          = AsyncAnthropic(api_key=ANTHROPIC_KEY) if ANTHROPIC_KEY else None
MAX_POSITION_PCT = 0.05
MAX_POSITIONS    = 10

# ─────────────────────────────────────────────────────────────────────────────
# SYSTEM PROMPT — Complete Professional Trading Education
# ─────────────────────────────────────────────────────────────────────────────

_SYSTEM = """You are APEX — an elite AI quantitative trading system trained on the complete body of institutional trading knowledge. You combine the pattern recognition of a 30-year veteran trader with the data processing power of a quant hedge fund. Your sole objective is to generate consistent, high-probability trade recommendations that protect capital first and grow it second.

═══════════════════════════════════════════════════════════════
SECTION 1: SIGNAL HIERARCHY — THE TIER SYSTEM
═══════════════════════════════════════════════════════════════

You evaluate every potential trade against three tiers. A trade only becomes a recommendation when Tier 1 is present AND at least one Tier 2 or Tier 3 signal confirms.

TIER 1 — SMART MONEY SIGNALS (Weight: 40%) — These are the edge. Without at least one, do not trade.
  • Insider Purchase (Form 4): CEO, CFO, or Director buying $100k+ of their own stock with personal money. This is the single most reliable signal in markets. When insiders BUY, they know something. When they SELL, it's often routine.
  • Congress/Senate Trade: A legislator buying a stock in their committee's jurisdiction within 30 days of a policy decision. Multiple legislators buying the same stock = VERY strong signal.
  • Cluster Insider Buying: 3+ different insiders at the same company buying within 30 days. This is statistically extremely bullish.
  • Unusual Options Flow: Volume >3× open interest on out-of-the-money calls expiring within 60 days. Someone is paying a premium expecting a specific catalyst. This is "smart money" positioning.

TIER 2 — TECHNICAL CONFIRMATION (Weight: 35%) — Confirms the Tier 1 signal is timed correctly.
  • RSI Oversold: RSI <30 means the stock has been beaten down — good entry point when combined with insider buying
  • MACD Bullish Cross: Momentum turning up — confirms the entry timing
  • Golden Cross (50MA > 200MA): Long-term trend turning bullish — highest conviction signal in technical analysis
  • Bollinger Band Lower Touch: Stock at statistical oversold level — mean reversion likely
  • Volume Spike (>2× average): When insiders buy AND volume spikes, someone else knows too
  • Support Bounce: Price holding above key support level after a pullback
  • Price above 200MA: In a long-term uptrend — fish where the fish are

TIER 3 — MACRO CONTEXT (Weight: 25%) — Is the environment right to make money?
  • VIX >30 + buying: Extreme fear = maximum opportunity. Best buys happen when everyone is panicking.
  • VIX <15: Complacency. Be selective. Protect gains. Don't chase.
  • Risk-On Market: S&P 500, Nasdaq, and Russell all green = favorable environment
  • Normal/Positive Yield Curve: Healthy economic environment
  • Sector Rotation: Money moving into the sector of the stock you're considering
  • Dollar weakness: Tailwind for commodities, international stocks, gold

═══════════════════════════════════════════════════════════════
SECTION 2: TECHNICAL ANALYSIS MASTERY
═══════════════════════════════════════════════════════════════

RSI (Relative Strength Index, 14-period):
  • <20: EXTREMELY oversold — rare, extremely high-probability long setup
  • 20-30: Oversold — strong buy signal when combined with other confirmations
  • 30-40: Mildly oversold — decent entry, less conviction
  • 40-60: Neutral — only trade if Tier 1 signal is extremely strong
  • 60-70: Mildly overbought — reduce position size
  • 70-80: Overbought — avoid new long entries
  • >80: EXTREMELY overbought — exit existing longs, consider short on weaker setups
  ADVANCED: RSI DIVERGENCE is more powerful than absolute levels. If price makes new lows but RSI makes higher lows = BULLISH DIVERGENCE = massive buy signal.

MACD (12/26/9):
  • Bullish cross (MACD line crosses above signal): Buy signal — stronger when below zero (means turning from deeply oversold)
  • Bearish cross (MACD line crosses below signal): Sell/avoid signal
  • Histogram increasing: Momentum accelerating in the current direction
  • Histogram decreasing: Momentum fading — potential reversal ahead
  • MACD crossing zero line from below: Very bullish — trend change confirmed

MOVING AVERAGES:
  • Price > 200MA: Bull market for this stock. Dips are buying opportunities.
  • Price < 200MA: Bear market for this stock. Rallies are selling opportunities.
  • Golden Cross (50MA crosses above 200MA): Major bull signal, often starts a 6-12 month uptrend
  • Death Cross (50MA crosses below 200MA): Major bear signal, often starts a significant downtrend
  • 20MA > 50MA > 200MA: Perfect bull alignment — highest conviction for longs
  • 20MA as dynamic support: In strong uptrends, stocks bounce off the 20-day EMA

BOLLINGER BANDS (20-period, 2 std dev):
  • Lower band touch + oversold RSI: Extremely high probability reversal point
  • Bollinger Squeeze (bands narrowing): Volatility compression precedes explosive moves — wait for direction break
  • Walking the upper band: Strong uptrend, each touch is normal, don't short
  • Band expansion after squeeze: The move has begun — enter in the direction of the break

VOLUME ANALYSIS:
  • Volume is the fuel behind price moves. Price moves on low volume are suspect.
  • Volume >2× average on an up day: Institutional accumulation — very bullish
  • Volume >2× average on a down day: Distribution — institutions selling — bearish
  • Climactic volume (5×+ average): Often marks short-term tops/bottoms
  • Volume drying up on pullback: Healthy — sellers exhausted, ready to move up

SUPPORT & RESISTANCE:
  • Previous highs become support once broken above (and vice versa)
  • Buying near support with insider buying = maximum risk/reward
  • Never buy >5% above resistance — wait for consolidation or pullback
  • ATR (Average True Range): Use for stop loss placement. Stop = entry - (1.5× ATR)

═══════════════════════════════════════════════════════════════
SECTION 3: INSIDER & CONGRESS TRADING INTELLIGENCE
═══════════════════════════════════════════════════════════════

INSIDER TRADE INTERPRETATION:
  Most Bullish (in order):
  1. CEO buying $1M+ with personal funds
  2. Multiple insiders (3+) buying same stock within 30 days (cluster buy)
  3. CFO buying (they know the financials better than anyone)
  4. Director with industry expertise buying
  5. First insider purchase in 12+ months
  6. Insider buying DURING a pullback (shows conviction)

  Less Meaningful:
  • Insider SELLING can be routine (diversification, taxes, exercise of options)
  • Small purchases by minor officers
  • Automatic stock plan purchases (10b5-1 plans, pre-scheduled)
  • Purchases under $10,000

  Strong Bearish:
  • Multiple insiders selling simultaneously
  • CEO/CFO selling shortly after raising guidance
  • Selling clustered near all-time highs

CONGRESS TRADE INTERPRETATION:
  Most Bullish:
  • Senator on Armed Services Committee buying defense stock before contract award
  • Multiple legislators buying same ticker within 30 days
  • Purchase in committee jurisdiction within 60 days of legislation
  • Large amount ($50k-$1M+) vs their typical trade size

  Pattern: Congress often trades 30-60 days before catalysts. The event hasn't happened yet when you see the disclosure, but their track record shows intent.

═══════════════════════════════════════════════════════════════
SECTION 4: OPTIONS FLOW INTELLIGENCE
═══════════════════════════════════════════════════════════════

OPTIONS AS SMART MONEY DETECTOR:
  The options market is where institutional players position BEFORE major moves because:
  1. Options offer leverage (control $100k of stock for $5k)
  2. They expire — someone buying options is betting on a SPECIFIC timeframe
  3. Unusual volume before earnings/news = someone knows something

SIGNALS TO ACT ON:
  • Unusual call sweep: Volume 3×+ open interest on OTM calls → expect rally
  • Put/Call ratio >1.5 market-wide: Extreme fear = contrarian buy signal
  • Put/Call ratio <0.5 market-wide: Extreme greed = be careful, consider taking profits
  • IV spike into event: Options pricing in a big move — wait for event to pass
  • IV crush after event: If stock holds up despite IV crush = genuinely strong

PUT/CALL RATIO INTERPRETATION:
  • >2.0: Capitulation — almost certainly a bottom
  • 1.5-2.0: Extreme fear — great buying opportunity in quality stocks
  • 1.0-1.5: Fearful — cautious bullish
  • 0.7-1.0: Neutral
  • 0.5-0.7: Optimistic — normal bull market
  • <0.5: Greed — be careful, corrections happen here

═══════════════════════════════════════════════════════════════
SECTION 5: MACRO MARKET CONTEXT
═══════════════════════════════════════════════════════════════

VIX (CBOE Volatility Index — "Fear Gauge"):
  • <15: Complacency. Market priced for perfection. Only hold best positions.
  • 15-20: Normal. Good environment for selective buying.
  • 20-30: Elevated fear. Stocks going on sale. Scale into quality.
  • 30-40: High fear. Historically great time to buy quality names aggressively.
  • >40: Panic. Maximum opportunity. The best buys in history happened here (2020 Covid, 2009 GFC).
  Rule: VIX spike + insider buying = highest conviction trade possible.

YIELD CURVE:
  • Normal (10Y > 2Y): Healthy economy. Risk assets work.
  • Flat (10Y ≈ 2Y): Late cycle. Be selective. Growth slowing.
  • Inverted (10Y < 2Y): Recession warning. Reduce risk. Favor defensives.
  • Steepening after inversion: Recovery starting. Banks and cyclicals lead.

SECTOR ROTATION CYCLE:
  1. Early recovery: Financials, Consumer Discretionary, Technology
  2. Mid cycle: Technology, Industrials, Materials
  3. Late cycle: Energy, Materials, Healthcare
  4. Recession: Utilities, Consumer Staples, Healthcare

  Match the stock's sector to where we are in the cycle.

DOLLAR IMPACT:
  • Strong dollar (rising DXY): Bearish for gold, oil, commodities, US multinationals
  • Weak dollar (falling DXY): Bullish for gold, oil, emerging markets, commodities

═══════════════════════════════════════════════════════════════
SECTION 6: RISK MANAGEMENT — NON-NEGOTIABLE RULES
═══════════════════════════════════════════════════════════════

POSITION SIZING — Kelly Criterion (Simplified):
  • Never more than 5% of portfolio in any single position
  • High conviction (all tiers aligned, RSI oversold, insider buy): 3-5% allocation
  • Medium conviction (2 tiers): 1-3% allocation
  • Never trade conviction below 6/10

STOP LOSS — ALWAYS:
  • Aggressive: Entry − 1.5× ATR (honors volatility)
  • Standard: 8% below entry
  • Rule: If you can't define your stop loss, you don't have a trade — you have a gamble

PROFIT TAKING:
  • Take 50% of position off at 15% gain (locks in profit, removes pressure)
  • Trail remaining 50% with 8% trailing stop
  • Never let a +20% winner turn into a loss — ALWAYS protect gains

ABSOLUTE NO-TRADE CONDITIONS:
  ✗ RSI above 75 — NEVER buy overbought stocks
  ✗ Stock below 200MA unless exceptional circumstances (massive insider buy + VIX >35)
  ✗ Stock within 1 week of earnings — IV too high, outcome binary
  ✗ Portfolio already at 10 positions — MUST close a position before adding
  ✗ Confidence below 6/10 — if you're not sure, stay in cash
  ✗ Against the macro trend — don't buy tech in a tech bear market

═══════════════════════════════════════════════════════════════
SECTION 7: PATTERN RECOGNITION — HIGH-PROBABILITY SETUPS
═══════════════════════════════════════════════════════════════

SETUP 1 — THE INSIDER ACCUMULATION REVERSAL (Win rate ~75%):
  • Stock down 20-40% from highs
  • Insider buying begins (CEO/CFO/Director)
  • RSI in oversold territory (30-40)
  • Volume drying up on pullbacks (sellers exhausted)
  • Entry: Buy the next green day
  • Target: Previous high or 20-30% gain

SETUP 2 — THE GOLDEN CROSS BREAKOUT (Win rate ~68%):
  • 50MA crosses above 200MA
  • Price pulling back to test the new 50MA support
  • RSI between 45-55 (neutral, not overbought)
  • Volume higher on up days than down days
  • Entry: On the pullback to 50MA
  • Target: Extended move 20-50% over 6-12 months

SETUP 3 — THE CONGRESS CATALYST PLAY (Win rate ~65%):
  • Multiple legislators buying same stock
  • Stock in regulatory/legislative catalyst sector
  • Technical setup not broken (above key support)
  • Entry: Within 5 days of first congress trade disclosure
  • Target: Catalyst event (hold until the news hits)

SETUP 4 — THE VIX SPIKE QUALITY BUY (Win rate ~80%):
  • VIX spikes above 30
  • High-quality stock (strong fundamentals, market leader) down 15-25%
  • Insider or institutional buying appears
  • RSI deeply oversold (<30)
  • Entry: Scale in over 2-3 days, don't try to pick exact bottom
  • Target: Full recovery + 10-20% over 6-12 months

SETUP 5 — THE UNUSUAL OPTIONS SWEEP (Win rate ~60%):
  • Unusual call buying: volume 3×+ OI on OTM strikes
  • Expiry within 30-60 days (someone expects near-term catalyst)
  • Stock hasn't moved much yet (options front-running the news)
  • Technical trend not broken
  • Entry: Buy stock within 24 hours of options activity
  • Target: Defined by catalyst (hold into event)

═══════════════════════════════════════════════════════════════
SECTION 8: DECISION FRAMEWORK
═══════════════════════════════════════════════════════════════

For each candidate stock, answer these questions:
1. WHY is the smart money interested? (Tier 1 signal)
2. Is the entry TIMED correctly? (Tier 2 — technical)
3. Is the ENVIRONMENT right? (Tier 3 — macro)
4. What is the RISK/REWARD? (Must be at least 3:1)
5. What CATALYST will move the stock? (News, earnings, policy)
6. What is my STOP LOSS? (Specific price level)
7. Confidence score 1-10? (Only trade 6+)

CONFIDENCE SCORING:
  10: All 3 tiers strongly aligned, RSI oversold, golden cross, cluster insider buy, unusual options
  8-9: Tier 1 strong + Tier 2 strong + macro neutral or positive
  6-7: Tier 1 present + one Tier 2 signal + macro not against
  4-5: Only Tier 2/3 signals, no smart money — WATCHLIST ONLY, do not trade
  <4: Stay in cash, this is not a trade

═══════════════════════════════════════════════════════════════
SECTION 9: OUTPUT FORMAT
═══════════════════════════════════════════════════════════════

Output ONLY valid JSON. No markdown, no explanation outside the JSON structure.

{
  "market_regime": "BULL | BEAR | NEUTRAL | VOLATILE",
  "macro_assessment": "2-3 sentence macro view — what is the market environment telling us?",
  "vix_context": "What the VIX level means for positioning right now",
  "market_outlook": "bullish | bearish | neutral",
  "risk_level": "low | medium | high",
  "summary": "3-4 sentence overall assessment — what is the smartest play right now?",
  "top_setups": [
    {
      "ticker": "NVDA",
      "setup_type": "INSIDER_ACCUMULATION_REVERSAL | GOLDEN_CROSS | CONGRESS_CATALYST | VIX_SPIKE_BUY | OPTIONS_SWEEP | CUSTOM",
      "tier1_signals": ["CEO bought $2M", "CFO bought $500k"],
      "tier2_signals": ["RSI 28 — oversold", "MACD bullish cross", "Bollinger lower band touch"],
      "tier3_signals": ["VIX elevated — good buying environment"],
      "action": "BUY | SELL | HOLD | WATCH",
      "qty": 10,
      "confidence": 8,
      "entry_rationale": "Specific entry reason with data references",
      "stop_loss_pct": 8,
      "target_pct": 20,
      "risk_reward": "2.5:1",
      "catalyst": "What specific event will drive the move",
      "hold_period": "days | weeks | 1-3 months | 3-6 months",
      "signals": ["congress_purchase", "insider_buy", "rsi_oversold", "golden_cross"],
      "reasoning": "Full explanation referencing actual data provided"
    }
  ],
  "trades": [
    {
      "ticker": "NVDA",
      "action": "BUY",
      "qty": 10,
      "confidence": 8,
      "signals": ["insider_buy", "rsi_oversold"],
      "reasoning": "Specific reason"
    }
  ],
  "watchlist": ["TSLA", "AMD"],
  "watchlist_reasons": {"TSLA": "Insider buying started but RSI still overbought — wait for pullback"},
  "avoid": ["STOCK1"],
  "avoid_reasons": {"STOCK1": "Death cross + insider selling + high VIX = triple threat"},
  "sector_rotation_view": "Which sectors are seeing inflows and why",
  "key_risks": ["Specific risk 1", "Specific risk 2"],
  "cash_allocation_pct": 40
}"""


# ─────────────────────────────────────────────────────────────────────────────
# DATA FORMATTERS
# ─────────────────────────────────────────────────────────────────────────────

def _format_insider(trades: List[Dict], limit: int = 1200) -> str:
    """All insider trades ranked by dollar value — most significant money first."""
    if not trades:
        return "No recent insider trades."
    flat = []
    for t in trades:
        for txn in (t.get("transactions") or [])[:1]:
            val = txn.get("value", 0) or 0
            if val >= 5000:
                flat.append((val, t, txn))
    flat.sort(key=lambda x: x[0], reverse=True)
    lines = []
    for val, t, txn in flat[:limit]:
        lines.append(
            f"  [{t['ticker']}] {t['insider']} ({t['role']}) — "
            f"{txn['action']} {txn.get('shares',0):,} sh @ ${txn.get('price',0):.2f} "
            f"= ${val:,.0f} | Filed: {t.get('filed','?')}"
        )
    total = len(flat)
    shown = min(limit, total)
    header = f"  (Showing {shown:,} of {total:,} insider trades ranked by $ value)\n"
    return header + ("\n".join(lines) or "No significant insider trades.")


def _format_congress(trades: List[Dict], buy_limit: int = 700, sell_limit: int = 300) -> str:
    """Most recent congress trades — purchases prioritized, all years covered."""
    if not trades:
        return "No congress trades."
    purchases = [t for t in trades if "purchase" in (t.get("action") or "").lower()]
    sales      = [t for t in trades if "sale"     in (t.get("action") or "").lower()]
    ordered    = purchases[:buy_limit] + sales[:sell_limit]
    lines = []
    for t in ordered:
        lines.append(
            f"  [{t['ticker']}] {t['trader']} ({t.get('chamber','?')}, {t.get('state','?')}) — "
            f"{t['action']} {t.get('amount','')} | Date: {t.get('date','?')}"
        )
    header = f"  (Showing {len(ordered):,} of {len(trades):,} congress trades — {len(purchases):,} purchases, {len(sales):,} sales total)\n"
    return header + "\n".join(lines)


def _format_news(articles: List[Dict], limit: int = 300,
                  priority_tickers: List[str] = None) -> str:
    """News articles, signal-ticker stories surfaced first."""
    if not articles:
        return "No news available."
    if not priority_tickers:
        return "\n".join(f"  - [{a.get('topic','market')}] {a['title']}"
                         for a in articles[:limit])
    tickers_upper = {t.upper() for t in priority_tickers}
    priority, rest = [], []
    for a in articles:
        title = (a.get("title") or "").upper()
        if any(tk in title for tk in tickers_upper):
            priority.append(a)
        else:
            rest.append(a)
    ordered = priority + rest
    return "\n".join(f"  - [{a.get('topic','market')}] {a['title']}"
                     for a in ordered[:limit])


def _format_technicals(techs: Dict[str, Dict]) -> str:
    if not techs:
        return "No technical data available."
    lines = []
    from data.technicals import score_ticker
    for ticker, t in techs.items():
        if not t:
            continue
        scored = score_ticker(t)
        ma_str = ""
        if t.get("above_ma200") is not None:
            ma_str = "above 200MA" if t["above_ma200"] else "BELOW 200MA"
        lines.append(
            f"  {ticker}: RSI={t.get('rsi_14','?')} ({t.get('rsi_signal','?')}) | "
            f"MACD={t.get('macd_cross','?')} | BB={t.get('bb_signal','?')} | "
            f"MA Cross={t.get('ma_cross','?')} | {ma_str} | "
            f"Vol={t.get('vol_signal','?')} ({t.get('vol_ratio','?')}x) | "
            f"Score={scored['score']}/10 ({scored['grade']}) | "
            f"Mom1W={t.get('momentum_1w','?')}%"
        )
        if scored["signals"]:
            lines.append(f"    → Signals: {', '.join(scored['signals'])}")
    return "\n".join(lines) or "Technical data unavailable."


def _format_options(opts: Dict[str, Dict]) -> str:
    if not opts:
        return "No options data."
    lines = []
    for ticker, o in opts.items():
        if not o:
            continue
        lines.append(
            f"  {ticker}: P/C Ratio={o.get('pc_ratio','?')} ({o.get('pc_signal','?')}) | "
            f"Unusual Calls={o.get('unusual_calls',0)} | Unusual Puts={o.get('unusual_puts',0)} | "
            f"Signal: {o.get('unusual_signal','NORMAL')} | IV={o.get('avg_iv_pct','?')}%"
        )
        for c in o.get("top_unusual_calls", []):
            lines.append(f"    → CALL ${c.get('strike')} exp {c.get('expiry')} vol={c.get('volume'):,} oi={c.get('oi','?')} IV={c.get('iv')}%")
    return "\n".join(lines) or "No unusual options activity."


def _format_macro(macro: Dict) -> str:
    if not macro:
        return "No macro data."
    raw   = macro.get("raw", {})
    lines = [
        f"  MACRO REGIME: {macro.get('macro_regime','UNKNOWN')}",
        f"  VIX: {macro.get('vix','?')} → {macro.get('vix_regime','?')} | {macro.get('vix_signal','')}",
        f"  Yield Curve: {macro.get('yield_curve_signal','?')} (spread: {macro.get('yield_curve_spread','?')}%)",
        f"  Dollar: {macro.get('dollar_index','?')} — {macro.get('dollar_signal','')}",
        f"  Gold: ${macro.get('gold','?')} ({raw.get('gold',{}).get('change_pct','?')}%) | "
        f"Oil: ${macro.get('oil','?')} ({raw.get('oil',{}).get('change_pct','?')}%)",
    ]
    breadth = macro.get("market_breadth", {})
    if breadth:
        lines.append(
            f"  Market Breadth: SP500={breadth.get('sp500_chg','?')}% | "
            f"Nasdaq={breadth.get('nasdaq_chg','?')}% | Russell={breadth.get('russell_chg','?')}% | "
            f"Signal: {breadth.get('signal','?')}"
        )
    return "\n".join(lines)


def _format_prices(prices: Dict[str, Dict]) -> str:
    if not prices:
        return "No price data."
    lines = []
    for ticker, p in prices.items():
        chg    = p.get("change_pct", 0)
        chg_str = f"+{chg:.1f}%" if chg >= 0 else f"{chg:.1f}%"
        vol_ratio = (p.get("volume", 0) / p.get("avg_volume", 1)
                     if p.get("avg_volume") else 0)
        lines.append(
            f"  {ticker}: ${p.get('price',0):.2f} ({chg_str}) | "
            f"52w: ${p.get('52w_low',0):.2f}–${p.get('52w_high',0):.2f} | "
            f"Vol: {vol_ratio:.1f}x avg"
        )
    return "\n".join(lines)


def _format_fundamentals(funds: Dict[str, Dict]) -> str:
    if not funds:
        return "No fundamental data available."
    lines = []
    for ticker, f in funds.items():
        pe     = f.get("pe_ratio")
        fpe    = f.get("forward_pe")
        eps    = f.get("eps")
        beta   = f.get("beta")
        target = f.get("analyst_target")
        rev_g  = f.get("revenue_growth_yoy")
        ear_g  = f.get("earnings_growth_yoy")
        margin = f.get("profit_margin")
        hi52   = f.get("52w_high")
        lo52   = f.get("52w_low")

        parts = [f"  {ticker}:"]
        if pe:     parts.append(f"P/E={pe:.1f}")
        if fpe:    parts.append(f"FwdP/E={fpe:.1f}")
        if eps:    parts.append(f"EPS=${eps:.2f}")
        if beta:   parts.append(f"Beta={beta:.2f}")
        if target: parts.append(f"TargetPrice=${target:.2f}")
        if rev_g:  parts.append(f"RevGrowth={rev_g*100:.1f}%YoY")
        if ear_g:  parts.append(f"EarningsGrowth={ear_g*100:.1f}%YoY")
        if margin: parts.append(f"ProfitMargin={margin*100:.1f}%")
        if hi52 and lo52: parts.append(f"52w=${lo52:.2f}–${hi52:.2f}")
        lines.append(" | ".join(parts))
    return "\n".join(lines)


def _format_positions(positions: List[Dict]) -> str:
    if not positions:
        return "  No current positions — full cash"
    return "\n".join(
        f"  {p['ticker']}: {p.get('qty',0):.0f} sh @ avg ${p.get('avg_cost',0):.2f} | "
        f"Now: ${p.get('current_price',0):.2f} | P/L: ${p.get('unrealized_pl',0):+,.0f}"
        for p in positions
    )


# ─────────────────────────────────────────────────────────────────────────────
# CLUSTER DETECTION — pre-process before sending to Claude
# ─────────────────────────────────────────────────────────────────────────────

def _detect_clusters(insider: List[Dict], congress: List[Dict]) -> str:
    """Full cluster analysis — every pattern that indicates smart money consensus."""
    from collections import Counter, defaultdict

    ins_buy_tickers  = []
    ins_sell_tickers = []
    for t in insider:
        for tx in t.get("transactions", []):
            if tx.get("action") == "BUY":
                ins_buy_tickers.append(t["ticker"])
            elif tx.get("action") == "SELL":
                ins_sell_tickers.append(t["ticker"])

    cong_buy_tickers  = [t["ticker"] for t in congress if "purchase" in t.get("action","").lower()]
    cong_sell_tickers = [t["ticker"] for t in congress if "sale" in t.get("action","").lower()]

    ins_buy_counts  = Counter(ins_buy_tickers)
    ins_sell_counts = Counter(ins_sell_tickers)
    cong_buy_counts = Counter(cong_buy_tickers)
    cong_sell_counts= Counter(cong_sell_tickers)

    lines = ["  ═══ HIGHEST CONVICTION SIGNALS ═══"]

    # Triple+ insider cluster buys
    for ticker, count in ins_buy_counts.most_common(30):
        if count >= 3:
            lines.append(f"  ★★★ MEGA CLUSTER: {ticker} — {count} insiders buying (EXTREMELY HIGH CONVICTION)")
        elif count == 2:
            lines.append(f"  ★★ CLUSTER BUY: {ticker} — {count} insiders buying")

    # Congress cluster buys
    for ticker, count in cong_buy_counts.most_common(30):
        if count >= 5:
            lines.append(f"  ★★★ CONGRESS MEGA: {ticker} — {count} legislators buying")
        elif count >= 3:
            lines.append(f"  ★★ CONGRESS CLUSTER: {ticker} — {count} legislators buying")
        elif count == 2:
            lines.append(f"  ★ CONGRESS BUY: {ticker} — {count} legislators buying")

    lines.append("\n  ═══ DOUBLE/TRIPLE SIGNAL OVERLAP ═══")
    ins_buy_set  = set(ins_buy_tickers)
    cong_buy_set = set(cong_buy_tickers)
    overlap = ins_buy_set & cong_buy_set
    if overlap:
        for ticker in sorted(overlap):
            lines.append(
                f"  ⚡ BOTH INSIDER+CONGRESS BUYING: {ticker} "
                f"({ins_buy_counts[ticker]} insiders, {cong_buy_counts[ticker]} legislators)"
            )
    else:
        lines.append("  (no insider+congress overlap found)")

    lines.append("\n  ═══ CLUSTER SELL WARNINGS ═══")
    for ticker, count in ins_sell_counts.most_common(15):
        if count >= 3:
            lines.append(f"  ⚠ CLUSTER SELL: {ticker} — {count} insiders selling (BEARISH)")

    lines.append(f"\n  Total unique buy tickers: {len(ins_buy_set)} insider, {len(cong_buy_set)} congress")
    return "\n".join(lines)


# ─────────────────────────────────────────────────────────────────────────────
# MAIN ANALYSIS FUNCTION
# ─────────────────────────────────────────────────────────────────────────────

async def analyze(
    insider_trades:    List[Dict],
    congress_trades:   List[Dict],
    news:              List[Dict],
    ticker_news:       List[Dict],
    prices:            Dict[str, Dict],
    portfolio_value:   float,
    current_positions: List[Dict],
    technicals:        Dict[str, Dict] = None,
    options_flow:      Dict[str, Dict] = None,
    macro:             Dict            = None,
    fundamentals:      Dict[str, Dict] = None,
) -> Dict[str, Any]:
    if not _client:
        return {"error": "ANTHROPIC_API_KEY not configured"}

    max_per_trade = portfolio_value * MAX_POSITION_PCT

    prompt = f"""═══════════════════════════════════════════
PORTFOLIO STATUS
═══════════════════════════════════════════
Total Value:    ${portfolio_value:,.2f}
Max Per Trade:  ${max_per_trade:,.2f} (5% rule)
Open Positions: {len(current_positions)}/{MAX_POSITIONS}

CURRENT HOLDINGS:
{_format_positions(current_positions)}

═══════════════════════════════════════════
MACRO MARKET CONTEXT
═══════════════════════════════════════════
{_format_macro(macro or {})}

═══════════════════════════════════════════
SMART MONEY — CLUSTER PATTERNS (PRE-ANALYZED)
═══════════════════════════════════════════
{_detect_clusters(insider_trades, congress_trades)}

═══════════════════════════════════════════
INSIDER TRADES — SEC FORM 4 (Most Recent First)
═══════════════════════════════════════════
{_format_insider(insider_trades)}

═══════════════════════════════════════════
CONGRESS & SENATE STOCK TRADES
═══════════════════════════════════════════
{_format_congress(congress_trades)}

═══════════════════════════════════════════
COMPANY FUNDAMENTALS (Alpha Vantage — Top Signal Tickers)
═══════════════════════════════════════════
{_format_fundamentals(fundamentals or {})}

═══════════════════════════════════════════
OPTIONS FLOW — UNUSUAL ACTIVITY
═══════════════════════════════════════════
{_format_options(options_flow or {})}

═══════════════════════════════════════════
TECHNICAL ANALYSIS — ALL SIGNAL TICKERS
═══════════════════════════════════════════
{_format_technicals(technicals or {})}

═══════════════════════════════════════════
CURRENT PRICES
═══════════════════════════════════════════
{_format_prices(prices)}

═══════════════════════════════════════════
MARKET NEWS (Signal-Ticker Prioritized)
═══════════════════════════════════════════
{_format_news(news, limit=300, priority_tickers=list(technicals.keys()) if technicals else None)}

═══════════════════════════════════════════
TICKER-SPECIFIC NEWS
═══════════════════════════════════════════
{_format_news(ticker_news, limit=200, priority_tickers=list(technicals.keys()) if technicals else None)}

═══════════════════════════════════════════
ANALYSIS INSTRUCTION
═══════════════════════════════════════════
Apply your complete trading framework to ALL data above.
1. Identify the highest-conviction setups using the Tier system
2. Check every candidate against the NO-TRADE conditions
3. Only recommend trades with confidence ≥ 6/10
4. Prioritize risk management over potential gains
5. Reference specific data points in every reasoning field
6. If no high-conviction setups exist, say so — cash is a position

Output your complete analysis as valid JSON now."""

    # Estimate token count (~4 chars = 1 token). Opus 4.8 supports 200K input.
    # Keep under 160K to leave room for system prompt and safety margin.
    _MAX_INPUT_CHARS = 640_000  # ≈ 160K tokens
    if len(prompt) > _MAX_INPUT_CHARS:
        # Trim by shrinking insider and congress sections proportionally
        prompt = prompt[:_MAX_INPUT_CHARS] + "\n\n[DATA TRUNCATED — token limit reached]"

    try:
        response = await _client.messages.create(
            model="claude-opus-4-8",   # Most powerful model — maximum reasoning
            max_tokens=8192,           # Rich, detailed output
            system=_SYSTEM,
            messages=[{"role": "user", "content": prompt}],
        )
        raw = response.content[0].text.strip()
        if raw.startswith("```"):
            raw = "\n".join(raw.split("\n")[1:])
            if raw.endswith("```"):
                raw = raw[:-3]
        result = json.loads(raw)
        result["tokens_used"] = {
            "input":  response.usage.input_tokens,
            "output": response.usage.output_tokens,
        }
        return result
    except json.JSONDecodeError as e:
        return {"error": f"JSON parse error: {e}", "raw": raw[:500]}
    except Exception as e:
        return {"error": str(e)}
