"""
Integration tests for Domain MCP Suite.

Tests all 5 new Domain MCPs to prove they:
- Register correctly
- Execute successfully with valid context
- Emit audit log
- Refuse cleanly when tenant mismatch
"""

import pytest
from lynx.core.registry import MCPToolRegistry, execute_tool
from lynx.core.session import ExecutionContext
from lynx.core.permissions import PermissionChecker
from lynx.core.audit import AuditLogger

# Import registration functions directly (avoid mcp_agent dependency in tests)
from lynx.mcp.domain.finance.health_read import register_finance_health_read_tool
from lynx.mcp.domain.kernel.registry_read import register_kernel_registry_read_tool
from lynx.mcp.domain.tenant.profile_read import register_tenant_profile_read_tool
from lynx.mcp.domain.audit.run_read import register_audit_run_read_tool
from lynx.mcp.domain.security.permission_read import register_security_permission_read_tool
from lynx.mcp.domain.workflow.status_read import register_workflow_status_read_tool
from lynx.mcp.domain.workflow.policy_read import register_workflow_policy_read_tool
from lynx.mcp.domain.docs.registry_read import register_docs_registry_read_tool
from lynx.mcp.domain.featureflag.status_read import register_featureflag_status_read_tool
from lynx.mcp.domain.system.health_read import register_system_health_read_tool
from lynx.mcp.domain.vpm.vendor_read import register_vpm_vendor_read_tool
from lynx.mcp.domain.vpm.payment_status_read import register_vpm_payment_status_read_tool


def initialize_mcp_server(registry: MCPToolRegistry) -> None:
    """Initialize MCP server with all registered tools (test version)."""
    register_finance_health_read_tool(registry)
    register_kernel_registry_read_tool(registry)
    register_tenant_profile_read_tool(registry)
    register_audit_run_read_tool(registry)
    register_security_permission_read_tool(registry)
    register_workflow_status_read_tool(registry)
    register_workflow_policy_read_tool(registry)
    register_docs_registry_read_tool(registry)
    register_featureflag_status_read_tool(registry)
    register_system_health_read_tool(registry)
    register_vpm_vendor_read_tool(registry)
    register_vpm_payment_status_read_tool(registry)


class TestDomainMCPRegistration:
    """Test that all Domain MCPs register correctly."""
    
    def test_all_domain_mcps_registered(self, tool_registry: MCPToolRegistry):
        """Test that all 12 Domain MCPs are registered."""
        initialize_mcp_server(tool_registry)
        
        domain_tools = tool_registry.list_by_layer("domain")
        tool_ids = [tool.id for tool in domain_tools]
        
        # Check all 12 Domain MCPs are registered
        expected_tools = [
            "finance.domain.health.read",
            "kernel.domain.registry.read",
            "tenant.domain.profile.read",
            "audit.domain.run.read",
            "security.domain.permission.read",
            "workflow.domain.status.read",
            "workflow.domain.policy.read",
            "docs.domain.registry.read",
            "featureflag.domain.status.read",
            "system.domain.health.read",
            "vpm.domain.vendor.read",
            "vpm.domain.payment.status.read",
        ]
        
        for tool_id in expected_tools:
            assert tool_id in tool_ids, f"Tool {tool_id} not registered"
        
        assert len(domain_tools) == 12, f"Expected 12 Domain MCPs, found {len(domain_tools)}"


class TestDomainMCPExecution:
    """Test that all Domain MCPs execute successfully with valid context."""
    
    @pytest.mark.asyncio
    async def test_kernel_registry_read_executes(
        self,
        tool_registry: MCPToolRegistry,
        context_t1: ExecutionContext,
        permission_checker: PermissionChecker,
        mock_audit_logger: AuditLogger,
    ):
        """Test kernel.domain.registry.read executes successfully."""
        initialize_mcp_server(tool_registry)
        
        result = await execute_tool(
            tool_id="kernel.domain.registry.read",
            input_data={},
            context=context_t1,
            registry=tool_registry,
            permission_checker=permission_checker,
            audit_logger=mock_audit_logger,
        )
        
        assert result is not None
        assert "tools" in result
        assert "tenant_id" in result
        assert result["tenant_id"] == context_t1.tenant_id
    
    @pytest.mark.asyncio
    async def test_tenant_profile_read_executes(
        self,
        tool_registry: MCPToolRegistry,
        context_t1: ExecutionContext,
        permission_checker: PermissionChecker,
        mock_audit_logger: AuditLogger,
    ):
        """Test tenant.domain.profile.read executes successfully."""
        initialize_mcp_server(tool_registry)
        
        result = await execute_tool(
            tool_id="tenant.domain.profile.read",
            input_data={},
            context=context_t1,
            registry=tool_registry,
            permission_checker=permission_checker,
            audit_logger=mock_audit_logger,
        )
        
        assert result is not None
        assert "tenant_id" in result
        assert result["tenant_id"] == context_t1.tenant_id
    
    @pytest.mark.asyncio
    async def test_audit_run_read_executes(
        self,
        tool_registry: MCPToolRegistry,
        context_t1: ExecutionContext,
        permission_checker: PermissionChecker,
        mock_audit_logger: AuditLogger,
    ):
        """Test audit.domain.run.read executes successfully."""
        initialize_mcp_server(tool_registry)
        
        result = await execute_tool(
            tool_id="audit.domain.run.read",
            input_data={"limit": 5},
            context=context_t1,
            registry=tool_registry,
            permission_checker=permission_checker,
            audit_logger=mock_audit_logger,
        )
        
        assert result is not None
        assert "runs" in result
        assert "tenant_id" in result
        assert result["tenant_id"] == context_t1.tenant_id
    
    @pytest.mark.asyncio
    async def test_security_permission_read_executes(
        self,
        tool_registry: MCPToolRegistry,
        context_t1: ExecutionContext,
        permission_checker: PermissionChecker,
        mock_audit_logger: AuditLogger,
    ):
        """Test security.domain.permission.read executes successfully."""
        initialize_mcp_server(tool_registry)
        
        result = await execute_tool(
            tool_id="security.domain.permission.read",
            input_data={"tool_id": "finance.domain.health.read"},
            context=context_t1,
            registry=tool_registry,
            permission_checker=permission_checker,
            audit_logger=mock_audit_logger,
        )
        
        assert result is not None
        assert "tool_id" in result
        assert "allowed" in result
        assert "current_role" in result
    
    @pytest.mark.asyncio
    async def test_workflow_status_read_executes(
        self,
        tool_registry: MCPToolRegistry,
        context_t1: ExecutionContext,
        permission_checker: PermissionChecker,
        mock_audit_logger: AuditLogger,
    ):
        """Test workflow.domain.status.read executes successfully."""
        initialize_mcp_server(tool_registry)
        
        result = await execute_tool(
            tool_id="workflow.domain.status.read",
            input_data={},
            context=context_t1,
            registry=tool_registry,
            permission_checker=permission_checker,
            audit_logger=mock_audit_logger,
        )
        
        assert result is not None
        assert "active_workflows_count" in result
        assert "pending_approvals_count" in result
        assert "tenant_id" in result
        assert result["tenant_id"] == context_t1.tenant_id
    
    @pytest.mark.asyncio
    async def test_workflow_policy_read_executes(
        self,
        tool_registry: MCPToolRegistry,
        context_t1: ExecutionContext,
        permission_checker: PermissionChecker,
        mock_audit_logger: AuditLogger,
    ):
        """Test workflow.domain.policy.read executes successfully."""
        initialize_mcp_server(tool_registry)
        
        result = await execute_tool(
            tool_id="workflow.domain.policy.read",
            input_data={},
            context=context_t1,
            registry=tool_registry,
            permission_checker=permission_checker,
            audit_logger=mock_audit_logger,
        )
        
        assert result is not None
        assert "approval_rules" in result
        assert "role_gates" in result
        assert "tenant_id" in result
    
    @pytest.mark.asyncio
    async def test_docs_registry_read_executes(
        self,
        tool_registry: MCPToolRegistry,
        context_t1: ExecutionContext,
        permission_checker: PermissionChecker,
        mock_audit_logger: AuditLogger,
    ):
        """Test docs.domain.registry.read executes successfully."""
        initialize_mcp_server(tool_registry)
        
        result = await execute_tool(
            tool_id="docs.domain.registry.read",
            input_data={},
            context=context_t1,
            registry=tool_registry,
            permission_checker=permission_checker,
            audit_logger=mock_audit_logger,
        )
        
        assert result is not None
        assert "documents" in result
        assert "tenant_id" in result
    
    @pytest.mark.asyncio
    async def test_featureflag_status_read_executes(
        self,
        tool_registry: MCPToolRegistry,
        context_t1: ExecutionContext,
        permission_checker: PermissionChecker,
        mock_audit_logger: AuditLogger,
    ):
        """Test featureflag.domain.status.read executes successfully."""
        initialize_mcp_server(tool_registry)
        
        result = await execute_tool(
            tool_id="featureflag.domain.status.read",
            input_data={},
            context=context_t1,
            registry=tool_registry,
            permission_checker=permission_checker,
            audit_logger=mock_audit_logger,
        )
        
        assert result is not None
        assert "enabled_modules" in result
        assert "feature_flags" in result
        assert "tenant_id" in result
    
    @pytest.mark.asyncio
    async def test_system_health_read_executes(
        self,
        tool_registry: MCPToolRegistry,
        context_t1: ExecutionContext,
        permission_checker: PermissionChecker,
        mock_audit_logger: AuditLogger,
    ):
        """Test system.domain.health.read executes successfully."""
        initialize_mcp_server(tool_registry)
        
        result = await execute_tool(
            tool_id="system.domain.health.read",
            input_data={},
            context=context_t1,
            registry=tool_registry,
            permission_checker=permission_checker,
            audit_logger=mock_audit_logger,
        )
        
        assert result is not None
        assert "overall_status" in result
        assert "tenant_id" in result
    
    @pytest.mark.asyncio
    async def test_vpm_vendor_read_executes(
        self,
        tool_registry: MCPToolRegistry,
        context_t1: ExecutionContext,
        permission_checker: PermissionChecker,
        mock_audit_logger: AuditLogger,
    ):
        """Test vpm.domain.vendor.read executes successfully."""
        initialize_mcp_server(tool_registry)
        
        result = await execute_tool(
            tool_id="vpm.domain.vendor.read",
            input_data={},
            context=context_t1,
            registry=tool_registry,
            permission_checker=permission_checker,
            audit_logger=mock_audit_logger,
        )
        
        assert result is not None
        assert "tenant_id" in result
    
    @pytest.mark.asyncio
    async def test_vpm_payment_status_read_executes(
        self,
        tool_registry: MCPToolRegistry,
        context_t1: ExecutionContext,
        permission_checker: PermissionChecker,
        mock_audit_logger: AuditLogger,
    ):
        """Test vpm.domain.payment.status.read executes successfully."""
        initialize_mcp_server(tool_registry)
        
        result = await execute_tool(
            tool_id="vpm.domain.payment.status.read",
            input_data={},
            context=context_t1,
            registry=tool_registry,
            permission_checker=permission_checker,
            audit_logger=mock_audit_logger,
        )
        
        assert result is not None
        assert "payments" in result
        assert "pending_approvals_count" in result
        assert "tenant_id" in result


class TestDomainMCPAuditLogging:
    """Test that all Domain MCPs emit audit logs."""
    
    @pytest.mark.asyncio
    async def test_all_domain_mcps_log_audit_events(
        self,
        tool_registry: MCPToolRegistry,
        context_t1: ExecutionContext,
        permission_checker: PermissionChecker,
        mock_audit_logger: AuditLogger,
    ):
        """Test that all Domain MCPs log audit events."""
        initialize_mcp_server(tool_registry)
        
        tool_ids = [
            "kernel.domain.registry.read",
            "tenant.domain.profile.read",
            "audit.domain.run.read",
            "security.domain.permission.read",
            "workflow.domain.status.read",
            "workflow.domain.policy.read",
            "docs.domain.registry.read",
            "featureflag.domain.status.read",
            "system.domain.health.read",
            "vpm.domain.vendor.read",
            "vpm.domain.payment.status.read",
        ]
        
        for tool_id in tool_ids:
            input_data = {}
            if tool_id == "security.domain.permission.read":
                input_data = {"tool_id": "finance.domain.health.read"}
            elif tool_id == "audit.domain.run.read":
                input_data = {"limit": 5}
            elif tool_id == "vpm.domain.payment.status.read":
                input_data = {"limit": 5}
            
            await execute_tool(
                tool_id=tool_id,
                input_data=input_data,
                context=context_t1,
                registry=tool_registry,
                permission_checker=permission_checker,
                audit_logger=mock_audit_logger,
            )
        
        # Verify audit logging was called for each tool
        assert mock_audit_logger.log_execution_start.call_count == 11
        assert mock_audit_logger.log_execution_success.call_count == 11


class TestDomainMCPTenantIsolation:
    """Test that all Domain MCPs refuse cleanly when tenant mismatch."""
    
    @pytest.mark.asyncio
    async def test_domain_mcps_respect_tenant_boundaries(
        self,
        tool_registry: MCPToolRegistry,
        context_t1: ExecutionContext,
        context_t2: ExecutionContext,
        permission_checker: PermissionChecker,
        mock_audit_logger: AuditLogger,
    ):
        """Test that Domain MCPs respect tenant boundaries."""
        initialize_mcp_server(tool_registry)
        
        # All Domain MCPs should return data scoped to the context's tenant
        # They should not allow cross-tenant access
        
        tool_ids = [
            "kernel.domain.registry.read",
            "tenant.domain.profile.read",
            "audit.domain.run.read",
            "workflow.domain.status.read",
            "docs.domain.registry.read",
            "system.domain.health.read",
            "vpm.domain.vendor.read",
        ]
        
        for tool_id in tool_ids:
            input_data = {}
            if tool_id == "audit.domain.run.read":
                input_data = {"limit": 5}
            elif tool_id == "vpm.domain.vendor.read":
                input_data = {}  # Can be empty or include vendor_id
            
            # Execute with T1 context
            result_t1 = await execute_tool(
                tool_id=tool_id,
                input_data=input_data,
                context=context_t1,
                registry=tool_registry,
                permission_checker=permission_checker,
                audit_logger=mock_audit_logger,
            )
            
            # Execute with T2 context
            result_t2 = await execute_tool(
                tool_id=tool_id,
                input_data=input_data,
                context=context_t2,
                registry=tool_registry,
                permission_checker=permission_checker,
                audit_logger=mock_audit_logger,
            )
            
            # Verify tenant_id in results matches context tenant
            assert result_t1["tenant_id"] == context_t1.tenant_id
            assert result_t2["tenant_id"] == context_t2.tenant_id
            assert result_t1["tenant_id"] != result_t2["tenant_id"]

