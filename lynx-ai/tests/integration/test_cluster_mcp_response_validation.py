"""
Comprehensive Response Validation Tests for Cluster MCPs.

Tests validate:
- Complete response schema (all required fields present)
- Response data correctness (values match expectations)
- Preview markdown structure and content
- Error message format and content
- Edge cases and boundary conditions
- Response type validation
"""

import pytest
from lynx.core.registry import MCPToolRegistry, execute_tool
from lynx.core.session import ExecutionContext
from lynx.core.permissions import PermissionChecker
from lynx.core.audit import AuditLogger
from lynx.mcp.cluster.drafts.base import get_draft_storage

# Import all Cluster MCP registration functions
from lynx.mcp.cluster.docs.draft_create import register_docs_draft_create_tool
from lynx.mcp.cluster.docs.batch_draft_create import register_batch_docs_draft_create_tool
from lynx.mcp.cluster.docs.message_draft_create import register_message_docs_draft_create_tool
from lynx.mcp.cluster.workflow.draft_create import register_workflow_draft_create_tool
from lynx.mcp.cluster.workflow.digital_draft_create import register_digital_workflow_draft_create_tool
from lynx.mcp.cluster.vpm.payment_draft_create import register_vpm_payment_draft_create_tool
from lynx.mcp.cluster.portal.scaffold_draft_create import register_portal_scaffold_draft_create_tool
from lynx.mcp.cluster.portal.config_draft_create import register_portal_config_draft_create_tool


class TestBatchDocsDraftResponseValidation:
    """Test batch docs draft response structure and content."""
    
    @pytest.mark.asyncio
    async def test_batch_draft_response_schema_complete(
        self,
        tool_registry: MCPToolRegistry,
        context_t1: ExecutionContext,
        permission_checker: PermissionChecker,
        mock_audit_logger: AuditLogger,
    ):
        """Test that batch draft response has all required fields."""
        register_batch_docs_draft_create_tool(tool_registry)
        
        result = await execute_tool(
            tool_id="docs.cluster.batch.draft.create",
            input_data={
                "batch_name": "Test Batch",
                "requests": [
                    {"doc_type": "SRS", "title": "Test SRS"},
                    {"doc_type": "ADR", "title": "Test ADR"},
                ],
            },
            context=context_t1,
            registry=tool_registry,
            permission_checker=permission_checker,
            audit_logger=mock_audit_logger,
        )
        
        # Verify all required fields present
        required_fields = [
            "draft_id",
            "status",
            "preview_markdown",
            "batch_summary",
            "next_actions",
            "tenant_id",
        ]
        for field in required_fields:
            assert field in result, f"Missing required field: {field}"
        
        # Verify field types
        assert isinstance(result["draft_id"], str)
        assert isinstance(result["status"], str)
        assert isinstance(result["preview_markdown"], str)
        assert isinstance(result["batch_summary"], dict)
        assert isinstance(result["next_actions"], list)
        assert isinstance(result["tenant_id"], str)
        
        # Verify status value
        assert result["status"] == "draft"
        
        # Verify tenant_id matches context
        assert result["tenant_id"] == context_t1.tenant_id
    
    @pytest.mark.asyncio
    async def test_batch_draft_response_data_correctness(
        self,
        tool_registry: MCPToolRegistry,
        context_t1: ExecutionContext,
        permission_checker: PermissionChecker,
        mock_audit_logger: AuditLogger,
    ):
        """Test that batch draft response data matches input."""
        register_batch_docs_draft_create_tool(tool_registry)
        
        batch_name = "My Test Batch"
        requests = [
            {"doc_type": "SRS", "title": "SRS Document"},
            {"doc_type": "ADR", "title": "ADR Document"},
        ]
        
        result = await execute_tool(
            tool_id="docs.cluster.batch.draft.create",
            input_data={
                "batch_name": batch_name,
                "requests": requests,
            },
            context=context_t1,
            registry=tool_registry,
            permission_checker=permission_checker,
            audit_logger=mock_audit_logger,
        )
        
        # Verify batch_summary matches input
        assert result["batch_summary"]["batch_size"] == len(requests)
        assert "SRS" in result["batch_summary"]["doc_type_counts"]
        assert "ADR" in result["batch_summary"]["doc_type_counts"]
        assert result["batch_summary"]["doc_type_counts"]["SRS"] == 1
        assert result["batch_summary"]["doc_type_counts"]["ADR"] == 1
        
        # Verify preview markdown contains batch name
        assert batch_name in result["preview_markdown"]
        
        # Verify preview markdown contains document titles
        assert "SRS Document" in result["preview_markdown"]
        assert "ADR Document" in result["preview_markdown"]
        
        # Verify next_actions is not empty
        assert len(result["next_actions"]) > 0
        assert "submit-for-approval" in result["next_actions"]
    
    @pytest.mark.asyncio
    async def test_batch_draft_preview_markdown_structure(
        self,
        tool_registry: MCPToolRegistry,
        context_t1: ExecutionContext,
        permission_checker: PermissionChecker,
        mock_audit_logger: AuditLogger,
    ):
        """Test that preview markdown has correct structure."""
        register_batch_docs_draft_create_tool(tool_registry)
        
        result = await execute_tool(
            tool_id="docs.cluster.batch.draft.create",
            input_data={
                "batch_name": "Test Batch",
                "requests": [{"doc_type": "SRS", "title": "Test"}],
            },
            context=context_t1,
            registry=tool_registry,
            permission_checker=permission_checker,
            audit_logger=mock_audit_logger,
        )
        
        preview = result["preview_markdown"]
        
        # Verify markdown structure
        assert preview.startswith("#"), "Preview should start with markdown header"
        assert "Batch Document Request" in preview or "Batch" in preview
        assert "Status:" in preview or "status" in preview.lower()
        assert "Draft" in preview
        assert "Created:" in preview or "created" in preview.lower()
        assert "Created By:" in preview or "created by" in preview.lower()
        assert context_t1.user_id in preview


class TestMessageDocsDraftResponseValidation:
    """Test message docs draft response structure and content."""
    
    @pytest.mark.asyncio
    async def test_message_draft_response_schema_complete(
        self,
        tool_registry: MCPToolRegistry,
        context_t1: ExecutionContext,
        permission_checker: PermissionChecker,
        mock_audit_logger: AuditLogger,
    ):
        """Test that message draft response has all required fields."""
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
        
        # Verify all required fields
        required_fields = [
            "draft_id",
            "status",
            "preview_markdown",
            "recipient_summary",
            "next_actions",
            "tenant_id",
        ]
        for field in required_fields:
            assert field in result, f"Missing required field: {field}"
        
        # Verify recipient_summary structure
        assert "count" in result["recipient_summary"]
        assert result["recipient_summary"]["count"] == 2
        assert "message_type" in result["recipient_summary"]
        assert result["recipient_summary"]["message_type"] == "reminder"
    
    @pytest.mark.asyncio
    async def test_message_draft_preview_contains_content(
        self,
        tool_registry: MCPToolRegistry,
        context_t1: ExecutionContext,
        permission_checker: PermissionChecker,
        mock_audit_logger: AuditLogger,
    ):
        """Test that preview markdown contains message content."""
        register_message_docs_draft_create_tool(tool_registry)
        
        subject = "Important Notice"
        body = "This is an important message"
        
        result = await execute_tool(
            tool_id="docs.cluster.message.draft.create",
            input_data={
                "message_type": "notification",
                "recipient_ids": ["user-1"],
                "subject": subject,
                "body": body,
            },
            context=context_t1,
            registry=tool_registry,
            permission_checker=permission_checker,
            audit_logger=mock_audit_logger,
        )
        
        preview = result["preview_markdown"]
        assert subject in preview
        assert body in preview
        assert "user-1" in preview


class TestDigitalWorkflowDraftResponseValidation:
    """Test digital workflow draft response structure and content."""
    
    @pytest.mark.asyncio
    async def test_digital_workflow_response_schema_complete(
        self,
        tool_registry: MCPToolRegistry,
        context_t1: ExecutionContext,
        permission_checker: PermissionChecker,
        mock_audit_logger: AuditLogger,
    ):
        """Test that digital workflow draft response has all required fields."""
        register_digital_workflow_draft_create_tool(tool_registry)
        context_t1.user_role = "admin"
        
        result = await execute_tool(
            tool_id="workflow.cluster.digital.draft.create",
            input_data={
                "workflow_name": "Test Workflow",
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
        
        # Verify all required fields
        required_fields = [
            "draft_id",
            "status",
            "preview_markdown",
            "risk_level",
            "recommended_approvers",
            "automation_summary",
            "tenant_id",
        ]
        for field in required_fields:
            assert field in result, f"Missing required field: {field}"
        
        # Verify automation_summary structure
        assert "step_count" in result["automation_summary"]
        assert result["automation_summary"]["step_count"] == 1
        assert "automation_types" in result["automation_summary"]
        assert isinstance(result["automation_summary"]["automation_types"], list)
        
        # Verify risk_level is valid
        assert result["risk_level"] in ["low", "medium", "high"]
        
        # Verify recommended_approvers is a list
        assert isinstance(result["recommended_approvers"], list)
        assert len(result["recommended_approvers"]) > 0


class TestPortalScaffoldDraftResponseValidation:
    """Test portal scaffold draft response structure and content."""
    
    @pytest.mark.asyncio
    async def test_portal_scaffold_response_schema_complete(
        self,
        tool_registry: MCPToolRegistry,
        context_t1: ExecutionContext,
        permission_checker: PermissionChecker,
        mock_audit_logger: AuditLogger,
    ):
        """Test that portal scaffold draft response has all required fields."""
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
        
        # Verify all required fields
        required_fields = [
            "draft_id",
            "status",
            "preview_markdown",
            "risk_level",
            "recommended_approvers",
            "scaffold_summary",
            "tenant_id",
        ]
        for field in required_fields:
            assert field in result, f"Missing required field: {field}"
        
        # Verify scaffold_summary structure
        assert "module_count" in result["scaffold_summary"]
        assert result["scaffold_summary"]["module_count"] == 1
        assert "portal_type" in result["scaffold_summary"]
        assert result["scaffold_summary"]["portal_type"] == "internal"


class TestPortalConfigDraftResponseValidation:
    """Test portal config draft response structure and content."""
    
    @pytest.mark.asyncio
    async def test_portal_config_response_schema_complete(
        self,
        tool_registry: MCPToolRegistry,
        context_t1: ExecutionContext,
        permission_checker: PermissionChecker,
        mock_audit_logger: AuditLogger,
    ):
        """Test that portal config draft response has all required fields."""
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
        
        # Verify all required fields
        required_fields = [
            "draft_id",
            "status",
            "preview_markdown",
            "risk_level",
            "recommended_approvers",
            "config_summary",
            "tenant_id",
        ]
        for field in required_fields:
            assert field in result, f"Missing required field: {field}"
        
        # Verify config_summary structure
        assert "config_sections" in result["config_summary"]
        assert "routing" in result["config_summary"]["config_sections"]
        assert "section_count" in result["config_summary"]
        assert result["config_summary"]["section_count"] == 1


class TestErrorResponseValidation:
    """Test error response format and content."""
    
    @pytest.mark.asyncio
    async def test_permission_denied_error_message_format(
        self,
        tool_registry: MCPToolRegistry,
        context_t1: ExecutionContext,
        permission_checker: PermissionChecker,
        mock_audit_logger: AuditLogger,
    ):
        """Test that permission denied errors have correct format."""
        register_digital_workflow_draft_create_tool(tool_registry)
        context_t1.user_role = "user"  # Insufficient role
        
        with pytest.raises(ValueError) as exc_info:
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
        
        error_message = str(exc_info.value)
        assert "lacks permission" in error_message
        assert "user" in error_message or "User role" in error_message
        assert "required roles" in error_message.lower() or "Required roles" in error_message
    
    @pytest.mark.asyncio
    async def test_input_validation_error_format(
        self,
        tool_registry: MCPToolRegistry,
        context_t1: ExecutionContext,
        permission_checker: PermissionChecker,
        mock_audit_logger: AuditLogger,
    ):
        """Test that input validation errors have correct format."""
        register_batch_docs_draft_create_tool(tool_registry)
        
        with pytest.raises(ValueError) as exc_info:
            await execute_tool(
                tool_id="docs.cluster.batch.draft.create",
                input_data={
                    "batch_name": "Test",
                    "requests": [],  # Empty list should fail validation
                },
                context=context_t1,
                registry=tool_registry,
                permission_checker=permission_checker,
                audit_logger=mock_audit_logger,
            )
        
        error_message = str(exc_info.value)
        assert "validation" in error_message.lower() or "Validation" in error_message
        assert "requests" in error_message.lower() or "List" in error_message


class TestEdgeCases:
    """Test edge cases and boundary conditions."""
    
    @pytest.mark.asyncio
    async def test_batch_draft_max_items_boundary(
        self,
        tool_registry: MCPToolRegistry,
        context_t1: ExecutionContext,
        permission_checker: PermissionChecker,
        mock_audit_logger: AuditLogger,
    ):
        """Test batch draft with maximum allowed items (50)."""
        register_batch_docs_draft_create_tool(tool_registry)
        
        # Create batch with 50 items (max allowed)
        requests = [{"doc_type": "SRS", "title": f"Doc {i}"} for i in range(50)]
        
        result = await execute_tool(
            tool_id="docs.cluster.batch.draft.create",
            input_data={
                "batch_name": "Max Batch",
                "requests": requests,
            },
            context=context_t1,
            registry=tool_registry,
            permission_checker=permission_checker,
            audit_logger=mock_audit_logger,
        )
        
        assert result["batch_summary"]["batch_size"] == 50
    
    @pytest.mark.asyncio
    async def test_message_draft_single_recipient(
        self,
        tool_registry: MCPToolRegistry,
        context_t1: ExecutionContext,
        permission_checker: PermissionChecker,
        mock_audit_logger: AuditLogger,
    ):
        """Test message draft with single recipient (minimum)."""
        register_message_docs_draft_create_tool(tool_registry)
        
        result = await execute_tool(
            tool_id="docs.cluster.message.draft.create",
            input_data={
                "message_type": "notification",
                "recipient_ids": ["user-1"],  # Minimum 1 recipient
                "subject": "Test",
                "body": "Test",
            },
            context=context_t1,
            registry=tool_registry,
            permission_checker=permission_checker,
            audit_logger=mock_audit_logger,
        )
        
        assert result["recipient_summary"]["count"] == 1
    
    @pytest.mark.asyncio
    async def test_portal_config_empty_sections(
        self,
        tool_registry: MCPToolRegistry,
        context_t1: ExecutionContext,
        permission_checker: PermissionChecker,
        mock_audit_logger: AuditLogger,
    ):
        """Test portal config draft with empty config sections."""
        register_portal_config_draft_create_tool(tool_registry)
        context_t1.user_role = "admin"
        
        result = await execute_tool(
            tool_id="portal.cluster.config.draft.create",
            input_data={
                "portal_id": "portal-001",
                "config_sections": {},  # Empty dict
            },
            context=context_t1,
            registry=tool_registry,
            permission_checker=permission_checker,
            audit_logger=mock_audit_logger,
        )
        
        assert result["config_summary"]["section_count"] == 0
        assert len(result["config_summary"]["config_sections"]) == 0

