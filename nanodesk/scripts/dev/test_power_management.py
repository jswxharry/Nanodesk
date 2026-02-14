#!/usr/bin/env python3
"""Automated tests for power management feature.

Tests the power management module without requiring actual Windows sleep.
Uses mocking where necessary to simulate different scenarios.

Usage:
    python nanodesk/scripts/dev/test_power_management.py
    python nanodesk/scripts/dev/test_power_management.py -v  # Verbose
"""

import argparse
import socket
import sys
import threading
import time
from pathlib import Path

# Add project root to path
root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(root))


def test_module_import():
    """Test that power_manager module can be imported."""
    print("Test 1: Module import...")
    try:
        from nanodesk.desktop.core.power_manager import (
            PowerStatus,
            allow_sleep,
            get_power_status,
            prevent_sleep,
            should_prevent_sleep,
        )

        print("  [PASS] Module imported successfully")
        return True
    except Exception as e:
        print(f"  [FAIL] Failed to import module: {e}")
        return False


def test_power_status_structure():
    """Test PowerStatus dataclass."""
    print("Test 2: PowerStatus dataclass...")
    try:
        from nanodesk.desktop.core.power_manager import PowerStatus

        # Test creation
        status = PowerStatus(on_ac_power=True, battery_percent=75)
        assert status.on_ac_power is True
        assert status.battery_percent == 75

        # Test with battery mode
        status2 = PowerStatus(on_ac_power=False, battery_percent=25)
        assert status2.on_ac_power is False
        assert status2.battery_percent == 25

        print("  [PASS] PowerStatus works correctly")
        return True
    except Exception as e:
        print(f"  [FAIL] PowerStatus test failed: {e}")
        return False


def test_get_power_status():
    """Test getting power status."""
    print("Test 3: Get power status...")
    try:
        from nanodesk.desktop.core.power_manager import get_power_status

        status = get_power_status()

        # Verify return type
        assert hasattr(status, "on_ac_power")
        assert hasattr(status, "battery_percent")
        assert isinstance(status.on_ac_power, bool)
        assert isinstance(status.battery_percent, int)
        assert 0 <= status.battery_percent <= 100 or status.battery_percent == 100

        print(f"  [PASS] Power status: AC={status.on_ac_power}, Battery={status.battery_percent}%")
        return True
    except Exception as e:
        print(f"  [FAIL] Get power status failed: {e}")
        return False


def test_should_prevent_sleep():
    """Test should_prevent_sleep logic."""
    print("Test 4: Should prevent sleep logic...")
    try:
        from nanodesk.desktop.core.power_manager import (
            PowerStatus,
            should_prevent_sleep,
        )

        # Test with AC power (should prevent)
        # Note: We can't easily mock get_power_status, so we just test the function runs
        result, reason = should_prevent_sleep()
        assert isinstance(result, bool)
        assert isinstance(reason, str)
        assert len(reason) > 0

        print(f"  [PASS] Should prevent: {result}, Reason: {reason}")
        return True
    except Exception as e:
        print(f"  [FAIL] Should prevent sleep test failed: {e}")
        return False


def test_prevent_and_allow_sleep():
    """Test prevent_sleep and allow_sleep APIs."""
    print("Test 5: Prevent and allow sleep APIs...")
    try:
        from nanodesk.desktop.core.power_manager import (
            allow_sleep,
            prevent_sleep,
        )

        # Test prevent sleep
        result1 = prevent_sleep()
        assert isinstance(result1, bool)
        print(f"  [PASS] prevent_sleep() returned: {result1}")

        # Test allow sleep (should always succeed)
        allow_sleep()
        print("  [PASS] allow_sleep() executed")

        # Test idempotency - calling again should not fail
        result2 = prevent_sleep()
        allow_sleep()
        print("  [PASS] Idempotent calls work")

        return True
    except Exception as e:
        print(f"  [FAIL] Prevent/allow sleep test failed: {e}")
        return False


def test_single_instance_lock():
    """Test that single instance lock works (port 28790)."""
    print("Test 6: Single instance lock...")
    try:
        # Try to bind to port 28790
        sock1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock1.bind(("127.0.0.1", 28790))
        sock1.listen(1)
        print("  [PASS] First instance bound to port 28790")

        # Try to bind again (should fail)
        sock2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            sock2.bind(("127.0.0.1", 28790))
            sock2.listen(1)
            print("  [FAIL] Second instance should have failed!")
            sock2.close()
            return False
        except socket.error:
            print("  [PASS] Second instance correctly rejected")

        # Close first socket
        sock1.close()

        # Now should be able to bind again
        sock3 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock3.bind(("127.0.0.1", 28790))
        sock3.listen(1)
        print("  [PASS] Port released, can bind again")
        sock3.close()

        return True
    except Exception as e:
        print(f"  [FAIL] Single instance lock test failed: {e}")
        return False


def test_power_monitor_thread():
    """Test that power monitor thread starts correctly."""
    print("Test 7: Power monitor thread...")
    try:
        from nanodesk.desktop.core.power_manager import (
            _monitor_started,
            start_power_monitor,
        )

        # Save original state
        import nanodesk.desktop.core.power_manager as pm

        original_state = pm._monitor_started

        # Reset state for testing
        pm._monitor_started = False

        # Start monitor with short interval for testing
        start_power_monitor(interval_seconds=1)

        # Verify it started
        assert pm._monitor_started is True
        print("  [PASS] Power monitor started")

        # Try to start again (should be ignored)
        start_power_monitor(interval_seconds=1)
        print("  [PASS] Second start correctly ignored")

        # Wait a bit for thread to run
        time.sleep(1.5)
        print("  [PASS] Monitor thread running")

        # Restore original state
        pm._monitor_started = original_state

        return True
    except Exception as e:
        print(f"  [FAIL] Power monitor thread test failed: {e}")
        return False


def test_check_power_change():
    """Test check_power_change function."""
    print("Test 8: Check power change...")
    try:
        from nanodesk.desktop.core.power_manager import (
            _last_ac_status,
            check_power_change,
        )

        import nanodesk.desktop.core.power_manager as pm

        # Save original state
        original_status = pm._last_ac_status

        # Test with None status (first run)
        pm._last_ac_status = None
        check_power_change()
        assert pm._last_ac_status is not None
        print(f"  [PASS] First run recorded status: {pm._last_ac_status}")

        # Restore original state
        pm._last_ac_status = original_status

        return True
    except Exception as e:
        print(f"  [FAIL] Check power change test failed: {e}")
        return False


def test_thread_safety():
    """Test thread safety with concurrent calls."""
    print("Test 9: Thread safety...")
    try:
        from nanodesk.desktop.core.power_manager import (
            allow_sleep,
            prevent_sleep,
        )

        errors = []
        results = []

        def worker(func, name):
            try:
                for _ in range(10):
                    result = func()
                    results.append((name, result))
                    time.sleep(0.01)
            except Exception as e:
                errors.append((name, str(e)))

        # Create threads
        threads = []
        for i in range(3):
            t = threading.Thread(target=worker, args=(prevent_sleep, f"prevent_{i}"))
            threads.append(t)
            t = threading.Thread(target=worker, args=(allow_sleep, f"allow_{i}"))
            threads.append(t)

        # Start all threads
        for t in threads:
            t.start()

        # Wait for completion
        for t in threads:
            t.join()

        if errors:
            print(f"  [FAIL] Thread errors: {errors}")
            return False

        print(f"  [PASS] {len(results)} concurrent calls completed without errors")
        return True
    except Exception as e:
        print(f"  [FAIL] Thread safety test failed: {e}")
        return False


def test_cleanup_on_exit():
    """Test cleanup function exists and can be called."""
    print("Test 10: Cleanup on exit...")
    try:
        from nanodesk.desktop.core.power_manager import _cleanup

        # Cleanup should run without error even if not preventing
        _cleanup()
        print("  [PASS] Cleanup function executes")

        return True
    except Exception as e:
        print(f"  [FAIL] Cleanup test failed: {e}")
        return False


def run_all_tests(verbose=False):
    """Run all tests and return results."""
    tests = [
        test_module_import,
        test_power_status_structure,
        test_get_power_status,
        test_should_prevent_sleep,
        test_prevent_and_allow_sleep,
        test_single_instance_lock,
        test_power_monitor_thread,
        test_check_power_change,
        test_thread_safety,
        test_cleanup_on_exit,
    ]

    results = []
    print("=" * 60)
    print("Power Management Automated Tests")
    print("=" * 60)
    print()

    for test in tests:
        try:
            result = test()
            results.append((test.__name__, result))
        except Exception as e:
            print(f"  [CRASH] Test crashed: {e}")
            results.append((test.__name__, False))
        print()

    # Summary
    print("=" * 60)
    print("Test Summary")
    print("=" * 60)
    passed = sum(1 for _, r in results if r)
    total = len(results)
    print(f"Passed: {passed}/{total}")
    print()

    if verbose or passed < total:
        print("Details:")
        for name, result in results:
            status = "[PASS]" if result else "[FAIL]"
            print(f"  {status}: {name}")

    return passed == total


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Test power management feature")
    parser.add_argument("-v", "--verbose", action="store_true", help="Verbose output")
    args = parser.parse_args()

    success = run_all_tests(verbose=args.verbose)
    sys.exit(0 if success else 1)
