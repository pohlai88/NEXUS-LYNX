"""
Settlement Intent Storage - Supabase backend implementation.

Stores settlement intent objects for payment executions.
"""

from typing import Dict, Any, Optional
from pydantic import BaseModel, Field
from lynx.config import Config

try:
    from supabase import create_client, Client
    SUPABASE_AVAILABLE = True
except ImportError:
    SUPABASE_AVAILABLE = False
    Client = None


class SettlementIntent(BaseModel):
    """Settlement Intent object for payment execution."""
    payment_id: str = Field(description="Payment ID")
    settlement_status: str = Field(default="queued", description="Settlement status")
    provider: str = Field(default="none", description="Settlement provider (none|manual|bank_x)")
    tenant_id: str = Field(description="Tenant ID")
    created_at: Optional[str] = Field(default=None, description="Creation timestamp")
    updated_at: Optional[str] = Field(default=None, description="Update timestamp")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class SettlementIntentStorage:
    """
    Base settlement intent storage interface (in-memory implementation).
    
    This is the fallback when Supabase is not available or in testing.
    """
    
    def __init__(self):
        """Initialize settlement intent storage."""
        self.intents: Dict[str, SettlementIntent] = {}  # payment_id -> SettlementIntent
    
    async def create_intent(self, intent: SettlementIntent) -> SettlementIntent:
        """Create a settlement intent."""
        self.intents[intent.payment_id] = intent
        return intent
    
    async def get_intent(self, payment_id: str, tenant_id: str) -> Optional[SettlementIntent]:
        """Get a settlement intent by payment_id (tenant-scoped)."""
        intent = self.intents.get(payment_id)
        if intent and intent.tenant_id == tenant_id:
            return intent
        return None
    
    async def update_status(
        self,
        payment_id: str,
        tenant_id: str,
        new_status: str,
    ) -> Optional[SettlementIntent]:
        """Update settlement status."""
        intent = await self.get_intent(payment_id, tenant_id)
        if intent:
            intent.settlement_status = new_status
            from datetime import datetime
            intent.updated_at = datetime.now().isoformat()
            self.intents[payment_id] = intent
        return intent


class SettlementIntentStorageSupabase(SettlementIntentStorage):
    """
    Supabase-backed settlement intent storage.
    
    Preserves tenant isolation (RLS + code checks).
    """
    
    def __init__(self, supabase_client: Optional[Client] = None):
        """
        Initialize Supabase settlement intent storage.
        
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
    
    async def create_intent(self, intent: SettlementIntent) -> SettlementIntent:
        """Create a settlement intent."""
        from datetime import datetime
        
        db_record = {
            "payment_id": intent.payment_id,
            "settlement_status": intent.settlement_status,
            "provider": intent.provider,
            "tenant_id": intent.tenant_id,
            "created_at": intent.created_at or datetime.now().isoformat(),
            "updated_at": intent.updated_at or datetime.now().isoformat(),
            "metadata": intent.metadata,
        }
        
        self.client.table("settlement_intents").insert(db_record).execute()
        
        return intent
    
    async def get_intent(self, payment_id: str, tenant_id: str) -> Optional[SettlementIntent]:
        """Get a settlement intent by payment_id (tenant-scoped)."""
        # Defense-in-depth: check tenant in query
        result = (
            self.client.table("settlement_intents")
            .select("*")
            .eq("payment_id", payment_id)
            .eq("tenant_id", tenant_id)  # Tenant check in code
            .single()
            .execute()
        )
        
        if not result.data:
            return None
        
        return self._from_db_record(result.data)
    
    async def update_status(
        self,
        payment_id: str,
        tenant_id: str,
        new_status: str,
    ) -> Optional[SettlementIntent]:
        """Update settlement status."""
        from datetime import datetime
        
        # Defense-in-depth: check tenant in update
        result = (
            self.client.table("settlement_intents")
            .update({
                "settlement_status": new_status,
                "updated_at": datetime.now().isoformat(),
            })
            .eq("payment_id", payment_id)
            .eq("tenant_id", tenant_id)  # Tenant check in code
            .execute()
        )
        
        if not result.data:
            return None
        
        return self._from_db_record(result.data[0])
    
    def _from_db_record(self, record: Dict[str, Any]) -> SettlementIntent:
        """Convert DB record to SettlementIntent."""
        return SettlementIntent(
            payment_id=record["payment_id"],
            settlement_status=record["settlement_status"],
            provider=record["provider"],
            tenant_id=record["tenant_id"],
            created_at=record.get("created_at"),
            updated_at=record.get("updated_at"),
            metadata=record.get("metadata", {}),
        )


# Global storage instance
_settlement_storage: Optional[SettlementIntentStorage] = None


def get_settlement_storage() -> SettlementIntentStorage:
    """
    Get the global settlement intent storage instance.
    
    Returns Supabase storage if configured, otherwise in-memory.
    """
    global _settlement_storage
    
    if _settlement_storage is None:
        # Try Supabase first
        if SUPABASE_AVAILABLE and Config.SUPABASE_URL and Config.SUPABASE_KEY:
            try:
                _settlement_storage = SettlementIntentStorageSupabase()
            except Exception:
                # Fallback to in-memory
                _settlement_storage = SettlementIntentStorage()
        else:
            _settlement_storage = SettlementIntentStorage()
    
    return _settlement_storage

