from fastapi import APIRouter

router = APIRouter(prefix="/french-reader", tags=["French Reader"])


@router.get("/status")
async def status() -> dict[str, str]:
    return {"module": "french-reader", "version": "0.1.0", "phase": "M0-skeleton"}
