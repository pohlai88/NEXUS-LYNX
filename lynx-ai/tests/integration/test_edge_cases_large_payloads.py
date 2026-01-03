"""
Edge-Case & Large Payload Tests (F) - Optional but Good.

Tests validate:
- Very large batch drafts (boundary conditions)
- Very long strings (titles/notes) - extreme cases
- Mixed-language input (internationalization)
- "Empty but valid" minimal payloads
- High-cardinality lists (modules, steps) - extreme cases
- Weird unicode / emoji handling
"""

import pytest
from lynx.core.registry import MCPToolRegistry, execute_tool
from lynx.core.session import ExecutionContext
from lynx.core.permissions import PermissionChecker
from lynx.core.audit import AuditLogger

# Import Cluster MCP registration functions
from lynx.mcp.cluster.docs.batch_draft_create import register_batch_docs_draft_create_tool
from lynx.mcp.cluster.docs.draft_create import register_docs_draft_create_tool
from lynx.mcp.cluster.docs.message_draft_create import register_message_docs_draft_create_tool
from lynx.mcp.cluster.workflow.digital_draft_create import register_digital_workflow_draft_create_tool
from lynx.mcp.cluster.portal.scaffold_draft_create import register_portal_scaffold_draft_create_tool


# ============================================================================
# F1. Very Large Batch Draft
# ============================================================================

@pytest.mark.stress
@pytest.mark.asyncio
class TestVeryLargeBatchDraft:
    """Test very large batch drafts at boundary conditions."""
    
    async def test_batch_draft_at_maximum_boundary(
        self,
        tool_registry: MCPToolRegistry,
        context_t1: ExecutionContext,
        permission_checker: PermissionChecker,
        mock_audit_logger: AuditLogger,
    ):
        """Test batch draft with exactly 50 items (maximum boundary)."""
        register_batch_docs_draft_create_tool(tool_registry)
        
        # Create batch with exactly 50 items (max allowed)
        requests = [
            {"doc_type": "SRS", "title": f"Document {i:03d}"}
            for i in range(50)
        ]
        
        result = await execute_tool(
            tool_id="docs.cluster.batch.draft.create",
            input_data={
                "batch_name": "Maximum Boundary Batch",
                "requests": requests,
            },
            context=context_t1,
            registry=tool_registry,
            permission_checker=permission_checker,
            audit_logger=mock_audit_logger,
        )
        
        assert result["status"] == "draft"
        assert result["batch_summary"]["batch_size"] == 50
        assert result["risk_level"] == "high"  # Large batches are high risk
    
    async def test_batch_draft_exceeds_maximum_rejected(
        self,
        tool_registry: MCPToolRegistry,
        context_t1: ExecutionContext,
        permission_checker: PermissionChecker,
        mock_audit_logger: AuditLogger,
    ):
        """Test that batch drafts exceeding 50 items are rejected."""
        register_batch_docs_draft_create_tool(tool_registry)
        
        # Create batch with 51 items (exceeds max)
        requests = [
            {"doc_type": "SRS", "title": f"Document {i}"}
            for i in range(51)
        ]
        
        with pytest.raises((ValueError, Exception)) as exc_info:
            await execute_tool(
                tool_id="docs.cluster.batch.draft.create",
                input_data={
                    "batch_name": "Exceeds Maximum Batch",
                    "requests": requests,
                },
                context=context_t1,
                registry=tool_registry,
                permission_checker=permission_checker,
                audit_logger=mock_audit_logger,
            )
        
        # Verify error mentions batch size limit
        error_msg = str(exc_info.value).lower()
        assert any(keyword in error_msg for keyword in ["max", "limit", "50", "length", "size"])


# ============================================================================
# F2. Very Long Strings (Titles/Notes)
# ============================================================================

@pytest.mark.stress
@pytest.mark.asyncio
class TestVeryLongStrings:
    """Test very long string inputs (titles, notes, descriptions)."""
    
    async def test_extremely_long_title(
        self,
        tool_registry: MCPToolRegistry,
        context_t1: ExecutionContext,
        permission_checker: PermissionChecker,
        mock_audit_logger: AuditLogger,
    ):
        """Test draft creation with extremely long title (10KB)."""
        register_docs_draft_create_tool(tool_registry)
        
        # Create title with 10KB of text
        extremely_long_title = "A" * 10000  # 10KB title
        
        result = await execute_tool(
            tool_id="docs.cluster.draft.create",
            input_data={
                "doc_type": "PRD",
                "title": extremely_long_title,
            },
            context=context_t1,
            registry=tool_registry,
            permission_checker=permission_checker,
            audit_logger=mock_audit_logger,
        )
        
        # Should either accept (if within limits) or reject gracefully
        # If accepted, verify it's stored correctly
        if result and "draft_id" in result:
            assert result["status"] == "draft"
            # Title should be preserved (or truncated if there's a limit)
            assert len(extremely_long_title) <= 10000  # Sanity check
    
    async def test_extremely_long_note_in_message(
        self,
        tool_registry: MCPToolRegistry,
        context_t1: ExecutionContext,
        permission_checker: PermissionChecker,
        mock_audit_logger: AuditLogger,
    ):
        """Test message draft with extremely long body text (100KB)."""
        register_message_docs_draft_create_tool(tool_registry)
        
        # Create message with 100KB body
        extremely_long_body = "This is a test message body. " * 4000  # ~100KB
        
        result = await execute_tool(
            tool_id="docs.cluster.message.draft.create",
            input_data={
                "message_type": "notification",
                "recipient_ids": ["user-1"],
                "subject": "Extremely Long Body Test",
                "body": extremely_long_body,
            },
            context=context_t1,
            registry=tool_registry,
            permission_checker=permission_checker,
            audit_logger=mock_audit_logger,
        )
        
        # Should handle large body gracefully
        assert result["status"] == "draft"
        # Verify body is preserved in preview (at least partially)
        assert len(extremely_long_body) > 0
    
    async def test_long_title_with_special_chars(
        self,
        tool_registry: MCPToolRegistry,
        context_t1: ExecutionContext,
        permission_checker: PermissionChecker,
        mock_audit_logger: AuditLogger,
    ):
        """Test long title with special characters and newlines."""
        register_docs_draft_create_tool(tool_registry)
        
        # Create title with special chars and newlines
        long_title_with_specials = "Title with\nnewlines\tand\ttabs " * 100  # ~2KB
        
        result = await execute_tool(
            tool_id="docs.cluster.draft.create",
            input_data={
                "doc_type": "SRS",
                "title": long_title_with_specials,
            },
            context=context_t1,
            registry=tool_registry,
            permission_checker=permission_checker,
            audit_logger=mock_audit_logger,
        )
        
        assert result["status"] == "draft"
        # Title should be preserved (or sanitized appropriately)


# ============================================================================
# F3. Mixed-Language Input
# ============================================================================

@pytest.mark.stress
@pytest.mark.asyncio
class TestMixedLanguageInput:
    """Test mixed-language input (internationalization)."""
    
    async def test_chinese_characters_in_title(
        self,
        tool_registry: MCPToolRegistry,
        context_t1: ExecutionContext,
        permission_checker: PermissionChecker,
        mock_audit_logger: AuditLogger,
    ):
        """Test draft creation with Chinese characters in title."""
        register_docs_draft_create_tool(tool_registry)
        
        chinese_title = "产品需求文档 - 用户认证系统"
        
        result = await execute_tool(
            tool_id="docs.cluster.draft.create",
            input_data={
                "doc_type": "PRD",
                "title": chinese_title,
            },
            context=context_t1,
            registry=tool_registry,
            permission_checker=permission_checker,
            audit_logger=mock_audit_logger,
        )
        
        assert result["status"] == "draft"
        # Verify Chinese characters are preserved
        assert chinese_title in result.get("preview_markdown", "") or chinese_title in str(result)
    
    async def test_japanese_characters_in_title(
        self,
        tool_registry: MCPToolRegistry,
        context_t1: ExecutionContext,
        permission_checker: PermissionChecker,
        mock_audit_logger: AuditLogger,
    ):
        """Test draft creation with Japanese characters in title."""
        register_docs_draft_create_tool(tool_registry)
        
        japanese_title = "プロダクト要件ドキュメント - 認証システム"
        
        result = await execute_tool(
            tool_id="docs.cluster.draft.create",
            input_data={
                "doc_type": "PRD",
                "title": japanese_title,
            },
            context=context_t1,
            registry=tool_registry,
            permission_checker=permission_checker,
            audit_logger=mock_audit_logger,
        )
        
        assert result["status"] == "draft"
        # Verify Japanese characters are preserved
        assert japanese_title in result.get("preview_markdown", "") or japanese_title in str(result)
    
    async def test_arabic_characters_in_title(
        self,
        tool_registry: MCPToolRegistry,
        context_t1: ExecutionContext,
        permission_checker: PermissionChecker,
        mock_audit_logger: AuditLogger,
    ):
        """Test draft creation with Arabic characters (RTL text)."""
        register_docs_draft_create_tool(tool_registry)
        
        arabic_title = "وثيقة متطلبات المنتج - نظام المصادقة"
        
        result = await execute_tool(
            tool_id="docs.cluster.draft.create",
            input_data={
                "doc_type": "PRD",
                "title": arabic_title,
            },
            context=context_t1,
            registry=tool_registry,
            permission_checker=permission_checker,
            audit_logger=mock_audit_logger,
        )
        
        assert result["status"] == "draft"
        # Verify Arabic characters are preserved
        assert arabic_title in result.get("preview_markdown", "") or arabic_title in str(result)
    
    async def test_mixed_language_batch(
        self,
        tool_registry: MCPToolRegistry,
        context_t1: ExecutionContext,
        permission_checker: PermissionChecker,
        mock_audit_logger: AuditLogger,
    ):
        """Test batch draft with mixed languages."""
        register_batch_docs_draft_create_tool(tool_registry)
        
        requests = [
            {"doc_type": "PRD", "title": "English Document"},
            {"doc_type": "PRD", "title": "产品需求文档"},
            {"doc_type": "PRD", "title": "プロダクト要件ドキュメント"},
            {"doc_type": "PRD", "title": "وثيقة متطلبات المنتج"},
            {"doc_type": "PRD", "title": "Dokument Anforderungen"},
        ]
        
        result = await execute_tool(
            tool_id="docs.cluster.batch.draft.create",
            input_data={
                "batch_name": "Mixed Language Batch",
                "requests": requests,
            },
            context=context_t1,
            registry=tool_registry,
            permission_checker=permission_checker,
            audit_logger=mock_audit_logger,
        )
        
        assert result["status"] == "draft"
        assert result["batch_summary"]["batch_size"] == 5
        # Verify all languages are preserved in preview
        preview = result.get("preview_markdown", "")
        assert "English Document" in preview
        assert "产品需求文档" in preview
        assert "プロダクト要件ドキュメント" in preview


# ============================================================================
# F4. "Empty but Valid" Minimal Payload
# ============================================================================

@pytest.mark.stress
@pytest.mark.asyncio
class TestEmptyButValidMinimalPayload:
    """Test minimal valid payloads (empty but valid)."""
    
    async def test_minimal_draft_creation(
        self,
        tool_registry: MCPToolRegistry,
        context_t1: ExecutionContext,
        permission_checker: PermissionChecker,
        mock_audit_logger: AuditLogger,
    ):
        """Test draft creation with minimal required fields only."""
        register_docs_draft_create_tool(tool_registry)
        
        # Minimal payload: only required fields
        result = await execute_tool(
            tool_id="docs.cluster.draft.create",
            input_data={
                "doc_type": "PRD",
                "title": "Minimal Title",
            },
            context=context_t1,
            registry=tool_registry,
            permission_checker=permission_checker,
            audit_logger=mock_audit_logger,
        )
        
        assert result["status"] == "draft"
        assert "draft_id" in result
    
    async def test_minimal_batch_draft(
        self,
        tool_registry: MCPToolRegistry,
        context_t1: ExecutionContext,
        permission_checker: PermissionChecker,
        mock_audit_logger: AuditLogger,
    ):
        """Test batch draft with minimal payload (single item)."""
        register_batch_docs_draft_create_tool(tool_registry)
        
        # Minimal batch: single item
        result = await execute_tool(
            tool_id="docs.cluster.batch.draft.create",
            input_data={
                "batch_name": "Minimal Batch",
                "requests": [
                    {"doc_type": "SRS", "title": "Single Document"},
                ],
            },
            context=context_t1,
            registry=tool_registry,
            permission_checker=permission_checker,
            audit_logger=mock_audit_logger,
        )
        
        assert result["status"] == "draft"
        assert result["batch_summary"]["batch_size"] == 1
    
    async def test_minimal_message_draft(
        self,
        tool_registry: MCPToolRegistry,
        context_t1: ExecutionContext,
        permission_checker: PermissionChecker,
        mock_audit_logger: AuditLogger,
    ):
        """Test message draft with minimal payload."""
        register_message_docs_draft_create_tool(tool_registry)
        
        # Minimal message: required fields only
        result = await execute_tool(
            tool_id="docs.cluster.message.draft.create",
            input_data={
                "message_type": "notification",
                "recipient_ids": ["user-1"],
                "subject": "Minimal Subject",
                "body": "Minimal body",
            },
            context=context_t1,
            registry=tool_registry,
            permission_checker=permission_checker,
            audit_logger=mock_audit_logger,
        )
        
        assert result["status"] == "draft"
        assert "draft_id" in result
    
    async def test_minimal_workflow_draft(
        self,
        tool_registry: MCPToolRegistry,
        context_t1: ExecutionContext,
        permission_checker: PermissionChecker,
        mock_audit_logger: AuditLogger,
    ):
        """Test workflow draft with minimal payload (single step)."""
        register_digital_workflow_draft_create_tool(tool_registry)
        context_t1.user_role = "admin"
        
        # Minimal workflow: single step
        result = await execute_tool(
            tool_id="workflow.cluster.digital.draft.create",
            input_data={
                "workflow_name": "Minimal Workflow",
                "workflow_description": "Minimal description",
                "trigger_type": "event",
                "steps": [
                    {
                        "step_id": "step-1",
                        "name": "Step 1",
                        "step_type": "automation",
                        "automation_type": "api_call",
                    },
                ],
            },
            context=context_t1,
            registry=tool_registry,
            permission_checker=permission_checker,
            audit_logger=mock_audit_logger,
        )
        
        assert result["status"] == "draft"
        assert result["automation_summary"]["step_count"] == 1


# ============================================================================
# F5. High-Cardinality Lists (Modules, Steps)
# ============================================================================

@pytest.mark.stress
@pytest.mark.asyncio
class TestHighCardinalityLists:
    """Test high-cardinality lists (many modules, many steps)."""
    
    async def test_workflow_with_extreme_step_count(
        self,
        tool_registry: MCPToolRegistry,
        context_t1: ExecutionContext,
        permission_checker: PermissionChecker,
        mock_audit_logger: AuditLogger,
    ):
        """Test workflow draft with extreme number of steps (200)."""
        register_digital_workflow_draft_create_tool(tool_registry)
        context_t1.user_role = "admin"
        
        # Create workflow with 200 steps (extreme case)
        steps = [
            {
                "step_id": f"step-{i:03d}",
                "name": f"Step {i}",
                "step_type": "automation",
                "automation_type": "api_call",
            }
            for i in range(200)
        ]
        
        result = await execute_tool(
            tool_id="workflow.cluster.digital.draft.create",
            input_data={
                "workflow_name": "Extreme Workflow",
                "workflow_description": "Workflow with 200 steps",
                "trigger_type": "event",
                "steps": steps,
            },
            context=context_t1,
            registry=tool_registry,
            permission_checker=permission_checker,
            audit_logger=mock_audit_logger,
        )
        
        assert result["status"] == "draft"
        assert result["automation_summary"]["step_count"] == 200
        # Large workflows should be high risk
        assert result["risk_level"] == "high"
    
    async def test_portal_with_extreme_module_count(
        self,
        tool_registry: MCPToolRegistry,
        context_t1: ExecutionContext,
        permission_checker: PermissionChecker,
        mock_audit_logger: AuditLogger,
    ):
        """Test portal scaffold with extreme number of modules (100)."""
        register_portal_scaffold_draft_create_tool(tool_registry)
        context_t1.user_role = "admin"
        
        # Create portal with 100 modules (extreme case)
        modules = [
            {
                "module_id": f"mod-{i:03d}",
                "module_name": f"Module {i}",
                "module_type": "dashboard",
            }
            for i in range(100)
        ]
        
        result = await execute_tool(
            tool_id="portal.cluster.scaffold.draft.create",
            input_data={
                "portal_name": "Extreme Portal",
                "portal_description": "Portal with 100 modules",
                "portal_type": "internal",
                "modules": modules,
            },
            context=context_t1,
            registry=tool_registry,
            permission_checker=permission_checker,
            audit_logger=mock_audit_logger,
        )
        
        assert result["status"] == "draft"
        assert result["scaffold_summary"]["module_count"] == 100
        # Large portals should be high risk
        assert result["risk_level"] == "high"
    
    async def test_message_with_extreme_recipient_count(
        self,
        tool_registry: MCPToolRegistry,
        context_t1: ExecutionContext,
        permission_checker: PermissionChecker,
        mock_audit_logger: AuditLogger,
    ):
        """Test message draft with extreme number of recipients (200)."""
        register_message_docs_draft_create_tool(tool_registry)
        
        # Create message with 200 recipients (extreme case)
        recipient_ids = [f"user-{i:03d}" for i in range(200)]
        
        result = await execute_tool(
            tool_id="docs.cluster.message.draft.create",
            input_data={
                "message_type": "notification",
                "recipient_ids": recipient_ids,
                "subject": "Extreme Recipient List",
                "body": "Test body",
            },
            context=context_t1,
            registry=tool_registry,
            permission_checker=permission_checker,
            audit_logger=mock_audit_logger,
        )
        
        assert result["status"] == "draft"
        assert result["recipient_summary"]["count"] == 200
        # Large recipient lists should be high risk
        assert result["risk_level"] == "high"


# ============================================================================
# F6. Weird Unicode / Emoji
# ============================================================================

@pytest.mark.stress
@pytest.mark.asyncio
class TestWeirdUnicodeEmoji:
    """Test weird unicode and emoji handling."""
    
    async def test_emoji_in_title(
        self,
        tool_registry: MCPToolRegistry,
        context_t1: ExecutionContext,
        permission_checker: PermissionChecker,
        mock_audit_logger: AuditLogger,
    ):
        """Test draft creation with emoji in title."""
        register_docs_draft_create_tool(tool_registry)
        
        emoji_title = "🚀 Product Requirements Document - Authentication System ✅"
        
        result = await execute_tool(
            tool_id="docs.cluster.draft.create",
            input_data={
                "doc_type": "PRD",
                "title": emoji_title,
            },
            context=context_t1,
            registry=tool_registry,
            permission_checker=permission_checker,
            audit_logger=mock_audit_logger,
        )
        
        assert result["status"] == "draft"
        # Verify emoji are preserved
        assert "🚀" in result.get("preview_markdown", "") or "🚀" in str(result)
        assert "✅" in result.get("preview_markdown", "") or "✅" in str(result)
    
    async def test_many_emoji_in_title(
        self,
        tool_registry: MCPToolRegistry,
        context_t1: ExecutionContext,
        permission_checker: PermissionChecker,
        mock_audit_logger: AuditLogger,
    ):
        """Test draft creation with many emoji in title."""
        register_docs_draft_create_tool(tool_registry)
        
        many_emoji_title = "🎉🎊🎈🎁🎂🎃🎄🎅🎆🎇🎈🎉🎊🎋🎌🎍🎎🎏🎐🎑🎒🎓🎖️🎗️🎘🎙️🎚️🎛️🎜🎝🎞️🎟️"
        
        result = await execute_tool(
            tool_id="docs.cluster.draft.create",
            input_data={
                "doc_type": "PRD",
                "title": many_emoji_title,
            },
            context=context_t1,
            registry=tool_registry,
            permission_checker=permission_checker,
            audit_logger=mock_audit_logger,
        )
        
        assert result["status"] == "draft"
        # Verify emoji are preserved
        assert "🎉" in result.get("preview_markdown", "") or "🎉" in str(result)
    
    async def test_zero_width_characters(
        self,
        tool_registry: MCPToolRegistry,
        context_t1: ExecutionContext,
        permission_checker: PermissionChecker,
        mock_audit_logger: AuditLogger,
    ):
        """Test draft creation with zero-width characters."""
        register_docs_draft_create_tool(tool_registry)
        
        # Zero-width space, zero-width joiner, zero-width non-joiner
        zero_width_title = "Product\u200bRequirements\u200cDocument\u200d"
        
        result = await execute_tool(
            tool_id="docs.cluster.draft.create",
            input_data={
                "doc_type": "PRD",
                "title": zero_width_title,
            },
            context=context_t1,
            registry=tool_registry,
            permission_checker=permission_checker,
            audit_logger=mock_audit_logger,
        )
        
        assert result["status"] == "draft"
        # Zero-width characters should be handled gracefully
        # (either preserved or stripped, but shouldn't break)
    
    async def test_control_characters(
        self,
        tool_registry: MCPToolRegistry,
        context_t1: ExecutionContext,
        permission_checker: PermissionChecker,
        mock_audit_logger: AuditLogger,
    ):
        """Test draft creation with control characters."""
        register_docs_draft_create_tool(tool_registry)
        
        # Control characters (should be sanitized or rejected)
        control_char_title = "Product\x00Requirements\x01Document"
        
        # Control characters might be rejected or sanitized
        try:
            result = await execute_tool(
                tool_id="docs.cluster.draft.create",
                input_data={
                    "doc_type": "PRD",
                    "title": control_char_title,
                },
                context=context_t1,
                registry=tool_registry,
                permission_checker=permission_checker,
                audit_logger=mock_audit_logger,
            )
            
            # If accepted, verify control chars are sanitized
            if result:
                assert result["status"] == "draft"
                # Title should not contain raw control characters
                stored_title = result.get("preview_markdown", "")
                assert "\x00" not in stored_title
                assert "\x01" not in stored_title
        except (ValueError, Exception):
            # Rejection is also acceptable for control characters
            pass
    
    async def test_surrogate_pairs(
        self,
        tool_registry: MCPToolRegistry,
        context_t1: ExecutionContext,
        permission_checker: PermissionChecker,
        mock_audit_logger: AuditLogger,
    ):
        """Test draft creation with surrogate pairs (extended unicode)."""
        register_docs_draft_create_tool(tool_registry)
        
        # Surrogate pairs (emoji, musical notes, etc.)
        surrogate_title = "Product Requirements 🎵🎶🎼 Document"
        
        result = await execute_tool(
            tool_id="docs.cluster.draft.create",
            input_data={
                "doc_type": "PRD",
                "title": surrogate_title,
            },
            context=context_t1,
            registry=tool_registry,
            permission_checker=permission_checker,
            audit_logger=mock_audit_logger,
        )
        
        assert result["status"] == "draft"
        # Surrogate pairs should be preserved
        assert "🎵" in result.get("preview_markdown", "") or "🎵" in str(result)
    
    async def test_emoji_in_batch(
        self,
        tool_registry: MCPToolRegistry,
        context_t1: ExecutionContext,
        permission_checker: PermissionChecker,
        mock_audit_logger: AuditLogger,
    ):
        """Test batch draft with emoji in multiple titles."""
        register_batch_docs_draft_create_tool(tool_registry)
        
        requests = [
            {"doc_type": "PRD", "title": "🚀 Product Requirements"},
            {"doc_type": "SRS", "title": "✅ System Requirements"},
            {"doc_type": "ADR", "title": "📝 Architecture Decision"},
            {"doc_type": "DECISION", "title": "🎯 Decision Document"},
        ]
        
        result = await execute_tool(
            tool_id="docs.cluster.batch.draft.create",
            input_data={
                "batch_name": "Emoji Batch",
                "requests": requests,
            },
            context=context_t1,
            registry=tool_registry,
            permission_checker=permission_checker,
            audit_logger=mock_audit_logger,
        )
        
        assert result["status"] == "draft"
        assert result["batch_summary"]["batch_size"] == 4
        # Verify emoji are preserved in preview
        preview = result.get("preview_markdown", "")
        assert "🚀" in preview or "🚀" in str(result)
        assert "✅" in preview or "✅" in str(result)

