"""
JSON contract validation utilities.

Provides strict validation for JSON API responses including required fields,
types, and enumerations.
"""

from typing import Any, Dict, List, Optional, Union
from datetime import datetime
import json


def validate_iso8601_timestamp(value: str) -> bool:
    """Validate ISO8601 timestamp format."""
    try:
        datetime.fromisoformat(value.replace("Z", "+00:00"))
        return True
    except (ValueError, AttributeError):
        return False


def assert_required_keys(data: Dict[str, Any], required_keys: List[str], path: str = "") -> None:
    """Assert all required keys are present in data."""
    missing = [key for key in required_keys if key not in data]
    if missing:
        prefix = f"{path}." if path else ""
        raise AssertionError(f"Missing required keys in {path or 'root'}: {', '.join(prefix + k for k in missing)}")


def assert_key_type(data: Dict[str, Any], key: str, expected_type: type, path: str = "") -> None:
    """Assert a key has the expected type."""
    if key not in data:
        return  # Missing keys handled by assert_required_keys
    
    actual_type = type(data[key])
    prefix = f"{path}." if path else ""
    assert actual_type == expected_type, (
        f"Key '{prefix}{key}' has type {actual_type.__name__}, expected {expected_type.__name__}"
    )


def assert_enum_value(data: Dict[str, Any], key: str, allowed_values: List[str], path: str = "") -> None:
    """Assert a key's value is in the allowed enumeration."""
    if key not in data:
        return
    
    value = data[key]
    prefix = f"{path}." if path else ""
    assert value in allowed_values, (
        f"Key '{prefix}{key}' has value '{value}', expected one of {allowed_values}"
    )


def validate_health_contract(data: Dict[str, Any]) -> None:
    """Validate /health endpoint contract."""
    assert_required_keys(data, ["status", "timestamp"])
    assert_key_type(data, "status", str)
    assert_key_type(data, "timestamp", str)
    assert_enum_value(data, "status", ["ok", "degraded", "down", "error"])
    
    # Validate timestamp format
    if "timestamp" in data:
        assert validate_iso8601_timestamp(data["timestamp"]), (
            f"Invalid ISO8601 timestamp: {data['timestamp']}"
        )


def validate_status_contract(data: Dict[str, Any]) -> None:
    """Validate /api/status endpoint contract."""
    # Required top-level keys
    required_keys = [
        "service_name",
        "status",
        "status_enum",
        "lynx_protocol_version",
        "mcp_toolset_version",
        "tool_registry_hash",
        "current_mode",
        "maintenance_mode",
        "storage_backend",
        "kernel_api_reachable",
        "kernel_status",
        "supabase_reachable",
        "supabase_status",
        "draft_count_24h",
        "execution_count_24h",
        "pending_settlement_count",
        "total_mcp_tools_registered",
        "last_5_runs_summary",
        "timestamp",
    ]
    
    assert_required_keys(data, required_keys)
    
    # Type validations
    assert_key_type(data, "service_name", str)
    assert_key_type(data, "status", str)
    assert_key_type(data, "status_enum", str)
    assert_key_type(data, "lynx_protocol_version", str)
    assert_key_type(data, "mcp_toolset_version", str)
    assert_key_type(data, "tool_registry_hash", str)
    assert_key_type(data, "current_mode", str)
    assert_key_type(data, "maintenance_mode", bool)
    assert_key_type(data, "storage_backend", str)
    assert_key_type(data, "kernel_api_reachable", bool)
    assert_key_type(data, "kernel_status", str)
    assert_key_type(data, "supabase_reachable", bool)
    assert_key_type(data, "supabase_status", str)
    assert_key_type(data, "draft_count_24h", int)
    assert_key_type(data, "execution_count_24h", int)
    assert_key_type(data, "pending_settlement_count", int)
    assert_key_type(data, "total_mcp_tools_registered", int)
    assert_key_type(data, "last_5_runs_summary", list)
    assert_key_type(data, "timestamp", str)
    
    # Enum validations
    assert_enum_value(data, "status", ["operational", "degraded", "error"])
    assert_enum_value(data, "status_enum", ["ok", "pending", "bad", "error", "info"])
    assert_enum_value(data, "kernel_status", ["ok", "pending", "bad", "error", "info"])
    assert_enum_value(data, "supabase_status", ["ok", "pending", "bad", "error", "info"])
    
    # Validate timestamp
    assert validate_iso8601_timestamp(data["timestamp"]), (
        f"Invalid ISO8601 timestamp: {data['timestamp']}"
    )
    
    # Validate last_5_runs_summary structure
    if data["last_5_runs_summary"]:
        for i, run in enumerate(data["last_5_runs_summary"]):
            assert isinstance(run, dict), f"last_5_runs_summary[{i}] must be a dict"
            # Optional: validate run structure if needed


def validate_degraded_status_contract(data: Dict[str, Any]) -> None:
    """Validate status contract when system is in degraded mode."""
    # Same as validate_status_contract, but ensure degraded indicators are present
    validate_status_contract(data)
    
    # In degraded mode, at least one service should be unreachable
    if data["status"] == "degraded":
        assert (
            not data["kernel_api_reachable"] or 
            not data["supabase_reachable"] or
            data.get("error_message") is not None
        ), "Degraded status should indicate at least one service issue"

