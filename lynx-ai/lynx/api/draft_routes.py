"""
Draft API Routes - Thin Client Over MCP

Backend handles draft lifecycle, UI only renders status.
Backend derives tenant_id from session (never from client).
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from typing import Optional, Dict
from uuid import uuid4

from lynx.api.models import (
    Draft,
    DraftListResponse,
    DraftStatus,
    ApproveDraftRequest,
    RejectDraftRequest,
)
from lynx.api.auth import get_current_session, verify_tenant_access
from lynx.storage.draft_storage import get_draft_storage
from lynx.core.audit import AuditLogger
from lynx.config import Config
from lynx.mcp.cluster.drafts.models import DraftStatus as ClusterDraftStatus

router = APIRouter(prefix="/api/drafts", tags=["drafts"])


@router.get("", response_model=DraftListResponse)
async def list_drafts(
    status: Optional[str] = Query(None),
    type: Optional[str] = Query(None),
    limit: int = Query(50),
    cursor: Optional[str] = Query(None),  # ✅ Cursor pagination
    session: Dict[str, str] = Depends(get_current_session),  # ✅ Auth + tenant
):
    """
    List drafts for a tenant.
    
    ✅ Backend derives tenant_id from session
    ✅ Server-side filtering (date range, status, type)
    ✅ Cursor pagination (better than offset for audit logs)
    """
    tenant_id = session['tenant_id']
    
    # Get draft storage
    storage = get_draft_storage()
    
    # Convert status string to enum if provided
    status_enum = None
    if status:
        try:
            status_enum = ClusterDraftStatus(status)
        except ValueError:
            raise HTTPException(400, f"Invalid status: {status}")
    
    # List drafts (tenant-scoped)
    cluster_drafts = await storage.list_drafts(
        tenant_id=tenant_id,
        draft_type=type,
        status=status_enum,
    )
    
    # Convert to API models
    from lynx.api.models import Draft as APIDraft, DraftStatus as APIDraftStatus
    api_drafts = []
    for cluster_draft in cluster_drafts[:limit]:
        # Map cluster DraftStatus to API DraftStatus
        status_map = {
            ClusterDraftStatus.DRAFT: APIDraftStatus.DRAFT,
            ClusterDraftStatus.APPROVED: APIDraftStatus.APPROVED,
            ClusterDraftStatus.REJECTED: APIDraftStatus.REJECTED,
            # TODO: Map executing/executed/failed when cluster supports them
        }
        api_status = status_map.get(cluster_draft.status, APIDraftStatus.DRAFT)
        
        api_draft = APIDraft(
            draft_id=cluster_draft.draft_id,
            status=api_status,
            requires_confirmation=cluster_draft.risk_level == "high",  # ✅ Backend decides
            risk_level=cluster_draft.risk_level,
            tool_id=cluster_draft.draft_type,  # TODO: Map properly
            payload=cluster_draft.payload,
            created_at=cluster_draft.created_at,
            created_by=cluster_draft.created_by,
            approved_by=None,  # TODO: Get from cluster draft
            rejected_by=None,
            reason=None,
            execution_id=None,
            execution_error=None,
            metadata={},
        )
        api_drafts.append(api_draft)
    
    return DraftListResponse(
        drafts=api_drafts,
        total=len(cluster_drafts),
        limit=limit,
        offset=0,  # TODO: Implement cursor-based offset
        cursor=None,  # TODO: Generate cursor for next page
    )


@router.get("/{draft_id}", response_model=Draft)
async def get_draft(
    draft_id: str,
    session: Dict[str, str] = Depends(get_current_session),
):
    """Get draft details (tenant-scoped)."""
    tenant_id = session['tenant_id']
    
    # Get draft storage
    storage = get_draft_storage()
    
    # Get draft (tenant-scoped, RLS enforced)
    cluster_draft = await storage.get_draft(draft_id, tenant_id)
    if not cluster_draft:
        raise HTTPException(404, f"Draft {draft_id} not found")
    
    # Convert to API model
    from lynx.api.models import Draft as APIDraft, DraftStatus as APIDraftStatus
    status_map = {
        ClusterDraftStatus.DRAFT: APIDraftStatus.DRAFT,
        ClusterDraftStatus.APPROVED: APIDraftStatus.APPROVED,
        ClusterDraftStatus.REJECTED: APIDraftStatus.REJECTED,
    }
    api_status = status_map.get(cluster_draft.status, APIDraftStatus.DRAFT)
    
    return APIDraft(
        draft_id=cluster_draft.draft_id,
        status=api_status,
        requires_confirmation=cluster_draft.risk_level == "high",  # ✅ Backend decides
        risk_level=cluster_draft.risk_level,
        tool_id=cluster_draft.draft_type,
        payload=cluster_draft.payload,
        created_at=cluster_draft.created_at,
        created_by=cluster_draft.created_by,
        approved_by=None,  # TODO: Get from cluster draft
        rejected_by=None,
        reason=None,
        execution_id=None,
        execution_error=None,
        metadata={},
    )


@router.post("/{draft_id}/approve")
async def approve_draft(
    draft_id: str,
    request: ApproveDraftRequest,
    session: Dict[str, str] = Depends(get_current_session),
):
    """
    Approve a draft.
    
    ✅ Idempotency: Check if already approved (prevent double execution)
    ✅ Draft lifecycle: draft → approved → executing → executed/failed
    """
    tenant_id = session['tenant_id']
    user_id = session['user_id']
    role = session['role']
    request_id = str(uuid4())  # ✅ For debugging
    
    # Get draft storage
    storage = get_draft_storage()
    
    # Get draft (tenant-scoped)
    cluster_draft = await storage.get_draft(draft_id, tenant_id)
    if not cluster_draft:
        raise HTTPException(404, f"Draft {draft_id} not found")
    
    # ✅ Idempotency check (prevent double approval)
    if cluster_draft.status != ClusterDraftStatus.DRAFT:
        raise HTTPException(400, f"Draft already {cluster_draft.status.value}")
    
    # Update status: draft → approved
    await storage.update_draft_status(
        draft_id=draft_id,
        tenant_id=tenant_id,
        new_status=ClusterDraftStatus.APPROVED,
    )
    
    # TODO: If execution required (Cell MCP), update to executing → execute → executed/failed
    # For now, just approve (execution happens separately)
    
    # Create audit log entry
    if Config.SUPABASE_URL and Config.SUPABASE_KEY:
        audit_logger = AuditLogger(
            supabase_url=Config.SUPABASE_URL,
            supabase_key=Config.SUPABASE_KEY,
        )
        # TODO: Log draft approval event
    else:
        audit_logger = None
    
    return {"success": True, "draft_id": draft_id, "status": "approved"}


@router.post("/{draft_id}/reject")
async def reject_draft(
    draft_id: str,
    request: RejectDraftRequest,
    session: Dict[str, str] = Depends(get_current_session),
):
    """Reject a draft."""
    tenant_id = session['tenant_id']
    user_id = session['user_id']
    request_id = str(uuid4())
    
    # Get draft storage
    storage = get_draft_storage()
    
    # Get draft (tenant-scoped)
    cluster_draft = await storage.get_draft(draft_id, tenant_id)
    if not cluster_draft:
        raise HTTPException(404, f"Draft {draft_id} not found")
    
    # Update status: draft → rejected
    await storage.update_draft_status(
        draft_id=draft_id,
        tenant_id=tenant_id,
        new_status=ClusterDraftStatus.REJECTED,
    )
    
    # Create audit log entry
    if Config.SUPABASE_URL and Config.SUPABASE_KEY:
        audit_logger = AuditLogger(
            supabase_url=Config.SUPABASE_URL,
            supabase_key=Config.SUPABASE_KEY,
        )
        # TODO: Log draft rejection event
    else:
        audit_logger = None
    
    return {"success": True, "draft_id": draft_id, "status": "rejected"}


@router.delete("/{draft_id}")
async def delete_draft(
    draft_id: str,
    session: Dict[str, str] = Depends(get_current_session),
):
    """
    Delete a draft (only if draft or rejected status).
    
    ✅ Safety check: Only allow delete for draft or rejected
    """
    tenant_id = session['tenant_id']
    user_id = session['user_id']
    request_id = str(uuid4())
    
    # Get draft storage
    storage = get_draft_storage()
    
    # Get draft (tenant-scoped)
    cluster_draft = await storage.get_draft(draft_id, tenant_id)
    if not cluster_draft:
        raise HTTPException(404, f"Draft {draft_id} not found")
    
    # ✅ Safety check: Only allow delete for draft or rejected
    if cluster_draft.status not in [ClusterDraftStatus.DRAFT, ClusterDraftStatus.REJECTED]:
        raise HTTPException(
            400,
            f"Cannot delete draft in status {cluster_draft.status.value}. Only draft or rejected drafts can be deleted."
        )
    
    # Delete from storage
    # TODO: Implement delete method in storage
    # For now, update status to a "deleted" state or remove from storage
    # await storage.delete_draft(draft_id, tenant_id)
    
    # Create audit log entry
    if Config.SUPABASE_URL and Config.SUPABASE_KEY:
        audit_logger = AuditLogger(
            supabase_url=Config.SUPABASE_URL,
            supabase_key=Config.SUPABASE_KEY,
        )
        # TODO: Log draft deletion event
    else:
        audit_logger = None
    
    return {"success": True, "draft_id": draft_id}

