"""
Draft Protocol - Shared draft model and storage interface.

This module defines the Draft Protocol that all Cluster MCPs must follow.
"""

from lynx.mcp.cluster.drafts.models import DraftProtocol, DraftStatus
from lynx.mcp.cluster.drafts.base import (
    create_draft,
)

__all__ = [
    "DraftProtocol",
    "DraftStatus",
    "create_draft",
]

