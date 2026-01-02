"""
Draft Protocol Models

Core models for the Draft Protocol (separated to avoid circular imports).
"""

from pydantic import BaseModel, Field
from typing import Dict, Any, Optional, List
from enum import Enum


class DraftStatus(str, Enum):
    """Draft status enumeration."""
    DRAFT = "draft"
    SUBMITTED = "submitted"
    APPROVED = "approved"
    REJECTED = "rejected"
    CANCELLED = "cancelled"
    # Execution states (Cell layer)
    PUBLISHED = "published"  # For workflow drafts
    EXECUTED = "executed"  # For payment/docs drafts


class DraftProtocol(BaseModel):
    """
    Draft Protocol - Non-negotiable structure for all Cluster MCP drafts.
    
    This ensures:
    - Draft-only (no side effects)
    - Approval-ready artifacts
    - Auditable and reversible
    """
    draft_id: str = Field(description="Unique draft identifier")
    tenant_id: str = Field(description="Tenant ID (enforces tenant isolation)")
    draft_type: str = Field(description="Draft type (docs|workflow|vpm_payment)")
    payload: Dict[str, Any] = Field(description="Draft payload (JSON)")
    status: DraftStatus = Field(default=DraftStatus.DRAFT, description="Draft status")
    risk_level: str = Field(description="Risk level (low|medium|high)")
    created_by: str = Field(description="User ID who created the draft")
    created_at: str = Field(description="Creation timestamp (ISO format)")
    source_context: Dict[str, Any] = Field(
        description="Source context (which Domain tools were used + timestamps)"
    )
    recommended_approvers: List[str] = Field(
        default_factory=list,
        description="Recommended approver roles/user IDs"
    )
    request_id: Optional[str] = Field(
        default=None,
        description="Request ID for idempotency"
    )

