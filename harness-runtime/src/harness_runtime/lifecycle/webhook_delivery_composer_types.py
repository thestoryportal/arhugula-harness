"""U-RT-96 webhook config carrier and first local operator endpoint policy.

The v1.26 empty marker remains accepted for legacy binding tests. A complete
endpoint and public identifier binds a one-attempt loopback HTTP delivery.
`None` at RuntimeConfig remains the production opt-out. Remote endpoints,
authentication and generalized retry need separate contracts.
"""

from __future__ import annotations

import ipaddress
import re
from dataclasses import dataclass
from urllib.parse import urlsplit

_WEBHOOK_PATH = re.compile(r"/[A-Za-z0-9/_-]*\Z")


def parse_loopback_webhook_endpoint(url: str) -> str:
    """Return one canonical HTTP endpoint on literal 127.0.0.1 or ::1.

    The first local production profile deliberately has no DNS, proxy, remote
    host, redirect, URL credential, query, or fragment route. A later network
    profile needs a separate resolution-time connection policy.
    """
    if not url or len(url) > 256 or any(ord(c) <= 32 or ord(c) == 127 or c in "\\?#" for c in url):
        raise ValueError("webhook endpoint contains an unsafe character or length")
    try:
        parts = urlsplit(url)
        host = parts.hostname
        port = parts.port
        address = ipaddress.ip_address(host or "")
    except ValueError as exc:
        raise ValueError("webhook endpoint must use a literal loopback address and port") from exc
    if (
        parts.scheme != "http"
        or parts.username is not None
        or parts.password is not None
        or "@" in parts.netloc
        or parts.query
        or parts.fragment
        or port is None
        or port == 0
        or str(address) != host
        or address not in (ipaddress.ip_address("127.0.0.1"), ipaddress.ip_address("::1"))
    ):
        raise ValueError("webhook endpoint must be plain HTTP on literal 127.0.0.1 or ::1")
    path = parts.path or "/"
    if _WEBHOOK_PATH.fullmatch(path) is None:
        raise ValueError("webhook endpoint path contains unsupported characters")
    host_text = f"[{address}]" if address.version == 6 else str(address)
    return f"http://{host_text}:{port}{path}"


@dataclass(frozen=True)
class WebhookDeliveryComposerConfig:
    """Operator-supplied local webhook binding, with legacy empty marker.

    Empty marker remains compatible where no pause protocol is bound. A complete
    endpoint and public identifier enable one-attempt loopback delivery.
    Absence (`None`) remains the production opt-out.
    """

    webhook_id: str | None = None
    endpoint_url: str | None = None
    timeout_seconds: int | None = None

    @classmethod
    def default(cls) -> WebhookDeliveryComposerConfig:
        """Return the legacy opt-in marker without an operator endpoint."""
        return cls()
