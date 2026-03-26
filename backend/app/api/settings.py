from fastapi import APIRouter
from app.models import AppSettings
from app.services.settings_service import settings_service

router = APIRouter(prefix="/settings", tags=["Settings"])

@router.get("", response_model=AppSettings)
async def get_settings():
    """Get application settings."""
    return settings_service.get_settings()

@router.post("", response_model=AppSettings)
async def update_settings(settings: AppSettings):
    """Update application settings."""
    return settings_service.update_settings(settings.model_dump())
