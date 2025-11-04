from __future__ import annotations

import argparse
import json
import statistics
import time
from typing import Any, Dict, List

from rich.console import Console
from rich.table import Table

from . import mock_exchange
from .cache import Cache


console = Console()


def fetch_order_book(symbol: str, cache: Cache | None, ttl_seconds: int) -> tuple[Dict[str, Any], float, bool]:
    """Fetch order book and measure latency.

    Returns (payload, latency_ms, cache_hit)
    """
    cache_key = f"orderbook:{symbol}"
    start = time.perf_counter()
    cache_hit = False

    if cache is not None:
        cached = cache.get_json(cache_key)
        if cached is not None:
            end = time.perf_counter()
            return cached, (end - start) * 1000.0, True

    payload = mock_exchange.get_order_book(symbol)

    if cache is not None:
        cache.set_json(cache_key, payload, ttl_seconds=ttl_seconds)

    end = time.perf_counter()
    return payload, (end - start) * 1000.0, cache_hit


def benchmark(symbol: str, iterations: int, use_cache: bool, ttl_seconds: int) -> None:
    cache = Cache() if use_cache else None
    console.print(f"Backend cache: [bold]{cache.backend if cache else 'disabled'}[/bold]")

    latencies_ms: List[float] = []
    hits = 0
    for i in range(iterations):
        payload, latency_ms, cache_hit = fetch_order_book(symbol, cache, ttl_seconds)
        latencies_ms.append(latency_ms)
        hits += 1 if cache_hit else 0
        console.print(
            f"[{i+1:02d}/{iterations}] latency={latency_ms:.1f}ms cache_hit={cache_hit} payload.ts={payload['ts']}"
        )

    p50 = statistics.median(latencies_ms)
    p95 = statistics.quantiles(latencies_ms, n=20)[18] if len(latencies_ms) > 1 else p50
    avg = sum(latencies_ms) / len(latencies_ms)

    table = Table(title="Latency Summary")
    table.add_column("Metric")
    table.add_column("Value")
    table.add_row("iterations", str(iterations))
    table.add_row("cache", cache.backend if cache else "disabled")
    table.add_row("cache_hits", str(hits))
    table.add_row("avg_ms", f"{avg:.1f}")
    table.add_row("p50_ms", f"{p50:.1f}")
    table.add_row("p95_ms", f"{p95:.1f}")
    console.print(table)


def main() -> None:
    parser = argparse.ArgumentParser(description="Monitor/benchmark simulated trade latency with optional Redis cache")
    parser.add_argument("--symbol", default="BTCUSDT", help="Trading pair symbol")
    parser.add_argument("--iterations", type=int, default=10, help="Number of requests to send")
    parser.add_argument("--use-cache", action=argparse.BooleanOptionalAction, default=True, help="Enable cache")
    parser.add_argument("--ttl", type=int, default=1, help="Cache TTL seconds")
    args = parser.parse_args()

    benchmark(args.symbol, args.iterations, args.use_cache, args.ttl)


if __name__ == "__main__":
    main()


