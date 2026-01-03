"""
Comprehensive Response Validation Tests for Domain MCPs.

Tests validate:
- Complete response schema (all required fields present)
- Response data correctness (values match expectations)
- Response type validation
- Tenant isolation in responses
"""

import pytest
from lynx.core.registry import MCPToolRegistry, execute_tool
from lynx.core.session import ExecutionContext
from lynx.core.permissions import PermissionChecker
from lynx.core.audit import AuditLogger

# Import all Domain MCP registration functions
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


class TestFinanceHealthReadResponseValidation:
    """Test finance.domain.health.read response structure and content."""
    
    @pytest.mark.asyncio
    async def test_finance_health_response_schema_complete(
        self,
        tool_registry: MCPToolRegistry,
        context_t1: ExecutionContext,
        permission_checker: PermissionChecker,
        mock_audit_logger: AuditLogger,
    ):
        """Test that finance health response has all required fields."""
        # Skip this test as it requires Kernel API (excluded per user request)
        pytest.skip("Finance health read requires Kernel API (excluded per user request)")


class TestKernelRegistryReadResponseValidation:
    """Test kernel.domain.registry.read response structure and content."""
    
    @pytest.mark.asyncio
    async def test_kernel_registry_response_schema_complete(
        self,
        tool_registry: MCPToolRegistry,
        context_t1: ExecutionContext,
        permission_checker: PermissionChecker,
        mock_audit_logger: AuditLogger,
    ):
        """Test that kernel registry response has all required fields."""
        register_kernel_registry_read_tool(tool_registry)
        
        result = await execute_tool(
            tool_id="kernel.domain.registry.read",
            input_data={},
            context=context_t1,
            registry=tool_registry,
            permission_checker=permission_checker,
            audit_logger=mock_audit_logger,
        )
        
        # Verify all required fields
        required_fields = ["tenant_id", "tools"]
        for field in required_fields:
            assert field in result, f"Missing required field: {field}"
        
        # Verify field types
        assert isinstance(result["tenant_id"], str)
        assert isinstance(result["tools"], list)
        
        # Verify tenant_id matches context
        assert result["tenant_id"] == context_t1.tenant_id
        
        # Verify tools is a list (may be empty)
        assert isinstance(result["tools"], list)


class TestTenantProfileReadResponseValidation:
    """Test tenant.domain.profile.read response structure and content."""
    
    @pytest.mark.asyncio
    async def test_tenant_profile_response_schema_complete(
        self,
        tool_registry: MCPToolRegistry,
        context_t1: ExecutionContext,
        permission_checker: PermissionChecker,
        mock_audit_logger: AuditLogger,
    ):
        """Test that tenant profile response has all required fields."""
        register_tenant_profile_read_tool(tool_registry)
        
        result = await execute_tool(
            tool_id="tenant.domain.profile.read",
            input_data={},
            context=context_t1,
            registry=tool_registry,
            permission_checker=permission_checker,
            audit_logger=mock_audit_logger,
        )
        
        # Verify all required fields (actual response structure)
        required_fields = ["tenant_id", "tenant_name", "plan", "region", "enabled_modules"]
        for field in required_fields:
            assert field in result, f"Missing required field: {field}"
        
        # Verify field types
        assert isinstance(result["tenant_id"], str)
        assert isinstance(result["enabled_modules"], list)
        
        # Verify tenant_id matches context
        assert result["tenant_id"] == context_t1.tenant_id


class TestAuditRunReadResponseValidation:
    """Test audit.domain.run.read response structure and content."""
    
    @pytest.mark.asyncio
    async def test_audit_run_response_schema_complete(
        self,
        tool_registry: MCPToolRegistry,
        context_t1: ExecutionContext,
        permission_checker: PermissionChecker,
        mock_audit_logger: AuditLogger,
    ):
        """Test that audit run response has all required fields."""
        register_audit_run_read_tool(tool_registry)
        
        result = await execute_tool(
            tool_id="audit.domain.run.read",
            input_data={"limit": 5},
            context=context_t1,
            registry=tool_registry,
            permission_checker=permission_checker,
            audit_logger=mock_audit_logger,
        )
        
        # Verify all required fields
        required_fields = ["tenant_id", "runs"]
        for field in required_fields:
            assert field in result, f"Missing required field: {field}"
        
        # Verify field types
        assert isinstance(result["tenant_id"], str)
        assert isinstance(result["runs"], list)
        
        # Verify tenant_id matches context
        assert result["tenant_id"] == context_t1.tenant_id


class TestSecurityPermissionReadResponseValidation:
    """Test security.domain.permission.read response structure and content."""
    
    @pytest.mark.asyncio
    async def test_security_permission_response_schema_complete(
        self,
        tool_registry: MCPToolRegistry,
        context_t1: ExecutionContext,
        permission_checker: PermissionChecker,
        mock_audit_logger: AuditLogger,
    ):
        """Test that security permission response has all required fields."""
        register_security_permission_read_tool(tool_registry)
        
        result = await execute_tool(
            tool_id="security.domain.permission.read",
            input_data={"tool_id": "finance.domain.health.read"},
            context=context_t1,
            registry=tool_registry,
            permission_checker=permission_checker,
            audit_logger=mock_audit_logger,
        )
        
        # Verify all required fields (actual response structure - no tenant_id)
        required_fields = ["tool_id", "allowed", "required_role", "required_scope", "current_role", "current_scope", "policy_source"]
        for field in required_fields:
            assert field in result, f"Missing required field: {field}"
        
        # Verify field types
        assert isinstance(result["tool_id"], str)
        assert isinstance(result["allowed"], bool)
        assert isinstance(result["required_role"], list)
        assert isinstance(result["required_scope"], list)
        
        # Verify tool_id matches input
        assert result["tool_id"] == "finance.domain.health.read"


class TestWorkflowStatusReadResponseValidation:
    """Test workflow.domain.status.read response structure and content."""
    
    @pytest.mark.asyncio
    async def test_workflow_status_response_schema_complete(
        self,
        tool_registry: MCPToolRegistry,
        context_t1: ExecutionContext,
        permission_checker: PermissionChecker,
        mock_audit_logger: AuditLogger,
    ):
        """Test that workflow status response has all required fields."""
        register_workflow_status_read_tool(tool_registry)
        
        result = await execute_tool(
            tool_id="workflow.domain.status.read",
            input_data={},
            context=context_t1,
            registry=tool_registry,
            permission_checker=permission_checker,
            audit_logger=mock_audit_logger,
        )
        
        # Verify all required fields (actual response structure)
        required_fields = ["tenant_id", "active_workflows_count", "pending_approvals_count", "recent_events"]
        for field in required_fields:
            assert field in result, f"Missing required field: {field}"
        
        # Verify field types
        assert isinstance(result["tenant_id"], str)
        assert isinstance(result["active_workflows_count"], int)
        assert isinstance(result["pending_approvals_count"], int)
        assert isinstance(result["recent_events"], list)
        
        # Verify tenant_id matches context
        assert result["tenant_id"] == context_t1.tenant_id


class TestWorkflowPolicyReadResponseValidation:
    """Test workflow.domain.policy.read response structure and content."""
    
    @pytest.mark.asyncio
    async def test_workflow_policy_response_schema_complete(
        self,
        tool_registry: MCPToolRegistry,
        context_t1: ExecutionContext,
        permission_checker: PermissionChecker,
        mock_audit_logger: AuditLogger,
    ):
        """Test that workflow policy response has all required fields."""
        register_workflow_policy_read_tool(tool_registry)
        
        result = await execute_tool(
            tool_id="workflow.domain.policy.read",
            input_data={},
            context=context_t1,
            registry=tool_registry,
            permission_checker=permission_checker,
            audit_logger=mock_audit_logger,
        )
        
        # Verify all required fields (actual response structure)
        required_fields = ["tenant_id", "approval_rules", "role_gates"]
        for field in required_fields:
            assert field in result, f"Missing required field: {field}"
        
        # Verify field types
        assert isinstance(result["tenant_id"], str)
        assert isinstance(result["approval_rules"], list)
        assert isinstance(result["role_gates"], dict)
        
        # Verify tenant_id matches context
        assert result["tenant_id"] == context_t1.tenant_id


class TestDocsRegistryReadResponseValidation:
    """Test docs.domain.registry.read response structure and content."""
    
    @pytest.mark.asyncio
    async def test_docs_registry_response_schema_complete(
        self,
        tool_registry: MCPToolRegistry,
        context_t1: ExecutionContext,
        permission_checker: PermissionChecker,
        mock_audit_logger: AuditLogger,
    ):
        """Test that docs registry response has all required fields."""
        register_docs_registry_read_tool(tool_registry)
        
        result = await execute_tool(
            tool_id="docs.domain.registry.read",
            input_data={},
            context=context_t1,
            registry=tool_registry,
            permission_checker=permission_checker,
            audit_logger=mock_audit_logger,
        )
        
        # Verify all required fields
        required_fields = ["tenant_id", "documents"]
        for field in required_fields:
            assert field in result, f"Missing required field: {field}"
        
        # Verify field types
        assert isinstance(result["tenant_id"], str)
        assert isinstance(result["documents"], list)
        
        # Verify tenant_id matches context
        assert result["tenant_id"] == context_t1.tenant_id


class TestFeatureFlagStatusReadResponseValidation:
    """Test featureflag.domain.status.read response structure and content."""
    
    @pytest.mark.asyncio
    async def test_featureflag_status_response_schema_complete(
        self,
        tool_registry: MCPToolRegistry,
        context_t1: ExecutionContext,
        permission_checker: PermissionChecker,
        mock_audit_logger: AuditLogger,
    ):
        """Test that featureflag status response has all required fields."""
        register_featureflag_status_read_tool(tool_registry)
        
        result = await execute_tool(
            tool_id="featureflag.domain.status.read",
            input_data={},
            context=context_t1,
            registry=tool_registry,
            permission_checker=permission_checker,
            audit_logger=mock_audit_logger,
        )
        
        # Verify all required fields (actual response structure)
        required_fields = ["tenant_id", "enabled_modules", "enabled_tools", "feature_flags"]
        for field in required_fields:
            assert field in result, f"Missing required field: {field}"
        
        # Verify field types
        assert isinstance(result["tenant_id"], str)
        assert isinstance(result["enabled_modules"], list)
        assert isinstance(result["enabled_tools"], list)
        assert isinstance(result["feature_flags"], dict)
        
        # Verify tenant_id matches context
        assert result["tenant_id"] == context_t1.tenant_id


class TestSystemHealthReadResponseValidation:
    """Test system.domain.health.read response structure and content."""
    
    @pytest.mark.asyncio
    async def test_system_health_response_schema_complete(
        self,
        tool_registry: MCPToolRegistry,
        context_t1: ExecutionContext,
        permission_checker: PermissionChecker,
        mock_audit_logger: AuditLogger,
    ):
        """Test that system health response has all required fields."""
        register_system_health_read_tool(tool_registry)
        
        result = await execute_tool(
            tool_id="system.domain.health.read",
            input_data={},
            context=context_t1,
            registry=tool_registry,
            permission_checker=permission_checker,
            audit_logger=mock_audit_logger,
        )
        
        # Verify all required fields (actual response structure)
        required_fields = ["tenant_id", "overall_status", "kernel_status", "supabase_status", "dependencies"]
        for field in required_fields:
            assert field in result, f"Missing required field: {field}"
        
        # Verify field types
        assert isinstance(result["tenant_id"], str)
        assert isinstance(result["overall_status"], str)
        assert isinstance(result["dependencies"], dict)
        
        # Verify tenant_id matches context
        assert result["tenant_id"] == context_t1.tenant_id
        
        # Verify overall_status is valid
        assert result["overall_status"] in ["healthy", "degraded", "unhealthy"]


class TestVPMVendorReadResponseValidation:
    """Test vpm.domain.vendor.read response structure and content."""
    
    @pytest.mark.asyncio
    async def test_vpm_vendor_response_schema_complete(
        self,
        tool_registry: MCPToolRegistry,
        context_t1: ExecutionContext,
        permission_checker: PermissionChecker,
        mock_audit_logger: AuditLogger,
    ):
        """Test that VPM vendor response has all required fields."""
        register_vpm_vendor_read_tool(tool_registry)
        
        result = await execute_tool(
            tool_id="vpm.domain.vendor.read",
            input_data={"vendor_id": "vendor-001"},
            context=context_t1,
            registry=tool_registry,
            permission_checker=permission_checker,
            audit_logger=mock_audit_logger,
        )
        
        # Verify all required fields
        required_fields = ["tenant_id", "vendor"]
        for field in required_fields:
            assert field in result, f"Missing required field: {field}"
        
        # Verify field types
        assert isinstance(result["tenant_id"], str)
        assert isinstance(result["vendor"], dict)
        
        # Verify tenant_id matches context
        assert result["tenant_id"] == context_t1.tenant_id


class TestVPMPaymentStatusReadResponseValidation:
    """Test vpm.domain.payment.status.read response structure and content."""
    
    @pytest.mark.asyncio
    async def test_vpm_payment_status_response_schema_complete(
        self,
        tool_registry: MCPToolRegistry,
        context_t1: ExecutionContext,
        permission_checker: PermissionChecker,
        mock_audit_logger: AuditLogger,
    ):
        """Test that VPM payment status response has all required fields."""
        register_vpm_payment_status_read_tool(tool_registry)
        
        result = await execute_tool(
            tool_id="vpm.domain.payment.status.read",
            input_data={},
            context=context_t1,
            registry=tool_registry,
            permission_checker=permission_checker,
            audit_logger=mock_audit_logger,
        )
        
        # Verify all required fields
        required_fields = ["tenant_id", "payments"]
        for field in required_fields:
            assert field in result, f"Missing required field: {field}"
        
        # Verify field types
        assert isinstance(result["tenant_id"], str)
        assert isinstance(result["payments"], list)
        
        # Verify tenant_id matches context
        assert result["tenant_id"] == context_t1.tenant_id

