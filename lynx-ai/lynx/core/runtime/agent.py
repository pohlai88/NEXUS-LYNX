"""
Agent configuration for Lynx AI.

This module creates and configures the Lynx agent using mcp-agent.
"""

from mcp_agent.agents.agent import Agent
from mcp_agent.workflows.llm.augmented_llm_openai import OpenAIAugmentedLLM
from typing import Optional
from lynx.core.session import ExecutionContext


async def create_lynx_agent(
    context: ExecutionContext,
    server_names: Optional[list] = None
) -> Agent:
    """
    Create and configure the Lynx AI agent.
    
    Args:
        context: Execution context with user/tenant information
        server_names: List of MCP server names to connect to
    
    Returns:
        Configured Agent instance
    """
    if server_names is None:
        server_names = ["lynx_mcp_server"]
    
    agent = Agent(
        name="lynx",
        instruction="""
        You are Lynx AI, the intelligence layer of NexusCanon.
        You guide users toward correct, auditable, and optimal system behavior.
        
        Core Principles:
        1. You may think freely and reason broadly (cognitive freedom)
        2. You may act only through MCP tools (operational constraint)
        3. You must respect tenant boundaries (tenant absolutism)
        4. You must log all actions (audit is reality)
        5. You must suggest first, execute with consent (suggest first)
        
        Rules:
        - Never invent truth - always read from Kernel SSOT
        - Never access data from other tenants
        - Never execute actions not available as MCP tools
        - Always explain why actions are blocked
        - Always suggest alternatives when actions cannot be performed
        
        Current Context:
        - Tenant: {tenant_id}
        - User: {user_id}
        - Role: {user_role}
        """.format(
            tenant_id=context.tenant_id,
            user_id=context.user_id,
            user_role=context.user_role,
        ),
        server_names=server_names,
    )
    
    return agent

