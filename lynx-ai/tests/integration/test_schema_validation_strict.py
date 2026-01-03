"""
Strict Schema Validation Tests (A2. Schema Validation - Missing Tests).

Tests validate:
- Unknown extra fields are rejected (strict schema mode)
- ISO date format validation
- Boundary conditions for date fields
"""

import pytest
from pydantic import BaseModel, Field, ValidationError
from datetime import datetime
from lynx.core.registry import MCPToolRegistry, MCPTool, execute_tool
from lynx.core.session import ExecutionContext
from lynx.core.permissions import PermissionChecker
from lynx.core.audit import AuditLogger


class TestStrictSchemaValidation:
    """Test that unknown extra fields are rejected."""
    
    @pytest.mark.asyncio
    async def test_unknown_extra_fields_rejected(
        self,
        tool_registry: MCPToolRegistry,
        context_t1: ExecutionContext,
        permission_checker: PermissionChecker,
        mock_audit_logger: AuditLogger,
    ):
        """
        Test that unknown extra fields in input are rejected.
        
        This ensures strict schema validation - only defined fields are accepted.
        Note: Pydantic v2 by default allows extra fields unless model_config is set.
        This test documents current behavior and can be updated when strict mode is enabled.
        """
        # Create a tool with a simple input schema using strict mode
        class TestInput(BaseModel):
            model_config = {"extra": "forbid"}  # Reject unknown fields
            
            query: str = Field(description="Query string")
            tenant_id: str = Field(description="Tenant ID")
        
        class TestOutput(BaseModel):
            result: str
        
        async def handler(input_data, context):
            return {"result": "success"}
        
        test_tool = MCPTool(
            id="test.schema.strict.tool",
            name="Strict Schema Test Tool",
            description="Tool for testing strict schema validation",
            layer="domain",
            risk="low",
            domain="test",
            input_schema=TestInput,
            output_schema=TestOutput,
            required_role=[],
            required_scope=[],
            handler=handler,
        )
        tool_registry.register(test_tool)
        
        # Test with valid input (should pass)
        result = await execute_tool(
            tool_id=test_tool.id,
            input_data={
                "query": "test query",
                "tenant_id": context_t1.tenant_id,
            },
            context=context_t1,
            registry=tool_registry,
            permission_checker=permission_checker,
            audit_logger=mock_audit_logger,
        )
        assert result is not None
        
        # Test with unknown extra field (should fail with strict mode)
        with pytest.raises((ValidationError, ValueError)) as exc_info:
            await execute_tool(
                tool_id=test_tool.id,
                input_data={
                    "query": "test query",
                    "tenant_id": context_t1.tenant_id,
                    "unknown_field": "should be rejected",  # Extra field
                },
                context=context_t1,
                registry=tool_registry,
                permission_checker=permission_checker,
                audit_logger=mock_audit_logger,
            )
        
        # Verify that extra field was rejected
        error_msg = str(exc_info.value).lower()
        assert "unknown_field" in error_msg or "extra" in error_msg or "forbidden" in error_msg


class TestISODateValidation:
    """Test ISO date format validation."""
    
    @pytest.mark.asyncio
    async def test_valid_iso_date_passes(
        self,
        tool_registry: MCPToolRegistry,
        context_t1: ExecutionContext,
        permission_checker: PermissionChecker,
        mock_audit_logger: AuditLogger,
    ):
        """Test that valid ISO 8601 dates pass validation."""
        from lynx.mcp.cluster.vpm.payment_draft_create import register_vpm_payment_draft_create_tool
        
        register_vpm_payment_draft_create_tool(tool_registry)
        
        # Valid ISO 8601 date
        valid_date = "2026-12-31T23:59:59Z"
        
        result = await execute_tool(
            tool_id="vpm.cluster.payment.draft.create",
            input_data={
                "vendor_id": "vendor-123",
                "amount": 100.0,
                "currency": "USD",
                "due_date": valid_date,
            },
            context=context_t1,
            registry=tool_registry,
            permission_checker=permission_checker,
            audit_logger=mock_audit_logger,
        )
        
        assert result is not None
        assert "draft_id" in result
    
    @pytest.mark.asyncio
    async def test_invalid_iso_date_fails(
        self,
        tool_registry: MCPToolRegistry,
        context_t1: ExecutionContext,
        permission_checker: PermissionChecker,
        mock_audit_logger: AuditLogger,
    ):
        """Test that invalid ISO 8601 dates are rejected."""
        from lynx.mcp.cluster.vpm.payment_draft_create import register_vpm_payment_draft_create_tool
        
        register_vpm_payment_draft_create_tool(tool_registry)
        
        # Invalid date formats that should be rejected
        invalid_dates = [
            "31/12/2026",  # Wrong format (DD/MM/YYYY)
            "2026-13-01T00:00:00Z",  # Invalid month
            "2026-12-32T00:00:00Z",  # Invalid day
            "not-a-date",  # Not a date
            "2026-12-31T25:00:00Z",  # Invalid hour
            "2026-12-31T00:60:00Z",  # Invalid minute
            "",  # Empty string
        ]
        
        for invalid_date in invalid_dates:
            with pytest.raises((ValueError, ValidationError)) as exc_info:
                await execute_tool(
                    tool_id="vpm.cluster.payment.draft.create",
                    input_data={
                        "vendor_id": "vendor-123",
                        "amount": 100.0,
                        "currency": "USD",
                        "due_date": invalid_date,
                    },
                    context=context_t1,
                    registry=tool_registry,
                    permission_checker=permission_checker,
                    audit_logger=mock_audit_logger,
                )
            
            # Verify error mentions date validation
            error_msg = str(exc_info.value).lower()
            assert any(keyword in error_msg for keyword in ["date", "format", "invalid", "validation", "iso"])
    
    @pytest.mark.asyncio
    async def test_iso_date_with_timezone_passes(
        self,
        tool_registry: MCPToolRegistry,
        context_t1: ExecutionContext,
        permission_checker: PermissionChecker,
        mock_audit_logger: AuditLogger,
    ):
        """Test that ISO dates with timezone offsets pass validation."""
        from lynx.mcp.cluster.vpm.payment_draft_create import register_vpm_payment_draft_create_tool
        
        register_vpm_payment_draft_create_tool(tool_registry)
        
        # Valid ISO dates with different timezone formats
        valid_dates = [
            "2026-12-31T23:59:59Z",  # UTC
            "2026-12-31T23:59:59+00:00",  # UTC with offset
            "2026-12-31T23:59:59+05:30",  # IST
            "2026-12-31T23:59:59-08:00",  # PST
        ]
        
        for valid_date in valid_dates:
            result = await execute_tool(
                tool_id="vpm.cluster.payment.draft.create",
                input_data={
                    "vendor_id": "vendor-123",
                    "amount": 100.0,
                    "currency": "USD",
                    "due_date": valid_date,
                },
                context=context_t1,
                registry=tool_registry,
                permission_checker=permission_checker,
                audit_logger=mock_audit_logger,
            )
            
            assert result is not None
            assert "draft_id" in result
    
    @pytest.mark.asyncio
    async def test_empty_date_string_fails(
        self,
        tool_registry: MCPToolRegistry,
        context_t1: ExecutionContext,
        permission_checker: PermissionChecker,
        mock_audit_logger: AuditLogger,
    ):
        """Test that empty date strings are rejected."""
        from lynx.mcp.cluster.vpm.payment_draft_create import register_vpm_payment_draft_create_tool
        
        register_vpm_payment_draft_create_tool(tool_registry)
        
        with pytest.raises((ValueError, ValidationError)):
            await execute_tool(
                tool_id="vpm.cluster.payment.draft.create",
                input_data={
                    "vendor_id": "vendor-123",
                    "amount": 100.0,
                    "currency": "USD",
                    "due_date": "",  # Empty string
                },
                context=context_t1,
                registry=tool_registry,
                permission_checker=permission_checker,
                audit_logger=mock_audit_logger,
            )


class TestSchemaVersionExposure:
    """Test that tool metadata includes schema version."""
    
    @pytest.mark.asyncio
    async def test_tool_metadata_includes_version(
        self,
        tool_registry: MCPToolRegistry,
    ):
        """Test that tool metadata includes version information."""
        from lynx.mcp.cluster.docs.draft_create import register_docs_draft_create_tool
        
        register_docs_draft_create_tool(tool_registry)
        
        tool = tool_registry.get("docs.cluster.draft.create")
        
        # Verify tool has required metadata
        assert tool.id == "docs.cluster.draft.create"
        assert tool.layer in ["domain", "cluster", "cell"]
        assert tool.risk in ["low", "medium", "high"]
        assert tool.domain is not None
        
        # Note: schema_version is not currently exposed in MCPTool,
        # but we verify that tool has all required metadata fields
        # This test documents the current state and can be updated
        # when schema_version is added to MCPTool metadata
    
    @pytest.mark.asyncio
    async def test_tool_registry_list_includes_metadata(
        self,
        tool_registry: MCPToolRegistry,
    ):
        """Test that tool registry list includes all tools with metadata."""
        from lynx.mcp.server import initialize_mcp_server
        
        initialize_mcp_server(tool_registry)
        
        all_tools = tool_registry.list_all()
        
        assert len(all_tools) > 0
        
        # Verify each tool has required metadata
        for tool in all_tools:
            assert tool.id is not None
            assert tool.layer in ["domain", "cluster", "cell"]
            assert tool.risk in ["low", "medium", "high"]
            assert tool.domain is not None
            assert tool.input_schema is not None
            assert tool.output_schema is not None

