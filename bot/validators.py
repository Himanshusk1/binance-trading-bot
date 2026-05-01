"""Input validation helpers."""

from __future__ import annotations

from typing import Optional


class ValidationError(ValueError):
    """Raised when CLI or business validation fails."""


def validate_order_request(
    symbol: str,
    side: str,
    order_type: str,
    quantity: float,
    price: Optional[float] = None,
) -> None:
    if not symbol or not symbol.strip():
        raise ValidationError("--symbol is required")

    if side not in {"BUY", "SELL"}:
        raise ValidationError("--side must be BUY or SELL")

    if order_type not in {"MARKET", "LIMIT"}:
        raise ValidationError("--type must be MARKET or LIMIT")

    if quantity <= 0:
        raise ValidationError("--quantity must be greater than 0")

    if order_type == "LIMIT" and price is None:
        raise ValidationError("--price is required when --type is LIMIT")

    if price is not None and price <= 0:
        raise ValidationError("--price must be greater than 0")
