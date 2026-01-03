"""
Large Payload Tests for Cluster MCPs.

Tests validate:
- Maximum payload sizes
- Boundary conditions
- Performance with large payloads
- Memory efficiency
"""

import pytest
from lynx.core.registry import MCPToolRegistry, execute_tool
from lynx.core.session import ExecutionContext
from lynx.core.permissions import PermissionChecker
from lynx.core.audit import AuditLogger

# Import Cluster MCP registration functions
from lynx.mcp.cluster.docs.batch_draft_create import register_batch_docs_draft_create_tool
from lynx.mcp.cluster.docs.message_draft_create import register_message_docs_draft_create_tool
from lynx.mcp.cluster.workflow.digital_draft_create import register_digital_workflow_draft_create_tool
from lynx.mcp.cluster.portal.scaffold_draft_create import register_portal_scaffold_draft_create_tool


class TestBatchDraftLargePayloads:
    """Test batch draft creation with large payloads."""
    
    @pytest.mark.asyncio
    async def test_batch_draft_maximum_items(
        self,
        tool_registry: MCPToolRegistry,
        context_t1: ExecutionContext,
        permission_checker: PermissionChecker,
        mock_audit_logger: AuditLogger,
    ):
        """Test batch draft with maximum allowed items (50)."""
        register_batch_docs_draft_create_tool(tool_registry)
        
        # Create batch with 50 items (max allowed)
        requests = [{"doc_type": "SRS", "title": f"Document {i}"} for i in range(50)]
        
        result = await execute_tool(
            tool_id="docs.cluster.batch.draft.create",
            input_data={
                "batch_name": "Maximum Batch",
                "requests": requests,
            },
            context=context_t1,
            registry=tool_registry,
            permission_checker=permission_checker,
            audit_logger=mock_audit_logger,
        )
        
        assert result["status"] == "draft"
        assert result["batch_summary"]["batch_size"] == 50
        assert len(result["batch_summary"]["doc_type_counts"]) > 0
    
    @pytest.mark.asyncio
    async def test_batch_draft_large_titles(
        self,
        tool_registry: MCPToolRegistry,
        context_t1: ExecutionContext,
        permission_checker: PermissionChecker,
        mock_audit_logger: AuditLogger,
    ):
        """Test batch draft with large title strings."""
        register_batch_docs_draft_create_tool(tool_registry)
        
        # Create batch with very long titles
        long_title = "A" * 500  # 500 character title
        requests = [
            {"doc_type": "SRS", "title": long_title},
            {"doc_type": "ADR", "title": long_title},
        ]
        
        result = await execute_tool(
            tool_id="docs.cluster.batch.draft.create",
            input_data={
                "batch_name": "Large Titles Batch",
                "requests": requests,
            },
            context=context_t1,
            registry=tool_registry,
            permission_checker=permission_checker,
            audit_logger=mock_audit_logger,
        )
        
        assert result["status"] == "draft"
        assert result["batch_summary"]["batch_size"] == 2
        # Verify long titles are in preview
        assert long_title in result["preview_markdown"]


class TestMessageDraftLargePayloads:
    """Test message draft creation with large payloads."""
    
    @pytest.mark.asyncio
    async def test_message_draft_maximum_recipients(
        self,
        tool_registry: MCPToolRegistry,
        context_t1: ExecutionContext,
        permission_checker: PermissionChecker,
        mock_audit_logger: AuditLogger,
    ):
        """Test message draft with maximum allowed recipients (100)."""
        register_message_docs_draft_create_tool(tool_registry)
        
        # Create message with 100 recipients (max allowed)
        recipient_ids = [f"user-{i}" for i in range(100)]
        
        result = await execute_tool(
            tool_id="docs.cluster.message.draft.create",
            input_data={
                "message_type": "notification",
                "recipient_ids": recipient_ids,
                "subject": "Large Recipient List",
                "body": "Test body",
            },
            context=context_t1,
            registry=tool_registry,
            permission_checker=permission_checker,
            audit_logger=mock_audit_logger,
        )
        
        assert result["status"] == "draft"
        assert result["recipient_summary"]["count"] == 100
    
    @pytest.mark.asyncio
    async def test_message_draft_large_body(
        self,
        tool_registry: MCPToolRegistry,
        context_t1: ExecutionContext,
        permission_checker: PermissionChecker,
        mock_audit_logger: AuditLogger,
    ):
        """Test message draft with very large body text."""
        register_message_docs_draft_create_tool(tool_registry)
        
        # Create message with very long body
        large_body = "Test body content. " * 1000  # ~20KB body
        
        result = await execute_tool(
            tool_id="docs.cluster.message.draft.create",
            input_data={
                "message_type": "notification",
                "recipient_ids": ["user-1"],
                "subject": "Large Body Test",
                "body": large_body,
            },
            context=context_t1,
            registry=tool_registry,
            permission_checker=permission_checker,
            audit_logger=mock_audit_logger,
        )
        
        assert result["status"] == "draft"
        # Verify large body is in preview
        assert large_body[:100] in result["preview_markdown"]


class TestDigitalWorkflowLargePayloads:
    """Test digital workflow draft creation with large payloads."""
    
    @pytest.mark.asyncio
    async def test_digital_workflow_many_steps(
        self,
        tool_registry: MCPToolRegistry,
        context_t1: ExecutionContext,
        permission_checker: PermissionChecker,
        mock_audit_logger: AuditLogger,
    ):
        """Test digital workflow draft with many steps."""
        register_digital_workflow_draft_create_tool(tool_registry)
        context_t1.user_role = "admin"
        
        # Create workflow with 50 steps
        steps = [
            {
                "step_id": f"step-{i}",
                "name": f"Step {i}",
                "step_type": "automation",
                "automation_type": "api_call",
            }
            for i in range(50)
        ]
        
        result = await execute_tool(
            tool_id="workflow.cluster.digital.draft.create",
            input_data={
                "workflow_name": "Large Workflow",
                "workflow_description": "Test workflow with many steps",
                "trigger_type": "event",
                "steps": steps,
            },
            context=context_t1,
            registry=tool_registry,
            permission_checker=permission_checker,
            audit_logger=mock_audit_logger,
        )
        
        assert result["status"] == "draft"
        assert result["automation_summary"]["step_count"] == 50


class TestPortalScaffoldLargePayloads:
    """Test portal scaffold draft creation with large payloads."""
    
    @pytest.mark.asyncio
    async def test_portal_scaffold_many_modules(
        self,
        tool_registry: MCPToolRegistry,
        context_t1: ExecutionContext,
        permission_checker: PermissionChecker,
        mock_audit_logger: AuditLogger,
    ):
        """Test portal scaffold draft with many modules."""
        register_portal_scaffold_draft_create_tool(tool_registry)
        context_t1.user_role = "admin"
        
        # Create portal with 30 modules
        modules = [
            {
                "module_id": f"mod-{i}",
                "module_name": f"Module {i}",
                "module_type": "dashboard",
            }
            for i in range(30)
        ]
        
        result = await execute_tool(
            tool_id="portal.cluster.scaffold.draft.create",
            input_data={
                "portal_name": "Large Portal",
                "portal_description": "Test portal with many modules",
                "portal_type": "internal",
                "modules": modules,
            },
            context=context_t1,
            registry=tool_registry,
            permission_checker=permission_checker,
            audit_logger=mock_audit_logger,
        )
        
        assert result["status"] == "draft"
        assert result["scaffold_summary"]["module_count"] == 30

