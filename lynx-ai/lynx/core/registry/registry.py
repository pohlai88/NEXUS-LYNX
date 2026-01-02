"""
MCP tool registry.

Manages registration and discovery of MCP tools.
"""

from typing import Dict, List, Optional, Callable, Any
from dataclasses import dataclass
from pydantic import BaseModel, Field
from lynx.core.session import ExecutionContext


@dataclass
class MCPTool:
    """Represents an MCP tool."""
    id: str
    name: str
    description: str
    layer: str  # "domain" | "cluster" | "cell"
    risk: str   # "low" | "medium" | "high"
    domain: str
    input_schema: type[BaseModel]
    output_schema: type[BaseModel]
    required_role: List[str] = None
    required_scope: List[str] = None
    handler: Callable = None
    
    def __post_init__(self):
        """Validate tool configuration."""
        if self.layer not in ["domain", "cluster", "cell"]:
            raise ValueError(f"Invalid layer: {self.layer}")
        if self.risk not in ["low", "medium", "high"]:
            raise ValueError(f"Invalid risk level: {self.risk}")
        if self.required_role is None:
            self.required_role = []
        if self.required_scope is None:
            self.required_scope = []


class MCPToolRegistry:
    """Registry for MCP tools."""
    
    def __init__(self):
        """Initialize the registry."""
        self.tools: Dict[str, MCPTool] = {}
    
    def register(self, tool: MCPTool) -> None:
        """
        Register an MCP tool.
        
        Args:
            tool: MCPTool instance to register
        
        Raises:
            ValueError: If tool ID already exists
        """
        if tool.id in self.tools:
            raise ValueError(f"Tool {tool.id} already registered")
        self.tools[tool.id] = tool
    
    def get(self, tool_id: str) -> MCPTool:
        """
        Get a tool by ID.
        
        Args:
            tool_id: Tool ID
        
        Returns:
            MCPTool instance
        
        Raises:
            ValueError: If tool not found
        """
        if tool_id not in self.tools:
            raise ValueError(f"Tool {tool_id} not found")
        return self.tools[tool_id]
    
    def list_by_layer(self, layer: str) -> List[MCPTool]:
        """
        List tools by layer.
        
        Args:
            layer: Layer name ("domain", "cluster", or "cell")
        
        Returns:
            List of MCPTool instances
        """
        return [t for t in self.tools.values() if t.layer == layer]
    
    def list_by_domain(self, domain: str) -> List[MCPTool]:
        """
        List tools by domain.
        
        Args:
            domain: Domain name (e.g., "finance", "vendor")
        
        Returns:
            List of MCPTool instances
        """
        return [t for t in self.tools.values() if t.domain == domain]
    
    def list_by_risk(self, risk: str) -> List[MCPTool]:
        """
        List tools by risk level.
        
        Args:
            risk: Risk level ("low", "medium", or "high")
        
        Returns:
            List of MCPTool instances
        """
        return [t for t in self.tools.values() if t.risk == risk]
    
    def list_all(self) -> List[MCPTool]:
        """
        List all registered tools.
        
        Returns:
            List of all MCPTool instances
        """
        return list(self.tools.values())

