"""
Cell Execution Protocol - Base implementation.

Defines the non-negotiable invariants for Cell MCPs:
- Execution-only (from approved drafts)
- Fully audited
- Idempotent
- Rollback-capable
"""

from typing import Dict, Any, Optional
from datetime import datetime
from uuid import uuid4

from lynx.core.session import ExecutionContext

# Import models (separated to avoid circular imports)
from lynx.mcp.cell.execution.models import ExecutionRecord, ExecutionStatus
from lynx.mcp.cluster.drafts.models import DraftStatus

# Import storage (will use Supabase if available, otherwise in-memory)
from lynx.storage.draft_storage import get_draft_storage
from lynx.storage.execution_storage import get_execution_storage


# ExecutionStorage is now imported from lynx.storage.execution_storage
# This maintains backward compatibility while allowing Supabase backend


async def check_draft_already_executed(
    draft_id: str,
    tool_id: str,
    tenant_id: str,
) -> Optional[str]:
    """
    Check if a draft has already been successfully executed by this tool.
    
    This enforces "exactly-once semantics": a given draft_id can only have
    one successful execution per tool_id (unless a new draft version exists).
    
    Args:
        draft_id: Draft ID to check
        tool_id: Cell MCP tool ID
        tenant_id: Tenant ID
    
    Returns:
        Execution ID if already executed, None otherwise
    """
    storage = get_execution_storage()
    executions = await storage.list_executions(
        tenant_id=tenant_id,
        draft_id=draft_id,
        tool_id=tool_id,
        status=ExecutionStatus.SUCCEEDED,
    )
    
    if executions:
        return executions[0].execution_id
    return None


async def validate_cell_execution(
    draft_id: str,
    context: ExecutionContext,
    tool_id: str,
    allow_bypass: bool = False,
) -> tuple[bool, Optional[str], Optional[Dict[str, Any]]]:
    """
    Validate that a Cell execution is allowed.
    
    This enforces the Cell Execution Protocol invariants:
    1. Draft exists & tenant match
    2. Draft status is APPROVED (or bypass allowed)
    3. Permissions pass (checked externally)
    4. Policy passes (checked externally)
    
    Args:
        draft_id: Draft ID to validate
        context: Execution context
        tool_id: Cell MCP tool ID
        allow_bypass: Whether to allow policy bypass (default: False)
    
    Returns:
        Tuple of (is_valid, error_message, bypass_info)
        - is_valid: True if execution is allowed
        - error_message: Error message if validation fails
        - bypass_info: Bypass information if bypass is used
    """
    # 1. Draft exists & tenant match
    draft_storage = get_draft_storage()
    draft = await draft_storage.get_draft(draft_id, context.tenant_id)
    
    if draft is None:
        return False, f"Draft {draft_id} not found or does not belong to tenant {context.tenant_id}", None
    
    # Check draft status
    if draft.status == DraftStatus.CANCELLED:
        return False, f"Draft {draft_id} is cancelled and cannot be executed", None
    
    # Check if draft already executed (exactly-once semantics)
    # This must be checked BEFORE approval check, because executed drafts have status PUBLISHED/EXECUTED
    existing_execution_id = await check_draft_already_executed(
        draft_id=draft_id,
        tool_id=tool_id,
        tenant_id=context.tenant_id,
    )
    
    if existing_execution_id:
        return False, f"Draft {draft_id} has already been successfully executed by {tool_id} (execution_id: {existing_execution_id})", None
    
    # Also check if draft status indicates it's already been executed
    if draft.status in [DraftStatus.PUBLISHED, DraftStatus.EXECUTED]:
        return False, f"Draft {draft_id} has already been executed (status: {draft.status.value})", None
    
    # 2. Draft status is APPROVED (or bypass allowed)
    if draft.status != DraftStatus.APPROVED:
        if allow_bypass:
            # Policy bypass (requires explicit authorization)
            bypass_info = {
                "bypass_reason": f"Draft status is {draft.status.value}, but policy allows bypass",
                "bypass_authorized_by": context.user_id,
                "bypass_timestamp": datetime.now().isoformat(),
                "bypass_policy_reference": f"tool:{tool_id}:allow_bypass",
            }
            return True, None, bypass_info
        else:
            return False, f"Draft {draft_id} is not approved (status: {draft.status.value})", None
    
    return True, None, None


async def create_execution_record(
    draft_id: str,
    tool_id: str,
    context: ExecutionContext,
    request_id: Optional[str] = None,
    source_context: Optional[Dict[str, Any]] = None,
) -> ExecutionRecord:
    """
    Create an execution record (STARTED status).
    
    Args:
        draft_id: Source draft ID
        tool_id: Cell MCP tool ID
        context: Execution context
        request_id: Request ID for idempotency
        source_context: Snapshot of relevant Domain/Cluster reads and policy checks
    
    Returns:
        ExecutionRecord with STARTED status
    """
    storage = get_execution_storage()
    
    execution = ExecutionRecord(
        execution_id=str(uuid4()),
        draft_id=draft_id,
        tool_id=tool_id,
        tenant_id=context.tenant_id,
        actor_id=context.user_id,
        status=ExecutionStatus.STARTED,
        result_payload={},
        created_at=datetime.now().isoformat(),
        request_id=request_id,
        source_context=source_context or {},
    )
    
    return await storage.create_execution(execution)


async def complete_execution(
    execution_id: str,
    status: ExecutionStatus,
    result_payload: Dict[str, Any],
    error_message: Optional[str] = None,
    rollback_instructions: Optional[Dict[str, Any]] = None,
) -> ExecutionRecord:
    """
    Complete an execution record.
    
    Args:
        execution_id: Execution ID
        status: Final status (SUCCEEDED, FAILED, or DENIED)
        result_payload: Execution result payload
        error_message: Error message (if failed)
        rollback_instructions: Rollback plan (if applicable)
    
    Returns:
        Updated ExecutionRecord
    """
    storage = get_execution_storage()
    
    # Update execution (storage handles the update)
    return await storage.update_execution_status(
        execution_id=execution_id,
        status=status,
        result_payload=result_payload,
        error_message=error_message,
        rollback_instructions=rollback_instructions,
    )

