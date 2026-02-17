#!/usr/bin/env python3
"""
Test Kimi Coding Adapter integration with Nanodesk.

This test verifies that Nanodesk can connect to the local Adapter
which bridges OpenAI format to Kimi Coding API.

Usage:
    python tests/test_adapter_integration.py

Requirements:
    - Adapter running on http://127.0.0.1:8000
    - Config: ~/.nanobot/config.json with OpenAI provider pointing to adapter
"""

import json
import urllib.request
import urllib.error
import sys
from pathlib import Path


def load_nanodesk_config():
    """Load Nanodesk config to verify adapter settings."""
    config_path = Path.home() / ".nanobot" / "config.json"
    if not config_path.exists():
        return None
    
    try:
        with open(config_path) as f:
            return json.load(f)
    except Exception as e:
        print(f"Warning: Failed to load config: {e}")
        return None


def test_adapter_health():
    """Test adapter health endpoint."""
    try:
        req = urllib.request.Request("http://127.0.0.1:8000/health")
        with urllib.request.urlopen(req, timeout=5) as response:
            data = json.loads(response.read().decode())
            assert data.get("status") == "ok", f"Unexpected status: {data}"
            assert data.get("kimi_configured") is True, "Kimi not configured"
            print(f"✅ Adapter health: {data}")
            return True
    except Exception as e:
        print(f"❌ Adapter health check failed: {e}")
        return False


def test_chat_completion():
    """Test chat completion through adapter."""
    config = load_nanodesk_config()
    if not config:
        print("❌ No Nanodesk config found")
        return False
    
    # Get adapter settings from config
    openai_config = config.get("providers", {}).get("openai", {})
    api_key = openai_config.get("api_key", "")
    base_url = openai_config.get("base_url", "http://127.0.0.1:8000/v1")
    
    if not api_key:
        print("❌ No API key configured for OpenAI provider")
        return False
    
    payload = {
        "model": "k2p5",
        "messages": [{"role": "user", "content": "Hello from Nanodesk test"}],
        "max_tokens": 100
    }
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    
    try:
        req = urllib.request.Request(
            f"{base_url}/chat/completions",
            data=json.dumps(payload).encode(),
            headers=headers,
            method="POST"
        )
        
        with urllib.request.urlopen(req, timeout=30) as response:
            data = json.loads(response.read().decode())
            
            assert "choices" in data, "No choices in response"
            assert len(data["choices"]) > 0, "Empty choices"
            
            content = data["choices"][0]["message"]["content"]
            print(f"✅ Chat response: {content[:80]}...")
            print(f"   Model: {data.get('model')}")
            print(f"   Usage: {data.get('usage', {})}")
            return True
            
    except urllib.error.HTTPError as e:
        print(f"❌ HTTP {e.code}: {e.read().decode()}")
        return False
    except Exception as e:
        print(f"❌ Chat test failed: {e}")
        return False


def test_auth_failure():
    """Test that invalid key is rejected."""
    payload = {
        "model": "k2p5",
        "messages": [{"role": "user", "content": "test"}]
    }
    
    try:
        req = urllib.request.Request(
            "http://127.0.0.1:8000/v1/chat/completions",
            data=json.dumps(payload).encode(),
            headers={"Content-Type": "application/json"},
            method="POST"
        )
        
        with urllib.request.urlopen(req, timeout=5) as response:
            print("❌ Should have rejected request without auth")
            return False
            
    except urllib.error.HTTPError as e:
        if e.code in (401, 403):
            print(f"✅ Auth correctly rejected: HTTP {e.code}")
            return True
        else:
            print(f"❌ Unexpected error: {e.code}")
            return False
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False


def main():
    print("=" * 50)
    print("Kimi Coding Adapter Integration Test")
    print("=" * 50)
    
    # Check config
    config = load_nanodesk_config()
    if config:
        print("\n📋 Nanodesk config found:")
        openai_cfg = config.get("providers", {}).get("openai", {})
        print(f"   Base URL: {openai_cfg.get('base_url', 'N/A')}")
        print(f"   API Key: {'*' * 8}{openai_cfg.get('api_key', '')[-4:] if openai_cfg.get('api_key') else 'N/A'}")
    else:
        print("\n⚠️  No Nanodesk config found at ~/.nanobot/config.json")
    
    print()
    
    # Run tests
    tests = [
        ("Adapter Health", test_adapter_health),
        ("Auth Rejection", test_auth_failure),
        ("Chat Completion", test_chat_completion),
    ]
    
    results = []
    for name, test_func in tests:
        print(f"\n🧪 {name}")
        print("-" * 30)
        result = test_func()
        results.append((name, result))
    
    # Summary
    print("\n" + "=" * 50)
    print("Test Results")
    print("=" * 50)
    
    passed = sum(1 for _, r in results if r)
    total = len(results)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {status}: {name}")
    
    print("=" * 50)
    print(f"Total: {passed}/{total} passed")
    
    if passed == total:
        print("\n🎉 All tests passed! Adapter is ready.")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed.")
        print("\nTroubleshooting:")
        print("  1. Ensure adapter is running: cd bridge/kimi_coding_adapter && ./adapter.sh start")
        print("  2. Check adapter health: curl http://127.0.0.1:8000/health")
        print("  3. Verify config: ~/.nanobot/config.json")
        return 1


if __name__ == "__main__":
    sys.exit(main())
