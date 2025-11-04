import time
from typing import Dict, Any


def _expensive_fetch(symbol: str) -> Dict[str, Any]:
    """Simulate a slow upstream call (~800ms)."""
    time.sleep(0.8)
    # Toy payload
    ts_ms = int(time.time() * 1000)
    return {
        "symbol": symbol,
        "best_bid": 100.0,
        "best_ask": 100.1,
        "ts": ts_ms,
    }


def get_order_book(symbol: str) -> Dict[str, Any]:
    """Public API: fetch the latest order book for a symbol."""
    return _expensive_fetch(symbol)


