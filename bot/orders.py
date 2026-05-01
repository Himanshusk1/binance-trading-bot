"""Order service layer.

This layer validates intent and coordinates the client call.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional

from .client import BinanceClient
from .validators import validate_order_request


@dataclass
class OrderRequest:
    symbol: str
    side: str
    order_type: str
    quantity: float
    price: Optional[float] = None


class OrderService:
    def __init__(self, client: BinanceClient):
        self.client = client

    def place_order(self, request: OrderRequest) -> Dict[str, Any]:
        validate_order_request(
            symbol=request.symbol,
            side=request.side,
            order_type=request.order_type,
            quantity=request.quantity,
            price=request.price,
        )
        return self.client.place_order(
            symbol=request.symbol,
            side=request.side,
            order_type=request.order_type,
            quantity=request.quantity,
            price=request.price,
        )
