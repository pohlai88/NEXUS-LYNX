"""
Audit API Routes - Thin Client Over MCP

Backend provides audit trail, UI only renders.
Backend derives tenant_id from session (never from client).
"""

from fastapi import APIRouter, Depends, Query, HTTPException, Response
from typing import Optional, Dict, List
from datetime import datetime
import csv
import json
import io

from lynx.api.models import AuditRun, AuditListResponse, ToolCall, RunStatus, ToolCallStatus
from lynx.api.auth import get_current_session
from lynx.config import Config

try:
    from supabase import create_client, Client
    SUPABASE_AVAILABLE = True
except ImportError:
    SUPABASE_AVAILABLE = False
    Client = None

router = APIRouter(prefix="/api/audit", tags=["audit"])


def get_supabase_client() -> Optional[Client]:
    """Get Supabase client for audit queries."""
    if not SUPABASE_AVAILABLE:
        return None
    if not Config.SUPABASE_URL or not Config.SUPABASE_KEY:
        return None
    return create_client(Config.SUPABASE_URL, Config.SUPABASE_KEY)


@router.get("/runs", response_model=AuditListResponse)
async def list_runs(
    limit: int = Query(50),
    offset: int = Query(0),
    cursor: Optional[str] = Query(None),  # ✅ Cursor pagination (for future use)
    from_date: Optional[str] = Query(None),  # ISO 8601 date
    to_date: Optional[str] = Query(None),  # ISO 8601 date
    user_id: Optional[str] = Query(None),
    # ✅ CRITICAL: Never accept tenant_id from query params - only from session
    session: Dict[str, str] = Depends(get_current_session),
):
    """
    List Lynx Runs (audit trail).
    
    ✅ Backend derives tenant_id from session (NEVER from query params)
    ✅ Server-side filtering (date, user)
    ✅ Offset pagination (cursor TODO for future)
    """
    tenant_id = session['tenant_id']  # ✅ Source of truth: session, not query param
    
    client = get_supabase_client()
    if not client:
        # Fallback: return empty list if Supabase not available
        return AuditListResponse(
            runs=[],
            total=0,
            limit=limit,
            offset=offset,
            cursor=None,
        )
    
    # Build query (tenant-scoped, RLS enforced)
    # Note: Schema uses "timestamp" not "created_at" (check SETUP.md)
    query = client.table("lynx_runs").select("*").eq("tenant_id", tenant_id)
    
    # Apply filters
    if from_date:
        try:
            from_dt = datetime.fromisoformat(from_date.replace('Z', '+00:00'))
            query = query.gte("timestamp", from_dt.isoformat())
        except ValueError:
            raise HTTPException(400, f"Invalid from_date format: {from_date}")
    
    if to_date:
        try:
            to_dt = datetime.fromisoformat(to_date.replace('Z', '+00:00'))
            query = query.lte("timestamp", to_dt.isoformat())
        except ValueError:
            raise HTTPException(400, f"Invalid to_date format: {to_date}")
    
    if user_id:
        query = query.eq("user_id", user_id)
    
    # Order by timestamp descending (newest first)
    query = query.order("timestamp", desc=True)
    
    # Apply pagination
    query = query.range(offset, offset + limit - 1)
    
    # Execute query
    result = query.execute()
    
    # Get total count (for pagination metadata)
    count_query = client.table("lynx_runs").select("*", count="exact").eq("tenant_id", tenant_id)
    if from_date:
        from_dt = datetime.fromisoformat(from_date.replace('Z', '+00:00'))
        count_query = count_query.gte("timestamp", from_dt.isoformat())
    if to_date:
        to_dt = datetime.fromisoformat(to_date.replace('Z', '+00:00'))
        count_query = count_query.lte("timestamp", to_dt.isoformat())
    if user_id:
        count_query = count_query.eq("user_id", user_id)
    count_result = count_query.execute()
    total = count_result.count if hasattr(count_result, 'count') else len(result.data)
    
    # Convert to API models
    runs: List[AuditRun] = []
    for record in result.data:
        # Get tool calls summary for this run (from audit_logs table)
        tool_calls_result = client.table("audit_logs").select("tool_id, approved, refused").eq("run_id", record["run_id"]).execute()
        tool_calls = [
            ToolCall(
                tool_id=tc.get("tool_id", ""),
                status=ToolCallStatus("success" if tc.get("approved") else "error" if tc.get("refused") else "pending"),
                input={},
                output=None,
                duration_ms=None,  # Schema doesn't have duration_ms
                error=None,
            )
            for tc in tool_calls_result.data
        ]
        
        # Map status
        status_map = {
            "completed": RunStatus.SUCCESS,
            "failed": RunStatus.ERROR,
            "pending": RunStatus.PENDING,
        }
        run_status = status_map.get(record.get("status", "pending"), RunStatus.PENDING)
        
        # Parse dates (schema uses "timestamp" not "created_at")
        created_at = datetime.fromisoformat(record["timestamp"].replace('Z', '+00:00'))
        completed_at = None  # Schema doesn't have completed_at, use timestamp for now
        
        runs.append(AuditRun(
            run_id=record["run_id"],
            tenant_id=record["tenant_id"],  # ✅ For display only (already tenant-scoped)
            actor_user_id=record.get("user_id", ""),
            actor_role="user",  # Schema doesn't have user_role, use default
            request_id="",  # Schema doesn't have request_id, use empty
            query=record.get("user_query", ""),
            response=record.get("lynx_response", ""),
            tool_calls=tool_calls,
            created_at=created_at,
            completed_at=completed_at,
        ))
    
    return AuditListResponse(
        runs=runs,
        total=total,
        limit=limit,
        offset=offset,
        cursor=None,  # TODO: Implement cursor-based pagination
    )


@router.get("/runs/{run_id}", response_model=AuditRun)
async def get_run(
    run_id: str,
    session: Dict[str, str] = Depends(get_current_session),
):
    """
    Get run details (tenant-scoped).
    
    ✅ Backend derives tenant_id from session
    ✅ Verifies tenant_id matches (RLS enforced)
    """
    tenant_id = session['tenant_id']  # ✅ Source of truth: session
    
    client = get_supabase_client()
    if not client:
        raise HTTPException(503, "Audit storage not available")
    
    # Get run (tenant-scoped, RLS enforced)
    run_result = client.table("lynx_runs").select("*").eq("run_id", run_id).eq("tenant_id", tenant_id).execute()
    
    if not run_result.data:
        raise HTTPException(404, f"Run {run_id} not found")
    
    record = run_result.data[0]
    
    # ✅ Verify tenant_id matches session (double-check)
    if record["tenant_id"] != tenant_id:
        raise HTTPException(403, "Tenant access denied")
    
    # Get tool calls for this run (from audit_logs table, not lynx_tool_calls)
    tool_calls_result = client.table("audit_logs").select("*").eq("run_id", run_id).execute()
    tool_calls = [
        ToolCall(
            tool_id=tc.get("tool_id", ""),
            status=ToolCallStatus("success" if tc.get("approved") else "error" if tc.get("refused") else "pending"),
            input=tc.get("input", {}),
            output=tc.get("output"),
            duration_ms=None,  # Schema doesn't have duration_ms
            error=tc.get("refusal_reason") if tc.get("refused") else None,
        )
        for tc in tool_calls_result.data
    ]
    
    # Map status
    status_map = {
        "completed": RunStatus.SUCCESS,
        "failed": RunStatus.ERROR,
        "blocked": RunStatus.ERROR,
        "pending": RunStatus.PENDING,
    }
    run_status = status_map.get(record.get("status", "pending"), RunStatus.PENDING)
    
    # Parse dates (schema uses "timestamp" not "created_at")
    created_at = datetime.fromisoformat(record["timestamp"].replace('Z', '+00:00'))
    completed_at = None  # Schema doesn't have completed_at
    
    return AuditRun(
        run_id=record["run_id"],
        tenant_id=record["tenant_id"],  # ✅ For display only
        actor_user_id=record.get("user_id", ""),
        actor_role="user",  # Schema doesn't have user_role, use default
        request_id="",  # Schema doesn't have request_id, use empty
        query=record.get("user_query", ""),
        response=record.get("lynx_response", ""),
        tool_calls=tool_calls,
        created_at=created_at,
        completed_at=completed_at,
    )


@router.get("/runs/export")
async def export_audit(
    format: str = Query('csv'),  # csv or json
    from_date: Optional[str] = Query(None),
    to_date: Optional[str] = Query(None),
    # ✅ CRITICAL: Never accept tenant_id from query params - only from session
    session: Dict[str, str] = Depends(get_current_session),
):
    """
    Export audit logs (CSV or JSON).
    
    ✅ Backend derives tenant_id from session (NEVER from query params)
    ✅ Server-side filtering (date range)
    ✅ Returns file download (CSV or JSON)
    """
    tenant_id = session['tenant_id']  # ✅ Source of truth: session
    
    if format not in ['csv', 'json']:
        raise HTTPException(400, "Format must be 'csv' or 'json'")
    
    client = get_supabase_client()
    if not client:
        raise HTTPException(503, "Audit storage not available")
    
    # Build query (tenant-scoped, RLS enforced)
    query = client.table("lynx_runs").select("*").eq("tenant_id", tenant_id)
    
    # Apply date filters
    if from_date:
        try:
            from_dt = datetime.fromisoformat(from_date.replace('Z', '+00:00'))
            query = query.gte("created_at", from_dt.isoformat())
        except ValueError:
            raise HTTPException(400, f"Invalid from_date format: {from_date}")
    
    if to_date:
        try:
            to_dt = datetime.fromisoformat(to_date.replace('Z', '+00:00'))
            query = query.lte("created_at", to_dt.isoformat())
        except ValueError:
            raise HTTPException(400, f"Invalid to_date format: {to_date}")
    
    # Order by created_at descending
    query = query.order("created_at", desc=True)
    
    # Execute query (no limit for export)
    result = query.execute()
    
    if format == 'csv':
        # Generate CSV
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write header
        writer.writerow([
            "run_id", "timestamp", "user_id",
            "query", "response", "status"
        ])
        
        # Write rows
        for record in result.data:
            writer.writerow([
                record.get("run_id", ""),
                record.get("timestamp", ""),
                record.get("user_id", ""),
                record.get("user_query", ""),
                record.get("lynx_response", ""),
                record.get("status", ""),
            ])
        
        csv_content = output.getvalue()
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        return Response(
            content=csv_content,
            media_type='text/csv',
            headers={
                'Content-Disposition': f'attachment; filename="audit-{timestamp}.csv"'
            }
        )
    
    else:  # JSON
        # Generate JSON
        json_data = []
        for record in result.data:
            json_data.append({
                "run_id": record.get("run_id"),
                "timestamp": record.get("timestamp"),
                "user_id": record.get("user_id"),
                "query": record.get("user_query"),
                "response": record.get("lynx_response"),
                "status": record.get("status"),
            })
        
        json_content = json.dumps(json_data, indent=2)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        return Response(
            content=json_content,
            media_type='application/json',
            headers={
                'Content-Disposition': f'attachment; filename="audit-{timestamp}.json"'
            }
        )

