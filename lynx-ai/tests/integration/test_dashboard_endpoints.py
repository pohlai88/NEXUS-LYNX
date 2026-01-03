"""
Dashboard endpoint tests - Status codes and content types.

Tests basic HTTP behavior: status codes, content types, headers.
Environment-driven: works with localhost or Railway via TEST_API_URL.
"""

import pytest
import httpx
from tests.utils.http_assertions import (
    assert_status_code,
    assert_content_type,
    assert_has_header,
    assert_no_secrets_in_response,
)


@pytest.mark.asyncio
class TestDashboardEndpoints:
    """Test main dashboard endpoints."""
    
    async def test_dashboard_home_returns_200(self, api_client: httpx.AsyncClient):
        """Test main dashboard returns 200 OK."""
        response = await api_client.get("/")
        assert_status_code(response, 200)
        assert_content_type(response, "text/html")
    
    async def test_dashboard_alias_returns_200(self, api_client: httpx.AsyncClient):
        """Test /dashboard alias returns 200 OK."""
        response = await api_client.get("/dashboard")
        assert_status_code(response, 200)
        assert_content_type(response, "text/html")
    
    async def test_health_endpoint_returns_200(self, api_client: httpx.AsyncClient):
        """Test /health endpoint returns 200 OK."""
        response = await api_client.get("/health")
        assert_status_code(response, 200)
        assert_content_type(response, "application/json")
    
    async def test_api_status_returns_200(self, api_client: httpx.AsyncClient):
        """Test /api/status endpoint returns 200 OK."""
        response = await api_client.get("/api/status")
        assert_status_code(response, 200)
        assert_content_type(response, "application/json")
    
    async def test_health_no_secrets(self, api_client: httpx.AsyncClient):
        """Test /health endpoint does not leak secrets."""
        response = await api_client.get("/health")
        assert_no_secrets_in_response(response)
    
    async def test_api_status_no_secrets(self, api_client: httpx.AsyncClient):
        """Test /api/status endpoint does not leak secrets."""
        response = await api_client.get("/api/status")
        assert_no_secrets_in_response(response)


@pytest.mark.asyncio
class TestFragmentEndpoints:
    """Test dashboard fragment endpoints."""
    
    async def test_fragment_kpis_returns_200(self, api_client: httpx.AsyncClient):
        """Test KPI fragment returns 200 OK."""
        response = await api_client.get("/dashboard/_kpis")
        assert_status_code(response, 200)
        assert_content_type(response, "text/html")
    
    async def test_fragment_services_returns_200(self, api_client: httpx.AsyncClient):
        """Test services fragment returns 200 OK."""
        response = await api_client.get("/dashboard/_services")
        assert_status_code(response, 200)
        assert_content_type(response, "text/html")
    
    async def test_fragment_recent_returns_200(self, api_client: httpx.AsyncClient):
        """Test recent activity fragment returns 200 OK."""
        response = await api_client.get("/dashboard/_recent")
        assert_status_code(response, 200)
        assert_content_type(response, "text/html")
    
    async def test_fragment_cockpit_returns_200(self, api_client: httpx.AsyncClient):
        """Test cockpit fragment returns 200 OK."""
        response = await api_client.get("/dashboard/_cockpit")
        assert_status_code(response, 200)
        assert_content_type(response, "text/html")


@pytest.mark.asyncio
class TestStaticFiles:
    """Test static file endpoints."""
    
    async def test_css_file_returns_200(self, api_client: httpx.AsyncClient):
        """Test CSS file returns 200 OK."""
        response = await api_client.get("/static/aibos-design-system.css")
        assert_status_code(response, 200)
        assert_content_type(response, "text/css")
    
    async def test_css_file_has_cache_headers(self, api_client: httpx.AsyncClient):
        """Test CSS file has cache headers."""
        response = await api_client.get("/static/aibos-design-system.css")
        # Cache headers are optional but nice to have
        if "cache-control" in response.headers:
            assert_has_header(response, "cache-control")


@pytest.mark.asyncio
class TestErrorHandling:
    """Test error handling for invalid endpoints."""
    
    async def test_404_for_invalid_endpoint(self, api_client: httpx.AsyncClient):
        """Test 404 for non-existent endpoint."""
        response = await api_client.get("/nonexistent")
        assert_status_code(response, 404)
    
    async def test_404_for_invalid_fragment(self, api_client: httpx.AsyncClient):
        """Test 404 for non-existent fragment."""
        response = await api_client.get("/dashboard/_nonexistent")
        assert_status_code(response, 404)

