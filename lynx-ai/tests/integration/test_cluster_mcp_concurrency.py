"""
Concurrency Tests for Cluster MCPs.

Tests validate:
- Concurrent draft creation
- Thread safety
- No race conditions
- Idempotency under concurrency
"""

import pytest
import asyncio
from lynx.core.registry import MCPToolRegistry, execute_tool
from lynx.core.session import ExecutionContext
from lynx.core.permissions import PermissionChecker
from lynx.core.audit import AuditLogger

# Import Cluster MCP registration functions
from lynx.mcp.cluster.docs.draft_create import register_docs_draft_create_tool
from lynx.mcp.cluster.docs.batch_draft_create import register_batch_docs_draft_create_tool
from lynx.mcp.cluster.docs.message_draft_create import register_message_docs_draft_create_tool
from lynx.mcp.cluster.workflow.draft_create import register_workflow_draft_create_tool
from lynx.mcp.cluster.vpm.payment_draft_create import register_vpm_payment_draft_create_tool


class TestConcurrentDraftCreation:
    """Test concurrent draft creation for Cluster MCPs."""
    
    @pytest.mark.asyncio
    async def test_concurrent_docs_draft_creation(
        self,
        tool_registry: MCPToolRegistry,
        context_t1: ExecutionContext,
        permission_checker: PermissionChecker,
        mock_audit_logger: AuditLogger,
    ):
        """Test concurrent document draft creation."""
        register_docs_draft_create_tool(tool_registry)
        
        async def create_draft(index: int):
            return await execute_tool(
                tool_id="docs.cluster.draft.create",
                input_data={
                    "doc_type": "SRS",
                    "title": f"Concurrent Test {index}",
                },
                context=context_t1,
                registry=tool_registry,
                permission_checker=permission_checker,
                audit_logger=mock_audit_logger,
            )
        
        # Create 10 drafts concurrently
        results = await asyncio.gather(*[create_draft(i) for i in range(10)])
        
        # Verify all succeeded
        assert len(results) == 10
        for result in results:
            assert result is not None
            assert result["status"] == "draft"
            assert "draft_id" in result
            assert result["tenant_id"] == context_t1.tenant_id
        
        # Verify all draft IDs are unique
        draft_ids = [r["draft_id"] for r in results]
        assert len(draft_ids) == len(set(draft_ids)), "Duplicate draft IDs found"
    
    @pytest.mark.asyncio
    async def test_concurrent_batch_draft_creation(
        self,
        tool_registry: MCPToolRegistry,
        context_t1: ExecutionContext,
        permission_checker: PermissionChecker,
        mock_audit_logger: AuditLogger,
    ):
        """Test concurrent batch draft creation."""
        register_batch_docs_draft_create_tool(tool_registry)
        
        async def create_batch(index: int):
            return await execute_tool(
                tool_id="docs.cluster.batch.draft.create",
                input_data={
                    "batch_name": f"Batch {index}",
                    "requests": [
                        {"doc_type": "SRS", "title": f"Doc {index}-1"},
                        {"doc_type": "ADR", "title": f"Doc {index}-2"},
                    ],
                },
                context=context_t1,
                registry=tool_registry,
                permission_checker=permission_checker,
                audit_logger=mock_audit_logger,
            )
        
        # Create 5 batches concurrently
        results = await asyncio.gather(*[create_batch(i) for i in range(5)])
        
        # Verify all succeeded
        assert len(results) == 5
        for result in results:
            assert result is not None
            assert result["status"] == "draft"
            assert "draft_id" in result
            assert result["batch_summary"]["batch_size"] == 2
    
    @pytest.mark.asyncio
    async def test_concurrent_message_draft_creation(
        self,
        tool_registry: MCPToolRegistry,
        context_t1: ExecutionContext,
        permission_checker: PermissionChecker,
        mock_audit_logger: AuditLogger,
    ):
        """Test concurrent message draft creation."""
        register_message_docs_draft_create_tool(tool_registry)
        
        async def create_message(index: int):
            return await execute_tool(
                tool_id="docs.cluster.message.draft.create",
                input_data={
                    "message_type": "notification",
                    "recipient_ids": [f"user-{index}"],
                    "subject": f"Message {index}",
                    "body": f"Body {index}",
                },
                context=context_t1,
                registry=tool_registry,
                permission_checker=permission_checker,
                audit_logger=mock_audit_logger,
            )
        
        # Create 8 messages concurrently
        results = await asyncio.gather(*[create_message(i) for i in range(8)])
        
        # Verify all succeeded
        assert len(results) == 8
        for result in results:
            assert result is not None
            assert result["status"] == "draft"
            assert "draft_id" in result
            assert result["recipient_summary"]["count"] == 1


class TestConcurrentIdempotency:
    """Test idempotency under concurrency."""
    
    @pytest.mark.asyncio
    async def test_concurrent_idempotent_docs_draft(
        self,
        tool_registry: MCPToolRegistry,
        context_t1: ExecutionContext,
        permission_checker: PermissionChecker,
        mock_audit_logger: AuditLogger,
    ):
        """Test that concurrent requests with same request_id return same draft_id."""
        register_docs_draft_create_tool(tool_registry)
        
        request_id = "concurrent-request-123"
        
        async def create_draft():
            return await execute_tool(
                tool_id="docs.cluster.draft.create",
                input_data={
                    "doc_type": "SRS",
                    "title": "Concurrent Idempotent Test",
                    "request_id": request_id,
                },
                context=context_t1,
                registry=tool_registry,
                permission_checker=permission_checker,
                audit_logger=mock_audit_logger,
            )
        
        # Create 5 concurrent requests with same request_id
        results = await asyncio.gather(*[create_draft() for _ in range(5)])
        
        # Verify all returned same draft_id
        draft_ids = [r["draft_id"] for r in results]
        assert len(set(draft_ids)) == 1, f"Expected same draft_id, got: {draft_ids}"
    
    @pytest.mark.asyncio
    async def test_concurrent_idempotent_batch_draft(
        self,
        tool_registry: MCPToolRegistry,
        context_t1: ExecutionContext,
        permission_checker: PermissionChecker,
        mock_audit_logger: AuditLogger,
    ):
        """Test that concurrent batch requests with same request_id return same draft_id."""
        register_batch_docs_draft_create_tool(tool_registry)
        
        request_id = "concurrent-batch-123"
        
        async def create_batch():
            return await execute_tool(
                tool_id="docs.cluster.batch.draft.create",
                input_data={
                    "batch_name": "Concurrent Batch",
                    "requests": [{"doc_type": "SRS", "title": "Test"}],
                    "request_id": request_id,
                },
                context=context_t1,
                registry=tool_registry,
                permission_checker=permission_checker,
                audit_logger=mock_audit_logger,
            )
        
        # Create 3 concurrent requests with same request_id
        results = await asyncio.gather(*[create_batch() for _ in range(3)])
        
        # Verify all returned same draft_id
        draft_ids = [r["draft_id"] for r in results]
        assert len(set(draft_ids)) == 1, f"Expected same draft_id, got: {draft_ids}"


class TestConcurrentMixedOperations:
    """Test concurrent mixed operations."""
    
    @pytest.mark.asyncio
    async def test_concurrent_mixed_cluster_mcps(
        self,
        tool_registry: MCPToolRegistry,
        context_t1: ExecutionContext,
        permission_checker: PermissionChecker,
        mock_audit_logger: AuditLogger,
    ):
        """Test concurrent operations across different Cluster MCPs."""
        register_docs_draft_create_tool(tool_registry)
        register_workflow_draft_create_tool(tool_registry)
        register_vpm_payment_draft_create_tool(tool_registry)
        
        async def create_docs_draft():
            return await execute_tool(
                tool_id="docs.cluster.draft.create",
                input_data={"doc_type": "SRS", "title": "Mixed Test"},
                context=context_t1,
                registry=tool_registry,
                permission_checker=permission_checker,
                audit_logger=mock_audit_logger,
            )
        
        async def create_workflow_draft():
            return await execute_tool(
                tool_id="workflow.cluster.draft.create",
                input_data={"workflow_kind": "approval", "name": "Mixed Test", "steps": []},
                context=context_t1,
                registry=tool_registry,
                permission_checker=permission_checker,
                audit_logger=mock_audit_logger,
            )
        
        async def create_payment_draft():
            return await execute_tool(
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
        
        # Run all three operations concurrently
        results = await asyncio.gather(
            create_docs_draft(),
            create_workflow_draft(),
            create_payment_draft(),
        )
        
        # Verify all succeeded
        assert len(results) == 3
        assert results[0]["status"] == "draft"
        assert results[1]["status"] == "draft"
        assert results[2]["status"] == "draft"
        
        # Verify all have unique draft IDs
        draft_ids = [r["draft_id"] for r in results]
        assert len(draft_ids) == len(set(draft_ids))

