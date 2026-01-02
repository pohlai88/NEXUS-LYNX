"""
Draft Protocol - Base implementation.

Defines the non-negotiable invariants for Cluster MCPs:
- Draft-only (no side effects)
- Approval-ready artifacts
- Auditable and reversible
"""

from typing import Dict, Any, Optional, List
from datetime import datetime
from uuid import uuid4

# Import models (separated to avoid circular imports)
from lynx.mcp.cluster.drafts.models import DraftProtocol, DraftStatus

# Import storage (will use Supabase if available, otherwise in-memory)
from lynx.storage.draft_storage import DraftStorage, get_draft_storage


# DraftStorage is now imported from lynx.storage.draft_storage
# This maintains backward compatibility while allowing Supabase backend


async def create_draft(
    tenant_id: str,
    draft_type: str,
    payload: Dict[str, Any],
    created_by: str,
    source_context: Dict[str, Any],
    risk_level: str = "medium",
    recommended_approvers: Optional[List[str]] = None,
    request_id: Optional[str] = None,
) -> DraftProtocol:
    """
    Create a draft following the Draft Protocol.
    
    This is the shared function all Cluster MCPs should use.
    
    Args:
        tenant_id: Tenant ID
        draft_type: Draft type (docs|workflow|vpm_payment)
        payload: Draft payload (JSON)
        created_by: User ID who created the draft
        source_context: Source context (Domain tool usage)
        risk_level: Risk level (low|medium|high)
        recommended_approvers: Recommended approver roles/user IDs
        request_id: Request ID for idempotency
    
    Returns:
        Created DraftProtocol instance
    """
    storage = get_draft_storage()
    
    draft = DraftProtocol(
        draft_id=str(uuid4()),
        tenant_id=tenant_id,
        draft_type=draft_type,
        payload=payload,
        status=DraftStatus.DRAFT,
        risk_level=risk_level,
        created_by=created_by,
        created_at=datetime.now().isoformat(),
        source_context=source_context,
        recommended_approvers=recommended_approvers or [],
        request_id=request_id,
    )
    
    return await storage.create_draft(draft)

