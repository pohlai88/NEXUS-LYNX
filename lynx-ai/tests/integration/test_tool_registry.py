"""
Integration tests for Tool Registry (PRD Law 3: Tool-Only Action).

These tests ensure that only registered tools can be executed.
"""

import pytest
from pydantic import BaseModel, ValidationError
from lynx.core.registry import MCPToolRegistry, MCPTool, execute_tool, ApprovalRequiredError
from lynx.core.session import ExecutionContext
from lynx.core.permissions import PermissionChecker
from lynx.core.audit import AuditLogger


class TestUnregisteredToolIsBlocked:
    """Test that unregistered tools cannot be executed."""
    
    @pytest.mark.asyncio
    async def test_unregistered_tool_raises_value_error(
        self,
        tool_registry: MCPToolRegistry,
        context_t1: ExecutionContext,
        permission_checker: PermissionChecker,
        mock_audit_logger: AuditLogger,
    ):
        """Test that executing an unregistered tool raises ValueError."""
        with pytest.raises(ValueError, match="Tool.*not found"):
            await execute_tool(
                tool_id="nonexistent.tool.id",
                input_data={},
                context=context_t1,
                registry=tool_registry,
                permission_checker=permission_checker,
                audit_logger=mock_audit_logger,
            )


class TestToolInputSchemaIsEnforced:
    """Test that tool input schemas are strictly enforced."""
    
    @pytest.mark.asyncio
    async def test_valid_input_passes_validation(
        self,
        registered_tool: MCPTool,
        tool_registry: MCPToolRegistry,
        context_t1: ExecutionContext,
        permission_checker: PermissionChecker,
        mock_audit_logger: AuditLogger,
    ):
        """Test that valid input passes schema validation."""
        result = await execute_tool(
            tool_id=registered_tool.id,
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
        assert "result" in result
        assert "status" in result
    
    @pytest.mark.asyncio
    async def test_invalid_input_raises_value_error(
        self,
        registered_tool: MCPTool,
        tool_registry: MCPToolRegistry,
        context_t1: ExecutionContext,
        permission_checker: PermissionChecker,
        mock_audit_logger: AuditLogger,
    ):
        """Test that invalid input raises ValueError and logs refusal."""
        with pytest.raises(ValueError, match="Input validation failed"):
            await execute_tool(
                tool_id=registered_tool.id,
                input_data={
                    "invalid_field": "invalid value",
                    # Missing required "query" field
                },
                context=context_t1,
                registry=tool_registry,
                permission_checker=permission_checker,
                audit_logger=mock_audit_logger,
            )
        
        # Verify refusal was logged
        mock_audit_logger.log_refusal.assert_called_once()
        call_args = mock_audit_logger.log_refusal.call_args
        assert "Input validation failed" in call_args[1]["reason"]


class TestPermissionDeniedBlocksExecution:
    """Test that insufficient permissions block tool execution."""
    
    @pytest.mark.asyncio
    async def test_insufficient_role_blocks_execution(
        self,
        tool_registry: MCPToolRegistry,
        context_t1: ExecutionContext,
        mock_audit_logger: AuditLogger,
    ):
        """Test that insufficient role blocks execution."""
        # Create a tool that requires a specific role
        class TestInput(BaseModel):
            query: str
        
        class TestOutput(BaseModel):
            result: str
        
        async def handler(input_data, context):
            return {"result": "success"}
        
        restricted_tool = MCPTool(
            id="test.restricted.tool",
            name="Restricted Tool",
            description="A tool that requires admin role",
            layer="domain",
            risk="low",
            domain="test",
            input_schema=TestInput,
            output_schema=TestOutput,
            required_role=["super_admin"],  # Context has "admin", not "super_admin"
            required_scope=[],
            handler=handler,
        )
        tool_registry.register(restricted_tool)
        
        # Create permission checker that will deny
        permission_checker = PermissionChecker(kernel_api=None)
        
        with pytest.raises(PermissionError, match="Insufficient permissions"):
            await execute_tool(
                tool_id=restricted_tool.id,
                input_data={"query": "test"},
                context=context_t1,
                registry=tool_registry,
                permission_checker=permission_checker,
                audit_logger=mock_audit_logger,
            )
        
        # Verify refusal was logged
        mock_audit_logger.log_refusal.assert_called_once()
        call_args = mock_audit_logger.log_refusal.call_args
        assert "Insufficient permissions" in call_args[1]["reason"]
    
    @pytest.mark.asyncio
    async def test_insufficient_scope_blocks_execution(
        self,
        tool_registry: MCPToolRegistry,
        context_t1: ExecutionContext,
        mock_audit_logger: AuditLogger,
    ):
        """Test that insufficient scope blocks execution."""
        # Create a tool that requires a specific scope
        class TestInput(BaseModel):
            query: str
        
        class TestOutput(BaseModel):
            result: str
        
        async def handler(input_data, context):
            return {"result": "success"}
        
        restricted_tool = MCPTool(
            id="test.scope.restricted.tool",
            name="Scope Restricted Tool",
            description="A tool that requires specific scope",
            layer="domain",
            risk="low",
            domain="test",
            input_schema=TestInput,
            output_schema=TestOutput,
            required_role=[],
            required_scope=["admin_write"],  # Context has ["read", "write"], not "admin_write"
            handler=handler,
        )
        tool_registry.register(restricted_tool)
        
        # Create permission checker that will deny
        permission_checker = PermissionChecker(kernel_api=None)
        
        with pytest.raises(PermissionError, match="Insufficient permissions"):
            await execute_tool(
                tool_id=restricted_tool.id,
                input_data={"query": "test"},
                context=context_t1,
                registry=tool_registry,
                permission_checker=permission_checker,
                audit_logger=mock_audit_logger,
            )


class TestHighRiskRequiresApproval:
    """Test that high-risk tools require explicit approval."""
    
    @pytest.mark.asyncio
    async def test_high_risk_tool_without_approval_raises_error(
        self,
        tool_registry: MCPToolRegistry,
        context_t1: ExecutionContext,
        permission_checker: PermissionChecker,
        mock_audit_logger: AuditLogger,
        monkeypatch,
    ):
        """Test that high-risk tool without approval raises ApprovalRequiredError in production mode."""
        # Set production mode
        monkeypatch.setenv("LYNX_MODE", "prod")
        from lynx.config import Config, LynxMode
        Config.LYNX_MODE = LynxMode.PROD
        
        class TestInput(BaseModel):
            action: str
        
        class TestOutput(BaseModel):
            result: str
        
        async def handler(input_data, context):
            return {"result": "executed"}
        
        high_risk_tool = MCPTool(
            id="test.high.risk.tool",
            name="High Risk Tool",
            description="A high-risk tool",
            layer="cell",
            risk="high",
            domain="test",
            input_schema=TestInput,
            output_schema=TestOutput,
            required_role=[],
            required_scope=[],
            handler=handler,
        )
        tool_registry.register(high_risk_tool)
        
        # Context does not have explicit_approval set
        context_t1.explicit_approval = None
        
        with pytest.raises(ApprovalRequiredError, match="requires explicit approval"):
            await execute_tool(
                tool_id=high_risk_tool.id,
                input_data={"action": "execute"},
                context=context_t1,
                registry=tool_registry,
                permission_checker=permission_checker,
                audit_logger=mock_audit_logger,
            )
        
        # Verify refusal was logged
        mock_audit_logger.log_refusal.assert_called_once()
        
        # Reset mode
        monkeypatch.setenv("LYNX_MODE", "dev")
        Config.LYNX_MODE = LynxMode.DEV
    
    @pytest.mark.asyncio
    async def test_high_risk_tool_with_approval_executes(
        self,
        tool_registry: MCPToolRegistry,
        context_t1: ExecutionContext,
        permission_checker: PermissionChecker,
        mock_audit_logger: AuditLogger,
    ):
        """Test that high-risk tool with approval executes successfully."""
        class TestInput(BaseModel):
            action: str
        
        class TestOutput(BaseModel):
            result: str
        
        async def handler(input_data, context):
            return {"result": "executed"}
        
        high_risk_tool = MCPTool(
            id="test.high.risk.tool.approved",
            name="High Risk Tool",
            description="A high-risk tool",
            layer="cell",
            risk="high",
            domain="test",
            input_schema=TestInput,
            output_schema=TestOutput,
            required_role=[],
            required_scope=[],
            handler=handler,
        )
        tool_registry.register(high_risk_tool)
        
        # Context has explicit approval
        context_t1.explicit_approval = True
        
        result = await execute_tool(
            tool_id=high_risk_tool.id,
            input_data={"action": "execute"},
            context=context_t1,
            registry=tool_registry,
            permission_checker=permission_checker,
            audit_logger=mock_audit_logger,
        )
        
        assert result is not None
        assert result["result"] == "executed"

