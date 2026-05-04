# D:/AI/ai-scout/browser-use/backend/api/browser.py

from fastapi import APIRouter

from backend.api.response import ApiResponse
from backend.schemas.browser_config import (
    BrowserConfigResponse,
    BrowserStatusResponse,
    ChromeProfileInfo,
)
from backend.services.browser_service import BrowserService
from backend.utils.chrome import get_available_profiles

router = APIRouter()


@router.get("/profiles", response_model=ApiResponse[list[ChromeProfileInfo]])
async def list_profiles():
    """Get available Chrome Profile list"""
    profiles = get_available_profiles()

    response_data = [
        ChromeProfileInfo(
            name=p["name"],
            path=p["path"],
        )
        for p in profiles
    ]

    return ApiResponse.success(data=response_data)


@router.get("/status", response_model=ApiResponse[BrowserStatusResponse])
async def get_browser_status(cdp_port: int = 9242):
    """Get browser status"""
    profiles = get_available_profiles()

    profile_infos = [
        ChromeProfileInfo(
            name=p["name"],
            path=p["path"],
        )
        for p in profiles
    ]

    # Test CDP connection
    is_connected = await BrowserService.test_connection(cdp_port)

    return ApiResponse.success(
        data=BrowserStatusResponse(
            is_connected=is_connected,
            cdp_url=f"http://localhost:{cdp_port}" if is_connected else None,
            profiles=profile_infos,
        )
    )


@router.post("/test-connection", response_model=ApiResponse[dict])
async def test_connection(cdp_port: int = 9242):
    """Test CDP connection"""
    result = await BrowserService.test_connection(cdp_port)

    return ApiResponse.success(
        data={
            "success": result,
            "message": "Connection successful" if result else "Connection failed",
        }
    )
