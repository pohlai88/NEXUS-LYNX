"""
Dashboard contract validation tests.

Strict validation of JSON API responses: required keys, types, enumerations.
Prevents "it returns 200 but shape drifted" failures.
"""

import pytest
import httpx
from tests.utils.json_contracts import (
    validate_health_contract,
    validate_status_contract,
    validate_degraded_status_contract,
)


@pytest.mark.asyncio
@pytest.mark.contract
class TestHealthContract:
    """Test /health endpoint contract."""
    
    async def test_health_contract_structure(self, api_client: httpx.AsyncClient):
        """Test /health response matches contract."""
        response = await api_client.get("/health")
        assert response.status_code == 200
        
        data = response.json()
        validate_health_contract(data)
    
    async def test_health_status_enum(self, api_client: httpx.AsyncClient):
        """Test /health status is valid enum value."""
        response = await api_client.get("/health")
        data = response.json()
        
        # Status should be one of the allowed values
        assert data["status"] in ["ok", "degraded", "down", "error"]
    
    async def test_health_timestamp_format(self, api_client: httpx.AsyncClient):
        """Test /health timestamp is ISO8601 format."""
        response = await api_client.get("/health")
        data = response.json()
        
        from tests.utils.json_contracts import validate_iso8601_timestamp
        assert validate_iso8601_timestamp(data["timestamp"]), (
            f"Invalid timestamp format: {data['timestamp']}"
        )


@pytest.mark.asyncio
@pytest.mark.contract
class TestStatusContract:
    """Test /api/status endpoint contract."""
    
    async def test_status_contract_structure(self, api_client: httpx.AsyncClient):
        """Test /api/status response matches contract."""
        response = await api_client.get("/api/status")
        assert response.status_code == 200
        
        data = response.json()
        validate_status_contract(data)
    
    async def test_status_required_fields(self, api_client: httpx.AsyncClient):
        """Test /api/status has all required fields."""
        response = await api_client.get("/api/status")
        data = response.json()
        
        required_fields = [
            "service_name", "status", "status_enum", "lynx_protocol_version",
            "mcp_toolset_version", "kernel_api_reachable", "supabase_reachable",
            "draft_count_24h", "execution_count_24h", "timestamp",
        ]
        
        for field in required_fields:
            assert field in data, f"Missing required field: {field}"
    
    async def test_status_field_types(self, api_client: httpx.AsyncClient):
        """Test /api/status field types are correct."""
        response = await api_client.get("/api/status")
        data = response.json()
        
        # Type checks
        assert isinstance(data["service_name"], str)
        assert isinstance(data["status"], str)
        assert isinstance(data["maintenance_mode"], bool)
        assert isinstance(data["kernel_api_reachable"], bool)
        assert isinstance(data["supabase_reachable"], bool)
        assert isinstance(data["draft_count_24h"], int)
        assert isinstance(data["execution_count_24h"], int)
        assert isinstance(data["total_mcp_tools_registered"], int)
        assert isinstance(data["last_5_runs_summary"], list)
    
    async def test_status_enum_values(self, api_client: httpx.AsyncClient):
        """Test /api/status enum fields have valid values."""
        response = await api_client.get("/api/status")
        data = response.json()
        
        # Status enum validation
        assert data["status"] in ["operational", "degraded", "error"]
        assert data["status_enum"] in ["ok", "pending", "bad", "error", "info"]
        assert data["kernel_status"] in ["ok", "pending", "bad", "error", "info"]
        assert data["supabase_status"] in ["ok", "pending", "bad", "error", "info"]
    
    async def test_status_timestamp_format(self, api_client: httpx.AsyncClient):
        """Test /api/status timestamp is ISO8601 format."""
        response = await api_client.get("/api/status")
        data = response.json()
        
        from tests.utils.json_contracts import validate_iso8601_timestamp
        assert validate_iso8601_timestamp(data["timestamp"]), (
            f"Invalid timestamp format: {data['timestamp']}"
        )
    
    async def test_status_runs_summary_structure(self, api_client: httpx.AsyncClient):
        """Test /api/status last_5_runs_summary structure."""
        response = await api_client.get("/api/status")
        data = response.json()
        
        runs = data["last_5_runs_summary"]
        assert isinstance(runs, list)
        
        # If runs exist, validate structure
        for run in runs:
            assert isinstance(run, dict), "Each run should be a dict"

