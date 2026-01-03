"""
API Request/Response Models - Single Source of Truth

These Pydantic models define the exact contracts between backend and frontend.
Frontend TypeScript types should be generated from these models.
"""

from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


# ============================================================================
# Enums (Shared)
# ============================================================================

class RunStatus(str, Enum):
    SUCCESS = "success"
    ERROR = "error"
    PENDING = "pending"


class DraftStatus(str, Enum):
    DRAFT = "draft"
    APPROVED = "approved"
    REJECTED = "rejected"
    EXECUTING = "executing"  # ✅ Transition state (approved → executing)
    EXECUTED = "executed"    # ✅ Approved + execution succeeded
    FAILED = "failed"        # ✅ Approved but execution failed


class RiskLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class ToolCallStatus(str, Enum):
    SUCCESS = "success"
    ERROR = "error"
    PENDING = "pending"


# ============================================================================
# Chat API Models
# ============================================================================

class ToolCall(BaseModel):
    """Tool call information."""
    tool_id: str
    status: ToolCallStatus
    input: Dict[str, Any]
    output: Optional[Dict[str, Any]] = None
    duration_ms: Optional[int] = None
    error: Optional[str] = None


class PolicyInfo(BaseModel):
    """Policy information (backend decides, UI only renders)."""
    requires_confirmation: bool  # ✅ Backend decides, UI only renders
    risk_level: RiskLevel
    blocked_reason: Optional[str] = None


class ChatQueryRequest(BaseModel):
    """Chat query request (no tenant_id - backend derives from session)."""
    query: str
    context: Optional[Dict[str, Any]] = None  # Optional: entity_type, entity_id only


class ChatQueryResponse(BaseModel):
    """Chat query response."""
    run_id: str
    response: str
    tool_calls: List[ToolCall]
    status: RunStatus
    policy: PolicyInfo  # ✅ Backend provides policy, UI renders


class ChatRun(BaseModel):
    """Complete chat run information."""
    run_id: str
    created_at: datetime
    completed_at: Optional[datetime] = None
    status: RunStatus
    query: str
    response: str
    tool_calls: List[ToolCall]
    policy: PolicyInfo


# ============================================================================
# Draft API Models
# ============================================================================

class Draft(BaseModel):
    """Draft information."""
    draft_id: str
    status: DraftStatus  # ✅ Includes executing/executed/failed
    requires_confirmation: bool  # ✅ Backend decides
    risk_level: RiskLevel
    tool_id: str
    payload: Dict[str, Any]
    created_at: datetime
    created_by: str
    approved_by: Optional[str] = None
    rejected_by: Optional[str] = None
    reason: Optional[str] = None
    execution_id: Optional[str] = None  # ✅ If executed
    execution_error: Optional[str] = None  # ✅ If failed
    metadata: Dict[str, Any] = {}


class DraftListResponse(BaseModel):
    """Draft list response with pagination."""
    drafts: List[Draft]
    total: int
    limit: int
    offset: int
    cursor: Optional[str] = None  # ✅ For cursor pagination


class ApproveDraftRequest(BaseModel):
    """Approve draft request."""
    notes: Optional[str] = None


class RejectDraftRequest(BaseModel):
    """Reject draft request."""
    reason: str


# ============================================================================
# Execution API Models
# ============================================================================

class ExecutionConfirmRequest(BaseModel):
    """Execution confirmation request."""
    notes: Optional[str] = None


class ExecutionDetail(BaseModel):
    """Execution detail information."""
    execution_id: str
    status: RunStatus
    result: Optional[Dict[str, Any]] = None
    tool_calls: List[ToolCall]
    created_at: datetime
    completed_at: Optional[datetime] = None
    error: Optional[str] = None


# ============================================================================
# Audit API Models
# ============================================================================

class AuditRun(BaseModel):
    """Audit run information (tenant-scoped)."""
    run_id: str
    tenant_id: str  # ✅ Server-side only (for display)
    actor_user_id: str
    actor_role: str
    request_id: str  # ✅ For debugging
    query: str
    response: str
    tool_calls: List[ToolCall]
    created_at: datetime
    completed_at: Optional[datetime] = None


class AuditListResponse(BaseModel):
    """Audit list response with pagination."""
    runs: List[AuditRun]
    total: int
    limit: int
    offset: int
    cursor: Optional[str] = None  # ✅ For cursor pagination

