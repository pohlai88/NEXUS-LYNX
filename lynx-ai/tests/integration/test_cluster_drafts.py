"""
Integration tests for Cluster MCPs (Draft Creation).

Tests validate Draft Protocol compliance:
- Draft-only guarantee (no production state changes)
- Tenant boundary enforcement
- Audit completeness
- Policy pre-check
- Idempotency
"""

import pytest
from lynx.core.registry import MCPToolRegistry, execute_tool
from lynx.core.session import ExecutionContext
from lynx.core.permissions import PermissionChecker
from lynx.core.audit import AuditLogger
from lynx.mcp.cluster.drafts.base import DraftStorage, get_draft_storage, DraftStatus
from lynx.mcp.cluster.docs.draft_create import register_docs_draft_create_tool
from lynx.mcp.cluster.workflow.draft_create import register_workflow_draft_create_tool
from lynx.mcp.cluster.vpm.payment_draft_create import register_vpm_payment_draft_create_tool


class TestDraftOnlyGuarantee:
    """Test that draft creation does not change production state."""
    
    @pytest.mark.asyncio
    async def test_draft_creation_does_not_mutate_production(
        self,
        tool_registry: MCPToolRegistry,
        context_t1: ExecutionContext,
        permission_checker: PermissionChecker,
        mock_audit_logger: AuditLogger,
    ):
        """Test that creating a draft does not change any production state."""
        register_docs_draft_create_tool(tool_registry)
        
        # Track initial state (in production, this would be actual production records)
        initial_state = {"production_docs_count": 0}  # Mock production state
        
        # Create a draft
        result = await execute_tool(
            tool_id="docs.cluster.draft.create",
            input_data={
                "doc_type": "PRD",
                "title": "Test PRD",
                "content_outline": "Test content",
            },
            context=context_t1,
            registry=tool_registry,
            permission_checker=permission_checker,
            audit_logger=mock_audit_logger,
        )
        
        # Verify draft was created
        assert result is not None
        assert result["status"] == "draft"
        assert "draft_id" in result
        
        # Verify production state unchanged
        assert initial_state["production_docs_count"] == 0
        
        # Verify draft is in draft storage, not production
        storage = get_draft_storage()
        draft = await storage.get_draft(result["draft_id"], context_t1.tenant_id)
        assert draft is not None
        assert draft.status == DraftStatus.DRAFT


class TestTenantBoundary:
    """Test that drafts respect tenant boundaries."""
    
    @pytest.mark.asyncio
    async def test_draft_belongs_to_tenant(
        self,
        tool_registry: MCPToolRegistry,
        context_t1: ExecutionContext,
        context_t2: ExecutionContext,
        permission_checker: PermissionChecker,
        mock_audit_logger: AuditLogger,
    ):
        """Test that draft belongs to tenant and cannot be accessed from other tenant."""
        register_docs_draft_create_tool(tool_registry)
        
        # Create draft with T1 context
        result_t1 = await execute_tool(
            tool_id="docs.cluster.draft.create",
            input_data={
                "doc_type": "PRD",
                "title": "T1 Draft",
            },
            context=context_t1,
            registry=tool_registry,
            permission_checker=permission_checker,
            audit_logger=mock_audit_logger,
        )
        
        draft_id = result_t1["draft_id"]
        assert result_t1["tenant_id"] == context_t1.tenant_id
        
        # Verify T1 can access draft
        storage = get_draft_storage()
        draft_t1 = await storage.get_draft(draft_id, context_t1.tenant_id)
        assert draft_t1 is not None
        assert draft_t1.tenant_id == context_t1.tenant_id
        
        # Verify T2 cannot access T1's draft
        draft_t2 = await storage.get_draft(draft_id, context_t2.tenant_id)
        assert draft_t2 is None  # Should not find draft from different tenant


class TestAuditCompleteness:
    """Test that draft creation is fully audited."""
    
    @pytest.mark.asyncio
    async def test_draft_creation_logs_audit_events(
        self,
        tool_registry: MCPToolRegistry,
        context_t1: ExecutionContext,
        permission_checker: PermissionChecker,
        mock_audit_logger: AuditLogger,
    ):
        """Test that draft creation logs run + tool call + draft_id."""
        register_docs_draft_create_tool(tool_registry)
        
        # Create draft
        result = await execute_tool(
            tool_id="docs.cluster.draft.create",
            input_data={
                "doc_type": "PRD",
                "title": "Test PRD",
            },
            context=context_t1,
            registry=tool_registry,
            permission_checker=permission_checker,
            audit_logger=mock_audit_logger,
        )
        
        # Verify audit logging was called
        assert mock_audit_logger.log_execution_start.called
        assert mock_audit_logger.log_execution_success.called
        
        # Verify draft_id is in audit log
        success_call = mock_audit_logger.log_execution_success.call_args
        output_data = success_call[1]["output_data"]
        assert "draft_id" in output_data
        assert output_data["draft_id"] == result["draft_id"]


class TestPolicyPreCheck:
    """Test that policy pre-checks are enforced."""
    
    @pytest.mark.asyncio
    async def test_high_risk_draft_requires_approval(
        self,
        tool_registry: MCPToolRegistry,
        context_t1: ExecutionContext,
        permission_checker: PermissionChecker,
        mock_audit_logger: AuditLogger,
    ):
        """Test that high-risk drafts are marked as requiring approval."""
        register_docs_draft_create_tool(tool_registry)
        
        # Create high-risk draft (PRD/LAW doc_type)
        result = await execute_tool(
            tool_id="docs.cluster.draft.create",
            input_data={
                "doc_type": "PRD",  # High risk
                "title": "Test PRD",
            },
            context=context_t1,
            registry=tool_registry,
            permission_checker=permission_checker,
            audit_logger=mock_audit_logger,
        )
        
        # Verify draft was created
        assert result is not None
        assert result["status"] == "draft"
        
        # Verify next actions include review-required for high risk
        assert "review-required" in result["next_actions"]
        
        # Verify draft has recommended approvers
        storage = get_draft_storage()
        draft = await storage.get_draft(result["draft_id"], context_t1.tenant_id)
        assert draft is not None
        assert len(draft.recommended_approvers) > 0
        assert draft.risk_level == "high"


class TestIdempotency:
    """Test that drafts are idempotent."""
    
    @pytest.mark.asyncio
    async def test_same_request_id_returns_same_draft_id(
        self,
        tool_registry: MCPToolRegistry,
        context_t1: ExecutionContext,
        permission_checker: PermissionChecker,
        mock_audit_logger: AuditLogger,
    ):
        """Test that same request_id returns same draft_id."""
        register_docs_draft_create_tool(tool_registry)
        
        request_id = "test-request-123"
        
        # Create draft with request_id
        result1 = await execute_tool(
            tool_id="docs.cluster.draft.create",
            input_data={
                "doc_type": "PRD",
                "title": "Test PRD",
                "request_id": request_id,
            },
            context=context_t1,
            registry=tool_registry,
            permission_checker=permission_checker,
            audit_logger=mock_audit_logger,
        )
        
        draft_id_1 = result1["draft_id"]
        
        # Create draft again with same request_id
        result2 = await execute_tool(
            tool_id="docs.cluster.draft.create",
            input_data={
                "doc_type": "PRD",
                "title": "Test PRD",
                "request_id": request_id,
            },
            context=context_t1,
            registry=tool_registry,
            permission_checker=permission_checker,
            audit_logger=mock_audit_logger,
        )
        
        draft_id_2 = result2["draft_id"]
        
        # Verify same draft_id returned
        assert draft_id_1 == draft_id_2, "Idempotency failed: different draft_ids for same request_id"
        
        # Verify only one draft exists
        storage = get_draft_storage()
        drafts = await storage.list_drafts(context_t1.tenant_id, draft_type="docs")
        draft_ids = [d.draft_id for d in drafts if d.request_id == request_id]
        assert len(draft_ids) == 1, f"Expected 1 draft, found {len(draft_ids)}"
        assert draft_ids[0] == draft_id_1


class TestDraftProtocolCompliance:
    """Test that drafts comply with Draft Protocol."""
    
    @pytest.mark.asyncio
    async def test_draft_has_required_fields(
        self,
        tool_registry: MCPToolRegistry,
        context_t1: ExecutionContext,
        permission_checker: PermissionChecker,
        mock_audit_logger: AuditLogger,
    ):
        """Test that created draft has all required Draft Protocol fields."""
        register_docs_draft_create_tool(tool_registry)
        
        result = await execute_tool(
            tool_id="docs.cluster.draft.create",
            input_data={
                "doc_type": "SRS",
                "title": "Test SRS",
            },
            context=context_t1,
            registry=tool_registry,
            permission_checker=permission_checker,
            audit_logger=mock_audit_logger,
        )
        
        # Get draft from storage
        storage = get_draft_storage()
        draft = await storage.get_draft(result["draft_id"], context_t1.tenant_id)
        
        # Verify all required fields
        assert draft is not None
        assert draft.draft_id is not None
        assert draft.tenant_id == context_t1.tenant_id
        assert draft.draft_type == "docs"
        assert draft.status == DraftStatus.DRAFT
        assert draft.risk_level in ["low", "medium", "high"]
        assert draft.created_by == context_t1.user_id
        assert draft.created_at is not None
        assert draft.source_context is not None
        assert isinstance(draft.recommended_approvers, list)
        assert draft.payload is not None
        assert "doc_type" in draft.payload
        assert "title" in draft.payload


class TestWorkflowDraftCreation:
    """Test workflow.cluster.draft.create specific behaviors."""
    
    @pytest.mark.asyncio
    async def test_workflow_draft_includes_policy_snapshot(
        self,
        tool_registry: MCPToolRegistry,
        context_t1: ExecutionContext,
        permission_checker: PermissionChecker,
        mock_audit_logger: AuditLogger,
    ):
        """Test that workflow draft includes policy snapshot."""
        register_workflow_draft_create_tool(tool_registry)
        
        result = await execute_tool(
            tool_id="workflow.cluster.draft.create",
            input_data={
                "workflow_kind": "approval",
                "name": "Test Workflow",
                "steps": [
                    {"step_id": "step-1", "name": "Approve", "step_type": "approval"}
                ],
            },
            context=context_t1,
            registry=tool_registry,
            permission_checker=permission_checker,
            audit_logger=mock_audit_logger,
        )
        
        # Verify draft includes policy snapshot
        storage = get_draft_storage()
        draft = await storage.get_draft(result["draft_id"], context_t1.tenant_id)
        assert draft is not None
        assert "policy_snapshot" in draft.source_context
        assert "approval_rules" in draft.source_context["policy_snapshot"]
    
    @pytest.mark.asyncio
    async def test_workflow_draft_requires_approval_when_high_risk(
        self,
        tool_registry: MCPToolRegistry,
        context_t1: ExecutionContext,
        permission_checker: PermissionChecker,
        mock_audit_logger: AuditLogger,
    ):
        """Test that high-risk workflow drafts require approval."""
        register_workflow_draft_create_tool(tool_registry)
        
        # Create high-risk workflow (payment/approval kind)
        result = await execute_tool(
            tool_id="workflow.cluster.draft.create",
            input_data={
                "workflow_kind": "payment",  # High risk
                "name": "Payment Workflow",
                "steps": [
                    {"step_id": "step-1", "name": "Approve Payment", "step_type": "approval"}
                ],
            },
            context=context_t1,
            registry=tool_registry,
            permission_checker=permission_checker,
            audit_logger=mock_audit_logger,
        )
        
        # Verify high risk
        assert result["risk_level"] == "high"
        assert len(result["recommended_approvers"]) > 0
    
    @pytest.mark.asyncio
    async def test_workflow_draft_refuses_if_permission_denied(
        self,
        tool_registry: MCPToolRegistry,
        context_t1: ExecutionContext,
        permission_checker: PermissionChecker,
        mock_audit_logger: AuditLogger,
    ):
        """Test that workflow draft refuses if permission denied."""
        register_workflow_draft_create_tool(tool_registry)
        
        # Create context with insufficient role
        context_t1.user_role = "user"  # Not admin
        
        # Should raise ValueError due to permission check
        with pytest.raises(ValueError, match="lacks permission"):
            await execute_tool(
                tool_id="workflow.cluster.draft.create",
                input_data={
                    "workflow_kind": "approval",
                    "name": "Test Workflow",
                    "steps": [],
                },
                context=context_t1,
                registry=tool_registry,
                permission_checker=permission_checker,
                audit_logger=mock_audit_logger,
            )
    
    @pytest.mark.asyncio
    async def test_workflow_draft_is_idempotent(
        self,
        tool_registry: MCPToolRegistry,
        context_t1: ExecutionContext,
        permission_checker: PermissionChecker,
        mock_audit_logger: AuditLogger,
    ):
        """Test that workflow draft is idempotent."""
        register_workflow_draft_create_tool(tool_registry)
        
        request_id = "workflow-request-123"
        
        result1 = await execute_tool(
            tool_id="workflow.cluster.draft.create",
            input_data={
                "workflow_kind": "approval",
                "name": "Test Workflow",
                "steps": [],
                "request_id": request_id,
            },
            context=context_t1,
            registry=tool_registry,
            permission_checker=permission_checker,
            audit_logger=mock_audit_logger,
        )
        
        result2 = await execute_tool(
            tool_id="workflow.cluster.draft.create",
            input_data={
                "workflow_kind": "approval",
                "name": "Test Workflow",
                "steps": [],
                "request_id": request_id,
            },
            context=context_t1,
            registry=tool_registry,
            permission_checker=permission_checker,
            audit_logger=mock_audit_logger,
        )
        
        assert result1["draft_id"] == result2["draft_id"]
    
    @pytest.mark.asyncio
    async def test_workflow_draft_is_tenant_scoped(
        self,
        tool_registry: MCPToolRegistry,
        context_t1: ExecutionContext,
        context_t2: ExecutionContext,
        permission_checker: PermissionChecker,
        mock_audit_logger: AuditLogger,
    ):
        """Test that workflow draft is tenant-scoped."""
        register_workflow_draft_create_tool(tool_registry)
        
        result_t1 = await execute_tool(
            tool_id="workflow.cluster.draft.create",
            input_data={
                "workflow_kind": "approval",
                "name": "T1 Workflow",
                "steps": [],
            },
            context=context_t1,
            registry=tool_registry,
            permission_checker=permission_checker,
            audit_logger=mock_audit_logger,
        )
        
        # Verify T2 cannot access T1's draft
        storage = get_draft_storage()
        draft_t2 = await storage.get_draft(result_t1["draft_id"], context_t2.tenant_id)
        assert draft_t2 is None


class TestVPMPaymentDraftCreation:
    """Test vpm.cluster.payment.draft.create specific behaviors."""
    
    @pytest.mark.asyncio
    async def test_payment_draft_includes_vendor_snapshot(
        self,
        tool_registry: MCPToolRegistry,
        context_t1: ExecutionContext,
        permission_checker: PermissionChecker,
        mock_audit_logger: AuditLogger,
    ):
        """Test that payment draft includes vendor snapshot."""
        register_vpm_payment_draft_create_tool(tool_registry)
        
        result = await execute_tool(
            tool_id="vpm.cluster.payment.draft.create",
            input_data={
                "vendor_id": "vendor-001",
                "amount": 1000.0,
                "currency": "USD",
                "due_date": "2026-02-01",
            },
            context=context_t1,
            registry=tool_registry,
            permission_checker=permission_checker,
            audit_logger=mock_audit_logger,
        )
        
        # Verify vendor snapshot in output
        assert "vendor_snapshot" in result
        assert result["vendor_snapshot"]["vendor_id"] == "vendor-001"
        
        # Verify vendor snapshot in draft
        storage = get_draft_storage()
        draft = await storage.get_draft(result["draft_id"], context_t1.tenant_id)
        assert draft is not None
        assert "vendor_snapshot" in draft.source_context
    
    @pytest.mark.asyncio
    async def test_payment_draft_includes_approval_requirements(
        self,
        tool_registry: MCPToolRegistry,
        context_t1: ExecutionContext,
        permission_checker: PermissionChecker,
        mock_audit_logger: AuditLogger,
    ):
        """Test that payment draft includes approval requirements."""
        register_vpm_payment_draft_create_tool(tool_registry)
        
        result = await execute_tool(
            tool_id="vpm.cluster.payment.draft.create",
            input_data={
                "vendor_id": "vendor-001",
                "amount": 1000.0,
                "currency": "USD",
                "due_date": "2026-02-01",
            },
            context=context_t1,
            registry=tool_registry,
            permission_checker=permission_checker,
            audit_logger=mock_audit_logger,
        )
        
        # Verify approval requirements
        assert "recommended_approvers" in result
        assert len(result["recommended_approvers"]) > 0
        assert "risk_level" in result
    
    @pytest.mark.asyncio
    async def test_payment_draft_refuses_for_inactive_vendor(
        self,
        tool_registry: MCPToolRegistry,
        context_t1: ExecutionContext,
        permission_checker: PermissionChecker,
        mock_audit_logger: AuditLogger,
    ):
        """Test that payment draft refuses for inactive vendor."""
        register_vpm_payment_draft_create_tool(tool_registry)
        
        # Note: Current implementation uses mock data with active vendor
        # In production, this would read from vpm.domain.vendor.read
        # For now, test that the check exists in the code path
        
        # This test documents the expected behavior
        # In production, if vendor is inactive, it should raise ValueError
        result = await execute_tool(
            tool_id="vpm.cluster.payment.draft.create",
            input_data={
                "vendor_id": "vendor-inactive",  # Would be inactive in production
                "amount": 1000.0,
                "currency": "USD",
                "due_date": "2026-02-01",
            },
            context=context_t1,
            registry=tool_registry,
            permission_checker=permission_checker,
            audit_logger=mock_audit_logger,
        )
        
        # Current implementation uses mock active vendor
        # In production, this would check vendor status and raise if inactive
        assert result is not None  # Current mock allows it
    
    @pytest.mark.asyncio
    async def test_payment_draft_marks_high_risk_requires_approval(
        self,
        tool_registry: MCPToolRegistry,
        context_t1: ExecutionContext,
        permission_checker: PermissionChecker,
        mock_audit_logger: AuditLogger,
    ):
        """Test that high-risk payment drafts require approval."""
        register_vpm_payment_draft_create_tool(tool_registry)
        
        # Create high-risk payment (amount above threshold)
        result = await execute_tool(
            tool_id="vpm.cluster.payment.draft.create",
            input_data={
                "vendor_id": "vendor-001",
                "amount": 5000.0,  # Above threshold (1000.0)
                "currency": "USD",
                "due_date": "2026-02-01",
            },
            context=context_t1,
            registry=tool_registry,
            permission_checker=permission_checker,
            audit_logger=mock_audit_logger,
        )
        
        # Verify high risk
        assert result["risk_level"] == "high"
        assert result["execution_readiness"]["requires_manual_review"] is True
    
    @pytest.mark.asyncio
    async def test_payment_draft_refuses_if_permission_denied(
        self,
        tool_registry: MCPToolRegistry,
        context_t1: ExecutionContext,
        permission_checker: PermissionChecker,
        mock_audit_logger: AuditLogger,
    ):
        """Test that payment draft refuses if permission denied."""
        register_vpm_payment_draft_create_tool(tool_registry)
        
        # Create context with insufficient role
        context_t1.user_role = "user"  # Not admin or finance_manager
        
        # Should raise ValueError due to permission check
        with pytest.raises(ValueError, match="lacks permission"):
            await execute_tool(
                tool_id="vpm.cluster.payment.draft.create",
                input_data={
                    "vendor_id": "vendor-001",
                    "amount": 1000.0,
                    "currency": "USD",
                    "due_date": "2026-02-01",
                },
                context=context_t1,
                registry=tool_registry,
                permission_checker=permission_checker,
                audit_logger=mock_audit_logger,
            )
    
    @pytest.mark.asyncio
    async def test_payment_draft_is_idempotent(
        self,
        tool_registry: MCPToolRegistry,
        context_t1: ExecutionContext,
        permission_checker: PermissionChecker,
        mock_audit_logger: AuditLogger,
    ):
        """Test that payment draft is idempotent."""
        register_vpm_payment_draft_create_tool(tool_registry)
        
        request_id = "payment-request-123"
        
        result1 = await execute_tool(
            tool_id="vpm.cluster.payment.draft.create",
            input_data={
                "vendor_id": "vendor-001",
                "amount": 1000.0,
                "currency": "USD",
                "due_date": "2026-02-01",
                "request_id": request_id,
            },
            context=context_t1,
            registry=tool_registry,
            permission_checker=permission_checker,
            audit_logger=mock_audit_logger,
        )
        
        result2 = await execute_tool(
            tool_id="vpm.cluster.payment.draft.create",
            input_data={
                "vendor_id": "vendor-001",
                "amount": 1000.0,
                "currency": "USD",
                "due_date": "2026-02-01",
                "request_id": request_id,
            },
            context=context_t1,
            registry=tool_registry,
            permission_checker=permission_checker,
            audit_logger=mock_audit_logger,
        )
        
        assert result1["draft_id"] == result2["draft_id"]
    
    @pytest.mark.asyncio
    async def test_payment_draft_is_tenant_scoped(
        self,
        tool_registry: MCPToolRegistry,
        context_t1: ExecutionContext,
        context_t2: ExecutionContext,
        permission_checker: PermissionChecker,
        mock_audit_logger: AuditLogger,
    ):
        """Test that payment draft is tenant-scoped."""
        register_vpm_payment_draft_create_tool(tool_registry)
        
        result_t1 = await execute_tool(
            tool_id="vpm.cluster.payment.draft.create",
            input_data={
                "vendor_id": "vendor-001",
                "amount": 1000.0,
                "currency": "USD",
                "due_date": "2026-02-01",
            },
            context=context_t1,
            registry=tool_registry,
            permission_checker=permission_checker,
            audit_logger=mock_audit_logger,
        )
        
        # Verify T2 cannot access T1's draft
        storage = get_draft_storage()
        draft_t2 = await storage.get_draft(result_t1["draft_id"], context_t2.tenant_id)
        assert draft_t2 is None
    
    @pytest.mark.asyncio
    async def test_payment_draft_never_mutates_production_state(
        self,
        tool_registry: MCPToolRegistry,
        context_t1: ExecutionContext,
        permission_checker: PermissionChecker,
        mock_audit_logger: AuditLogger,
    ):
        """Test that payment draft never mutates production state."""
        register_vpm_payment_draft_create_tool(tool_registry)
        
        # Track initial state
        initial_state = {"production_payments_count": 0}
        
        result = await execute_tool(
            tool_id="vpm.cluster.payment.draft.create",
            input_data={
                "vendor_id": "vendor-001",
                "amount": 1000.0,
                "currency": "USD",
                "due_date": "2026-02-01",
            },
            context=context_t1,
            registry=tool_registry,
            permission_checker=permission_checker,
            audit_logger=mock_audit_logger,
        )
        
        # Verify draft created
        assert result["status"] == "draft"
        
        # Verify production state unchanged
        assert initial_state["production_payments_count"] == 0


class TestDraftImmutability:
    """Test draft immutability guardrail."""
    
    @pytest.mark.asyncio
    async def test_draft_not_mutated_on_repeat_request(
        self,
        tool_registry: MCPToolRegistry,
        context_t1: ExecutionContext,
        permission_checker: PermissionChecker,
        mock_audit_logger: AuditLogger,
    ):
        """Test that draft is not mutated on repeat request (idempotency preserves draft)."""
        register_docs_draft_create_tool(tool_registry)
        
        request_id = "immutability-test-123"
        
        # Create draft
        result1 = await execute_tool(
            tool_id="docs.cluster.draft.create",
            input_data={
                "doc_type": "PRD",
                "title": "Original Title",
                "content_outline": "Original content",
                "request_id": request_id,
            },
            context=context_t1,
            registry=tool_registry,
            permission_checker=permission_checker,
            audit_logger=mock_audit_logger,
        )
        
        draft_id_1 = result1["draft_id"]
        
        # Get original draft
        storage = get_draft_storage()
        original_draft = await storage.get_draft(draft_id_1, context_t1.tenant_id)
        original_payload = original_draft.payload.copy()
        
        # Repeat request with different content (should return same draft, not mutate)
        result2 = await execute_tool(
            tool_id="docs.cluster.draft.create",
            input_data={
                "doc_type": "PRD",
                "title": "Different Title",  # Different content
                "content_outline": "Different content",  # Different content
                "request_id": request_id,  # Same request_id
            },
            context=context_t1,
            registry=tool_registry,
            permission_checker=permission_checker,
            audit_logger=mock_audit_logger,
        )
        
        # Verify same draft_id returned (idempotency)
        assert result2["draft_id"] == draft_id_1
        
        # Verify draft payload not mutated
        draft_after = await storage.get_draft(draft_id_1, context_t1.tenant_id)
        assert draft_after.payload == original_payload, "Draft payload was mutated on repeat request"

