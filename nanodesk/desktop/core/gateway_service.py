"""Gateway service that can be started from the desktop app."""

import asyncio
import threading
from typing import Optional

from PySide6.QtCore import QObject, Signal


class GatewayService(QObject):
    """Service for running nanobot gateway in background thread."""
    
    log_message = Signal(str)
    status_changed = Signal(bool)  # running
    error_occurred = Signal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()
        self._is_running = False
    
    @property
    def is_running(self) -> bool:
        return self._is_running
    
    def start(self) -> bool:
        """Start gateway in background thread."""
        if self._is_running:
            return True
        
        try:
            self._stop_event.clear()
            self._thread = threading.Thread(target=self._run_gateway, daemon=True)
            self._thread.start()
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
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=5)
        
        self._is_running = False
        self.status_changed.emit(False)
    
    def _run_gateway(self):
        """Run gateway in thread."""
        try:
            # Import here to avoid issues with Qt thread
            import asyncio
            
            # Inject nanodesk
            from nanodesk import bootstrap
            bootstrap.inject()
            
            # Import nanobot components
            from nanobot.config.loader import load_config
            from nanobot.bus.queue import MessageBus
            from nanobot.agent.loop import AgentLoop
            from nanobot.channels.manager import ChannelManager
            from nanobot.session.manager import SessionManager
            from nanobot.cron.service import CronService
            from nanobot.heartbeat.service import HeartbeatService
            from nanobot.providers.litellm_provider import LiteLLMProvider
            
            # Load config
            config = load_config()
            
            # Create event loop for this thread
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            # Initialize components
            bus = MessageBus()
            
            # Get provider
            provider_name = config.agents.defaults.provider
            provider_config = getattr(config.providers, provider_name, None)
            
            if provider_config and provider_config.api_key:
                provider = LiteLLMProvider(
                    api_key=provider_config.api_key,
                    api_base=provider_config.api_base or None,
                    default_model=config.agents.defaults.model,
                    provider_name=provider_name
                )
            else:
                # Fallback to default
                provider = LiteLLMProvider(default_model=config.agents.defaults.model)
            
            # Create agent
            agent = AgentLoop(
                bus=bus,
                provider=provider,
                workspace=config.workspace_path,
                model=config.agents.defaults.model,
                brave_api_key=config.tools.web.search.api_key or None,
                exec_config=config.tools.exec,
                cron_service=CronService(),
                restrict_to_workspace=config.tools.exec.restrict_to_workspace,
            )
            
            # Create channel manager
            channel_manager = ChannelManager(
                config=config.channels,
                message_bus=bus,
            )
            
            # Create heartbeat service
            heartbeat = HeartbeatService(
                bus=bus,
                prompt=config.agents.heartbeat.prompt if config.agents.heartbeat else None,
                interval=config.agents.heartbeat.interval if config.agents.heartbeat else 300,
            )
            
            # Start services
            self.log_message.emit("Starting Gateway...")
            
            async def run_services():
                # Start channels
                await channel_manager.start()
                self.log_message.emit(f"Gateway listening on port {config.gateway.port}")
                
                # Start agent
                agent_task = asyncio.create_task(agent.run())
                
                # Start heartbeat if enabled
                if config.agents.heartbeat and config.agents.heartbeat.enabled:
                    heartbeat_task = asyncio.create_task(heartbeat.run())
                else:
                    heartbeat_task = None
                
                # Wait for stop signal
                while not self._stop_event.is_set():
                    await asyncio.sleep(0.1)
                
                # Stop services
                agent.stop()
                await channel_manager.stop()
                if heartbeat_task:
                    heartbeat.stop()
                
                # Cancel tasks
                agent_task.cancel()
                try:
                    await agent_task
                except asyncio.CancelledError:
                    pass
                
                if heartbeat_task:
                    heartbeat_task.cancel()
                    try:
                        await heartbeat_task
                    except asyncio.CancelledError:
                        pass
            
            # Run until stopped
            loop.run_until_complete(run_services())
            loop.close()
            
            self.log_message.emit("Gateway stopped")
            
        except Exception as e:
            self.error_occurred.emit(f"Gateway error: {e}")
        finally:
            self._is_running = False
            self.status_changed.emit(False)


# Singleton instance
_service = None


def get_gateway_service() -> GatewayService:
    """Get singleton GatewayService instance."""
    global _service
    if _service is None:
        _service = GatewayService()
    return _service
