import ipaddress
from urllib.parse import urlsplit

from fastapi import HTTPException, Request, status

LOOPBACK_HOSTS = {"127.0.0.1", "::1"}
ALLOWED_HOSTNAMES = {"localhost", "127.0.0.1", "::1"}
LAN_HOSTNAMES = {"localhost", "127.0.0.1", "::1", "streamdeck.local"}


def _host_from_header(value: str) -> str | None:
    """Extrai o hostname (sem porta) de um header Host; IPv6 vem entre colchetes."""
    try:
        return urlsplit("//" + value.strip()).hostname
    except ValueError:
        return None


def _forbidden(detail: str = "Endpoint restrito ao loopback.") -> HTTPException:
    return HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=detail)


def require_loopback(request: Request) -> None:
    """Permite apenas requisicoes do proprio host: cliente loopback, Host/Origin
    locais (anti DNS-rebinding) e sem Sec-Fetch-Site cross-site."""
    client = request.client
    if client is None or client.host not in LOOPBACK_HOSTS:
        raise _forbidden()
    host = _host_from_header(request.headers.get("host", ""))
    if host not in ALLOWED_HOSTNAMES:
        raise _forbidden()
    origin = request.headers.get("origin")
    if origin is not None:
        try:
            origin_host = urlsplit(origin).hostname
        except ValueError:
            origin_host = None
        if origin_host not in ALLOWED_HOSTNAMES:
            raise _forbidden()
    if request.headers.get("sec-fetch-site", "").lower() == "cross-site":
        raise _forbidden()


def _is_private_ip(value: str | None) -> bool:
    try:
        ip = ipaddress.ip_address(value or "")
    except ValueError:
        return False
    return ip.is_private or ip.is_loopback


def _lan_host_ok(hostname: str | None) -> bool:
    return hostname in LAN_HOSTNAMES or _is_private_ip(hostname)


def require_lan(request: Request) -> None:
    """Permite apenas requisicoes da rede local: cliente IP privado/loopback,
    Host/Origin locais (anti DNS-rebinding) e sem Sec-Fetch-Site cross-site."""
    detail = "Endpoint restrito a rede local."
    client = request.client
    if client is None or not _is_private_ip(client.host):
        raise _forbidden(detail)
    if not _lan_host_ok(_host_from_header(request.headers.get("host", ""))):
        raise _forbidden(detail)
    origin = request.headers.get("origin")
    if origin is not None:
        try:
            origin_host = urlsplit(origin).hostname
        except ValueError:
            origin_host = None
        if not _lan_host_ok(origin_host):
            raise _forbidden(detail)
    if request.headers.get("sec-fetch-site", "").lower() == "cross-site":
        raise _forbidden(detail)
