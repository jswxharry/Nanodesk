"""Embedded gateway that runs in background thread.

This avoids the need for external Python and dependencies.
"""

import threading
import time
from typing import Optional

from PySide6.QtCore import QObject, Signal, QRunnable, QThreadPool


class GatewayWorker(QRunnable):
    """Worker to run gateway in Qt thread pool."""
    
    def __init__(self, stop_event):
        super().__init__()
        self.stop_event = stop_event
        self._is_running = False
    
    def run(self):
        """Run gateway."""
        try:
            # Import here to avoid circular imports
            from nanodesk import bootstrap
            bootstrap.inject()
            
            from nanobot.config.loader import load_config
            from nanobot.bus.queue import MessageBus
            from nanobot.agent.loop import AgentLoop
            from nanobot.channels.manager import ChannelManager
            from nanobot.cron.service import CronService
            from nanobot.providers.litellm_provider import LiteLLMProvider
            
            config = load_config()
            
            # Create components
            bus = MessageBus()
            provider = LiteLLMProvider(
                api_key=config.providers.dashscope.api_key if hasattr(config.providers, 'dashscope') else None,
                default_model=config.agents.defaults.model
            )
            
            agent = AgentLoop(
                bus=bus,
                provider=provider,
                workspace=config.workspace_path,
                model=config.agents.defaults.model,
                exec_config=config.tools.exec,
                cron_service=CronService(),
            )
            
            # Start in thread
            import asyncio
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            # Run until stopped
            while not self.stop_event.is_set():
                time.sleep(0.1)
            
            agent.stop()
            
        except Exception as e:
            print(f"Gateway error: {e}")


class EmbeddedGateway(QObject):
    """Gateway that runs embedded in the desktop app."""
    
    status_changed = Signal(bool)
    log_message = Signal(str)
    error_occurred = Signal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._stop_event = threading.Event()
        self._worker: Optional[GatewayWorker] = None
        self._is_running = False
    
    @property
    def is_running(self) -> bool:
        return self._is_running
    
    def start(self) -> bool:
        """Start gateway."""
        if self._is_running:
            return True
        
        try:
            self._stop_event.clear()
            self._worker = GatewayWorker(self._stop_event)
            QThreadPool.globalInstance().start(self._worker)
            self._is_running = True
            self.status_changed.emit(True)
            return True
        except Exception as e:
            self.error_occurred.emit(str(e))
            return False
    
    def stop(self):
        """Stop gateway."""
        if not self._is_running:
            return
        
        self._stop_event.set()
        self._is_running = False
        self.status_changed.emit(False)


# Singleton
_gateway = None

def get_embedded_gateway():
    global _gateway
    if _gateway is None:
        _gateway = EmbeddedGateway()
    return _gateway
