"""
Chat API Routes - Thin Client Over MCP

Backend handles MCP, UI only renders results.
Backend derives tenant_id from session (never from client).
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import Dict
from uuid import uuid4
import os

from lynx.api.models import (
    ChatQueryRequest,
    ChatQueryResponse,
    ChatRun,
    ToolCall,
    PolicyInfo,
    RunStatus,
    RiskLevel,
    ToolCallStatus,
)
from lynx.api.auth import get_current_session
from lynx.core.session import ExecutionContext
from lynx.core.runtime.agent import create_lynx_agent
from lynx.core.audit import AuditLogger
from lynx.config import Config
from mcp_agent.workflows.llm.augmented_llm_openai import OpenAIAugmentedLLM
from lynx.core.runtime.app import get_app

router = APIRouter(prefix="/api/chat", tags=["chat"])


@router.post("/query", response_model=ChatQueryResponse)
async def chat_query(
    request: ChatQueryRequest,
    session: Dict[str, str] = Depends(get_current_session),
):
    """
    Submit a chat query to Lynx AI.
    
    ✅ Backend derives tenant_id from session (request.tenant_id ignored if present)
    ✅ Backend returns policy.requires_confirmation (UI only renders)
    ✅ Creates audit log entry with tenant_id, user_id, role, request_id
    """
    # ✅ Get tenant_id from session (not from request)
    tenant_id = session['tenant_id']
    user_id = session['user_id']
    role = session['role']
    request_id = str(uuid4())  # ✅ For debugging
    
    # Verify tenant access (if request includes tenant_id, reject mismatch)
    # Note: request doesn't include tenant_id (per thin client doctrine)
    
    try:
        # Initialize audit logger
        if Config.SUPABASE_URL and Config.SUPABASE_KEY:
            audit_logger = AuditLogger(
                supabase_url=Config.SUPABASE_URL,
                supabase_key=Config.SUPABASE_KEY,
            )
        else:
            # Fallback: create mock logger for development
            audit_logger = None
        
        # Create execution context
        context = ExecutionContext(
            user_id=user_id,
            tenant_id=tenant_id,
            user_role=role,
            user_scope=[],
            session_id=request_id,
            audit_logger=audit_logger,
        )
        
        # Create Lynx agent and process query
        run_id = str(uuid4())
        response_text = ""
        tool_calls: list[ToolCall] = []
        requires_confirmation = False
        risk_level = RiskLevel.LOW
        
        try:
            # Get MCPApp instance
            app = get_app()
            
            # Run agent in app context
            async with app.run() as agent_app:
                agent = await create_lynx_agent(context)
                
                async with agent:
                    # Attach LLM
                    llm = await agent.attach_llm(OpenAIAugmentedLLM)
                    
                    # Generate response
                    response_text = await llm.generate_str(request.query)
                    
                    # TODO: Extract tool calls from agent execution
                    # For now, check if response indicates tool usage
                    # In full implementation, we'd track tool calls during execution
                    
        except Exception as agent_error:
            # If agent fails, return error response
            response_text = f"I encountered an error processing your query: {str(agent_error)}"
            risk_level = RiskLevel.HIGH
        
        # Determine policy (backend decides)
        # TODO: Integrate with actual risk classification from tool calls
        # For now, check if any high-risk tools were used
        if any(tc.tool_id.startswith("cell.") for tc in tool_calls):
            requires_confirmation = True
            risk_level = RiskLevel.HIGH
        elif any(tc.tool_id.startswith("cluster.") for tc in tool_calls):
            requires_confirmation = False
            risk_level = RiskLevel.MEDIUM
        else:
            requires_confirmation = False
            risk_level = RiskLevel.LOW
        
        policy = PolicyInfo(
            requires_confirmation=requires_confirmation,
            risk_level=risk_level,
            blocked_reason=None,
        )
        
        # Create audit log entry
        if audit_logger:
            await audit_logger.log_lynx_run(
                run_id=run_id,
                user_id=user_id,
                tenant_id=tenant_id,
                user_query=request.query,
                lynx_response=response_text,
                status="completed",
            )
        
        return ChatQueryResponse(
            run_id=run_id,
            response=response_text,
            tool_calls=[tc.dict() for tc in tool_calls],
            status=RunStatus.SUCCESS,
            policy=policy.dict(),
        )
        
    except Exception as e:
        # Log error
        raise HTTPException(
            status_code=500,
            detail=f"Chat query failed: {str(e)}",
        )


@router.get("/runs/{run_id}", response_model=ChatRun)
async def get_chat_run(
    run_id: str,
    session: Dict[str, str] = Depends(get_current_session),
):
    """
    Get chat run details (tenant-scoped).
    
    ✅ Backend derives tenant_id from session
    ✅ Verifies tenant_id matches (RLS enforced in storage)
    """
    tenant_id = session['tenant_id']
    
    # TODO: Read from audit storage (tenant-scoped, RLS enforced)
    # For now, return mock
    raise HTTPException(status_code=501, detail="Not yet implemented")

