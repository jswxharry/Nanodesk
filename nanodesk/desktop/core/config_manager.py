"""Configuration manager with Windows DPAPI encryption."""

import base64
import ctypes
import json
from ctypes import wintypes
from pathlib import Path


class ConfigManager:
    """Manage nanobot configuration with encrypted API keys."""

    CONFIG_DIR = Path.home() / ".nanobot"
    CONFIG_FILE = CONFIG_DIR / "config.json"

    # Default configuration template
    DEFAULT_CONFIG = {
        "agents": {
            "defaults": {
                "model": "qwen-turbo",
                "provider": "dashscope",
                "workspace": str(Path.home() / ".nanobot" / "workspace"),
                "max_tokens": 4096,
                "temperature": 0.7,
                "max_tool_iterations": 20,
            }
        },
        "channels": {
            "feishu": {
                "enabled": False,
                "appId": "",
                "appSecret": "",
                "encryptKey": "",
                "verificationToken": "",
                "webhookHost": "0.0.0.0",
                "webhookPort": 18999,
                "allowFrom": [],
            }
        },
        "providers": {
            "dashscope": {
                "apiKey": "",
                "apiBase": "https://dashscope.aliyuncs.com/compatible-mode/v1",
            },
            "openai": {"apiKey": "", "apiBase": "https://api.openai.com/v1"},
            "openrouter": {"apiKey": "", "apiBase": "https://openrouter.ai/api/v1"},
        },
        "gateway": {"host": "127.0.0.1", "port": 18790},
        "tools": {
            "web": {"search": {"enabled": False, "api_key": ""}},
            "exec": {"timeout": 60, "restrict_to_workspace": True},
        },
    }

    def __init__(self):
        self.CONFIG_DIR.mkdir(parents=True, exist_ok=True)

    def is_first_run(self) -> bool:
        """Check if this is the first run (no config exists)."""
        return not self.CONFIG_FILE.exists()

    def load(self) -> dict:
        """Load configuration from file."""
        if not self.CONFIG_FILE.exists():
            return self.DEFAULT_CONFIG.copy()

        try:
            with open(self.CONFIG_FILE, "r", encoding="utf-8") as f:
                config = json.load(f)

            # Decrypt sensitive fields
            self._decrypt_api_keys(config)

            # Merge with defaults for any missing fields
            return self._merge_with_defaults(config)

        except (json.JSONDecodeError, IOError):
            return self.DEFAULT_CONFIG.copy()

    def save(self, config: dict) -> bool:
        """Save configuration to file with encrypted API keys."""
        try:
            # Make a copy to avoid modifying original
            config_to_save = json.loads(json.dumps(config))

            # Encrypt sensitive fields
            self._encrypt_api_keys(config_to_save)

            # Save to file
            with open(self.CONFIG_FILE, "w", encoding="utf-8") as f:
                json.dump(config_to_save, f, indent=2, ensure_ascii=False)

            return True

        except (json.JSONDecodeError, IOError):
            return False

    def update_provider(self, provider: str, api_key: str, api_base: str = None) -> None:
        """Update provider configuration."""
        config = self.load()

        if provider not in config["providers"]:
            config["providers"][provider] = {}

        config["providers"][provider]["apiKey"] = api_key
        if api_base:
            config["providers"][provider]["apiBase"] = api_base

        self.save(config)

    def update_agent_model(self, model: str, provider: str) -> None:
        """Update agent default model and provider."""
        config = self.load()
        config["agents"]["defaults"]["model"] = model
        config["agents"]["defaults"]["provider"] = provider
        self.save(config)

    def update_feishu(self, enabled: bool, app_id: str = "", app_secret: str = "") -> None:
        """Update Feishu channel configuration."""
        config = self.load()
        config["channels"]["feishu"]["enabled"] = enabled
        if app_id:
            config["channels"]["feishu"]["appId"] = app_id
        if app_secret:
            config["channels"]["feishu"]["appSecret"] = app_secret
        self.save(config)

    def _encrypt_api_keys(self, config: dict) -> None:
        """Encrypt API keys using Windows DPAPI."""
        try:
            for provider in config.get("providers", {}).values():
                if api_key := provider.get("apiKey"):
                    provider["apiKey"] = self._encrypt_string(api_key)

            # Encrypt Feishu secrets
            feishu = config.get("channels", {}).get("feishu", {})
            if app_secret := feishu.get("appSecret"):
                feishu["appSecret"] = self._encrypt_string(app_secret)

        except Exception:
            pass  # Silently fail encryption, store plaintext

    def _decrypt_api_keys(self, config: dict) -> None:
        """Decrypt API keys using Windows DPAPI."""
        try:
            for provider in config.get("providers", {}).values():
                if api_key := provider.get("apiKey"):
                    if api_key.startswith("dpapi:"):
                        provider["apiKey"] = self._decrypt_string(api_key)

            # Decrypt Feishu secrets
            feishu = config.get("channels", {}).get("feishu", {})
            if app_secret := feishu.get("appSecret"):
                if app_secret.startswith("dpapi:"):
                    feishu["appSecret"] = self._decrypt_string(app_secret)

        except Exception:
            pass  # Silently fail decryption

    def _encrypt_string(self, plaintext: str) -> str:
        """Encrypt string using Windows DPAPI."""
        if not plaintext:
            return ""

        try:
            data = plaintext.encode("utf-16le")
            blob = self._encrypt_data(data)
            return f"dpapi:{base64.b64encode(blob).decode('ascii')}"
        except Exception:
            return plaintext

    def _decrypt_string(self, ciphertext: str) -> str:
        """Decrypt string using Windows DPAPI."""
        if not ciphertext or not ciphertext.startswith("dpapi:"):
            return ciphertext

        try:
            blob = base64.b64decode(ciphertext[6:])  # Remove "dpapi:" prefix
            data = self._decrypt_data(blob)
            return data.decode("utf-16le")
        except Exception:
            return ciphertext

    def _encrypt_data(self, data: bytes) -> bytes:
        """Encrypt data using Windows DPAPI."""

        # CRYPTPROTECT_UI_FORBIDDEN = 0x01
        class DATA_BLOB(ctypes.Structure):
            _fields_ = [("cbData", wintypes.DWORD), ("pbData", ctypes.POINTER(wintypes.BYTE))]

        CryptProtectData = ctypes.windll.crypt32.CryptProtectData
        CryptProtectData.argtypes = [
            ctypes.POINTER(DATA_BLOB),  # pDataIn
            wintypes.LPCWSTR,  # szDataDescr
            ctypes.POINTER(DATA_BLOB),  # pOptionalEntropy
            ctypes.c_void_p,  # pvReserved
            ctypes.c_void_p,  # pPromptStruct
            wintypes.DWORD,  # dwFlags
            ctypes.POINTER(DATA_BLOB),  # pDataOut
        ]
        CryptProtectData.restype = wintypes.BOOL

        LocalFree = ctypes.windll.kernel32.LocalFree
        LocalFree.argtypes = [ctypes.c_void_p]
        LocalFree.restype = ctypes.c_void_p

        # Create input blob
        in_blob = DATA_BLOB()
        in_blob.cbData = len(data)
        in_blob.pbData = ctypes.cast(
            ctypes.create_string_buffer(data), ctypes.POINTER(wintypes.BYTE)
        )

        # Create output blob
        out_blob = DATA_BLOB()

        # Encrypt
        if not CryptProtectData(
            ctypes.byref(in_blob),
            None,  # No description
            None,  # No entropy
            None,  # Reserved
            None,  # No prompt
            0x01,  # CRYPTPROTECT_UI_FORBIDDEN
            ctypes.byref(out_blob),
        ):
            raise ctypes.WinError()

        # Copy encrypted data
        encrypted = bytes(out_blob.pbData[: out_blob.cbData])

        # Free memory
        LocalFree(out_blob.pbData)

        return encrypted

    def _decrypt_data(self, data: bytes) -> bytes:
        """Decrypt data using Windows DPAPI."""

        class DATA_BLOB(ctypes.Structure):
            _fields_ = [("cbData", wintypes.DWORD), ("pbData", ctypes.POINTER(wintypes.BYTE))]

        CryptUnprotectData = ctypes.windll.crypt32.CryptUnprotectData
        CryptUnprotectData.argtypes = [
            ctypes.POINTER(DATA_BLOB),  # pDataIn
            ctypes.POINTER(wintypes.LPWSTR),  # ppszDataDescr
            ctypes.POINTER(DATA_BLOB),  # pOptionalEntropy
            ctypes.c_void_p,  # pvReserved
            ctypes.c_void_p,  # pPromptStruct
            wintypes.DWORD,  # dwFlags
            ctypes.POINTER(DATA_BLOB),  # pDataOut
        ]
        CryptUnprotectData.restype = wintypes.BOOL

        LocalFree = ctypes.windll.kernel32.LocalFree
        LocalFree.argtypes = [ctypes.c_void_p]
        LocalFree.restype = ctypes.c_void_p

        # Create input blob
        in_blob = DATA_BLOB()
        in_blob.cbData = len(data)
        in_blob.pbData = ctypes.cast(
            ctypes.create_string_buffer(data), ctypes.POINTER(wintypes.BYTE)
        )

        # Create output blob
        out_blob = DATA_BLOB()

        # Decrypt
        if not CryptUnprotectData(
            ctypes.byref(in_blob),
            None,  # No description needed
            None,  # No entropy
            None,  # Reserved
            None,  # No prompt
            0x01,  # CRYPTPROTECT_UI_FORBIDDEN
            ctypes.byref(out_blob),
        ):
            raise ctypes.WinError()

        # Copy decrypted data
        decrypted = bytes(out_blob.pbData[: out_blob.cbData])

        # Free memory
        LocalFree(out_blob.pbData)

        return decrypted

    def _merge_with_defaults(self, config: dict) -> dict:
        """Merge loaded config with defaults for missing fields."""

        def merge_dict(default: dict, override: dict) -> dict:
            result = default.copy()
            for key, value in override.items():
                if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                    result[key] = merge_dict(result[key], value)
                else:
                    result[key] = value
            return result

        return merge_dict(self.DEFAULT_CONFIG, config)


# Singleton instance
_config_manager = None


def get_config_manager() -> ConfigManager:
    """Get singleton ConfigManager instance."""
    global _config_manager
    if _config_manager is None:
        _config_manager = ConfigManager()
    return _config_manager
