"""
MCP-Agent Framework Bridge for Lynx AI.

This module bridges Lynx's custom tool registry with mcp-agent's tool system,
allowing us to leverage framework benefits while maintaining PRD-specific features.

Following PRD-LYNX-003 requirements and mcp-agent best practices.
"""

from typing import List
from lynx.core.registry import MCPToolRegistry, MCPTool
from lynx.core.runtime.app import get_app


class MCPAgentBridge:
    """
    Bridge between Lynx custom tool registry and mcp-agent framework.
    
    This allows us to:
    1. Keep custom registry for PRD-specific features (layer, risk, domain)
    2. Register tools with mcp-agent for framework benefits (discovery, versioning)
    3. Maintain backward compatibility with existing code
    """
    
    def __init__(self, registry: MCPToolRegistry):
        """
        Initialize the bridge.
        
        Args:
            registry: Lynx custom tool registry
        """
        self.registry = registry
        self._app = None
    
    @property
    def app(self):
        """Get MCPApp instance (lazy)."""
        if self._app is None:
            self._app = get_app()
        return self._app
    
    def register_all_tools(self) -> None:
        """
        Register all tools from custom registry with mcp-agent.
        
        This creates mcp-agent compatible tool definitions from our custom
        MCPTool objects, allowing the framework to discover and manage them.
        
        Note: This is a bridge for future integration. Currently, we maintain
        the custom registry as primary. Full mcp-agent integration will be
        implemented in Phase 2 of recovery plan.
        """
        # Future implementation:
        # 1. Convert custom MCPTool to mcp-agent Tool format
        # 2. Register with mcp-agent app using @app.tool() decorator pattern
        # 3. Maintain backward compatibility with custom registry
        
        # For now, this is a placeholder for future enhancement
        # The custom registry continues to work as primary system
        pass
    
    def _schema_to_json_schema(self, schema_class) -> dict:
        """
        Convert Pydantic schema to JSON Schema format.
        
        Args:
            schema_class: Pydantic BaseModel class
            
        Returns:
            JSON Schema properties dict
        """
        if hasattr(schema_class, "model_json_schema"):
            schema = schema_class.model_json_schema()
            return schema.get("properties", {})
        return {}
    
    def _get_required_fields(self, schema_class) -> List[str]:
        """
        Extract required fields from Pydantic schema.
        
        Args:
            schema_class: Pydantic BaseModel class
            
        Returns:
            List of required field names
        """
        if hasattr(schema_class, "model_json_schema"):
            schema = schema_class.model_json_schema()
            return schema.get("required", [])
        return []


def bridge_tools_to_mcp_agent(registry: MCPToolRegistry) -> MCPAgentBridge:
    """
    Create bridge and register tools with mcp-agent.
    
    Args:
        registry: Lynx custom tool registry
        
    Returns:
        MCPAgentBridge instance
    """
    bridge = MCPAgentBridge(registry)
    # Future: bridge.register_all_tools() when full integration is ready
    return bridge

