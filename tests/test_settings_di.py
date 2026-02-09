import pytest
from httpx import ASGITransport, AsyncClient

from app.core.config import get_settings
from app.main import app


@pytest.mark.asyncio
async def test_get_settings_dependency_override(dependency_overrides):
    def override_get_settings():
        base_settings = get_settings()
        return base_settings.model_copy(update={"api_key": "override-key"})

    dependency_overrides({get_settings: override_get_settings})
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        ok_response = await client.get("/health", headers={"X-API-Key": "override-key"})
        assert ok_response.status_code == 200

        bad_response = await client.get("/health", headers={"X-API-Key": "test-key"})
        assert bad_response.status_code == 401
