"""Binance Futures Testnet REST client.

This module owns request signing, network calls, and API-level error handling.
"""

from __future__ import annotations

import hashlib
import hmac
import logging
import time
from dataclasses import dataclass
from typing import Any, Dict, Optional
from urllib.parse import urlencode

import requests


class BinanceAPIError(Exception):
    """Raised when Binance returns an error payload."""

    def __init__(self, message: str, status_code: Optional[int] = None, payload: Any = None):
        super().__init__(message)
        self.status_code = status_code
        self.payload = payload


class NetworkError(Exception):
    """Raised when the HTTP request fails before Binance responds."""


@dataclass(frozen=True)
class BinanceConfig:
    api_key: str
    api_secret: str
    base_url: str = "https://testnet.binancefuture.com"
    recv_window: int = 5000


class BinanceClient:
    """Small Binance Futures REST wrapper.

    The client logs safe request metadata only. Secrets are never logged.
    """

    def __init__(self, config: BinanceConfig, session: Optional[requests.Session] = None):
        self.config = config
        self.session = session or requests.Session()
        self.logger = logging.getLogger(__name__)

    def _sign(self, params: Dict[str, Any]) -> str:
        query_string = urlencode(params, doseq=True)
        return hmac.new(
            self.config.api_secret.encode("utf-8"),
            query_string.encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()

    def _request(self, method: str, path: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        request_params = dict(params or {})
        request_params["timestamp"] = int(time.time() * 1000)
        request_params["recvWindow"] = self.config.recv_window
        request_params["signature"] = self._sign(request_params)

        headers = {"X-MBX-APIKEY": self.config.api_key}
        url = f"{self.config.base_url}{path}"

        safe_params = {key: value for key, value in request_params.items() if key != "signature"}
        self.logger.info("Binance request %s %s params=%s", method, path, safe_params)

        try:
            response = self.session.request(
                method=method,
                url=url,
                params=request_params if method.upper() == "GET" else None,
                data=request_params if method.upper() != "GET" else None,
                headers=headers,
                timeout=15,
            )
        except requests.RequestException as exc:
            self.logger.exception("Network error calling Binance")
            raise NetworkError(f"Network error calling Binance: {exc}") from exc

        self.logger.info("Binance response status=%s body=%s", response.status_code, self._shorten(response.text))

        try:
            payload = response.json()
        except ValueError as exc:
            raise BinanceAPIError("Binance returned a non-JSON response", response.status_code, response.text) from exc

        if response.status_code >= 400:
            message = payload.get("msg") if isinstance(payload, dict) else response.text
            raise BinanceAPIError(message or "Binance API error", response.status_code, payload)

        if isinstance(payload, dict) and payload.get("code") not in (None, 200):
            message = payload.get("msg") or "Binance API error"
            raise BinanceAPIError(message, response.status_code, payload)

        return payload

    @staticmethod
    def _shorten(text: str, limit: int = 500) -> str:
        if len(text) <= limit:
            return text
        return f"{text[:limit]}..."

    def place_order(
        self,
        symbol: str,
        side: str,
        order_type: str,
        quantity: float,
        price: Optional[float] = None,
    ) -> Dict[str, Any]:
        params: Dict[str, Any] = {
            "symbol": symbol,
            "side": side,
            "type": order_type,
            "quantity": quantity,
            "newOrderRespType": "RESULT",
        }

        if order_type == "LIMIT":
            params["timeInForce"] = "GTC"
            params["price"] = price

        return self._request("POST", "/fapi/v1/order", params)
