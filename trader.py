import os
from typing import List, Dict, Optional

ALPACA_KEY    = os.environ.get("ALPACA_API_KEY", "")
ALPACA_SECRET = os.environ.get("ALPACA_SECRET_KEY", "")
_PAPER = True  # Always paper trade


def _client():
    from alpaca.trading.client import TradingClient
    return TradingClient(ALPACA_KEY, ALPACA_SECRET, paper=_PAPER)


def get_account() -> Dict:
    if not (ALPACA_KEY and ALPACA_SECRET):
        return {"error": "Alpaca keys not configured. Add ALPACA_API_KEY and ALPACA_SECRET_KEY to .env"}
    try:
        acct = _client().get_account()
        return {
            "cash": float(acct.cash),
            "portfolio_value": float(acct.portfolio_value),
            "buying_power": float(acct.buying_power),
            "equity": float(acct.equity),
            "pl_today": float(acct.equity) - float(acct.last_equity),
            "pl_today_pct": ((float(acct.equity) - float(acct.last_equity)) / float(acct.last_equity) * 100)
                           if float(acct.last_equity) else 0,
        }
    except Exception as e:
        return {"error": str(e)}


def get_positions() -> List[Dict]:
    if not (ALPACA_KEY and ALPACA_SECRET):
        return []
    try:
        positions = _client().get_all_positions()
        return [{
            "ticker": p.symbol,
            "qty": float(p.qty),
            "avg_cost": float(p.avg_entry_price),
            "current_price": float(p.current_price),
            "market_value": float(p.market_value),
            "unrealized_pl": float(p.unrealized_pl),
            "unrealized_pl_pct": float(p.unrealized_plpc) * 100,
        } for p in positions]
    except Exception:
        return []


def get_orders(status: str = "all", limit: int = 20) -> List[Dict]:
    if not (ALPACA_KEY and ALPACA_SECRET):
        return []
    try:
        from alpaca.trading.requests import GetOrdersRequest
        from alpaca.trading.enums import QueryOrderStatus
        req = GetOrdersRequest(status=QueryOrderStatus.ALL, limit=limit)
        orders = _client().get_orders(filter=req)
        return [{
            "id": str(o.id),
            "ticker": o.symbol,
            "side": o.side.value,
            "qty": float(o.qty or 0),
            "filled_qty": float(o.filled_qty or 0),
            "filled_price": float(o.filled_avg_price or 0),
            "status": o.status.value,
            "submitted_at": str(o.submitted_at)[:19] if o.submitted_at else "",
            "type": o.type.value,
        } for o in orders]
    except Exception:
        return []


def place_order(ticker: str, side: str, qty: int, reason: str = "") -> Dict:
    """Place a paper market order. side = 'buy' or 'sell'."""
    if not (ALPACA_KEY and ALPACA_SECRET):
        return {"error": "Alpaca keys not configured"}
    if qty <= 0:
        return {"error": "Quantity must be positive"}
    try:
        from alpaca.trading.requests import MarketOrderRequest
        from alpaca.trading.enums import OrderSide, TimeInForce
        order_data = MarketOrderRequest(
            symbol=ticker.upper(),
            qty=qty,
            side=OrderSide.BUY if side.lower() == "buy" else OrderSide.SELL,
            time_in_force=TimeInForce.DAY,
        )
        order = _client().submit_order(order_data)
        return {
            "success": True,
            "order_id": str(order.id),
            "ticker": ticker.upper(),
            "side": side,
            "qty": qty,
            "status": order.status.value,
            "reason": reason,
        }
    except Exception as e:
        return {"error": str(e), "ticker": ticker, "side": side, "qty": qty}


def close_position(ticker: str) -> Dict:
    """Close all shares of a position."""
    if not (ALPACA_KEY and ALPACA_SECRET):
        return {"error": "Alpaca keys not configured"}
    try:
        resp = _client().close_position(ticker.upper())
        return {"success": True, "ticker": ticker.upper(), "order_id": str(resp.id)}
    except Exception as e:
        return {"error": str(e)}
