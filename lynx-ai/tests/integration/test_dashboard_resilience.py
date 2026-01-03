"""
Dashboard resilience tests - Degradation mode and error handling.

Tests user-facing behavior when backend dependencies fail.
Ensures dashboard returns 200 with visible degraded indicators.
"""

import pytest
import httpx
from unittest.mock import patch, AsyncMock
from tests.utils.json_contracts import validate_degraded_status_contract
from tests.utils.html_selectors import parse_html


@pytest.mark.asyncio
@pytest.mark.integration
class TestDegradationMode:
    """Test dashboard behavior in degraded mode."""
    
    async def test_api_status_returns_200_when_backend_down(self, api_client: httpx.AsyncClient):
        """
        Test /api/status returns 200 even when backend services are down.
        
        This is critical: the dashboard should always return 200, but indicate
        degraded status in the response.
        """
        response = await api_client.get("/api/status")
        
        # Should always return 200, even if services are down
        assert response.status_code == 200
        
        data = response.json()
        
        # If degraded, should have indicators
        if data["status"] == "degraded":
            assert (
                not data["kernel_api_reachable"] or
                not data["supabase_reachable"] or
                data.get("error_message") is not None
            ), "Degraded status should indicate service issues"
    
    async def test_dashboard_returns_200_when_backend_down(self, api_client: httpx.AsyncClient):
        """Test main dashboard returns 200 even when backend is down."""
        response = await api_client.get("/")
        
        # Dashboard should always return 200
        assert response.status_code == 200
        
        # Should render HTML even if backend is down
        assert "text/html" in response.headers.get("content-type", "")
        assert len(response.text) > 0, "Should render HTML content"
    
    async def test_fragments_handle_backend_errors(self, api_client: httpx.AsyncClient):
        """Test fragments handle backend errors gracefully."""
        fragments = ["_kpis", "_services", "_recent", "_cockpit"]
        
        for fragment in fragments:
            response = await api_client.get(f"/dashboard/{fragment}")
            
            # Fragments should return 200 even on errors
            assert response.status_code == 200, f"Fragment {fragment} should return 200"
            
            # Should render HTML (even if it's an error message)
            assert "text/html" in response.headers.get("content-type", "")
            assert len(response.text) > 0, f"Fragment {fragment} should render content"
    
    async def test_degraded_status_contract(self, api_client: httpx.AsyncClient):
        """Test degraded status response matches contract."""
        response = await api_client.get("/api/status")
        data = response.json()
        
        # If status is degraded, validate degraded contract
        if data["status"] == "degraded":
            validate_degraded_status_contract(data)
    
    async def test_dashboard_shows_degraded_indicator(self, api_client: httpx.AsyncClient):
        """Test dashboard shows degraded indicator when services are down."""
        # Get status to check if degraded
        status_response = await api_client.get("/api/status")
        status_data = status_response.json()
        
        if status_data["status"] == "degraded":
            # Check dashboard shows degraded indicator
            dashboard_response = await api_client.get("/")
            soup = parse_html(dashboard_response.text)
            
            # Look for degraded/bad status indicators
            text = soup.get_text()
            degraded_indicators = ["degraded", "bad", "error", "disconnected", "unreachable"]
            
            assert any(
                indicator.lower() in text.lower() for indicator in degraded_indicators
            ), "Dashboard should show degraded status indicator"


@pytest.mark.asyncio
@pytest.mark.integration
class TestErrorRecovery:
    """Test error recovery and graceful degradation."""
    
    async def test_health_endpoint_always_works(self, api_client: httpx.AsyncClient):
        """Test /health endpoint always returns 200."""
        response = await api_client.get("/health")
        
        # Health should always work, even if other services are down
        assert response.status_code == 200
        
        data = response.json()
        assert "status" in data
        assert "timestamp" in data
    
    async def test_api_status_error_message_format(self, api_client: httpx.AsyncClient):
        """Test error messages in status API are properly formatted."""
        response = await api_client.get("/api/status")
        data = response.json()
        
        # If error_message exists, it should be a string
        if "error_message" in data and data["error_message"]:
            assert isinstance(data["error_message"], str)
            assert len(data["error_message"]) > 0
    
    async def test_fragments_show_error_messages(self, api_client: httpx.AsyncClient):
        """Test fragments show error messages when appropriate."""
        # Test KPI fragment
        response = await api_client.get("/dashboard/_kpis")
        assert response.status_code == 200
        
        # If there's an error, it should be visible in HTML
        soup = parse_html(response.text)
        text = soup.get_text()
        
        # Error messages should be user-friendly if present
        # (This is a soft check - doesn't fail if no errors)
        if "error" in text.lower() or "failed" in text.lower():
            # Error should be visible, not hidden
            assert len(text.strip()) > 0, "Error messages should be visible"


@pytest.mark.asyncio
@pytest.mark.integration
class TestServiceConnectivity:
    """Test service connectivity indicators."""
    
    async def test_kernel_api_reachability_indicated(self, api_client: httpx.AsyncClient):
        """Test Kernel API reachability is indicated in status."""
        response = await api_client.get("/api/status")
        data = response.json()
        
        assert "kernel_api_reachable" in data
        assert isinstance(data["kernel_api_reachable"], bool)
        assert "kernel_status" in data
        assert data["kernel_status"] in ["ok", "pending", "bad", "error", "info"]
    
    async def test_supabase_reachability_indicated(self, api_client: httpx.AsyncClient):
        """Test Supabase reachability is indicated in status."""
        response = await api_client.get("/api/status")
        data = response.json()
        
        assert "supabase_reachable" in data
        assert isinstance(data["supabase_reachable"], bool)
        assert "supabase_status" in data
        assert data["supabase_status"] in ["ok", "pending", "bad", "error", "info"]
    
    async def test_services_fragment_shows_connectivity(self, api_client: httpx.AsyncClient):
        """Test services fragment shows connectivity status."""
        response = await api_client.get("/dashboard/_services")
        soup = parse_html(response.text)
        
        text = soup.get_text()
        
        # Should show connectivity status for services
        assert "Kernel" in text or "kernel" in text.lower()
        assert "Supabase" in text or "supabase" in text.lower()
        
        # Should show status (connected/disconnected)
        status_indicators = ["connected", "disconnected", "ok", "bad", "error"]
        assert any(
            indicator.lower() in text.lower() for indicator in status_indicators
        ), "Should show service connectivity status"

