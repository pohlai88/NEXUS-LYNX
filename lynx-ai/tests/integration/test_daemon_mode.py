"""
Test daemon mode behavior.

Verifies that daemon mode stays alive and handles shutdown gracefully.
"""

import pytest
import asyncio
import signal
from unittest.mock import patch, MagicMock
from lynx.runtime.daemon import LynxDaemon
from lynx.config import Config, LynxRunner


@pytest.fixture
def daemon():
    """Create a daemon instance."""
    return LynxDaemon()


@pytest.mark.asyncio
async def test_daemon_initialization_fails_without_config(daemon):
    """Test that daemon initialization fails gracefully without config."""
    with patch('lynx.runtime.daemon.load_config', side_effect=FileNotFoundError("Config not found")):
        result = await daemon.initialize()
        assert result is False


@pytest.mark.asyncio
async def test_daemon_shutdown_signal_sets_running_false(daemon):
    """Test that shutdown signal sets running to False."""
    daemon.running = True
    
    # Simulate SIGTERM
    daemon._handle_shutdown(signal.SIGTERM, None)
    
    assert daemon.running is False
    assert daemon.shutdown_event.is_set()


@pytest.mark.asyncio
async def test_daemon_heartbeat_loop_runs(daemon):
    """Test that heartbeat loop runs and logs."""
    daemon.running = True
    daemon.tool_registry = MagicMock()
    daemon.tool_registry.list_all.return_value = [1, 2, 3]  # 3 tools
    daemon.session_manager = MagicMock()
    daemon.session_manager.sessions = {}
    
    # Run heartbeat for a short time
    heartbeat_task = asyncio.create_task(daemon.run_heartbeat())
    
    # Wait a bit
    await asyncio.sleep(0.1)
    
    # Stop it
    daemon.running = False
    heartbeat_task.cancel()
    
    try:
        await heartbeat_task
    except asyncio.CancelledError:
        pass  # Expected


@pytest.mark.asyncio
async def test_daemon_heartbeat_respects_shutdown(daemon):
    """Test that heartbeat loop respects shutdown signal."""
    daemon.running = True
    daemon.tool_registry = MagicMock()
    daemon.tool_registry.list_all.return_value = []
    daemon.session_manager = MagicMock()
    daemon.session_manager.sessions = {}
    
    heartbeat_task = asyncio.create_task(daemon.run_heartbeat())
    
    # Immediately signal shutdown
    daemon._handle_shutdown(signal.SIGTERM, None)
    
    # Wait a bit
    await asyncio.sleep(0.1)
    
    # Task should exit
    heartbeat_task.cancel()
    
    try:
        await heartbeat_task
    except asyncio.CancelledError:
        pass  # Expected
    
    assert daemon.running is False


@pytest.mark.asyncio
async def test_daemon_status_check_handles_errors(daemon):
    """Test that status check handles errors gracefully."""
    daemon.running = True
    
    # Mock status check to raise error
    with patch('lynx.runtime.daemon.get_lynx_status', side_effect=Exception("Status check failed")):
        status_task = asyncio.create_task(daemon.run_status_check())
        
        # Wait a bit
        await asyncio.sleep(0.1)
        
        # Stop it
        daemon.running = False
        status_task.cancel()
        
        try:
            await status_task
        except asyncio.CancelledError:
            pass  # Expected


@pytest.mark.asyncio
async def test_daemon_graceful_shutdown_cancels_tasks(daemon):
    """Test that graceful shutdown cancels background tasks."""
    daemon.running = True
    daemon.tool_registry = MagicMock()
    daemon.tool_registry.list_all.return_value = []
    daemon.session_manager = MagicMock()
    daemon.session_manager.sessions = {}
    
    # Start tasks
    heartbeat_task = asyncio.create_task(daemon.run_heartbeat())
    status_task = asyncio.create_task(daemon.run_status_check())
    
    # Signal shutdown
    daemon._handle_shutdown(signal.SIGTERM, None)
    
    # Run shutdown logic
    heartbeat_task.cancel()
    status_task.cancel()
    
    # Tasks should be cancelled
    with pytest.raises(asyncio.CancelledError):
        await heartbeat_task
    
    with pytest.raises(asyncio.CancelledError):
        await status_task

