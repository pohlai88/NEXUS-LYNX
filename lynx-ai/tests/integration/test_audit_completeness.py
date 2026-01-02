"""
Integration tests for Audit Completeness (PRD Law 5: Audit Is Reality).

These tests ensure that all actions are logged and auditable.
"""

import pytest
from lynx.core.audit import AuditLogger
from lynx.core.session import ExecutionContext
from lynx.core.registry import MCPTool, MCPToolRegistry, execute_tool
from lynx.core.permissions import PermissionChecker
from pydantic import BaseModel


class TestEachRunCreatesAuditRunRecord:
    """Test that every Lynx Run creates an audit record."""
    
    @pytest.mark.asyncio
    async def test_lynx_run_is_logged(
        self,
        audit_logger_in_memory,
        context_t1: ExecutionContext,
    ):
        """Test that a Lynx Run is logged."""
        await audit_logger_in_memory.log_lynx_run(
            run_id=context_t1.lynx_run_id,
            user_id=context_t1.user_id,
            tenant_id=context_t1.tenant_id,
            user_query="What is our financial health?",
            lynx_response="Your financial health is good.",
            status="completed",
        )
        
        runs = audit_logger_in_memory.get_runs()
        assert len(runs) == 1
        assert runs[0]["run_id"] == context_t1.lynx_run_id
        assert runs[0]["user_id"] == context_t1.user_id
        assert runs[0]["tenant_id"] == context_t1.tenant_id
        assert runs[0]["status"] == "completed"
    
    @pytest.mark.asyncio
    async def test_multiple_runs_are_logged(
        self,
        audit_logger_in_memory,
        context_t1: ExecutionContext,
    ):
        """Test that multiple runs are logged separately."""
        # Create multiple runs
        for i in range(3):
            await audit_logger_in_memory.log_lynx_run(
                run_id=f"run-{i}",
                user_id=context_t1.user_id,
                tenant_id=context_t1.tenant_id,
                user_query=f"Query {i}",
                lynx_response=f"Response {i}",
                status="completed",
            )
        
        runs = audit_logger_in_memory.get_runs()
        assert len(runs) == 3
        assert runs[0]["run_id"] == "run-0"
        assert runs[1]["run_id"] == "run-1"
        assert runs[2]["run_id"] == "run-2"


class TestToolCallCreatesAuditEvent:
    """Test that every tool call creates an audit event."""
    
    @pytest.mark.asyncio
    async def test_successful_tool_call_is_logged(
        self,
        audit_logger_in_memory,
        registered_tool: MCPTool,
        tool_registry: MCPToolRegistry,
        context_t1: ExecutionContext,
        permission_checker: PermissionChecker,
    ):
        """Test that a successful tool call is logged."""
        await execute_tool(
            tool_id=registered_tool.id,
            input_data={
                "query": "test query",
                "tenant_id": context_t1.tenant_id,
            },
            context=context_t1,
            registry=tool_registry,
            permission_checker=permission_checker,
            audit_logger=audit_logger_in_memory,
        )
        
        logs = audit_logger_in_memory.get_logs()
        
        # Should have execution_start and execution_success
        start_logs = [log for log in logs if log["type"] == "execution_start"]
        success_logs = [log for log in logs if log["type"] == "execution_success"]
        
        assert len(start_logs) == 1
        assert len(success_logs) == 1
        
        assert start_logs[0]["tool_id"] == registered_tool.id
        assert start_logs[0]["tenant_id"] == context_t1.tenant_id
        assert start_logs[0]["run_id"] == context_t1.lynx_run_id
        
        assert success_logs[0]["tool_id"] == registered_tool.id
        assert success_logs[0]["tenant_id"] == context_t1.tenant_id
        assert success_logs[0]["run_id"] == context_t1.lynx_run_id
    
    @pytest.mark.asyncio
    async def test_failed_tool_call_is_logged(
        self,
        audit_logger_in_memory,
        registered_tool: MCPTool,
        tool_registry: MCPToolRegistry,
        context_t1: ExecutionContext,
        permission_checker: PermissionChecker,
    ):
        """Test that a failed tool call is logged."""
        # Create a tool that will fail
        class TestInput(BaseModel):
            query: str
        
        class TestOutput(BaseModel):
            result: str
        
        async def failing_handler(input_data, context):
            raise ValueError("Tool execution failed")
        
        failing_tool = MCPTool(
            id="test.failing.tool",
            name="Failing Tool",
            description="A tool that fails",
            layer="domain",
            risk="low",
            domain="test",
            input_schema=TestInput,
            output_schema=TestOutput,
            required_role=[],
            required_scope=[],
            handler=failing_handler,
        )
        tool_registry.register(failing_tool)
        
        with pytest.raises(ValueError):
            await execute_tool(
                tool_id=failing_tool.id,
                input_data={"query": "test"},
                context=context_t1,
                registry=tool_registry,
                permission_checker=permission_checker,
                audit_logger=audit_logger_in_memory,
            )
        
        logs = audit_logger_in_memory.get_logs()
        
        # Should have execution_start and execution_failure
        start_logs = [log for log in logs if log["type"] == "execution_start"]
        failure_logs = [log for log in logs if log["type"] == "execution_failure"]
        
        assert len(start_logs) == 1
        assert len(failure_logs) == 1
        
        assert failure_logs[0]["tool_id"] == failing_tool.id
        assert "Tool execution failed" in failure_logs[0]["error"]


class TestToolCallCreatesAuditEventEvenOnDenial:
    """Test that denied tool calls are also logged."""
    
    @pytest.mark.asyncio
    async def test_permission_denied_is_logged(
        self,
        audit_logger_in_memory,
        tool_registry: MCPToolRegistry,
        context_t1: ExecutionContext,
    ):
        """Test that permission denial is logged."""
        class TestInput(BaseModel):
            query: str
        
        class TestOutput(BaseModel):
            result: str
        
        async def handler(input_data, context):
            return {"result": "success"}
        
        restricted_tool = MCPTool(
            id="test.restricted.tool",
            name="Restricted Tool",
            description="A tool that requires permission",
            layer="domain",
            risk="low",
            domain="test",
            input_schema=TestInput,
            output_schema=TestOutput,
            required_role=["super_admin"],
            required_scope=[],
            handler=handler,
        )
        tool_registry.register(restricted_tool)
        
        # Create permission checker that will deny
        permission_checker = PermissionChecker(kernel_api=None)
        
        with pytest.raises(PermissionError):
            await execute_tool(
                tool_id=restricted_tool.id,
                input_data={"query": "test"},
                context=context_t1,
                registry=tool_registry,
                permission_checker=permission_checker,
                audit_logger=audit_logger_in_memory,
            )
        
        logs = audit_logger_in_memory.get_logs()
        
        # Should have refusal log
        refusal_logs = [log for log in logs if log["type"] == "refusal"]
        assert len(refusal_logs) == 1
        assert refusal_logs[0]["tool_id"] == restricted_tool.id
        assert "Insufficient permissions" in refusal_logs[0]["reason"]
    
    @pytest.mark.asyncio
    async def test_input_validation_failure_is_logged(
        self,
        audit_logger_in_memory,
        registered_tool: MCPTool,
        tool_registry: MCPToolRegistry,
        context_t1: ExecutionContext,
        permission_checker: PermissionChecker,
    ):
        """Test that input validation failure is logged."""
        with pytest.raises(ValueError):
            await execute_tool(
                tool_id=registered_tool.id,
                input_data={"invalid": "data"},  # Invalid input
                context=context_t1,
                registry=tool_registry,
                permission_checker=permission_checker,
                audit_logger=audit_logger_in_memory,
            )
        
        logs = audit_logger_in_memory.get_logs()
        
        # Should have refusal log
        refusal_logs = [log for log in logs if log["type"] == "refusal"]
        assert len(refusal_logs) == 1
        assert "Input validation failed" in refusal_logs[0]["reason"]


class TestAuditLogsContainRequiredFields:
    """Test that audit logs contain all required fields."""
    
    @pytest.mark.asyncio
    async def test_audit_log_contains_run_id(
        self,
        audit_logger_in_memory,
        registered_tool: MCPTool,
        tool_registry: MCPToolRegistry,
        context_t1: ExecutionContext,
        permission_checker: PermissionChecker,
    ):
        """Test that audit logs contain run_id."""
        await execute_tool(
            tool_id=registered_tool.id,
            input_data={
                "query": "test",
                "tenant_id": context_t1.tenant_id,
            },
            context=context_t1,
            registry=tool_registry,
            permission_checker=permission_checker,
            audit_logger=audit_logger_in_memory,
        )
        
        logs = audit_logger_in_memory.get_logs()
        for log in logs:
            assert "run_id" in log
            assert log["run_id"] == context_t1.lynx_run_id
    
    @pytest.mark.asyncio
    async def test_audit_log_contains_tool_id(
        self,
        audit_logger_in_memory,
        registered_tool: MCPTool,
        tool_registry: MCPToolRegistry,
        context_t1: ExecutionContext,
        permission_checker: PermissionChecker,
    ):
        """Test that audit logs contain tool_id."""
        await execute_tool(
            tool_id=registered_tool.id,
            input_data={
                "query": "test",
                "tenant_id": context_t1.tenant_id,
            },
            context=context_t1,
            registry=tool_registry,
            permission_checker=permission_checker,
            audit_logger=audit_logger_in_memory,
        )
        
        logs = audit_logger_in_memory.get_logs()
        for log in logs:
            assert "tool_id" in log
            assert log["tool_id"] == registered_tool.id
    
    @pytest.mark.asyncio
    async def test_audit_log_contains_tenant_id(
        self,
        audit_logger_in_memory,
        registered_tool: MCPTool,
        tool_registry: MCPToolRegistry,
        context_t1: ExecutionContext,
        permission_checker: PermissionChecker,
    ):
        """Test that audit logs contain tenant_id."""
        await execute_tool(
            tool_id=registered_tool.id,
            input_data={
                "query": "test",
                "tenant_id": context_t1.tenant_id,
            },
            context=context_t1,
            registry=tool_registry,
            permission_checker=permission_checker,
            audit_logger=audit_logger_in_memory,
        )
        
        logs = audit_logger_in_memory.get_logs()
        for log in logs:
            assert "tenant_id" in log
            assert log["tenant_id"] == context_t1.tenant_id

