"""Integration smoke tests for SequenceItem, config serialization, and execution."""
import os
import sys
import time

# Ensure src/ is on sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from features.shortcut_panel.types.panel_types import MenuItem, SequenceItem
from features.shortcut_panel.services import config_service, shortcut_executor


def test_sequence_serialization() -> None:
    """1. Test Serialization: parse_items and items_to_raw roundtrip."""
    raw_input = [
        {
            "type": "sequence",
            "label": "Test Sequence",
            "steps": [
                {"type": "shortcut", "keys": "ctrl+c", "delay_ms": 50},
                {"type": "command", "cmd": "echo 1", "delay_ms": 0},
            ],
        }
    ]
    items = config_service.parse_items(raw_input)
    assert len(items) == 1, f"Expected 1 item, got {len(items)}"
    seq = items[0]
    assert isinstance(seq, SequenceItem), f"Expected SequenceItem, got {type(seq)}"
    assert seq.label == "Test Sequence"
    assert len(seq.steps) == 2
    assert seq.steps[0]["keys"] == "ctrl+c"
    assert seq.steps[1]["cmd"] == "echo 1"

    # Test roundtrip back to raw dict
    raw_output = config_service.items_to_raw(items)
    assert len(raw_output) == 1
    assert raw_output[0]["type"] == "sequence"
    assert raw_output[0]["label"] == "Test Sequence"
    assert len(raw_output[0]["steps"]) == 2
    print("PASS: test_sequence_serialization")


def test_sequence_execution_and_timing() -> None:
    """2. Test Execution & Timing: measure execution time with step delays."""
    steps = [
        {"type": "command", "cmd": "echo step1", "delay_ms": 100},
        {"type": "command", "cmd": "echo step2", "delay_ms": 0},
    ]
    t0 = time.time()
    shortcut_executor.execute_sequence(steps)
    elapsed = time.time() - t0
    assert elapsed >= 0.08, f"Expected elapsed >= 0.08s, got {elapsed:.3f}s"
    assert elapsed < 0.6, f"Expected elapsed < 0.6s, got {elapsed:.3f}s"
    print(f"PASS: test_sequence_execution_and_timing (elapsed={elapsed:.3f}s)")


def test_sequence_error_resilience() -> None:
    """3. Test Error Resilience: faulty step should not stop subsequent steps."""
    steps = [
        {"type": "unknown_invalid_type", "data": "invalid", "delay_ms": 10},
        {"type": "command", "cmd": "echo resilient", "delay_ms": 10},
    ]
    # execute_sequence should swallow the error, log warning, and continue
    try:
        shortcut_executor.execute_sequence(steps)
    except Exception as exc:
        assert False, f"execute_sequence raised unexpected exception: {exc}"
    print("PASS: test_sequence_error_resilience")


if __name__ == "__main__":
    test_sequence_serialization()
    test_sequence_execution_and_timing()
    test_sequence_error_resilience()
    print("ALL SEQUENCE INTEGRATION TESTS PASSED.")
