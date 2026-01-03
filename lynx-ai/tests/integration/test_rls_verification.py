"""
RLS Verification Tests - Prove tenant isolation at database level.

These tests run against a REAL Supabase instance to verify:
1. RLS policies are correctly configured
2. Cross-tenant access is blocked
3. Tenant-scoped queries work correctly

Prerequisites:
- SUPABASE_URL and SUPABASE_KEY environment variables set
- Supabase schema applied (run supabase-migration.sql)
"""

import pytest
import os
from uuid import uuid4
from typing import Optional

from lynx.mcp.cluster.drafts.models import DraftProtocol, DraftStatus
from lynx.storage.draft_storage import DraftStorageSupabase, get_draft_storage
from lynx.mcp.cell.execution.models import ExecutionRecord, ExecutionStatus
from lynx.storage.execution_storage import ExecutionStorageSupabase, get_execution_storage
from lynx.storage.settlement_storage import SettlementIntentStorageSupabase, get_settlement_storage
from lynx.mcp.cell.vpm.payment_execute import SettlementIntent


# Skip all tests if Supabase credentials not set
pytestmark = pytest.mark.skipif(
    not os.getenv("SUPABASE_URL") or not os.getenv("SUPABASE_KEY"),
    reason="SUPABASE_URL and SUPABASE_KEY must be set for RLS verification tests"
)


@pytest.fixture
def tenant_a() -> str:
    """Tenant A ID for testing."""
    return f"test-tenant-a-{uuid4().hex[:8]}"


@pytest.fixture
def tenant_b() -> str:
    """Tenant B ID for testing."""
    return f"test-tenant-b-{uuid4().hex[:8]}"


@pytest.fixture
def draft_storage() -> DraftStorageSupabase:
    """Get Supabase draft storage."""
    storage = get_draft_storage()
    if not isinstance(storage, DraftStorageSupabase):
        pytest.skip("Supabase storage not configured (using in-memory)")
    return storage


@pytest.fixture
def execution_storage() -> ExecutionStorageSupabase:
    """Get Supabase execution storage."""
    storage = get_execution_storage()
    if not isinstance(storage, ExecutionStorageSupabase):
        pytest.skip("Supabase storage not configured (using in-memory)")
    return storage


@pytest.fixture
def settlement_storage() -> SettlementIntentStorageSupabase:
    """Get Supabase settlement intent storage."""
    storage = get_settlement_storage()
    if not isinstance(storage, SettlementIntentStorageSupabase):
        pytest.skip("Supabase storage not configured (using in-memory)")
    return storage


class TestRLSDraftIsolation:
    """Test RLS isolation for drafts."""
    
    @pytest.mark.asyncio
    async def test_draft_created_by_tenant_a_not_visible_to_tenant_b(
        self,
        draft_storage: DraftStorageSupabase,
        tenant_a: str,
        tenant_b: str,
    ):
        """Test that Tenant B cannot see drafts created by Tenant A."""
        # Create draft as Tenant A
        draft_a = DraftProtocol(
            draft_id=str(uuid4()),
            tenant_id=tenant_a,
            draft_type="docs",
            payload={"title": "Tenant A Document"},
            status=DraftStatus.DRAFT,
            risk_level="low",
            created_by="user-a",
            created_at="2023-01-01T12:00:00Z",
            source_context={},
            recommended_approvers=[],
        )
        
        created_draft = await draft_storage.create_draft(draft_a)
        assert created_draft.draft_id == draft_a.draft_id
        
        # Try to retrieve as Tenant B (should return None due to RLS)
        retrieved_by_b = await draft_storage.get_draft(created_draft.draft_id, tenant_b)
        assert retrieved_by_b is None, "Tenant B should not be able to access Tenant A's draft"
        
        # Verify Tenant A can still access it
        retrieved_by_a = await draft_storage.get_draft(created_draft.draft_id, tenant_a)
        assert retrieved_by_a is not None, "Tenant A should be able to access their own draft"
        assert retrieved_by_a.draft_id == created_draft.draft_id
    
    @pytest.mark.asyncio
    async def test_draft_list_respects_tenant_boundary(
        self,
        draft_storage: DraftStorageSupabase,
        tenant_a: str,
        tenant_b: str,
    ):
        """Test that list_drafts only returns drafts for the specified tenant."""
        # Create drafts for both tenants
        draft_a1 = DraftProtocol(
            draft_id=str(uuid4()),
            tenant_id=tenant_a,
            draft_type="docs",
            payload={"title": "Tenant A Doc 1"},
            status=DraftStatus.DRAFT,
            risk_level="low",
            created_by="user-a",
            created_at="2023-01-01T12:00:00Z",
            source_context={},
        )
        draft_a2 = DraftProtocol(
            draft_id=str(uuid4()),
            tenant_id=tenant_a,
            draft_type="docs",
            payload={"title": "Tenant A Doc 2"},
            status=DraftStatus.DRAFT,
            risk_level="low",
            created_by="user-a",
            created_at="2023-01-01T12:01:00Z",
            source_context={},
        )
        draft_b1 = DraftProtocol(
            draft_id=str(uuid4()),
            tenant_id=tenant_b,
            draft_type="docs",
            payload={"title": "Tenant B Doc 1"},
            status=DraftStatus.DRAFT,
            risk_level="low",
            created_by="user-b",
            created_at="2023-01-01T12:00:00Z",
            source_context={},
        )
        
        await draft_storage.create_draft(draft_a1)
        await draft_storage.create_draft(draft_a2)
        await draft_storage.create_draft(draft_b1)
        
        # List drafts for Tenant A (should only see Tenant A drafts)
        tenant_a_drafts = await draft_storage.list_drafts(tenant_a, limit=100)
        tenant_a_ids = {d.draft_id for d in tenant_a_drafts}
        
        assert draft_a1.draft_id in tenant_a_ids, "Tenant A should see draft_a1"
        assert draft_a2.draft_id in tenant_a_ids, "Tenant A should see draft_a2"
        assert draft_b1.draft_id not in tenant_a_ids, "Tenant A should NOT see Tenant B's draft"
        
        # List drafts for Tenant B (should only see Tenant B drafts)
        tenant_b_drafts = await draft_storage.list_drafts(tenant_b, limit=100)
        tenant_b_ids = {d.draft_id for d in tenant_b_drafts}
        
        assert draft_b1.draft_id in tenant_b_ids, "Tenant B should see draft_b1"
        assert draft_a1.draft_id not in tenant_b_ids, "Tenant B should NOT see Tenant A's draft"
        assert draft_a2.draft_id not in tenant_b_ids, "Tenant B should NOT see Tenant A's draft"


class TestRLSExecutionIsolation:
    """Test RLS isolation for executions."""
    
    @pytest.mark.asyncio
    async def test_execution_created_by_tenant_a_not_visible_to_tenant_b(
        self,
        execution_storage: ExecutionStorageSupabase,
        draft_storage: DraftStorageSupabase,
        tenant_a: str,
        tenant_b: str,
    ):
        """Test that Tenant B cannot see executions created by Tenant A."""
        # Create a draft for Tenant A first
        draft = DraftProtocol(
            draft_id=str(uuid4()),
            tenant_id=tenant_a,
            draft_type="docs",
            payload={"title": "Test Draft"},
            status=DraftStatus.APPROVED,
            risk_level="low",
            created_by="user-a",
            created_at="2023-01-01T12:00:00Z",
            source_context={},
        )
        created_draft = await draft_storage.create_draft(draft)
        
        # Create execution as Tenant A
        execution = ExecutionRecord(
            execution_id=str(uuid4()),
            draft_id=created_draft.draft_id,
            tool_id="docs.cell.draft.submit_for_approval",
            tenant_id=tenant_a,
            actor_id="user-a",
            status=ExecutionStatus.SUCCEEDED,
            result_payload={"status": "submitted"},
            created_at="2023-01-01T12:00:00Z",
            completed_at="2023-01-01T12:00:01Z",
        )
        
        created_execution = await execution_storage.create_execution(execution)
        assert created_execution.execution_id == execution.execution_id
        
        # Try to retrieve as Tenant B (should return None due to RLS)
        retrieved_by_b = await execution_storage.get_execution(created_execution.execution_id, tenant_b)
        assert retrieved_by_b is None, "Tenant B should not be able to access Tenant A's execution"
        
        # Verify Tenant A can still access it
        retrieved_by_a = await execution_storage.get_execution(created_execution.execution_id, tenant_a)
        assert retrieved_by_a is not None, "Tenant A should be able to access their own execution"
        assert retrieved_by_a.execution_id == created_execution.execution_id


class TestRLSSettlementIntentIsolation:
    """Test RLS isolation for settlement intents."""
    
    @pytest.mark.asyncio
    async def test_settlement_intent_created_by_tenant_a_not_visible_to_tenant_b(
        self,
        settlement_storage: SettlementIntentStorageSupabase,
        tenant_a: str,
        tenant_b: str,
    ):
        """Test that Tenant B cannot see settlement intents created by Tenant A."""
        # Create settlement intent as Tenant A
        intent = SettlementIntent(
            payment_id=f"payment-{uuid4().hex[:8]}",
            settlement_status="queued",
            provider="none",
        )
        
        created_intent = await settlement_storage.create_settlement_intent(intent, tenant_a)
        assert created_intent.payment_id == intent.payment_id
        
        # Try to retrieve as Tenant B (should return None due to RLS)
        retrieved_by_b = await settlement_storage.get_settlement_intent(created_intent.payment_id, tenant_b)
        assert retrieved_by_b is None, "Tenant B should not be able to access Tenant A's settlement intent"
        
        # Verify Tenant A can still access it
        retrieved_by_a = await settlement_storage.get_settlement_intent(created_intent.payment_id, tenant_a)
        assert retrieved_by_a is not None, "Tenant A should be able to access their own settlement intent"
        assert retrieved_by_a.payment_id == created_intent.payment_id


class TestRLSIdempotencyRespectsTenant:
    """Test that idempotency (request_id) respects tenant boundaries."""
    
    @pytest.mark.asyncio
    async def test_same_request_id_different_tenants_creates_separate_drafts(
        self,
        draft_storage: DraftStorageSupabase,
        tenant_a: str,
        tenant_b: str,
    ):
        """Test that same request_id for different tenants creates separate drafts."""
        request_id = f"req-{uuid4().hex[:8]}"
        
        # Create draft for Tenant A with request_id
        draft_a = DraftProtocol(
            draft_id=str(uuid4()),
            tenant_id=tenant_a,
            draft_type="docs",
            payload={"title": "Tenant A Doc"},
            status=DraftStatus.DRAFT,
            risk_level="low",
            created_by="user-a",
            created_at="2023-01-01T12:00:00Z",
            source_context={},
            request_id=request_id,
        )
        created_a = await draft_storage.create_draft(draft_a)
        
        # Create draft for Tenant B with same request_id
        draft_b = DraftProtocol(
            draft_id=str(uuid4()),
            tenant_id=tenant_b,
            draft_type="docs",
            payload={"title": "Tenant B Doc"},
            status=DraftStatus.DRAFT,
            risk_level="low",
            created_by="user-b",
            created_at="2023-01-01T12:00:00Z",
            source_context={},
            request_id=request_id,  # Same request_id
        )
        created_b = await draft_storage.create_draft(draft_b)
        
        # Should create separate drafts (different draft_ids)
        assert created_a.draft_id != created_b.draft_id, "Same request_id for different tenants should create separate drafts"
        
        # Verify both tenants can access their own drafts
        retrieved_a = await draft_storage.get_draft(created_a.draft_id, tenant_a)
        retrieved_b = await draft_storage.get_draft(created_b.draft_id, tenant_b)
        
        assert retrieved_a is not None, "Tenant A should access their draft"
        assert retrieved_b is not None, "Tenant B should access their draft"
        assert retrieved_a.draft_id == created_a.draft_id
        assert retrieved_b.draft_id == created_b.draft_id


class TestRLSAuditEventIsolation:
    """Test RLS isolation for audit events."""
    
    @pytest.mark.asyncio
    async def test_audit_event_tenant_isolation_documented(
        self,
        tenant_a: str,
        tenant_b: str,
    ):
        """
        Document expected RLS behavior for audit events.
        
        Note: Audit events are typically written by the audit logger,
        not directly by tests. This test documents the expected RLS behavior:
        - Tenant B should not be able to query audit events from Tenant A
        - RLS policies on lynx_audit_events table enforce tenant isolation
        
        Actual verification would require:
        1. Creating audit events via audit logger
        2. Querying via Supabase client with different tenant contexts
        3. Verifying cross-tenant access is blocked
        """
        # This test documents expected behavior rather than executing it
        # Full RLS verification for audit events would require audit logger integration
        pass


class TestRLSUpdateDeleteIsolation:
    """Test that UPDATE and DELETE operations respect tenant boundaries."""
    
    @pytest.mark.asyncio
    async def test_draft_status_update_respects_tenant_boundary(
        self,
        draft_storage: DraftStorageSupabase,
        tenant_a: str,
        tenant_b: str,
    ):
        """Test that Tenant B cannot update draft status of Tenant A's drafts."""
        # Create draft as Tenant A
        draft = DraftProtocol(
            draft_id=str(uuid4()),
            tenant_id=tenant_a,
            draft_type="docs",
            payload={"title": "Tenant A Document"},
            status=DraftStatus.DRAFT,
            risk_level="low",
            created_by="user-a",
            created_at="2023-01-01T12:00:00Z",
            source_context={},
        )
        created_draft = await draft_storage.create_draft(draft)
        
        # Try to update status as Tenant B (should fail or return None)
        # The storage layer validates tenant_id matches in the update query
        updated = await draft_storage.update_draft_status(
            created_draft.draft_id,
            tenant_b,  # Wrong tenant
            DraftStatus.SUBMITTED,
        )
        
        # Update should return None (RLS blocks cross-tenant updates)
        assert updated is None, "Tenant B should not be able to update Tenant A's draft status"
        
        # Verify Tenant A's draft is unchanged
        retrieved_by_a = await draft_storage.get_draft(created_draft.draft_id, tenant_a)
        assert retrieved_by_a is not None, "Tenant A's draft should still exist"
        assert retrieved_by_a.status == DraftStatus.DRAFT, "Tenant A's draft status should not be modified"