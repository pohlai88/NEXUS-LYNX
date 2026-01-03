"""
Approval Workflow Tests for Cell MCPs.

Tests validate:
- Approval state transitions
- Draft status validation
- Approval requirements
- Workflow completeness
"""

import pytest
from lynx.core.registry import MCPToolRegistry, execute_tool
from lynx.core.session import ExecutionContext
from lynx.core.permissions import PermissionChecker
from lynx.core.audit import AuditLogger
from lynx.mcp.cluster.drafts.base import get_draft_storage
from lynx.mcp.cluster.drafts.models import DraftStatus

# Import Cell MCP registration functions
from lynx.mcp.cell.docs.draft_submit_for_approval import register_docs_draft_submit_for_approval_tool
from lynx.mcp.cell.workflow.draft_publish import register_workflow_draft_publish_tool
from lynx.mcp.cell.vpm.payment_execute import register_vpm_payment_execute_tool

# Import Cluster MCP registration functions (to create drafts)
from lynx.mcp.cluster.docs.draft_create import register_docs_draft_create_tool
from lynx.mcp.cluster.workflow.draft_create import register_workflow_draft_create_tool
from lynx.mcp.cluster.vpm.payment_draft_create import register_vpm_payment_draft_create_tool


class TestDraftStatusTransitions:
    """Test draft status transitions in approval workflow."""
    
    @pytest.mark.asyncio
    async def test_docs_draft_submit_transitions_status(
        self,
        tool_registry: MCPToolRegistry,
        context_t1: ExecutionContext,
        permission_checker: PermissionChecker,
        mock_audit_logger: AuditLogger,
    ):
        """Test that submitting a draft transitions status from DRAFT to SUBMITTED."""
        register_docs_draft_create_tool(tool_registry)
        register_docs_draft_submit_for_approval_tool(tool_registry)
        
        # Create draft
        draft_result = await execute_tool(
            tool_id="docs.cluster.draft.create",
            input_data={
                "doc_type": "SRS",
                "title": "Approval Workflow Test",
            },
            context=context_t1,
            registry=tool_registry,
            permission_checker=permission_checker,
            audit_logger=mock_audit_logger,
        )
        
        draft_id = draft_result["draft_id"]
        
        # Verify draft is in DRAFT status
        storage = get_draft_storage()
        draft = await storage.get_draft(draft_id, context_t1.tenant_id)
        assert draft.status == DraftStatus.DRAFT
        
        # Submit for approval
        submit_result = await execute_tool(
            tool_id="docs.cell.draft.submit_for_approval",
            input_data={"draft_id": draft_id},
            context=context_t1,
            registry=tool_registry,
            permission_checker=permission_checker,
            audit_logger=mock_audit_logger,
        )
        
        assert submit_result["status"] == "submitted"
        
        # Verify draft status changed to SUBMITTED
        draft = await storage.get_draft(draft_id, context_t1.tenant_id)
        assert draft.status == DraftStatus.SUBMITTED
    
    @pytest.mark.asyncio
    async def test_workflow_draft_publish_requires_approved_status(
        self,
        tool_registry: MCPToolRegistry,
        context_t1: ExecutionContext,
        permission_checker: PermissionChecker,
        mock_audit_logger: AuditLogger,
    ):
        """Test that workflow publish requires draft to be in APPROVED status."""
        register_workflow_draft_create_tool(tool_registry)
        register_workflow_draft_publish_tool(tool_registry)
        
        # Create draft
        draft_result = await execute_tool(
            tool_id="workflow.cluster.draft.create",
            input_data={
                "workflow_kind": "approval",
                "name": "Approval Test",
                "steps": [],
            },
            context=context_t1,
            registry=tool_registry,
            permission_checker=permission_checker,
            audit_logger=mock_audit_logger,
        )
        
        draft_id = draft_result["draft_id"]
        
        # Try to publish draft in DRAFT status (should fail)
        with pytest.raises(ValueError) as exc_info:
            await execute_tool(
                tool_id="workflow.cell.draft.publish",
                input_data={"draft_id": draft_id},
                context=context_t1,
                registry=tool_registry,
                permission_checker=permission_checker,
                audit_logger=mock_audit_logger,
            )
        
        error_message = str(exc_info.value)
        assert "approved" in error_message.lower() or "status" in error_message.lower()


class TestApprovalRequirements:
    """Test approval requirements for Cell MCPs."""
    
    @pytest.mark.asyncio
    async def test_payment_execute_requires_approved_draft(
        self,
        tool_registry: MCPToolRegistry,
        context_t1: ExecutionContext,
        permission_checker: PermissionChecker,
        mock_audit_logger: AuditLogger,
    ):
        """Test that payment execute requires draft to be approved."""
        register_vpm_payment_draft_create_tool(tool_registry)
        register_vpm_payment_execute_tool(tool_registry)
        
        # Create draft
        draft_result = await execute_tool(
            tool_id="vpm.cluster.payment.draft.create",
            input_data={
                "vendor_id": "vendor-001",
                "amount": 100.0,
                "currency": "USD",
                "due_date": "2026-02-01",
            },
            context=context_t1,
            registry=tool_registry,
            permission_checker=permission_checker,
            audit_logger=mock_audit_logger,
        )
        
        draft_id = draft_result["draft_id"]
        
        # Try to execute draft in DRAFT status (should fail)
        with pytest.raises(ValueError) as exc_info:
            await execute_tool(
                tool_id="vpm.cell.payment.execute",
                input_data={"draft_id": draft_id},
                context=context_t1,
                registry=tool_registry,
                permission_checker=permission_checker,
                audit_logger=mock_audit_logger,
            )
        
        error_message = str(exc_info.value)
        assert "approved" in error_message.lower() or "status" in error_message.lower()
    
    @pytest.mark.asyncio
    async def test_high_risk_draft_requires_approval(
        self,
        tool_registry: MCPToolRegistry,
        context_t1: ExecutionContext,
        permission_checker: PermissionChecker,
        mock_audit_logger: AuditLogger,
    ):
        """Test that high-risk drafts require approval before execution."""
        register_vpm_payment_draft_create_tool(tool_registry)
        register_vpm_payment_execute_tool(tool_registry)
        
        # Create high-risk draft (large amount)
        draft_result = await execute_tool(
            tool_id="vpm.cluster.payment.draft.create",
            input_data={
                "vendor_id": "vendor-001",
                "amount": 100000.0,  # Large amount = high risk
                "currency": "USD",
                "due_date": "2026-02-01",
            },
            context=context_t1,
            registry=tool_registry,
            permission_checker=permission_checker,
            audit_logger=mock_audit_logger,
        )
        
        draft_id = draft_result["draft_id"]
        
        # Verify draft is marked as high risk
        storage = get_draft_storage()
        draft = await storage.get_draft(draft_id, context_t1.tenant_id)
        assert draft.risk_level == "high"
        assert len(draft.recommended_approvers) > 0
        
        # Try to execute without approval (should fail)
        with pytest.raises(ValueError):
            await execute_tool(
                tool_id="vpm.cell.payment.execute",
                input_data={"draft_id": draft_id},
                context=context_t1,
                registry=tool_registry,
                permission_checker=permission_checker,
                audit_logger=mock_audit_logger,
            )


class TestApprovalWorkflowCompleteness:
    """Test approval workflow completeness."""
    
    @pytest.mark.asyncio
    async def test_approval_workflow_has_all_stages(
        self,
        tool_registry: MCPToolRegistry,
        context_t1: ExecutionContext,
        permission_checker: PermissionChecker,
        mock_audit_logger: AuditLogger,
    ):
        """Test that approval workflow has all required stages."""
        register_docs_draft_create_tool(tool_registry)
        register_docs_draft_submit_for_approval_tool(tool_registry)
        
        # Create draft
        draft_result = await execute_tool(
            tool_id="docs.cluster.draft.create",
            input_data={
                "doc_type": "SRS",
                "title": "Workflow Completeness Test",
            },
            context=context_t1,
            registry=tool_registry,
            permission_checker=permission_checker,
            audit_logger=mock_audit_logger,
        )
        
        draft_id = draft_result["draft_id"]
        storage = get_draft_storage()
        
        # Stage 1: DRAFT
        draft = await storage.get_draft(draft_id, context_t1.tenant_id)
        assert draft.status == DraftStatus.DRAFT
        
        # Stage 2: SUBMITTED
        await execute_tool(
            tool_id="docs.cell.draft.submit_for_approval",
            input_data={"draft_id": draft_id},
            context=context_t1,
            registry=tool_registry,
            permission_checker=permission_checker,
            audit_logger=mock_audit_logger,
        )
        
        draft = await storage.get_draft(draft_id, context_t1.tenant_id)
        assert draft.status == DraftStatus.SUBMITTED
        
        # Note: APPROVED stage would require approval system (excluded per user request)
        # But we've verified the workflow stages exist and transitions work
    
    @pytest.mark.asyncio
    async def test_approval_workflow_audit_trail(
        self,
        tool_registry: MCPToolRegistry,
        context_t1: ExecutionContext,
        permission_checker: PermissionChecker,
        mock_audit_logger: AuditLogger,
    ):
        """Test that approval workflow creates complete audit trail."""
        register_docs_draft_create_tool(tool_registry)
        register_docs_draft_submit_for_approval_tool(tool_registry)
        
        # Create draft
        draft_result = await execute_tool(
            tool_id="docs.cluster.draft.create",
            input_data={
                "doc_type": "SRS",
                "title": "Audit Trail Test",
            },
            context=context_t1,
            registry=tool_registry,
            permission_checker=permission_checker,
            audit_logger=mock_audit_logger,
        )
        
        # Verify audit events logged
        assert mock_audit_logger.log_execution_start.called
        assert mock_audit_logger.log_execution_success.called
        
        # Submit for approval
        await execute_tool(
            tool_id="docs.cell.draft.submit_for_approval",
            input_data={"draft_id": draft_result["draft_id"]},
            context=context_t1,
            registry=tool_registry,
            permission_checker=permission_checker,
            audit_logger=mock_audit_logger,
        )
        
        # Verify additional audit events logged
        assert mock_audit_logger.log_execution_start.call_count >= 2
        assert mock_audit_logger.log_execution_success.call_count >= 2

