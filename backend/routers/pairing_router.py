from fastapi import APIRouter, Depends, Request
from fastapi.responses import JSONResponse

from routers.security_deps import require_lan
from schemas.deck_schemas import PairConfirmInput
from services import pairing_service

router = APIRouter(
    prefix="/api/v1/deck/pair",
    tags=["pairing"],
    dependencies=[Depends(require_lan)],
)


def _client_ip(request: Request) -> str:
    return request.client.host if request.client else ""


@router.post("/request")
async def pair_request(request: Request):
    status, body = await pairing_service.pairing.request(_client_ip(request))
    return JSONResponse(status_code=status, content=body)


@router.post("/confirm")
async def pair_confirm(payload: PairConfirmInput, request: Request):
    status, body = pairing_service.pairing.confirm(
        payload.pair_id, payload.code, _client_ip(request)
    )
    return JSONResponse(status_code=status, content=body)
