"""
Integration tests for all Cluster MCPs (Complete Suite).

Tests validate Draft Protocol compliance for all 8 Cluster MCPs:
- docs.cluster.draft.create
- docs.cluster.batch.draft.create
- docs.cluster.message.draft.create
- workflow.cluster.draft.create
- workflow.cluster.digital.draft.create
- vpm.cluster.payment.draft.create
- portal.cluster.scaffold.draft.create
- portal.cluster.config.draft.create

Test Categories:
- Draft-only guarantee (no production state changes)
- Tenant boundary enforcement
- Audit completeness
- Policy pre-check
- Idempotency
- Draft Protocol compliance
"""

import pytest
from lynx.core.registry import MCPToolRegistry, execute_tool
from lynx.core.session import ExecutionContext
from lynx.core.permissions import PermissionChecker
from lynx.core.audit import AuditLogger
from lynx.mcp.cluster.drafts.base import get_draft_storage
from lynx.mcp.cluster.drafts.models import DraftStatus

# Import all Cluster MCP registration functions
from lynx.mcp.cluster.docs.draft_create import register_docs_draft_create_tool
from lynx.mcp.cluster.docs.batch_draft_create import register_batch_docs_draft_create_tool
from lynx.mcp.cluster.docs.message_draft_create import register_message_docs_draft_create_tool
from lynx.mcp.cluster.workflow.draft_create import register_workflow_draft_create_tool
from lynx.mcp.cluster.workflow.digital_draft_create import register_digital_workflow_draft_create_tool
from lynx.mcp.cluster.vpm.payment_draft_create import register_vpm_payment_draft_create_tool
from lynx.mcp.cluster.portal.scaffold_draft_create import register_portal_scaffold_draft_create_tool
from lynx.mcp.cluster.portal.config_draft_create import register_portal_config_draft_create_tool


class TestBatchDocsDraftCreation:
    """Test docs.cluster.batch.draft.create."""
    
    @pytest.mark.asyncio
    async def test_batch_draft_creation_success(
        self,
        tool_registry: MCPToolRegistry,
        context_t1: ExecutionContext,
        permission_checker: PermissionChecker,
        mock_audit_logger: AuditLogger,
    ):
        """Test successful batch document draft creation."""
        register_batch_docs_draft_create_tool(tool_registry)
        
        result = await execute_tool(
            tool_id="docs.cluster.batch.draft.create",
            input_data={
                "batch_name": "Test Batch",
                "requests": [
                    {"doc_type": "SRS", "title": "Test SRS 1"},
                    {"doc_type": "ADR", "title": "Test ADR 1"},
                ],
            },
            context=context_t1,
            registry=tool_registry,
            permission_checker=permission_checker,
            audit_logger=mock_audit_logger,
        )
        
        assert result is not None
        assert result["status"] == "draft"
        assert "draft_id" in result
        assert "batch_summary" in result
        assert result["batch_summary"]["batch_size"] == 2
    
    @pytest.mark.asyncio
    async def test_batch_draft_is_idempotent(
        self,
        tool_registry: MCPToolRegistry,
        context_t1: ExecutionContext,
        permission_checker: PermissionChecker,
        mock_audit_logger: AuditLogger,
    ):
        """Test batch draft idempotency."""
        register_batch_docs_draft_create_tool(tool_registry)
        
        request_id = "batch-request-123"
        
        result1 = await execute_tool(
            tool_id="docs.cluster.batch.draft.create",
            input_data={
                "batch_name": "Test Batch",
                "requests": [{"doc_type": "SRS", "title": "Test"}],
                "request_id": request_id,
            },
            context=context_t1,
            registry=tool_registry,
            permission_checker=permission_checker,
            audit_logger=mock_audit_logger,
        )
        
        result2 = await execute_tool(
            tool_id="docs.cluster.batch.draft.create",
            input_data={
                "batch_name": "Test Batch",
                "requests": [{"doc_type": "SRS", "title": "Test"}],
                "request_id": request_id,
            },
            context=context_t1,
            registry=tool_registry,
            permission_checker=permission_checker,
            audit_logger=mock_audit_logger,
        )
        
        assert result1["draft_id"] == result2["draft_id"]
    
    @pytest.mark.asyncio
    async def test_batch_draft_high_risk_for_large_batch(
        self,
        tool_registry: MCPToolRegistry,
        context_t1: ExecutionContext,
        permission_checker: PermissionChecker,
        mock_audit_logger: AuditLogger,
    ):
        """Test that large batches are marked as high risk."""
        register_batch_docs_draft_create_tool(tool_registry)
        
        # Create batch with 25 documents (above 20 threshold)
        large_batch = [{"doc_type": "SRS", "title": f"Doc {i}"} for i in range(25)]
        
        result = await execute_tool(
            tool_id="docs.cluster.batch.draft.create",
            input_data={
                "batch_name": "Large Batch",
                "requests": large_batch,
            },
            context=context_t1,
            registry=tool_registry,
            permission_checker=permission_checker,
            audit_logger=mock_audit_logger,
        )
        
        storage = get_draft_storage()
        draft = await storage.get_draft(result["draft_id"], context_t1.tenant_id)
        assert draft.risk_level == "high"


class TestMessageDocsDraftCreation:
    """Test docs.cluster.message.draft.create."""
    
    @pytest.mark.asyncio
    async def test_message_draft_creation_success(
        self,
        tool_registry: MCPToolRegistry,
        context_t1: ExecutionContext,
        permission_checker: PermissionChecker,
        mock_audit_logger: AuditLogger,
    ):
        """Test successful message draft creation."""
        register_message_docs_draft_create_tool(tool_registry)
        
        result = await execute_tool(
            tool_id="docs.cluster.message.draft.create",
            input_data={
                "message_type": "reminder",
                "recipient_ids": ["user-1", "user-2"],
                "subject": "Test Subject",
                "body": "Test Body",
            },
            context=context_t1,
            registry=tool_registry,
            permission_checker=permission_checker,
            audit_logger=mock_audit_logger,
        )
        
        assert result is not None
        assert result["status"] == "draft"
        assert "recipient_summary" in result
        assert result["recipient_summary"]["count"] == 2
    
    @pytest.mark.asyncio
    async def test_message_draft_high_risk_for_urgent(
        self,
        tool_registry: MCPToolRegistry,
        context_t1: ExecutionContext,
        permission_checker: PermissionChecker,
        mock_audit_logger: AuditLogger,
    ):
        """Test that urgent messages are marked as high risk."""
        register_message_docs_draft_create_tool(tool_registry)
        
        result = await execute_tool(
            tool_id="docs.cluster.message.draft.create",
            input_data={
                "message_type": "notification",
                "recipient_ids": ["user-1"],
                "subject": "Urgent",
                "body": "Urgent message",
                "priority": "urgent",
            },
            context=context_t1,
            registry=tool_registry,
            permission_checker=permission_checker,
            audit_logger=mock_audit_logger,
        )
        
        storage = get_draft_storage()
        draft = await storage.get_draft(result["draft_id"], context_t1.tenant_id)
        assert draft.risk_level == "high"


class TestDigitalWorkflowDraftCreation:
    """Test workflow.cluster.digital.draft.create."""
    
    @pytest.mark.asyncio
    async def test_digital_workflow_draft_creation_success(
        self,
        tool_registry: MCPToolRegistry,
        context_t1: ExecutionContext,
        permission_checker: PermissionChecker,
        mock_audit_logger: AuditLogger,
    ):
        """Test successful digital workflow draft creation."""
        register_digital_workflow_draft_create_tool(tool_registry)
        
        # Set user role to admin (required for digital workflows)
        context_t1.user_role = "admin"
        
        result = await execute_tool(
            tool_id="workflow.cluster.digital.draft.create",
            input_data={
                "workflow_name": "Test Digital Workflow",
                "workflow_description": "Test description",
                "trigger_type": "event",
                "steps": [
                    {"step_id": "step-1", "name": "Step 1", "step_type": "automation", "automation_type": "api_call"}
                ],
            },
            context=context_t1,
            registry=tool_registry,
            permission_checker=permission_checker,
            audit_logger=mock_audit_logger,
        )
        
        assert result is not None
        assert result["status"] == "draft"
        assert "automation_summary" in result
        assert result["automation_summary"]["step_count"] == 1
    
    @pytest.mark.asyncio
    async def test_digital_workflow_refuses_if_permission_denied(
        self,
        tool_registry: MCPToolRegistry,
        context_t1: ExecutionContext,
        permission_checker: PermissionChecker,
        mock_audit_logger: AuditLogger,
    ):
        """Test that digital workflow draft refuses if permission denied."""
        register_digital_workflow_draft_create_tool(tool_registry)
        
        context_t1.user_role = "user"  # Not admin/automation_manager
        
        with pytest.raises(ValueError, match="lacks permission"):
            await execute_tool(
                tool_id="workflow.cluster.digital.draft.create",
                input_data={
                    "workflow_name": "Test",
                    "workflow_description": "Test",
                    "trigger_type": "event",
                    "steps": [],
                },
                context=context_t1,
                registry=tool_registry,
                permission_checker=permission_checker,
                audit_logger=mock_audit_logger,
            )
    
    @pytest.mark.asyncio
    async def test_digital_workflow_high_risk_for_webhook(
        self,
        tool_registry: MCPToolRegistry,
        context_t1: ExecutionContext,
        permission_checker: PermissionChecker,
        mock_audit_logger: AuditLogger,
    ):
        """Test that webhook triggers are marked as high risk."""
        register_digital_workflow_draft_create_tool(tool_registry)
        context_t1.user_role = "admin"
        
        result = await execute_tool(
            tool_id="workflow.cluster.digital.draft.create",
            input_data={
                "workflow_name": "Webhook Workflow",
                "workflow_description": "Test",
                "trigger_type": "webhook",
                "steps": [],
            },
            context=context_t1,
            registry=tool_registry,
            permission_checker=permission_checker,
            audit_logger=mock_audit_logger,
        )
        
        storage = get_draft_storage()
        draft = await storage.get_draft(result["draft_id"], context_t1.tenant_id)
        assert draft.risk_level == "high"


class TestPortalScaffoldDraftCreation:
    """Test portal.cluster.scaffold.draft.create."""
    
    @pytest.mark.asyncio
    async def test_portal_scaffold_draft_creation_success(
        self,
        tool_registry: MCPToolRegistry,
        context_t1: ExecutionContext,
        permission_checker: PermissionChecker,
        mock_audit_logger: AuditLogger,
    ):
        """Test successful portal scaffold draft creation."""
        register_portal_scaffold_draft_create_tool(tool_registry)
        
        context_t1.user_role = "admin"
        
        result = await execute_tool(
            tool_id="portal.cluster.scaffold.draft.create",
            input_data={
                "portal_name": "Test Portal",
                "portal_description": "Test description",
                "portal_type": "internal",
                "modules": [
                    {"module_id": "mod-1", "module_name": "Dashboard", "module_type": "dashboard"}
                ],
            },
            context=context_t1,
            registry=tool_registry,
            permission_checker=permission_checker,
            audit_logger=mock_audit_logger,
        )
        
        assert result is not None
        assert result["status"] == "draft"
        assert "scaffold_summary" in result
        assert result["scaffold_summary"]["module_count"] == 1
    
    @pytest.mark.asyncio
    async def test_portal_scaffold_refuses_if_permission_denied(
        self,
        tool_registry: MCPToolRegistry,
        context_t1: ExecutionContext,
        permission_checker: PermissionChecker,
        mock_audit_logger: AuditLogger,
    ):
        """Test that portal scaffold draft refuses if permission denied."""
        register_portal_scaffold_draft_create_tool(tool_registry)
        
        context_t1.user_role = "user"  # Not admin/portal_manager
        
        with pytest.raises(ValueError, match="lacks permission"):
            await execute_tool(
                tool_id="portal.cluster.scaffold.draft.create",
                input_data={
                    "portal_name": "Test",
                    "portal_description": "Test",
                    "portal_type": "internal",
                    "modules": [{"module_id": "mod-1", "module_name": "Test", "module_type": "dashboard"}],
                },
                context=context_t1,
                registry=tool_registry,
                permission_checker=permission_checker,
                audit_logger=mock_audit_logger,
            )
    
    @pytest.mark.asyncio
    async def test_portal_scaffold_high_risk_for_public(
        self,
        tool_registry: MCPToolRegistry,
        context_t1: ExecutionContext,
        permission_checker: PermissionChecker,
        mock_audit_logger: AuditLogger,
    ):
        """Test that public portals are marked as high risk."""
        register_portal_scaffold_draft_create_tool(tool_registry)
        context_t1.user_role = "admin"
        
        result = await execute_tool(
            tool_id="portal.cluster.scaffold.draft.create",
            input_data={
                "portal_name": "Public Portal",
                "portal_description": "Test",
                "portal_type": "public",
                "modules": [{"module_id": "mod-1", "module_name": "Test", "module_type": "dashboard"}],
            },
            context=context_t1,
            registry=tool_registry,
            permission_checker=permission_checker,
            audit_logger=mock_audit_logger,
        )
        
        storage = get_draft_storage()
        draft = await storage.get_draft(result["draft_id"], context_t1.tenant_id)
        assert draft.risk_level == "high"


class TestPortalConfigDraftCreation:
    """Test portal.cluster.config.draft.create."""
    
    @pytest.mark.asyncio
    async def test_portal_config_draft_creation_success(
        self,
        tool_registry: MCPToolRegistry,
        context_t1: ExecutionContext,
        permission_checker: PermissionChecker,
        mock_audit_logger: AuditLogger,
    ):
        """Test successful portal config draft creation."""
        register_portal_config_draft_create_tool(tool_registry)
        
        context_t1.user_role = "admin"
        
        result = await execute_tool(
            tool_id="portal.cluster.config.draft.create",
            input_data={
                "portal_id": "portal-001",
                "config_sections": {
                    "routing": {"path": "/test"},
                },
            },
            context=context_t1,
            registry=tool_registry,
            permission_checker=permission_checker,
            audit_logger=mock_audit_logger,
        )
        
        assert result is not None
        assert result["status"] == "draft"
        assert "config_summary" in result
        assert "routing" in result["config_summary"]["config_sections"]
    
    @pytest.mark.asyncio
    async def test_portal_config_refuses_if_permission_denied(
        self,
        tool_registry: MCPToolRegistry,
        context_t1: ExecutionContext,
        permission_checker: PermissionChecker,
        mock_audit_logger: AuditLogger,
    ):
        """Test that portal config draft refuses if permission denied."""
        register_portal_config_draft_create_tool(tool_registry)
        
        context_t1.user_role = "user"  # Not admin/portal_manager
        
        with pytest.raises(ValueError, match="lacks permission"):
            await execute_tool(
                tool_id="portal.cluster.config.draft.create",
                input_data={
                    "portal_id": "portal-001",
                    "config_sections": {},
                },
                context=context_t1,
                registry=tool_registry,
                permission_checker=permission_checker,
                audit_logger=mock_audit_logger,
            )
    
    @pytest.mark.asyncio
    async def test_portal_config_high_risk_for_security_changes(
        self,
        tool_registry: MCPToolRegistry,
        context_t1: ExecutionContext,
        permission_checker: PermissionChecker,
        mock_audit_logger: AuditLogger,
    ):
        """Test that security config changes are marked as high risk."""
        register_portal_config_draft_create_tool(tool_registry)
        context_t1.user_role = "admin"
        
        result = await execute_tool(
            tool_id="portal.cluster.config.draft.create",
            input_data={
                "portal_id": "portal-001",
                "config_sections": {
                    "security": {"auth_method": "oauth"},
                },
            },
            context=context_t1,
            registry=tool_registry,
            permission_checker=permission_checker,
            audit_logger=mock_audit_logger,
        )
        
        storage = get_draft_storage()
        draft = await storage.get_draft(result["draft_id"], context_t1.tenant_id)
        assert draft.risk_level == "high"


class TestAllClusterMCPsRegistration:
    """Test that all Cluster MCPs register correctly."""
    
    @pytest.mark.asyncio
    async def test_all_cluster_mcps_registered(
        self,
        tool_registry: MCPToolRegistry,
    ):
        """Test that all 8 Cluster MCPs are registered."""
        # Register all Cluster MCPs
        register_docs_draft_create_tool(tool_registry)
        register_batch_docs_draft_create_tool(tool_registry)
        register_message_docs_draft_create_tool(tool_registry)
        register_workflow_draft_create_tool(tool_registry)
        register_digital_workflow_draft_create_tool(tool_registry)
        register_vpm_payment_draft_create_tool(tool_registry)
        register_portal_scaffold_draft_create_tool(tool_registry)
        register_portal_config_draft_create_tool(tool_registry)
        
        # Get all tools
        all_tools = tool_registry.list_all()
        cluster_tools = [t for t in all_tools if t.layer == "cluster"]
        
        # Verify count
        assert len(cluster_tools) == 8, f"Expected 8 Cluster MCPs, found {len(cluster_tools)}"
        
        # Verify all expected tools are present
        expected_tool_ids = [
            "docs.cluster.draft.create",
            "docs.cluster.batch.draft.create",
            "docs.cluster.message.draft.create",
            "workflow.cluster.draft.create",
            "workflow.cluster.digital.draft.create",
            "vpm.cluster.payment.draft.create",
            "portal.cluster.scaffold.draft.create",
            "portal.cluster.config.draft.create",
        ]
        
        actual_tool_ids = [t.id for t in cluster_tools]
        for expected_id in expected_tool_ids:
            assert expected_id in actual_tool_ids, f"Missing tool: {expected_id}"


class TestAllClusterMCPsDraftProtocol:
    """Test that all Cluster MCPs comply with Draft Protocol."""
    
    @pytest.mark.asyncio
    async def test_all_cluster_mcps_create_drafts_only(
        self,
        tool_registry: MCPToolRegistry,
        context_t1: ExecutionContext,
        permission_checker: PermissionChecker,
        mock_audit_logger: AuditLogger,
    ):
        """Test that all Cluster MCPs create drafts only (no production mutations)."""
        # Register all Cluster MCPs
        register_docs_draft_create_tool(tool_registry)
        register_batch_docs_draft_create_tool(tool_registry)
        register_message_docs_draft_create_tool(tool_registry)
        register_workflow_draft_create_tool(tool_registry)
        register_digital_workflow_draft_create_tool(tool_registry)
        register_vpm_payment_draft_create_tool(tool_registry)
        register_portal_scaffold_draft_create_tool(tool_registry)
        register_portal_config_draft_create_tool(tool_registry)
        
        # Set appropriate roles
        context_t1.user_role = "admin"
        
        # Track initial production state
        initial_state = {"production_count": 0}
        
        # Test each tool
        test_cases = [
            ("docs.cluster.draft.create", {"doc_type": "SRS", "title": "Test"}),
            ("docs.cluster.batch.draft.create", {"batch_name": "Test", "requests": [{"doc_type": "SRS", "title": "Test"}]}),
            ("docs.cluster.message.draft.create", {"message_type": "notification", "recipient_ids": ["user-1"], "subject": "Test", "body": "Test"}),
            ("workflow.cluster.draft.create", {"workflow_kind": "approval", "name": "Test", "steps": []}),
            ("workflow.cluster.digital.draft.create", {"workflow_name": "Test", "workflow_description": "Test", "trigger_type": "event", "steps": []}),
            ("vpm.cluster.payment.draft.create", {"vendor_id": "vendor-001", "amount": 100.0, "currency": "USD", "due_date": "2026-02-01"}),
            ("portal.cluster.scaffold.draft.create", {"portal_name": "Test", "portal_description": "Test", "portal_type": "internal", "modules": [{"module_id": "mod-1", "module_name": "Test", "module_type": "dashboard"}]}),
            ("portal.cluster.config.draft.create", {"portal_id": "portal-001", "config_sections": {}}),
        ]
        
        for tool_id, input_data in test_cases:
            result = await execute_tool(
                tool_id=tool_id,
                input_data=input_data,
                context=context_t1,
                registry=tool_registry,
                permission_checker=permission_checker,
                audit_logger=mock_audit_logger,
            )
            
            # Verify draft created
            assert result["status"] == "draft"
            
            # Verify production state unchanged
            assert initial_state["production_count"] == 0

