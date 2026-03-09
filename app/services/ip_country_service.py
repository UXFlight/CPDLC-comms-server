from __future__ import annotations

import ipaddress
from urllib import request

def _normalize_ip(ip: str) -> str:
    return ip.split(",")[0].strip()


def _is_local_or_private(ip: str) -> bool:
    try:
        parsed = ipaddress.ip_address(ip)
        return bool(
            parsed.is_private
            or parsed.is_loopback
            or parsed.is_link_local
            or parsed.is_reserved
            or parsed.is_multicast
            or parsed.is_unspecified
        )
    except ValueError:
        return True


def _lookup_country_from_ip(ip: str) -> str | None:
    try:
        url = f"https://ipapi.co/{ip}/country/"
        req = request.Request(url, method="GET")
        with request.urlopen(req, timeout=2) as resp:
            if resp.status != 200:
                return None
            code = resp.read().decode("utf-8").strip().upper()
            if len(code) == 2 and code.isalpha():
                return code
    except Exception:
        return None
    return None


def detect_country_code(ip: str | None, cache: dict[str, str] | None = None) -> str:
    if not ip:
        return "UNKNOWN"
    normalized = _normalize_ip(ip)
    if not normalized:
        return "UNKNOWN"
    if _is_local_or_private(normalized):
        return "LOCAL"

    working_cache = cache if cache is not None else {}
    if normalized in working_cache:
        return working_cache[normalized]

    country = _lookup_country_from_ip(normalized) or "UNKNOWN"
    working_cache[normalized] = country
    return country
