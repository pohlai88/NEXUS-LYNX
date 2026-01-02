"""
Lynx Runtime Components

Contains daemon and server runtime implementations.
"""

from lynx.runtime.daemon import LynxDaemon, main as daemon_main

__all__ = ["LynxDaemon", "daemon_main"]

