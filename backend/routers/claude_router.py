import asyncio
import logging

from fastapi import APIRouter, Depends, Request, Response

from managers.connection_manager import manager
from routers.deck_router import verify_bearer_token
from routers.security_deps import require_loopback
from schemas.deck_schemas import ClaudePermissionHookInput
from services import claude_permission_service

logger = logging.getLogger("streamdeck.claude_router")

router = APIRouter(prefix="/api/v1/claude", tags=["claude"])


async def _watch_disconnect(request: Request) -> None:
    """Retorna quando o cliente (hook) fechar a conexao."""
    while True:
        if await request.is_disconnected():
            return
        await asyncio.sleep(1.0)


@router.post(
    "/permission",
    dependencies=[Depends(require_loopback), Depends(verify_bearer_token)],
)
async def claude_permission(payload: ClaudePermissionHookInput, request: Request):
    """Recebe o hook PermissionRequest, pede decisao ao celular e devolve allow/deny.

    204 (corpo vazio) = sem decisao: o Claude Code segue o fluxo normal no terminal.
    """
    if not manager.active_connections:
        return Response(status_code=204)

    broker = claude_permission_service.broker
    request_id = await broker.submit(payload.tool_name, payload.tool_input, payload.cwd)
    if request_id is None:
        return Response(status_code=204)

    wait_task = asyncio.ensure_future(broker.wait(request_id))
    watch_task = asyncio.ensure_future(_watch_disconnect(request))
    try:
        await asyncio.wait({wait_task, watch_task}, return_when=asyncio.FIRST_COMPLETED)
        if wait_task.done():
            decision = wait_task.result()
            if decision in ("allow", "deny"):
                return {"behavior": decision}
            return Response(status_code=204)
        # Hook desconectou antes da decisao.
        await broker.cancel(request_id)
        return Response(status_code=204)
    finally:
        for t in (wait_task, watch_task):
            if not t.done():
                t.cancel()
        await asyncio.gather(wait_task, watch_task, return_exceptions=True)
