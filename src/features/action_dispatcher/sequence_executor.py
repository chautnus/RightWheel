"""Sequence Executor module for running macro step sequences (ADR-008)."""
from __future__ import annotations

import ctypes
import os
import shutil
import subprocess
import threading
import time
from typing import Any
import webbrowser

from src.core.app_paths import log_debug
from src.features.action_dispatcher import clipboard_web_actions
from src.features.action_dispatcher.dispatcher import (
    INPUT_KEYBOARD,
    KEYEVENTF_EXTENDEDKEY,
    KEYEVENTF_KEYUP,
    ActionDispatcher,
    _EXTENDED,
    _SZ,
    _VK,
    _INPUT,
)

KEYEVENTF_UNICODE = 0x0004
_URL_STEP_TYPES = {"URL", "OPEN_URL", "URL_CLIPBOARD", "WEB_CLIPBOARD", "GEMINI"}
_KEYSTROKE_STEP_TYPES = {"SHORTCUT", "KEY_COMBO", "TEXT", "TYPE_TEXT"}

# Set of modifier virtual-key codes that must be released in finally block
MODIFIER_VKS: set[int] = {
    _VK["ctrl"],
    _VK["alt"],
    _VK["shift"],
    _VK["win"],
    _VK["win_r"],
}


def release_modifier_keys() -> None:
    """Explicitly release all modifier keys (Ctrl, Alt, Shift, Win).
    
    Guaranteed cleanup in finally block to prevent stuck keys after macro crash/exception.
    """
    if not (hasattr(ctypes, "windll") and hasattr(ctypes.windll, "user32")):
        return

    n = len(MODIFIER_VKS)
    arr = (_INPUT * n)()
    for i, vk in enumerate(MODIFIER_VKS):
        flags = (KEYEVENTF_EXTENDEDKEY if vk in _EXTENDED else 0) | KEYEVENTF_KEYUP
        arr[i].type = INPUT_KEYBOARD
        arr[i].ki.wVk = vk
        arr[i].ki.dwFlags = flags

    try:
        ctypes.windll.user32.SendInput(n, arr, _SZ)
    except Exception as exc:
        log_debug(f"release_modifier_keys failed: {exc}")


def _send_single_vk(vk: int, is_up: bool) -> None:
    """Send a single key press/release with resolved hardware scan code."""
    if not (hasattr(ctypes, "windll") and hasattr(ctypes.windll, "user32")):
        return
    inp = _INPUT()
    inp.type = INPUT_KEYBOARD
    inp.ki.wVk = vk
    inp.ki.wScan = ActionDispatcher._resolve_scan_code(vk)
    flags = KEYEVENTF_EXTENDEDKEY if vk in _EXTENDED else 0
    if is_up:
        flags |= KEYEVENTF_KEYUP
    inp.ki.dwFlags = flags
    ctypes.windll.user32.SendInput(1, ctypes.byref(inp), _SZ)


def _send_key_combo(combo: str) -> bool:
    """Simulate key combination via SendInput with scan codes and hold micro-delays."""
    if not combo or not combo.strip():
        return False
    parts = [p.strip().lower() for p in combo.split("+")]
    vks = [_VK[p] for p in parts if p in _VK]
    if not vks:
        return False

    if hasattr(ctypes, "windll") and hasattr(ctypes.windll, "user32"):
        try:
            from src.features.action_dispatcher.window_manager import get_window_exe, get_window_title
            fg = ctypes.windll.user32.GetForegroundWindow()
            log_debug(f"_send_key_combo({combo!r}) fg_hwnd={fg} exe={get_window_exe(fg)!r} title={get_window_title(fg)!r}")
        except Exception:
            pass
        for vk in vks:
            _send_single_vk(vk, is_up=False)
            time.sleep(0.015)
        time.sleep(0.015)
        for vk in reversed(vks):
            _send_single_vk(vk, is_up=True)
            time.sleep(0.015)
    return True


def _send_text(text: str) -> bool:
    """Type Unicode text via SendInput KEYEVENTF_UNICODE."""
    if not text:
        return False
    if not (hasattr(ctypes, "windll") and hasattr(ctypes.windll, "user32")):
        return False

    events: list[_INPUT] = []
    for ch in text:
        code = ord(ch)
        ev_down = _INPUT()
        ev_down.type = INPUT_KEYBOARD
        ev_down.ki.wVk = 0
        ev_down.ki.wScan = code
        ev_down.ki.dwFlags = KEYEVENTF_UNICODE
        events.append(ev_down)

        ev_up = _INPUT()
        ev_up.type = INPUT_KEYBOARD
        ev_up.ki.wVk = 0
        ev_up.ki.wScan = code
        ev_up.ki.dwFlags = KEYEVENTF_UNICODE | KEYEVENTF_KEYUP
        events.append(ev_up)

    arr = (_INPUT * len(events))(*events)
    ctypes.windll.user32.SendInput(len(events), arr, _SZ)
    return True


def _get_clipboard_seq() -> int:
    """Return Windows clipboard sequence number (0 if unavailable)."""
    if hasattr(ctypes, "windll") and hasattr(ctypes.windll, "user32"):
        try:
            return int(ctypes.windll.user32.GetClipboardSequenceNumber())
        except Exception:
            return 0
    return 0


def _execute_single_step(step: dict[str, Any]) -> None:
    stype = str(step.get("type", "")).upper()
    if stype in ("SHORTCUT", "KEY_COMBO"):
        keys = step.get("keys") or step.get("target") or ""
        norm_keys = "+".join(p.strip().lower() for p in str(keys).split("+") if p.strip())
        if norm_keys in ("ctrl+c", "ctrl+x"):
            seq_before = _get_clipboard_seq()
            _send_key_combo(keys)
            time.sleep(0.08)
            seq_after = _get_clipboard_seq()
            if seq_before and seq_after == seq_before:
                log_debug(f"Clipboard unchanged after {norm_keys!r} (seq={seq_before}), retrying once")
                release_modifier_keys()
                time.sleep(0.06)
                _send_key_combo(keys)
                time.sleep(0.08)
                seq_after = _get_clipboard_seq()
            log_debug(f"Clipboard after {norm_keys!r}: changed={seq_after != seq_before} ({seq_before}->{seq_after})")
        else:
            _send_key_combo(keys)
    elif stype in ("APP", "RUN_APP"):
        path = step.get("path") or step.get("target") or ""
        args = step.get("args", "")
        if path:
            cmd = [path]
            if args:
                cmd.extend(args.split() if isinstance(args, str) else list(args))
            subprocess.Popen(cmd, shell=False)
    elif stype in ("URL", "OPEN_URL"):
        url = step.get("url") or step.get("target") or ""
        if url:
            clipboard_web_actions.open_url_default_browser(url)
    elif stype in ("COMMAND", "RUN_SHELL"):
        cmd_str = step.get("cmd") or step.get("target") or ""
        cwd = step.get("cwd") or None
        if cmd_str:
            subprocess.Popen(cmd_str, shell=True, cwd=cwd)
    elif stype in ("URL_CLIPBOARD", "WEB_CLIPBOARD"):
        template = step.get("url_template") or step.get("url") or step.get("target") or ""
        if template:
            clipboard_web_actions.execute_url_clipboard(
                template,
                prompt=str(step.get("prompt", "") or ""),
                mode=str(step.get("mode", "url_query") or "url_query"),
                base_url=str(step.get("base_url", "") or ""),
                auto_submit=bool(step.get("auto_submit", True)),
                send_key_fn=_send_key_combo,
                send_text_fn=_send_text,
            )
    elif stype == "GEMINI":
        prompt = step.get("prompt") or step.get("target") or ""
        clipboard_web_actions.execute_gemini(prompt)
    elif stype in ("TEXT", "TYPE_TEXT"):
        text = step.get("text") or step.get("target") or ""
        _send_text(text)
    elif stype == "DELAY":
        pass


def execute_steps(steps: list[dict[str, Any]]) -> dict[str, Any]:
    """Execute a list of macro steps sequentially.
    
    Test Contract:
        execute_steps(steps:list) -> {ok, data:{executed_steps, elapsed_ms}} | {ok:False, error:{code:'INVALID_STEP_SCHEMA', ...}}
    """
    start_t = time.perf_counter()

    if not isinstance(steps, list):
        return {
            "ok": False,
            "error": {
                "code": "INVALID_STEP_SCHEMA",
                "message": "Steps must be a list of step dictionaries",
            },
        }

    # Validate each step schema
    valid_types = {
        "SHORTCUT", "KEY_COMBO",
        "APP", "RUN_APP",
        "URL", "OPEN_URL",
        "COMMAND", "RUN_SHELL",
        "URL_CLIPBOARD", "WEB_CLIPBOARD",
        "GEMINI",
        "TEXT", "TYPE_TEXT",
        "DELAY",
    }

    for idx, step in enumerate(steps):
        if not isinstance(step, dict):
            return {
                "ok": False,
                "error": {
                    "code": "INVALID_STEP_SCHEMA",
                    "message": f"Step at index {idx} must be a dictionary",
                },
            }
        stype = str(step.get("type", "")).upper()
        if stype not in valid_types:
            return {
                "ok": False,
                "error": {
                    "code": "INVALID_STEP_SCHEMA",
                    "message": f"Step at index {idx} has unsupported type: {step.get('type')!r}",
                },
            }

    executed_count = 0
    try:
        for idx, step in enumerate(steps):
            stype = str(step.get("type", "")).upper()
            log_debug(f"Macro step [{idx + 1}/{len(steps)}] start type={stype}")
            _execute_single_step(step)
            executed_count += 1

            # Handle delay (strictly use configured delay_ms, never override user settings)
            delay_ms = 0
            if stype == "DELAY":
                delay_ms = step.get("duration_ms", step.get("delay_ms", 0))
            else:
                delay_ms = step.get("delay_ms", 0)

            try:
                delay_ms = float(delay_ms)
            except (ValueError, TypeError):
                delay_ms = 0.0

            if delay_ms > 0:
                log_debug(f"Macro step [{idx + 1}/{len(steps)}] sleeping {delay_ms}ms")
                time.sleep(delay_ms / 1000.0)

            # After a URL step, ensure default browser window has foreground and tab finished loading
            if stype in _URL_STEP_TYPES and idx + 1 < len(steps):
                next_type = str(steps[idx + 1].get("type", "")).upper()
                if next_type in _KEYSTROKE_STEP_TYPES:
                    focused = clipboard_web_actions.focus_default_browser_window()
                    ready = clipboard_web_actions.wait_until_browser_tab_ready(timeout_s=5.0)
                    log_debug(f"Macro post-URL focus={focused} tab_ready={ready}")

        elapsed_ms = (time.perf_counter() - start_t) * 1000.0
        log_debug(f"Macro finished: executed_steps={executed_count} elapsed_ms={elapsed_ms:.1f}")
        return {
            "ok": True,
            "data": {
                "executed_steps": executed_count,
                "elapsed_ms": elapsed_ms,
            },
        }
    except Exception as exc:
        log_debug(f"Macro execution error: {exc}")
        return {
            "ok": False,
            "error": {
                "code": "STEP_EXECUTION_ERROR",
                "message": str(exc),
            },
        }
    finally:
        # HARD REQUIREMENT ADR-008: release all modifier keys in finally
        release_modifier_keys()


def execute_steps_async(
    steps: list[dict[str, Any]],
    on_complete: Any = None,
) -> threading.Thread:
    """Execute steps on a dedicated background worker thread (ADR-008)."""
    def _worker():
        res = execute_steps(steps)
        if callable(on_complete):
            try:
                on_complete(res)
            except Exception as e:
                log_debug(f"execute_steps_async callback error: {e}")

    thread = threading.Thread(target=_worker, daemon=True, name="SequenceExecutorWorker")
    thread.start()
    return thread
