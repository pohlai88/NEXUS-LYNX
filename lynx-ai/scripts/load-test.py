#!/usr/bin/env python3
"""
Load Test - Create many drafts and executions to verify performance.

Usage:
    export SUPABASE_URL=https://<project-ref>.supabase.co
    export SUPABASE_KEY=your-service-role-key
    python scripts/load-test.py
"""

import asyncio
import os
import sys
import time
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


async def create_drafts_batch(tenant_id: str, count: int) -> list:
    """Create a batch of drafts."""
    print(f"Creating {count} drafts...")
    start_time = time.time()
    
    tasks = []
    for i in range(count):
        tasks.append(create_draft(
            tenant_id=tenant_id,
            draft_type="docs",
            payload={"title": f"Load Test Doc {i}", "content": f"Content for doc {i}"},
            created_by="load-test-user",
            source_context={"test": "load_test", "batch_index": i},
        ))
    
    drafts = await asyncio.gather(*tasks)
    elapsed = time.time() - start_time
    
    print(f"  ✅ Created {len(drafts)} drafts in {elapsed:.2f}s ({elapsed/len(drafts)*1000:.2f}ms per draft)")
    return drafts


async def create_executions_batch(tenant_id: str, user_id: str, drafts: list, count: int) -> list:
    """Create a batch of executions."""
    print(f"\nCreating {count} executions...")
    start_time = time.time()
    
    context = ExecutionContext(
        tenant_id=tenant_id,
        user_id=user_id,
        run_id=f"load-test-run-{uuid4().hex[:8]}",
    )
    
    execution_storage = get_execution_storage()
    executions = []
    
    for i, draft in enumerate(drafts[:count]):
        # Approve draft first
        draft_storage = get_draft_storage()
        await draft_storage.update_draft_status(draft.draft_id, tenant_id, DraftStatus.APPROVED)
        
        # Create execution
        execution = await create_execution_record(
            draft_id=draft.draft_id,
            tool_id="docs.cell.draft.submit_for_approval",
            context=context,
        )
        
        # Complete execution
        completed = await complete_execution(
            execution_id=execution.execution_id,
            status=ExecutionStatus.SUCCEEDED,
            result_payload={"status": "submitted", "draft_id": draft.draft_id},
        )
        
        executions.append(completed)
    
    elapsed = time.time() - start_time
    print(f"  ✅ Created {len(executions)} executions in {elapsed:.2f}s ({elapsed/len(executions)*1000:.2f}ms per execution)")
    return executions


async def verify_data(tenant_id: str, expected_draft_count: int, expected_execution_count: int):
    """Verify all data was stored correctly."""
    print("\nVerifying data...")
    
    draft_storage = get_draft_storage()
    execution_storage = get_execution_storage()
    
    # Verify drafts
    drafts = await draft_storage.list_drafts(tenant_id, limit=1000)
    print(f"  Drafts in storage: {len(drafts)} (expected: {expected_draft_count})")
    assert len(drafts) == expected_draft_count, f"Draft count mismatch: {len(drafts)} != {expected_draft_count}"
    
    # Verify executions
    executions = await execution_storage.list_executions(tenant_id, limit=1000)
    print(f"  Executions in storage: {len(executions)} (expected: {expected_execution_count})")
    assert len(executions) == expected_execution_count, f"Execution count mismatch: {len(executions)} != {expected_execution_count}"
    
    # Verify no duplicates
    draft_ids = {d.draft_id for d in drafts}
    execution_ids = {e.execution_id for e in executions}
    
    assert len(draft_ids) == len(drafts), "Duplicate draft IDs found"
    assert len(execution_ids) == len(executions), "Duplicate execution IDs found"
    
    print("  ✅ No duplicates found")
    print("  ✅ All data verified")


async def main():
    """Run load test."""
    print("🚀 Lynx AI Load Test\n")
    
    # Check environment
    if not os.getenv("SUPABASE_URL") or not os.getenv("SUPABASE_KEY"):
        print("❌ ERROR: SUPABASE_URL and SUPABASE_KEY must be set")
        sys.exit(1)
    
    tenant_id = f"load-test-{uuid4().hex[:8]}"
    user_id = "load-test-user"
    
    print(f"Tenant ID: {tenant_id}")
    print(f"User ID: {user_id}\n")
    
    # Test parameters
    draft_count = 50
    execution_count = 20
    
    total_start = time.time()
    
    try:
        # Create drafts
        drafts = await create_drafts_batch(tenant_id, draft_count)
        
        # Create executions
        executions = await create_executions_batch(tenant_id, user_id, drafts, execution_count)
        
        # Verify data
        await verify_data(tenant_id, draft_count, execution_count)
        
        total_elapsed = time.time() - total_start
        
        # Summary
        print("\n" + "="*50)
        print("🎉 Load test passed!")
        print(f"   Total time: {total_elapsed:.2f}s")
        print(f"   Drafts created: {draft_count}")
        print(f"   Executions created: {execution_count}")
        print(f"   Average draft creation: {total_elapsed/draft_count*1000:.2f}ms")
        print("="*50 + "\n")
        
    except Exception as e:
        print(f"\n❌ Load test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())

