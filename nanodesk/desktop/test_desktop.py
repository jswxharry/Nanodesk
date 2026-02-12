"""Test script for desktop application."""

import sys
from pathlib import Path

# Add project root to path
root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(root))


def test_config_manager():
    """Test ConfigManager."""
    print("Testing ConfigManager...")
    
    from nanodesk.desktop.core.config_manager import get_config_manager
    
    cm = get_config_manager()
    
    # Test first run check
    is_first = cm.is_first_run()
    print(f"  First run: {is_first}")
    
    # Test load
    config = cm.load()
    print(f"  Config loaded: {len(config)} top-level keys")
    
    # Test save
    test_config = {
        "agents": {
            "defaults": {
                "model": "test-model",
                "provider": "test-provider"
            }
        },
        "providers": {
            "test-provider": {
                "apiKey": "test-key-12345",
                "apiBase": "https://test.example.com"
            }
        },
        "channels": {
            "feishu": {
                "enabled": False,
                "appId": "",
                "appSecret": ""
            }
        },
        "gateway": {"host": "127.0.0.1", "port": 18790},
        "tools": {"web": {"search": {"enabled": False}}}
    }
    
    result = cm.save(test_config)
    print(f"  Save result: {result}")
    
    # Load again and verify
    loaded = cm.load()
    assert loaded["agents"]["defaults"]["model"] == "test-model"
    print("  Config save/load: OK")
    
    print("ConfigManager: PASSED\n")
    return True


def test_log_handler():
    """Test LogHandler."""
    print("Testing LogHandler...")
    
    from nanodesk.desktop.core.log_handler import get_log_handler
    
    lh = get_log_handler()
    
    # Test start session
    log_file = lh.start_session()
    print(f"  Log file: {log_file}")
    
    # Test write
    lh.write("Test message 1")
    lh.write("Test message 2", "WARN")
    lh.write("Test message 3", "ERROR")
    
    # Test end session
    lh.end_session()
    print("  Log write: OK")
    
    # Test read
    content = lh.read_log_file(log_file)
    assert "Test message 1" in content
    print("  Log read: OK")
    
    print("LogHandler: PASSED\n")
    return True


def test_process_manager():
    """Test ProcessManager."""
    print("Testing ProcessManager...")
    
    from nanodesk.desktop.core.process_manager import get_process_manager
    
    pm = get_process_manager()
    
    # Test initial state
    assert not pm.is_running
    print("  Initial state: OK")
    
    # Test status
    status = pm.get_status()
    assert "gateway" in status
    print(f"  Status: {status}")
    
    print("ProcessManager: PASSED (basic checks)\n")
    return True


def test_imports():
    """Test all imports."""
    print("Testing imports...")
    
    try:
        from nanodesk.desktop.app import NanodeskApp
        print("  NanodeskApp: OK")
        
        from nanodesk.desktop.windows.main_window import MainWindow
        print("  MainWindow: OK")
        
        from nanodesk.desktop.windows.setup_wizard import SetupWizard
        print("  SetupWizard: OK")
        
        from nanodesk.desktop.core.system_tray import SystemTray
        print("  SystemTray: OK")
        
        print("Imports: PASSED\n")
        return True
    except Exception as e:
        print(f"  Import error: {e}")
        return False


def main():
    """Run all tests."""
    print("=" * 50)
    print("Nanodesk Desktop Component Tests")
    print("=" * 50)
    print()
    
    tests = [
        ("Imports", test_imports),
        ("ConfigManager", test_config_manager),
        ("LogHandler", test_log_handler),
        ("ProcessManager", test_process_manager),
    ]
    
    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"{name}: FAILED - {e}\n")
            results.append((name, False))
    
    # Summary
    print("=" * 50)
    print("Test Summary")
    print("=" * 50)
    
    passed = sum(1 for _, r in results if r)
    total = len(results)
    
    for name, result in results:
        status = "PASS" if result else "FAIL"
        print(f"  {status} - {name}")
    
    print()
    print(f"Total: {passed}/{total} passed")
    
    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
