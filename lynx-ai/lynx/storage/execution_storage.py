"""
Execution Storage - Supabase backend implementation.

Preserves all Execution Protocol guarantees:
- Idempotency (request_id)
- Exactly-once semantics (one successful execution per draft_id per tool_id)
- Tenant isolation
"""

from typing import Dict, Any, Optional, List
from lynx.config import Config

# Import models (separated to avoid circular imports)
from lynx.mcp.cell.execution.models import ExecutionRecord, ExecutionStatus

try:
    from supabase import create_client, Client
    SUPABASE_AVAILABLE = True
except ImportError:
    SUPABASE_AVAILABLE = False
    Client = None


class ExecutionStorage:
    """
    Base execution storage interface (in-memory implementation).
    
    This is the fallback when Supabase is not available or in testing.
    """
    
    def __init__(self):
        """Initialize execution storage."""
        self.executions: Dict[str, ExecutionRecord] = {}
        self.request_id_map: Dict[str, str] = {}  # request_id -> execution_id
    
    async def create_execution(self, execution: ExecutionRecord) -> ExecutionRecord:
        """Create an execution record."""
        # Check idempotency
        if execution.request_id and execution.request_id in self.request_id_map:
            existing_execution_id = self.request_id_map[execution.request_id]
            return self.executions[existing_execution_id]
        
        # Store execution
        self.executions[execution.execution_id] = execution
        
        # Map request_id for idempotency
        if execution.request_id:
            self.request_id_map[execution.request_id] = execution.execution_id
        
        return execution
    
    async def get_execution(self, execution_id: str, tenant_id: str) -> Optional[ExecutionRecord]:
        """Get an execution record by ID (tenant-scoped)."""
        execution = self.executions.get(execution_id)
        if execution and execution.tenant_id == tenant_id:
            return execution
        return None
    
    async def list_executions(
        self,
        tenant_id: str,
        draft_id: Optional[str] = None,
        tool_id: Optional[str] = None,
        status: Optional[ExecutionStatus] = None,
    ) -> List[ExecutionRecord]:
        """List executions for a tenant."""
        executions = [e for e in self.executions.values() if e.tenant_id == tenant_id]
        
        if draft_id:
            executions = [e for e in executions if e.draft_id == draft_id]
        
        if tool_id:
            executions = [e for e in executions if e.tool_id == tool_id]
        
        if status:
            executions = [e for e in executions if e.status == status]
        
        return executions
    
    async def update_execution_status(
        self,
        execution_id: str,
        status: ExecutionStatus,
        result_payload: Optional[Dict[str, Any]] = None,
        error_message: Optional[str] = None,
        rollback_instructions: Optional[Dict[str, Any]] = None,
    ) -> Optional[ExecutionRecord]:
        """Update execution status."""
        execution = self.executions.get(execution_id)
        if execution:
            execution.status = status
            if result_payload:
                execution.result_payload.update(result_payload)
            execution.error_message = error_message
            execution.rollback_instructions = rollback_instructions
            from datetime import datetime
            execution.completed_at = datetime.now().isoformat()
        return execution


class ExecutionStorageSupabase(ExecutionStorage):
    """
    Supabase-backed execution storage.
    
    Preserves all guarantees:
    - Idempotency via request_id
    - Exactly-once semantics (DB-level unique constraint)
    - Tenant isolation (RLS + code checks)
    """
    
    def __init__(self, supabase_client: Optional[Client] = None):
        """
        Initialize Supabase execution storage.
        
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
    
    async def create_execution(self, execution: ExecutionRecord) -> ExecutionRecord:
        """Create an execution record with idempotency check."""
        # Check idempotency: query by request_id (if provided)
        if execution.request_id:
            existing = await self._get_by_request_id(execution.tenant_id, execution.request_id)
            if existing:
                return existing
        
        # Convert to DB format
        db_record = {
            "execution_id": execution.execution_id,
            "draft_id": execution.draft_id,
            "tool_id": execution.tool_id,
            "tenant_id": execution.tenant_id,
            "actor_id": execution.actor_id,
            "status": execution.status.value,
            "result_payload": execution.result_payload,
            "created_at": execution.created_at,
            "completed_at": execution.completed_at,
            "error_message": execution.error_message,
            "rollback_instructions": execution.rollback_instructions,
            "request_id": execution.request_id,
            "source_context": execution.source_context,
        }
        
        # Insert (will fail if unique constraint violated for exactly-once)
        try:
            self.client.table("lynx_executions").insert(db_record).execute()
        except Exception as e:
            # If unique constraint violation (exactly-once), fetch existing
            if "unique" in str(e).lower() or "duplicate" in str(e).lower():
                # Check if it's the exactly-once constraint (draft_id + tool_id + succeeded)
                existing = await self._get_successful_execution(
                    execution.tenant_id,
                    execution.draft_id,
                    execution.tool_id,
                )
                if existing:
                    return existing
            # If request_id idempotency, fetch existing
            if execution.request_id:
                existing = await self._get_by_request_id(execution.tenant_id, execution.request_id)
                if existing:
                    return existing
            raise
        
        return execution
    
    async def get_execution(self, execution_id: str, tenant_id: str) -> Optional[ExecutionRecord]:
        """Get an execution record by ID (tenant-scoped)."""
        # Defense-in-depth: check tenant in query
        result = (
            self.client.table("lynx_executions")
            .select("*")
            .eq("execution_id", execution_id)
            .eq("tenant_id", tenant_id)  # Tenant check in code
            .single()
            .execute()
        )
        
        if not result.data:
            return None
        
        return self._from_db_record(result.data)
    
    async def list_executions(
        self,
        tenant_id: str,
        draft_id: Optional[str] = None,
        tool_id: Optional[str] = None,
        status: Optional[ExecutionStatus] = None,
    ) -> List[ExecutionRecord]:
        """List executions for a tenant."""
        query = (
            self.client.table("lynx_executions")
            .select("*")
            .eq("tenant_id", tenant_id)
            .order("created_at", desc=True)
        )
        
        if draft_id:
            query = query.eq("draft_id", draft_id)
        
        if tool_id:
            query = query.eq("tool_id", tool_id)
        
        if status:
            query = query.eq("status", status.value)
        
        result = query.execute()
        
        return [self._from_db_record(record) for record in result.data]
    
    async def update_execution_status(
        self,
        execution_id: str,
        status: ExecutionStatus,
        result_payload: Optional[Dict[str, Any]] = None,
        error_message: Optional[str] = None,
        rollback_instructions: Optional[Dict[str, Any]] = None,
    ) -> Optional[ExecutionRecord]:
        """Update execution status."""
        from datetime import datetime
        
        update_data: Dict[str, Any] = {
            "status": status.value,
            "completed_at": datetime.now().isoformat(),
        }
        
        if result_payload is not None:
            # Merge with existing payload
            existing = await self.get_execution(execution_id, "")  # Get without tenant check first
            if existing:
                merged_payload = existing.result_payload.copy()
                merged_payload.update(result_payload)
                update_data["result_payload"] = merged_payload
            else:
                update_data["result_payload"] = result_payload
        
        if error_message is not None:
            update_data["error_message"] = error_message
        
        if rollback_instructions is not None:
            update_data["rollback_instructions"] = rollback_instructions
        
        # Get tenant_id from existing execution
        existing = await self.get_execution(execution_id, "")  # Get without tenant check
        if not existing:
            return None
        
        # Defense-in-depth: check tenant in update
        result = (
            self.client.table("lynx_executions")
            .update(update_data)
            .eq("execution_id", execution_id)
            .eq("tenant_id", existing.tenant_id)  # Tenant check in code
            .execute()
        )
        
        if not result.data:
            return None
        
        return self._from_db_record(result.data[0])
    
    async def _get_by_request_id(
        self,
        tenant_id: str,
        request_id: str,
    ) -> Optional[ExecutionRecord]:
        """Get execution by request_id (for idempotency)."""
        result = (
            self.client.table("lynx_executions")
            .select("*")
            .eq("tenant_id", tenant_id)
            .eq("request_id", request_id)
            .limit(1)
            .execute()
        )
        
        if result.data:
            return self._from_db_record(result.data[0])
        return None
    
    async def _get_successful_execution(
        self,
        tenant_id: str,
        draft_id: str,
        tool_id: str,
    ) -> Optional[ExecutionRecord]:
        """Get successful execution for exactly-once check."""
        result = (
            self.client.table("lynx_executions")
            .select("*")
            .eq("tenant_id", tenant_id)
            .eq("draft_id", draft_id)
            .eq("tool_id", tool_id)
            .eq("status", ExecutionStatus.SUCCEEDED.value)
            .limit(1)
            .execute()
        )
        
        if result.data:
            return self._from_db_record(result.data[0])
        return None
    
    def _from_db_record(self, record: Dict[str, Any]) -> ExecutionRecord:
        """Convert DB record to ExecutionRecord."""
        return ExecutionRecord(
            execution_id=str(record["execution_id"]),
            draft_id=str(record["draft_id"]),
            tool_id=record["tool_id"],
            tenant_id=record["tenant_id"],
            actor_id=record["actor_id"],
            status=ExecutionStatus(record["status"]),
            result_payload=record.get("result_payload", {}),
            created_at=record["created_at"],
            completed_at=record.get("completed_at"),
            error_message=record.get("error_message"),
            rollback_instructions=record.get("rollback_instructions"),
            request_id=record.get("request_id"),
            source_context=record.get("source_context", {}),
        )


# Global storage instance
_execution_storage: Optional[ExecutionStorage] = None


def get_execution_storage() -> ExecutionStorage:
    """
    Get the global execution storage instance.
    
    Returns Supabase storage if configured, otherwise in-memory.
    """
    global _execution_storage
    
    if _execution_storage is None:
        # Try Supabase first
        if SUPABASE_AVAILABLE and Config.SUPABASE_URL and Config.SUPABASE_KEY:
            try:
                _execution_storage = ExecutionStorageSupabase()
            except Exception:
                # Fallback to in-memory
                _execution_storage = ExecutionStorage()
        else:
            _execution_storage = ExecutionStorage()
    
    return _execution_storage

