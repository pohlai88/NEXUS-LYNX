"""
Session manager for Lynx AI.

Manages tenant-scoped sessions and execution context.
"""

from typing import Optional, Dict, Any, TYPE_CHECKING
from uuid import uuid4
from datetime import datetime, timedelta
from dataclasses import dataclass, field

if TYPE_CHECKING:
    from lynx.core.audit import AuditLogger
# AuditLogger will be imported when needed to avoid circular imports


@dataclass
class Session:
    """Represents a Lynx session."""
    session_id: str
    user_id: str
    tenant_id: str
    user_role: str
    user_scope: list[str]
    created_at: datetime
    expires_at: datetime


@dataclass
class ExecutionContext:
    """Execution context for MCP tool calls."""
    # User & Tenant
    user_id: str
    tenant_id: str
    user_role: str
    user_scope: list[str]
    
    # Session
    session_id: str
    lynx_run_id: str = field(default_factory=lambda: str(uuid4()))
    
    # Kernel (will be populated from Kernel API)
    kernel_metadata: dict = field(default_factory=dict)
    tenant_customizations: dict = field(default_factory=dict)
    
    # Approval
    explicit_approval: Optional[bool] = None
    
    # Audit (using Any to avoid circular import)
    audit_logger: Optional[Any] = None


class SessionManager:
    """Manages tenant-scoped sessions."""
    
    def __init__(self, session_timeout_hours: int = 8):
        """
        Initialize session manager.
        
        Args:
            session_timeout_hours: Session timeout in hours (default: 8)
        """
        self.sessions: Dict[str, Session] = {}
        self.session_timeout_hours = session_timeout_hours
    
    def create_session(
        self,
        user_id: str,
        tenant_id: str,
        user_role: str,
        user_scope: list[str],
    ) -> Session:
        """
        Create a new tenant-scoped session.
        
        Args:
            user_id: User ID
            tenant_id: Tenant ID (enforces tenant isolation)
            user_role: User role
            user_scope: User scope/permissions
        
        Returns:
            Created Session instance
        """
        session = Session(
            session_id=str(uuid4()),
            user_id=user_id,
            tenant_id=tenant_id,
            user_role=user_role,
            user_scope=user_scope,
            created_at=datetime.now(),
            expires_at=datetime.now() + timedelta(hours=self.session_timeout_hours),
        )
        self.sessions[session.session_id] = session
        return session
    
    def get_session(self, session_id: str) -> Optional[Session]:
        """
        Get session by ID.
        
        Args:
            session_id: Session ID
        
        Returns:
            Session if found and not expired, None otherwise
        """
        session = self.sessions.get(session_id)
        if session and session.expires_at > datetime.now():
            return session
        # Remove expired session
        if session:
            del self.sessions[session_id]
        return None
    
    def create_execution_context(
        self,
        session: Session,
        audit_logger: Optional["AuditLogger"] = None,
    ) -> ExecutionContext:
        """
        Create execution context from session.
        
        Args:
            session: Session instance
            audit_logger: Audit logger instance
        
        Returns:
            ExecutionContext instance
        """
        return ExecutionContext(
            user_id=session.user_id,
            tenant_id=session.tenant_id,
            user_role=session.user_role,
            user_scope=session.user_scope,
            session_id=session.session_id,
            audit_logger=audit_logger,
        )

