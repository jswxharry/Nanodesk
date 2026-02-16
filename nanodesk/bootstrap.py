"""Nanodesk Bootstrap - Customization injection

Automatically loads customizations before nanobot starts.
Includes power management for Gateway mode on Windows.
"""

import os
import socket
import sys
from pathlib import Path

# Windows encoding fix: set UTF-8 encoding to avoid Unicode errors
if sys.platform == "win32":
    os.environ.setdefault("PYTHONIOENCODING", "utf-8")


def _is_gateway_mode() -> bool:
    """Check if running in Gateway mode"""
    return "gateway" in sys.argv


GATEWAY_LOCK_PORT = 28790  # Port for single instance lock


def _ensure_single_gateway():
    """Use socket port lock to ensure single instance"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind(("127.0.0.1", GATEWAY_LOCK_PORT))
        sock.listen(1)
        return sock  # Keep reference, auto-released on process exit
    except OSError:
        # Port already in use - another Gateway is running
        print("Gateway already running")
        sys.exit(1)


# Global lock reference to prevent garbage collection
_gateway_lock = None


def inject():
    """Inject Nanodesk customization into nanobot.

    Registers custom tools, channels, and providers.
    """
    global _gateway_lock
    
    # Ensure project root is in path
    root = Path(__file__).parent.parent
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))

    # Patch Windows encoding for compatibility
    _patch_windows_encoding()

    print("[INFO] Loading Nanodesk customization...")

    # Monkey patch config schema to add Ollama support
    _patch_config_schema()
    
    # Monkey patch AgentLoop to register custom tools
    _patch_agent_loop()
    
    # Monkey patch provider factory to support Ollama
    _patch_provider_factory()

    print("[INFO] Nanodesk customization loaded")

    # Gateway mode: single instance lock + power management
    if _is_gateway_mode():
        # 1. Ensure single instance (prevent multiple instances)
        _gateway_lock = _ensure_single_gateway()

        # 2. Start power management (Windows only)
        if sys.platform == "win32":
            from nanodesk.desktop.core.power_manager import (
                prevent_sleep,
                start_power_monitor,
            )

            prevent_sleep()
            start_power_monitor()


def _patch_agent_loop():
    """Patch AgentLoop to register custom tools."""
    from nanobot.agent.loop import AgentLoop

    # Store original method
    original_register = AgentLoop._register_default_tools

    def _register_with_custom_tools(self):
        """Register default tools plus custom tools."""
        # Call original method
        original_register(self)

        # Register custom tools
        from nanodesk.tools.browser_search import BrowserFetchTool, BrowserSearchTool
        from nanodesk.tools.ddg_search import DuckDuckGoSearchTool

        self.tools.register(DuckDuckGoSearchTool())
        self.tools.register(BrowserSearchTool())
        self.tools.register(BrowserFetchTool())
        print("[INFO] Registered Nanodesk custom tools")

    # Replace method
    AgentLoop._register_default_tools = _register_with_custom_tools


def _patch_config_schema():
    """Patch config schema to add Ollama provider support."""
    from pydantic import Field
    from nanobot.config.schema import ProvidersConfig, ProviderConfig, AgentDefaults
    
    # Add provider field to AgentDefaults if not exists
    if 'provider' not in AgentDefaults.model_fields:
        AgentDefaults.model_fields['provider'] = Field(
            default="custom",
            description="LLM provider name"
        )
        AgentDefaults.model_rebuild(force=True)
        print(f"[INFO] Added provider field to AgentDefaults, fields={list(AgentDefaults.model_fields.keys())}")
    
    # Add ollama field to ProvidersConfig if not exists
    if 'ollama' not in ProvidersConfig.model_fields:
        ProvidersConfig.model_fields['ollama'] = Field(
            default_factory=ProviderConfig,
            description="Ollama local LLM provider"
        )
        ProvidersConfig.model_rebuild(force=True)
        print(f"[INFO] Added Ollama to ProvidersConfig, fields={list(ProvidersConfig.model_fields.keys())}")


def _patch_provider_factory():
    """Patch provider factory to support Ollama provider."""
    import nanobot.cli.commands as commands
    
    # Store original function
    original_make_provider = commands._make_provider
    
    def _make_provider_with_ollama(config):
        """Create provider, using OllamaProvider for ollama provider type."""
        # Check if provider is set to ollama
        provider_name = getattr(config.agents.defaults, 'provider', None)
        if provider_name == "ollama":
            from nanodesk.providers.ollama_provider import OllamaProvider
            
            # Load config file directly to get ollama settings
            # (ProvidersConfig may not have ollama field yet when this runs)
            import json
            from pathlib import Path
            
            ollama_api_key = "not-needed"
            ollama_api_base = "http://localhost:11434"
            
            config_file = Path.home() / ".nanobot" / "config.json"
            if config_file.exists():
                try:
                    with open(config_file, 'r', encoding='utf-8') as f:
                        file_config = json.load(f)
                    ollama_provider = file_config.get("providers", {}).get("ollama", {})
                    ollama_api_key = ollama_provider.get("apiKey") or ollama_provider.get("api_key", "not-needed") or "not-needed"
                    ollama_api_base = ollama_provider.get("apiBase") or ollama_provider.get("api_base", "http://localhost:11434") or "http://localhost:11434"
                except Exception as e:
                    print(f"[WARN] Failed to load Ollama config from file: {e}")
            
            print(f"[INFO] Using Ollama provider with model: {config.agents.defaults.model}")
            return OllamaProvider(
                api_key=ollama_api_key,
                api_base=ollama_api_base,
                default_model=config.agents.defaults.model,
            )
        
        # Fall back to original provider creation
        return original_make_provider(config)
    
    # Replace function
    commands._make_provider = _make_provider_with_ollama
    print("[INFO] Patched provider factory for Ollama support")


def _patch_windows_encoding():
    """Patch Windows encoding to avoid UnicodeEncodeError."""
    if sys.platform != "win32":
        return

    import nanobot

    # Use ASCII fallback on Windows to avoid UnicodeEncodeError
    nanobot.__logo__ = "[nanobot]"
