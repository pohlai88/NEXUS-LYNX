"""
Draft Storage - Supabase backend implementation.

Preserves all Draft Protocol guarantees:
- Idempotency (request_id)
- Tenant isolation
- Draft immutability
"""

from typing import Dict, Any, Optional, List
from uuid import UUID
from lynx.config import Config

# Import models (separated to avoid circular imports)
from lynx.mcp.cluster.drafts.models import DraftProtocol, DraftStatus

try:
    from supabase import create_client, Client
    SUPABASE_AVAILABLE = True
except ImportError:
    SUPABASE_AVAILABLE = False
    Client = None


class DraftStorage:
    """
    Base draft storage interface (in-memory implementation).
    
    This is the fallback when Supabase is not available or in testing.
    """
    
    def __init__(self):
        """Initialize draft storage."""
        self.drafts: Dict[str, DraftProtocol] = {}
        self.request_id_map: Dict[str, str] = {}  # request_id -> draft_id
    
    async def create_draft(self, draft: DraftProtocol) -> DraftProtocol:
        """Create a draft."""
        # Check idempotency
        if draft.request_id and draft.request_id in self.request_id_map:
            existing_draft_id = self.request_id_map[draft.request_id]
            return self.drafts[existing_draft_id]
        
        # Store draft
        self.drafts[draft.draft_id] = draft
        
        # Map request_id for idempotency
        if draft.request_id:
            self.request_id_map[draft.request_id] = draft.draft_id
        
        return draft
    
    async def get_draft(self, draft_id: str, tenant_id: str) -> Optional[DraftProtocol]:
        """Get a draft by ID (tenant-scoped)."""
        draft = self.drafts.get(draft_id)
        if draft and draft.tenant_id == tenant_id:
            return draft
        return None
    
    async def list_drafts(
        self,
        tenant_id: str,
        draft_type: Optional[str] = None,
        status: Optional[DraftStatus] = None,
    ) -> List[DraftProtocol]:
        """List drafts for a tenant."""
        drafts = [d for d in self.drafts.values() if d.tenant_id == tenant_id]
        
        if draft_type:
            drafts = [d for d in drafts if d.draft_type == draft_type]
        
        if status:
            drafts = [d for d in drafts if d.status == status]
        
        return drafts
    
    async def update_draft_status(
        self,
        draft_id: str,
        tenant_id: str,
        new_status: DraftStatus,
    ) -> Optional[DraftProtocol]:
        """Update draft status (for submit/publish/executed transitions)."""
        draft = await self.get_draft(draft_id, tenant_id)
        if draft:
            draft.status = new_status
            # Re-save
            self.drafts[draft_id] = draft
        return draft


class DraftStorageSupabase(DraftStorage):
    """
    Supabase-backed draft storage.
    
    Preserves all guarantees:
    - Idempotency via request_id (unique per tenant + draft_type + request_id)
    - Tenant isolation (RLS + code checks)
    - Draft immutability
    """
    
    def __init__(self, supabase_client: Optional[Client] = None):
        """
        Initialize Supabase draft storage.
        
        Args:
            supabase_client: Supabase client (if None, creates from Config)
        """
        super().__init__()
        
        if not SUPABASE_AVAILABLE:
            raise ImportError("supabase package not installed")
        
        if supabase_client is None:
            if not Config.SUPABASE_URL or not Config.SUPABASE_KEY:
                raise ValueError("Supabase URL and key must be configured")
            self.client: Client = create_client(Config.SUPABASE_URL, Config.SUPABASE_KEY)
        else:
            self.client = supabase_client
    
    async def create_draft(self, draft: DraftProtocol) -> DraftProtocol:
        """Create a draft with idempotency check."""
        # Check idempotency: query by request_id (if provided)
        if draft.request_id:
            existing = await self._get_by_request_id(draft.tenant_id, draft.request_id, draft.draft_type)
            if existing:
                return existing
        
        # Convert to DB format
        db_record = {
            "draft_id": draft.draft_id,
            "tenant_id": draft.tenant_id,
            "draft_type": draft.draft_type,
            "payload": draft.payload,
            "status": draft.status.value,
            "risk_level": draft.risk_level,
            "created_by": draft.created_by,
            "created_at": draft.created_at,
            "source_context": draft.source_context,
            "recommended_approvers": draft.recommended_approvers,
            "request_id": draft.request_id,
        }
        
        # Insert (will fail if unique constraint violated)
        try:
            self.client.table("lynx_drafts").insert(db_record).execute()
        except Exception as e:
            # If unique constraint violation, fetch existing
            if "unique" in str(e).lower() or "duplicate" in str(e).lower():
                if draft.request_id:
                    existing = await self._get_by_request_id(draft.tenant_id, draft.request_id, draft.draft_type)
                    if existing:
                        return existing
            raise
        
        return draft
    
    async def get_draft(self, draft_id: str, tenant_id: str) -> Optional[DraftProtocol]:
        """Get a draft by ID (tenant-scoped)."""
        # Defense-in-depth: check tenant in query
        result = (
            self.client.table("lynx_drafts")
            .select("*")
            .eq("draft_id", draft_id)
            .eq("tenant_id", tenant_id)  # Tenant check in code
            .single()
            .execute()
        )
        
        if not result.data:
            return None
        
        return self._from_db_record(result.data)
    
    async def list_drafts(
        self,
        tenant_id: str,
        draft_type: Optional[str] = None,
        status: Optional[DraftStatus] = None,
    ) -> List[DraftProtocol]:
        """List drafts for a tenant."""
        query = (
            self.client.table("lynx_drafts")
            .select("*")
            .eq("tenant_id", tenant_id)
            .order("created_at", desc=True)
        )
        
        if draft_type:
            query = query.eq("draft_type", draft_type)
        
        if status:
            query = query.eq("status", status.value)
        
        result = query.execute()
        
        return [self._from_db_record(record) for record in result.data]
    
    async def update_draft_status(
        self,
        draft_id: str,
        tenant_id: str,
        new_status: DraftStatus,
    ) -> Optional[DraftProtocol]:
        """Update draft status."""
        # Defense-in-depth: check tenant in update
        result = (
            self.client.table("lynx_drafts")
            .update({"status": new_status.value})
            .eq("draft_id", draft_id)
            .eq("tenant_id", tenant_id)  # Tenant check in code
            .execute()
        )
        
        if not result.data:
            return None
        
        return self._from_db_record(result.data[0])
    
    async def _get_by_request_id(
        self,
        tenant_id: str,
        request_id: str,
        draft_type: Optional[str] = None,
    ) -> Optional[DraftProtocol]:
        """Get draft by request_id (for idempotency)."""
        query = (
            self.client.table("lynx_drafts")
            .select("*")
            .eq("tenant_id", tenant_id)
            .eq("request_id", request_id)
        )
        
        if draft_type:
            query = query.eq("draft_type", draft_type)
        
        result = query.limit(1).execute()
        
        if result.data:
            return self._from_db_record(result.data[0])
        return None
    
    def _from_db_record(self, record: Dict[str, Any]) -> DraftProtocol:
        """Convert DB record to DraftProtocol."""
        return DraftProtocol(
            draft_id=str(record["draft_id"]),
            tenant_id=record["tenant_id"],
            draft_type=record["draft_type"],
            payload=record["payload"],
            status=DraftStatus(record["status"]),
            risk_level=record["risk_level"],
            created_by=record["created_by"],
            created_at=record["created_at"],
            source_context=record["source_context"],
            recommended_approvers=record.get("recommended_approvers", []),
            request_id=record.get("request_id"),
        )


# Global storage instance
_draft_storage: Optional[DraftStorage] = None


def get_draft_storage() -> DraftStorage:
    """
    Get the global draft storage instance.
    
    Returns Supabase storage if configured, otherwise in-memory.
    """
    global _draft_storage
    
    if _draft_storage is None:
        # Try Supabase first
        if SUPABASE_AVAILABLE and Config.SUPABASE_URL and Config.SUPABASE_KEY:
            try:
                _draft_storage = DraftStorageSupabase()
            except Exception:
                # Fallback to in-memory
                _draft_storage = DraftStorage()
        else:
            _draft_storage = DraftStorage()
    
    return _draft_storage

