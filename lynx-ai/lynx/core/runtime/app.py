"""
MCPApp initialization for Lynx AI.

This module initializes the mcp-agent MCPApp and core components.
"""

from mcp_agent.app import MCPApp
from typing import Optional
import os
import yaml

# Initialize MCPApp
app = MCPApp(
    name="lynx",
    settings={
        "execution_engine": "asyncio",
        "logger": {
            "transports": ["console", "file"],
            "level": os.getenv("LOG_LEVEL", "info"),
        },
    },
)


def load_config(config_path: Optional[str] = None) -> dict:
    """Load configuration from YAML file."""
    if config_path is None:
        config_path = os.getenv(
            "LYNX_CONFIG_PATH", "config/config.yaml"
        )
    
    if not os.path.exists(config_path):
        raise FileNotFoundError(
            f"Configuration file not found: {config_path}. "
            "Please copy config/config.yaml.example to config/config.yaml"
        )
    
    with open(config_path, "r") as f:
        config = yaml.safe_load(f)
    
    # Replace environment variables
    def replace_env_vars(obj):
        if isinstance(obj, dict):
            return {k: replace_env_vars(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [replace_env_vars(item) for item in obj]
        elif isinstance(obj, str) and obj.startswith("${") and obj.endswith("}"):
            env_var = obj[2:-1]
            return os.getenv(env_var, obj)
        return obj
    
    return replace_env_vars(config)


# Global config (will be loaded on startup)
config: Optional[dict] = None

