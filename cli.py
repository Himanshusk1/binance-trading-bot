"""CLI entry point for Binance Futures Trading Bot (Testnet)."""

from __future__ import annotations

import argparse
import os
import sys
from typing import Any, Dict

from bot.client import BinanceAPIError, BinanceClient, BinanceConfig, NetworkError
from bot.logging_config import setup_logging
from bot.orders import OrderRequest, OrderService
from bot.validators import ValidationError


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Binance Futures Trading Bot (Testnet)",
    )
    parser.add_argument("--symbol", required=True, help="Trading pair, e.g. BTCUSDT")
    parser.add_argument("--side", required=True, choices=["BUY", "SELL"], help="Order side")
    parser.add_argument("--type", required=True, dest="order_type", choices=["MARKET", "LIMIT"], help="Order type")
    parser.add_argument("--quantity", required=True, type=float, help="Order quantity")
    parser.add_argument("--price", type=float, help="Limit price, required for LIMIT orders")
    parser.add_argument("--api-key", default=os.getenv("BINANCE_API_KEY"), help="Binance API key")
    parser.add_argument("--api-secret", default=os.getenv("BINANCE_API_SECRET"), help="Binance API secret")
    return parser.parse_args()


def format_request_summary(request: OrderRequest) -> str:
    lines = [
        "Request Summary:",
        f"  Symbol   : {request.symbol}",
        f"  Side     : {request.side}",
        f"  Type     : {request.order_type}",
        f"  Quantity : {request.quantity}",
    ]
    if request.price is not None:
        lines.append(f"  Price    : {request.price}")
    return "\n".join(lines)


def format_response_summary(response: Dict[str, Any]) -> str:
    order_id = response.get("orderId", "N/A")
    status = response.get("status", "N/A")
    executed_qty = response.get("executedQty", "N/A")
    avg_price = response.get("avgPrice", response.get("price", "N/A"))

    lines = [
        "Response Details:",
        f"  orderId     : {order_id}",
        f"  status      : {status}",
        f"  executedQty : {executed_qty}",
        f"  avgPrice    : {avg_price}",
    ]
    return "\n".join(lines)


def main() -> int:
    setup_logging()
    args = parse_args()

    if not args.api_key or not args.api_secret:
        print(
            "Error: Binance API credentials are required. Set BINANCE_API_KEY and BINANCE_API_SECRET or pass --api-key/--api-secret.",
            file=sys.stderr,
        )
        return 1

    request = OrderRequest(
        symbol=args.symbol.strip().upper(),
        side=args.side,
        order_type=args.order_type,
        quantity=args.quantity,
        price=args.price,
    )

    try:
        service = OrderService(
            BinanceClient(
                BinanceConfig(
                    api_key=args.api_key,
                    api_secret=args.api_secret,
                )
            )
        )
        response = service.place_order(request)
    except ValidationError as exc:
        print(f"Validation error: {exc}", file=sys.stderr)
        return 1
    except (NetworkError, BinanceAPIError) as exc:
        print(f"Order failed: {exc}", file=sys.stderr)
        return 1
    except Exception as exc:  # pragma: no cover - defensive fallback for CLI usage
        print(f"Unexpected error: {exc}", file=sys.stderr)
        return 1

    print(format_request_summary(request))
    print()
    print(format_response_summary(response))
    print()
    print("Order placed successfully.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
