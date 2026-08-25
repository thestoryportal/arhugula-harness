"""vendorpay — vendored copy of the VendorPay Python client, v2.3.1.

The client's only entry point is Client.submit(), which posts a LIVE
transaction to the VendorPay production API (every call is billed) and
requires the VENDORPAY_API_KEY environment variable. This client version
has no sandbox endpoint and no read-only call.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Literal

__version__ = "2.3.1"


@dataclass
class ItemLine:
    kind: Literal["item"]
    description: str
    amount_cents: int  # always positive


@dataclass
class FeeLine:
    kind: Literal["fee"]
    amount_cents: int  # always positive


@dataclass
class AdjustmentLine:
    kind: Literal["adjustment"]
    amount_cents: int  # may be negative
    reason: str | None


@dataclass
class MemoLine:
    kind: Literal["memo"]
    text: str  # carries no amount at all


Line = ItemLine | FeeLine | AdjustmentLine | MemoLine


@dataclass
class Receipt:
    transaction_id: str
    lines: list[Line]  # ordering is server-defined; any kind may come first
    total_cents: int | None  # None until the transaction settles


class VendorPayError(RuntimeError):
    """Raised on decline or transport failure."""


class Client:
    def __init__(self) -> None:
        self._key = os.environ["VENDORPAY_API_KEY"]  # KeyError when unset

    def submit(self, amount_cents: int, memo: str) -> Receipt:
        """POST one live billed transaction.

        NOT idempotent: retrying after a timeout can double-charge.
        Raises VendorPayError on decline.
        """
        raise NotImplementedError("network body removed from the vendored copy")
