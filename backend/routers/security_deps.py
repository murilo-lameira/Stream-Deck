from fastapi import HTTPException, Request, status

LOOPBACK_HOSTS = {"127.0.0.1", "::1"}


def require_loopback(request: Request) -> None:
    """Permite apenas requisições originadas no próprio host (loopback)."""
    client = request.client
    if client is None or client.host not in LOOPBACK_HOSTS:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Endpoint restrito ao loopback.",
        )
