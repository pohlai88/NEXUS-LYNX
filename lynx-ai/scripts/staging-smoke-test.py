#!/usr/bin/env python3
"""
Staging Smoke Test - Verify basic operations work with Supabase backend.

Usage:
    export SUPABASE_URL=https://<project-ref>.supabase.co
    export SUPABASE_KEY=your-service-role-key
    python scripts/staging-smoke-test.py
"""

import asyncio
import os
import sys
from uuid import uuid4

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lynx.mcp.cluster.drafts.base import create_draft
from lynx.storage.draft_storage import get_draft_storage
from lynx.mcp.cluster.drafts.models import DraftStatus
from lynx.mcp.cell.execution.base import create_execution_record, complete_execution
from lynx.storage.execution_storage import get_execution_storage
from lynx.mcp.cell.execution.models import ExecutionStatus
from lynx.core.session import ExecutionContext


async def main():
    """Run smoke tests."""
    print("🔥 Lynx AI Staging Smoke Test\n")
    
    # Check environment
    if not os.getenv("SUPABASE_URL") or not os.getenv("SUPABASE_KEY"):
        print("❌ ERROR: SUPABASE_URL and SUPABASE_KEY must be set")
        sys.exit(1)
    
    tenant_id = f"smoke-test-{uuid4().hex[:8]}"
    user_id = "smoke-test-user"
    
    print(f"Tenant ID: {tenant_id}")
    print(f"User ID: {user_id}\n")
    
    # Test 1: Verify storage backend
    print("Test 1: Verify storage backend...")
    draft_storage = get_draft_storage()
    backend_type = "supabase" if hasattr(draft_storage, 'client') else "memory"
    print(f"  ✅ Storage backend: {backend_type}")
    
    if backend_type == "memory":
        print("  ⚠️  WARNING: Using in-memory storage. Set SUPABASE_URL and SUPABASE_KEY to use Supabase.")
    
    # Test 2: Create draft
    print("\nTest 2: Create draft...")
    draft = await create_draft(
        tenant_id=tenant_id,
        draft_type="docs",
        payload={"title": "Smoke Test Document", "content": "This is a test"},
        created_by=user_id,
        source_context={"test": "smoke_test"},
    )
    print(f"  ✅ Draft created: {draft.draft_id}")
    print(f"     Status: {draft.status.value}")
    print(f"     Risk Level: {draft.risk_level}")
    
    # Test 3: Retrieve draft
    print("\nTest 3: Retrieve draft...")
    retrieved = await draft_storage.get_draft(draft.draft_id, tenant_id)
    assert retrieved is not None, "Draft retrieval failed"
    assert retrieved.draft_id == draft.draft_id, "Draft ID mismatch"
    print(f"  ✅ Draft retrieved: {retrieved.draft_id}")
    print(f"     Payload: {retrieved.payload.get('title')}")
    
    # Test 4: Update draft status
    print("\nTest 4: Update draft status...")
    await draft_storage.update_draft_status(draft.draft_id, tenant_id, DraftStatus.APPROVED)
    updated = await draft_storage.get_draft(draft.draft_id, tenant_id)
    assert updated.status == DraftStatus.APPROVED, "Status update failed"
    print(f"  ✅ Draft status updated to: {updated.status.value}")
    
    # Test 5: Create execution record
    print("\nTest 5: Create execution record...")
    context = ExecutionContext(
        tenant_id=tenant_id,
        user_id=user_id,
        run_id=f"run-{uuid4().hex[:8]}",
    )
    
    execution = await create_execution_record(
        draft_id=draft.draft_id,
        tool_id="docs.cell.draft.submit_for_approval",
        context=context,
    )
    print(f"  ✅ Execution created: {execution.execution_id}")
    print(f"     Status: {execution.status.value}")
    
    # Test 6: Complete execution
    print("\nTest 6: Complete execution...")
    completed = await complete_execution(
        execution_id=execution.execution_id,
        status=ExecutionStatus.SUCCEEDED,
        result_payload={"status": "submitted", "draft_id": draft.draft_id},
    )
    assert completed.status == ExecutionStatus.SUCCEEDED, "Execution completion failed"
    print(f"  ✅ Execution completed: {completed.execution_id}")
    print(f"     Final status: {completed.status.value}")
    
    # Test 7: Retrieve execution
    print("\nTest 7: Retrieve execution...")
    execution_storage = get_execution_storage()
    retrieved_exec = await execution_storage.get_execution(execution.execution_id, tenant_id)
    assert retrieved_exec is not None, "Execution retrieval failed"
    assert retrieved_exec.status == ExecutionStatus.SUCCEEDED, "Execution status mismatch"
    print(f"  ✅ Execution retrieved: {retrieved_exec.execution_id}")
    print(f"     Result: {retrieved_exec.result_payload}")
    
    # Test 8: List drafts
    print("\nTest 8: List drafts...")
    drafts = await draft_storage.list_drafts(tenant_id, limit=10)
    assert len(drafts) >= 1, "Draft list should include created draft"
    print(f"  ✅ Listed {len(drafts)} draft(s)")
    
    # Test 9: List executions
    print("\nTest 9: List executions...")
    executions = await execution_storage.list_executions(tenant_id, limit=10)
    assert len(executions) >= 1, "Execution list should include created execution"
    print(f"  ✅ Listed {len(executions)} execution(s)")
    
    # Summary
    print("\n" + "="*50)
    print("🎉 All smoke tests passed!")
    print(f"   Backend: {backend_type}")
    print(f"   Drafts created: 1")
    print(f"   Executions created: 1")
    print("="*50 + "\n")


if __name__ == "__main__":
    asyncio.run(main())

