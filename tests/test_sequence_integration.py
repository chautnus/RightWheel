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


def test_prtsc_virtual_key_resolution() -> None:
    """4. Test Virtual Key Resolution: verify prtsc, printscreen, and dialog mappings."""
    assert shortcut_executor._VK.get("prtsc") == 0x2C, "Expected prtsc to map to 0x2C"
    assert shortcut_executor._VK.get("printscreen") == 0x2C, "Expected printscreen to map to 0x2C"
    assert shortcut_executor._VK.get("snapshot") == 0x2C, "Expected snapshot to map to 0x2C"

    from features.shortcut_panel.ui.key_recorder_dialog import _SPECIAL
    assert _SPECIAL.get("Print") == "prtsc", "Expected Tkinter 'Print' keysym to map to 'prtsc'"
    print("PASS: test_prtsc_virtual_key_resolution")


def test_chatgpt_macro_execution_flow(monkeypatch) -> None:
    """5. Test ChatGPT Macro Execution Flow: verify step execution and browser focusing."""
    from src.features.action_dispatcher import clipboard_web_actions, sequence_executor

    call_log = []

    monkeypatch.setattr(clipboard_web_actions, "open_url_default_browser", lambda url: call_log.append(("open_url", url)))
    monkeypatch.setattr(clipboard_web_actions, "focus_default_browser_window", lambda: (call_log.append("focus_browser"), True)[1])
    monkeypatch.setattr(clipboard_web_actions, "wait_until_browser_tab_ready", lambda timeout_s=5.0: (call_log.append("wait_tab"), True)[1])
    monkeypatch.setattr(sequence_executor, "_send_key_combo", lambda combo: call_log.append(("key_combo", combo)))
    monkeypatch.setattr(sequence_executor, "_send_text", lambda text: call_log.append(("text", text)))

    macro_steps = [
        {"type": "shortcut", "keys": "ctrl+c", "delay_ms": 10},
        {"type": "url", "url": "https://chatgpt.com", "delay_ms": 10},
        {"type": "shortcut", "keys": "ctrl+v", "delay_ms": 10},
        {"type": "text", "text": "text this", "delay_ms": 10},
        {"type": "shortcut", "keys": "enter", "delay_ms": 10},
    ]

    res = sequence_executor.execute_steps(macro_steps)
    assert res.get("ok") is True, f"Expected ok=True, got {res}"
    assert res.get("data", {}).get("executed_steps") == 5

    # Check that open_url, focus_browser, wait_tab occurred in correct order
    assert ("open_url", "https://chatgpt.com") in call_log
    assert "focus_browser" in call_log
    assert "wait_tab" in call_log
    assert ("key_combo", "ctrl+v") in call_log
    assert ("text", "text this") in call_log
    assert ("key_combo", "enter") in call_log
    print("PASS: test_chatgpt_macro_execution_flow")


def test_panel_logic_sequence_delegation(monkeypatch) -> None:
    """6. Test PanelLogic delegation: ensure SequenceItem triggers execute_steps_async."""
    import threading
    from src.features.shortcut_panel.logic.panel_logic import PanelLogic
    from src.features.shortcut_panel.types.panel_types import SequenceItem

    dispatched = []

    def mock_execute_async(steps):
        dispatched.append(steps)
        t = threading.Thread(target=lambda: None)
        t.start()
        return t

    import src.features.action_dispatcher.sequence_executor as seq_mod
    monkeypatch.setattr(seq_mod, "execute_steps_async", mock_execute_async)

    # Mock Timer so it fires immediately or synchronously for testing
    class ImmediateTimer:
        def __init__(self, interval, function, args=None, kwargs=None):
            self.fn = function
            self.args = args or []
            self.kwargs = kwargs or {}
        def start(self):
            self.fn(*self.args, **self.kwargs)

    monkeypatch.setattr(threading, "Timer", ImmediateTimer)

    logic = PanelLogic()
    test_item = SequenceItem(
        label="Test ChatGPT Macro",
        steps=[
            {"type": "shortcut", "keys": "ctrl+c", "delay_ms": 10},
            {"type": "url", "url": "https://chatgpt.com", "delay_ms": 10},
        ]
    )
    logic._items = [test_item]
    logic._index = 0
    logic.visible = True

    logic.select_current()
    assert len(dispatched) == 1, f"Expected 1 dispatched sequence, got {len(dispatched)}"
    assert dispatched[0] == test_item.steps
    print("PASS: test_panel_logic_sequence_delegation")


def test_default_commands_include_chatgpt_macro() -> None:
    """7. Verify built-in DEFAULT_COMMANDS contains ChatGPT macro."""
    from src.core.config_service import DEFAULT_COMMANDS

    labels = [cmd.get("label", "") for cmd in DEFAULT_COMMANDS if isinstance(cmd, dict)]
    assert "ChatGPT: Paste Clipboard" in labels, f"ChatGPT macro missing from DEFAULT_COMMANDS: {labels}"
    print("PASS: test_default_commands_include_chatgpt_macro")


if __name__ == "__main__":
    test_sequence_serialization()
    test_sequence_execution_and_timing()
    test_sequence_error_resilience()
    test_prtsc_virtual_key_resolution()
    print("ALL SEQUENCE INTEGRATION TESTS PASSED.")
