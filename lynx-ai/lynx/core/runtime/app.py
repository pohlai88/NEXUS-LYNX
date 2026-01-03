"""
MCPApp initialization for Lynx AI.

This module initializes the mcp-agent MCPApp and core components following
mcp-agent best practices and PRD-LYNX-003 requirements.
"""

from typing import Optional
import os
import yaml
from pathlib import Path

# MCPApp is initialized lazily when needed (not at module import time)
# This prevents errors when the daemon doesn't need MCPApp
app = None

def get_app():
    """
    Get or create MCPApp instance (lazy initialization).
    
    Returns properly configured MCPApp using mcp-agent Settings object
    following the framework's best practices and PRD-LYNX-003 requirements.
    
    Configuration is loaded from:
    1. mcp_agent.config.yaml (if exists) - mcp-agent framework config
    2. Environment variables - fallback values
    3. Defaults - safe production defaults
    """
    global app
    if app is None:
        from mcp_agent.app import MCPApp
        from mcp_agent.config import Settings, LoggerSettings
        from pathlib import Path
        
        # Check for mcp-agent config file (framework standard)
        # Following mcp-agent patterns from examples/basic/mcp_basic_agent/
        config_path = Path("mcp_agent.config.yaml")
        
        # If config file exists, MCPApp will load it automatically (preferred)
        # This follows the framework pattern: let MCPApp handle config loading
        if config_path.exists():
            # Let mcp-agent load config from file (preferred pattern)
            # MCPApp automatically loads mcp_agent.config.yaml and mcp_agent.secrets.yaml
            app = MCPApp(name="lynx")
        else:
            # Build Settings object programmatically (fallback for Railway/env-only)
            # Following mcp-agent patterns from examples
            # Best practice: Use transports array when programmatic, but LoggerSettings
            # accepts 'type' for single transport (backward compatibility)
            log_transports = ["console"]
            if os.getenv("LOG_FILE_ENABLED", "false").lower() == "true":
                log_transports.append("file")
            
            # Use 'type' for single transport (framework supports both patterns)
            log_type = "file" if "file" in log_transports else "console"
            
            settings = Settings(
                execution_engine="asyncio",
                logger=LoggerSettings(
                    type=log_type,  # Single transport (framework accepts this)
                    level=os.getenv("LOG_LEVEL", "info"),
                ),
            )
            
            app = MCPApp(
                name="lynx",
                settings=settings,
            )
    return app


def load_config(config_path: Optional[str] = None) -> dict:
    """Load configuration from YAML file or use environment variables."""
    if config_path is None:
        config_path = os.getenv(
            "LYNX_CONFIG_PATH", "config/config.yaml"
        )
    
    # If config file doesn't exist, use environment variables only
    if not os.path.exists(config_path):
        # For Railway deployment, use environment variables directly
        # Config file is optional when all values come from env vars
        return {
            "execution_engine": "asyncio",
            "logger": {
                "transports": ["console"],
                "level": os.getenv("LOG_LEVEL", "info"),
            },
            "supabase": {
                "url": os.getenv("SUPABASE_URL", ""),
                "key": os.getenv("SUPABASE_KEY", ""),
            },
            "openai": {
                "api_key": os.getenv("OPENAI_API_KEY", ""),
            },
            "kernel": {
                "api_url": os.getenv("KERNEL_API_URL", ""),
                "api_key": os.getenv("KERNEL_API_KEY", ""),
            },
        }
    
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

