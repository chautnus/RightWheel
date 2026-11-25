import pytest
from src.core import app_paths, memory_manager, store_license_service, config_service, profile_service, i18n
from src.features.action_dispatcher.dispatcher import ActionDispatcher
from src.features.webview_ui.bridge_api import WebViewBridgeAPI, resolve_ui_index_path
from src.features.webview_ui.launcher import is_webview_available, get_preferred_ui_engine


def test_app_paths():
    root = app_paths.get_app_root()
    cfg = app_paths.get_config_root()
    assert root.exists()
    assert cfg.name == "RightWheel"


def test_memory_manager_trim():
    assert memory_manager.trim_memory() is True
    memory_manager.notify_activity()
    assert memory_manager.get_idle_seconds() < 2.0


def test_store_license_simulation(tmp_path):
    state_file = tmp_path / "store_license.json"
    svc = store_license_service.StoreLicenseService(state_file_override=state_file)
    st = svc.get_status()
    assert st["status"] == "TRIAL_ACTIVE"
    assert st["days_remaining"] == 30

    exp = svc.simulate_expire_trial()
    assert exp["status"] == "TRIAL_EXPIRED"
    assert exp["days_remaining"] == 0

    custom = svc.simulate_set_remaining(hours=2, minutes=30, seconds=0)
    assert custom["status"] == "TRIAL_ACTIVE"
    assert custom["seconds_remaining"] == 9000

    rst = svc.reset_trial()
    assert rst["status"] == "TRIAL_ACTIVE"
    assert rst["days_remaining"] == 30


def test_config_and_profile_service(tmp_path, monkeypatch):
    monkeypatch.setattr(config_service, "get_config_root", lambda: tmp_path)
    doc = config_service.load_unified_profiles()
    assert doc["version"] == 4
    assert len(doc["profiles"]) >= 1
    assert doc["profiles"][0]["id"] == "global"

    res = profile_service.resolve_active_profile_full(0, config_data=doc)
    assert res["ok"] is True
    assert res["data"]["profile_id"] == "global"
    assert len(res["data"]["commands"]) > 0


def test_action_dispatcher():
    ad = ActionDispatcher()
    assert "KEY_COMBO" in ad.VALID_TYPES
    assert "RUN_APP" in ad.VALID_TYPES
    assert "OPEN_URL" in ad.VALID_TYPES
    assert "SEQUENCE" in ad.VALID_TYPES
    assert "TYPE_TEXT" in ad.VALID_TYPES
    assert "WEB_CLIP" in ad.VALID_TYPES

    # Invalid action schema
    res = ad.execute("invalid")
    assert res["ok"] is False


def test_webview_bridge_api(tmp_path, monkeypatch):
    monkeypatch.setattr(config_service, "get_config_root", lambda: tmp_path)
    api = WebViewBridgeAPI(config_dir=tmp_path)
    init_res = api.get_initial_state("settings")
    assert init_res["ok"] is True
    data = init_res["data"]
    assert data["version"] == "3.0.0"
    assert data["view"] == "settings"
    assert "general" in data
    assert "profiles" in data
    assert "license" in data

    # Test save settings (temporarily locked to English-only)
    patch_res = api.save_general_settings({"ui_engine": "webview", "language": "vi"})
    assert patch_res["ok"] is True
    assert patch_res["data"]["ui_engine"] == "webview"
    assert patch_res["data"]["language"] == "en"
    assert patch_res["data"]["available_languages"] == ["en"]

    # Test UI dist index path
    idx = resolve_ui_index_path()
    assert idx is not None and idx.exists()
    assert is_webview_available() is True


def test_command_sync_settings_to_panel(tmp_path, monkeypatch):
    monkeypatch.setattr(app_paths, "get_config_root", lambda: tmp_path)
    monkeypatch.setattr(config_service, "get_config_root", lambda: tmp_path)

    from src.features.shortcut_panel.logic.panel_logic import PanelLogic
    from src.features.shortcut_panel.services import config_service as panel_cfg

    monkeypatch.setattr(panel_cfg, "_get_config_dir", lambda: tmp_path)

    api = WebViewBridgeAPI(config_dir=tmp_path)
    panel = PanelLogic()

    # Modify commands via WebViewBridgeAPI (simulating Settings UI)
    new_commands = [
        {"type": "shortcut", "label": "My Custom Test Command", "keys": "ctrl+alt+t"},
        {"type": "url", "label": "Open GitHub", "url": "https://github.com"},
    ]
    res = api.save_profile_commands("global", new_commands)
    assert res["ok"] is True

    # Both profiles.json and shortcuts.json should exist and be in sync
    profiles_file = tmp_path / "profiles.json"
    shortcuts_file = tmp_path / "shortcuts.json"
    assert profiles_file.exists()
    assert shortcuts_file.exists()

    # Reload panel logic
    panel.reload()
    assert len(panel._root) == 2
    assert panel._root[0].label == "My Custom Test Command"
    assert getattr(panel._root[0], "keys", "") == "ctrl+alt+t"
    assert panel._root[1].label == "Open GitHub"
    assert getattr(panel._root[1], "url", "") == "https://github.com"

    # Simulate show() on desktop
    panel.show()
    assert len(panel._root) == 2
    assert panel._root[0].label == "My Custom Test Command"


def test_reference_save_and_config_sync(tmp_path, monkeypatch):
    monkeypatch.setattr(app_paths, "get_config_root", lambda: tmp_path)
    monkeypatch.setattr(config_service, "get_config_root", lambda: tmp_path)
    from src.features.shortcut_panel.services import config_service as panel_cfg
    monkeypatch.setattr(panel_cfg, "_get_config_dir", lambda: tmp_path)

    # Initial load creates default config
    data = panel_cfg.load()
    initial_len = len(data.get("default", []))
    assert initial_len > 0

    # Simulate ReferenceTab / IntentPicker adding a shortcut
    new_item = {"type": "shortcut", "label": "Search Files", "keys": "win+e"}
    data.setdefault("default", []).append(new_item)
    panel_cfg.save(data)

    # Reload from panel_cfg and unified profiles to verify persistence
    reloaded_panel = panel_cfg.load()
    assert len(reloaded_panel["default"]) == initial_len + 1
    assert reloaded_panel["default"][-1]["label"] == "Search Files"

    v4_doc = config_service.load_unified_profiles()
    global_p = next(p for p in v4_doc["profiles"] if p["is_default"])
    assert any(c.get("label") == "Search Files" for c in global_p["commands"])


def test_gesture_recognizer_shape_and_sort():
    from src.features.mouse_mapper.logic.gesture_recognizer import GestureRecognizer
    gr = GestureRecognizer()
    gr._directions = ["D", "R"]

    # Modern V3 UI preset format (only shape and target)
    ui_presets = [
        {"shape": "D_R", "target": "ctrl+w", "enabled": True, "label": "Close Tab"},
        {"shape": "U", "target": "ctrl+t", "enabled": True, "label": "New Tab"},
    ]
    res = gr.finish(ui_presets)
    assert res["ok"] is True
    assert res["data"]["matched"] is True
    assert res["data"]["keys"] == "ctrl+w"
    assert res["data"]["preset"]["shape"] == "D_R"

    # Test stroke order sorting
    raw_gestures = [
        {"kind": "draw", "shape": "R_D"},
        {"kind": "wheel", "direction": "DOWN"},
        {"kind": "draw", "shape": "U"},
        {"kind": "wheel", "direction": "UP"},
        {"kind": "draw", "shape": "U_D"},
        {"kind": "draw", "shape": "D_R"},
        {"kind": "draw", "shape": "L"},
    ]
    sorted_g = config_service.sort_gestures(raw_gestures)
    shapes = [g.get("shape") or g.get("direction") for g in sorted_g]
    assert shapes == ["UP", "DOWN", "U", "U_D", "D_R", "L", "R_D"]


def test_mouse_hook_win64_signatures_and_stats():
    from src.features.mouse_mapper.services.mouse_hook_service import MouseHookService, user32
    import ctypes

    # Verify 64-bit argtypes and restype
    assert user32.CallNextHookEx.restype == ctypes.c_ssize_t
    assert len(user32.CallNextHookEx.argtypes) == 4
    assert user32.CallNextHookEx.argtypes[3] == ctypes.c_void_p
    assert user32.SetWindowsHookExW.restype == ctypes.c_void_p
    assert len(user32.SetWindowsHookExW.argtypes) == 4

    hook_svc = MouseHookService(on_event=lambda ev: False, wants_move_events=lambda: False)
    assert hook_svc.is_hook_alive is False
    assert "rmb_down" in hook_svc.stats
    assert "rmb_up" in hook_svc.stats
    assert "moves" in hook_svc.stats

    # Verify _hook_proc does NOT raise ctypes.ArgumentError on pointer l_param
    from src.features.mouse_mapper.services.mouse_hook_service import MSLLHOOKSTRUCT, WM_MOUSEMOVE
    st = MSLLHOOKSTRUCT()
    ptr = ctypes.pointer(st)
    assert hook_svc._hook_proc(0, WM_MOUSEMOVE, ptr) == 0


def test_trail_overlay_root_getter():
    from src.features.mouse_mapper.ui.trail_overlay import TrailOverlay

    mock_holder = {"root": None}
    trail = TrailOverlay(lambda: mock_holder["root"])

    # Before root initializes
    assert trail._get_root() is None

    # After root initializes
    fake_root = object()
    mock_holder["root"] = fake_root
    assert trail._get_root() is fake_root


def test_move_threshold_default_and_config():
    from src.features.mouse_mapper.types.mouse_mapper_types import HotkeyConfig
    from src.features.mouse_mapper.logic.mouse_mapper_logic import MouseMapperLogic

    # Default is now 16px (responsive on all screens and touchpads)
    cfg = HotkeyConfig()
    assert cfg.move_threshold == 16

    mapper = MouseMapperLogic()
    assert mapper._cfg.move_threshold == 16


def test_gesture_recognizer_noise_tolerance_touchpad_parity():
    from src.features.mouse_mapper.logic.gesture_recognizer import normalize_directions, _is_effectively_single_stroke

    # 1. Entry wobble
    assert normalize_directions(["DR", "D"]) == ["D"]
    assert normalize_directions(["UL", "U"]) == ["U"]
    assert normalize_directions(["DL", "L"]) == ["L"]
    assert normalize_directions(["UR", "R"]) == ["R"]

    # 2. Lift-off trailing wobble
    assert normalize_directions(["D", "DR"]) == ["D"]
    assert normalize_directions(["U", "UL"]) == ["U"]
    assert normalize_directions(["L", "DL"]) == ["L"]
    assert normalize_directions(["R", "UR"]) == ["R"]

    # 3. Mid-stroke wobble (sandwiched diagonal)
    assert normalize_directions(["D", "DR", "D"]) == ["D"]
    assert normalize_directions(["R", "DR", "R"]) == ["R"]
    assert normalize_directions(["U", "UL", "U"]) == ["U"]
    assert normalize_directions(["L", "DL", "L"]) == ["L"]

    # 4. Turnaround U-turns (180°)
    assert normalize_directions(["D", "DR", "U"]) == ["D", "U"]
    assert normalize_directions(["D", "DL", "U"]) == ["D", "U"]
    assert normalize_directions(["U", "UR", "D"]) == ["U", "D"]
    assert normalize_directions(["R", "UR", "L"]) == ["R", "L"]
    assert normalize_directions(["L", "DL", "R"]) == ["L", "R"]

    # 5. Orthogonal 90° corners
    assert normalize_directions(["D", "DR", "R"]) == ["D", "R"]
    assert normalize_directions(["D", "DL", "L"]) == ["D", "L"]
    assert normalize_directions(["U", "UR", "R"]) == ["U", "R"]
    assert normalize_directions(["U", "UL", "L"]) == ["U", "L"]

    # 6. Single stroke detector
    assert _is_effectively_single_stroke(["D", "DR"]) is True
    assert _is_effectively_single_stroke(["DL", "D"]) is True
    assert _is_effectively_single_stroke(["D", "R"]) is False  # 90° turn is compound
    assert _is_effectively_single_stroke(["D", "U"]) is False  # 180° turn is compound


def test_gesture_recognizer_single_stroke_dominant_displacement():
    from src.features.mouse_mapper.logic.gesture_recognizer import GestureRecognizer

    rec = GestureRecognizer()
    presets = [
        {"shape": "D", "keys": "prtsc", "enabled": True},
        {"shape": "D_R", "keys": "ctrl+w", "enabled": True},
        {"shape": "D_U", "keys": "win+v", "enabled": True},
        {"shape": "L", "keys": "ctrl+shift+tab", "enabled": True},
        {"shape": "R", "keys": "ctrl+tab", "enabled": True},
    ]

    # Slanted down (dy=160, dx=25) -> should 100% resolve to D (prtsc)
    rec.reset()
    rec.feed_point(500, 500)
    rec.feed_point(520, 520)  # DR entry slant
    rec.feed_point(525, 580)  # D
    rec.feed_point(525, 660)  # D
    res = rec.finish(presets)
    assert res["ok"] is True
    assert res["data"]["matched"] is True
    assert res["data"]["keys"] == "prtsc"
    assert res["data"]["directions"] == ["D"]

    # 2-segment with corner noise and lift-off (D_R -> ctrl+w)
    rec.reset()
    rec.feed_point(500, 500)
    rec.feed_point(500, 560)  # D
    rec.feed_point(525, 585)  # DR corner curve
    rec.feed_point(570, 585)  # R
    rec.feed_point(630, 585)  # R
    rec.feed_point(645, 570)  # UR lift-off
    res = rec.finish(presets)
    assert res["ok"] is True
    assert res["data"]["matched"] is True
    assert res["data"]["keys"] == "ctrl+w"
    assert res["data"]["directions"] == ["D", "R"]


def test_gesture_async_execution_timer():
    from unittest.mock import patch
    from src.features.mouse_mapper.logic.mouse_mapper_logic import MouseMapperLogic
    from src.features.mouse_mapper.types.mouse_mapper_types import MouseEvent

    logic = MouseMapperLogic()
    logic.handle(MouseEvent("right_down", x=500, y=500))
    logic.handle(MouseEvent("move", x=500, y=530))
    logic.handle(MouseEvent("move", x=500, y=600))

    with patch("threading.Timer") as mock_timer:
        res = logic.handle(MouseEvent("right_up", x=500, y=600))
        assert res is True
        assert mock_timer.called
        args, _ = mock_timer.call_args
        assert args[0] == 0.06
        assert callable(args[1])


def test_welcome_bento_and_wizard_i18n():
    """Verify updated 3 core welcome pillars and wizard strings across i18n locales."""
    for lang in ["vi", "en", "fr", "es", "it", "pt", "id"]:
        d = i18n._TRANSLATIONS[lang]
        assert "welcome_bento_1_title" in d and len(d["welcome_bento_1_title"]) > 0
        assert "welcome_bento_2_title" in d and len(d["welcome_bento_2_title"]) > 0
        assert "welcome_bento_3_title" in d and len(d["welcome_bento_3_title"]) > 0
        assert "welcome_bento_1_desc" in d and len(d["welcome_bento_1_desc"]) > 0
        assert "welcome_bento_2_desc" in d and len(d["welcome_bento_2_desc"]) > 0
        assert "welcome_bento_3_desc" in d and len(d["welcome_bento_3_desc"]) > 0

    # Specific pillar checks for Vietnamese
    vi = i18n._TRANSLATIONS["vi"]
    assert "Cử chỉ vẽ chuột" in vi["welcome_bento_1_title"]
    assert "Bảng lệnh nhanh không giới hạn" in vi["welcome_bento_2_title"]
    assert "Chuỗi tác vụ tự động 1 cú nhấp" in vi["welcome_bento_3_title"]
    assert "wiz_tab_gestures" in vi
    assert "wiz_tab_commands" in vi

    # Specific pillar checks for English
    en = i18n._TRANSLATIONS["en"]
    assert "Hold Right Mouse & Draw Gestures" == en["welcome_bento_1_title"]
    assert "Unlimited Quick Commands" == en["welcome_bento_2_title"]
    assert "A Series of Actions in One Click" == en["welcome_bento_3_title"]
    assert "wiz_tab_gestures" in en
    assert "wiz_tab_commands" in en


def test_gesture_lead_in_tremor_pruning():
    """Verify that mechanical click wobble (<25px lead-in) is cleanly pruned."""
    from src.features.mouse_mapper.logic.gesture_recognizer import GestureRecognizer

    gr = GestureRecognizer()
    gr.reset()
    gr.feed_point(100, 100)
    # 1-step lead-in tremor in UL
    gr.feed_point(85, 85)
    # Main stroke downward
    for y in range(110, 260, 25):
        gr.feed_point(85, y)

    presets = [{"shape": "D", "keys": "prtsc", "enabled": True}]
    res = gr.finish(presets)
    assert res["data"]["matched"] is True
    assert res["data"]["keys"] == "prtsc"
    assert res["data"]["directions"] == ["D"]


def test_gesture_compound_with_lead_in_tremor():
    """Verify that compound gestures (D_R) with lead-in wobble trigger correctly."""
    from src.features.mouse_mapper.logic.gesture_recognizer import GestureRecognizer

    gr = GestureRecognizer()
    gr.reset()
    gr.feed_point(100, 100)
    # Lead-in tremor
    gr.feed_point(85, 85)
    # Down leg
    for y in range(110, 210, 25):
        gr.feed_point(85, y)
    # Right leg
    for x in range(110, 210, 25):
        gr.feed_point(x, 210)

    presets = [{"shape": "D_R", "keys": "ctrl+w", "enabled": True}]
    res = gr.finish(presets)
    assert res["data"]["matched"] is True
    assert res["data"]["keys"] == "ctrl+w"
    assert res["data"]["directions"] == ["D", "R"]


def test_shortcut_executor_scan_codes():
    """Verify that _resolve_scan_code handles VK_SNAPSHOT (0x2C) without collision."""
    from src.features.shortcut_panel.services.shortcut_executor import _resolve_scan_code

    # PrtScn must return 0 to prevent SysRq duplicate snapshot in Snipping Tool
    assert _resolve_scan_code(0x2C) == 0
    # Common keys (Enter, Esc, letters) must return valid positive scan codes
    assert _resolve_scan_code(0x0D) > 0  # Enter


def test_bridge_api_search_intents():
    """Verify WebViewBridgeAPI search_intents localized fuzzy search."""
    from src.features.webview_ui.bridge_api import WebViewBridgeAPI

    api = WebViewBridgeAPI()

    # Vietnamese query
    res_vi = api.search_intents("chụp màn hình", lang="vi")
    assert res_vi["ok"] is True
    assert len(res_vi["data"]) > 0
    assert any("Chụp" in it["title"] or "win+shift+s" in it["keys"] for it in res_vi["data"])

    # English query (default)
    res_en = api.search_intents("task manager", lang="en")
    assert res_en["ok"] is True
    assert len(res_en["data"]) > 0
    assert any("Task Manager" in it["title"] for it in res_en["data"])

    # Empty query should return default list in English
    res_empty = api.search_intents("")
    assert res_empty["ok"] is True
    assert len(res_empty["data"]) > 0


def test_legacy_vi_config_migrates_default_descriptions_to_en(tmp_path, monkeypatch):
    """Verify legacy Vietnamese default descriptions normalize to English while preserving custom ones."""
    import json
    monkeypatch.setattr(config_service, "get_config_root", lambda: tmp_path)
    legacy_doc = {
        "version": 4,
        "profiles": [
            {
                "id": "global",
                "name": "Global",
                "is_default": True,
                "commands": [],
                "gestures": [
                    {"kind": "draw", "shape": "D_R", "keys": "ctrl+w", "description": "Đóng tab trình duyệt hiện tại (Close Tab)"},
                    {"kind": "draw", "shape": "U", "keys": "ctrl+1", "description": "My Custom User Gesture"},
                ],
            }
        ],
    }
    (tmp_path / "profiles.json").write_text(json.dumps(legacy_doc, ensure_ascii=False), encoding="utf-8")

    loaded = config_service.load_unified_profiles()
    gestures = loaded["profiles"][0]["gestures"]
    assert gestures[0]["description"] == "Close the current browser tab (Close Tab)"
    assert gestures[1]["description"] == "My Custom User Gesture"


def test_gesture_guide_overlay_and_mapper_hold_events():
    """Verify MouseMapperLogic on_hold_start and on_sector_change callbacks for GestureGuideOverlay."""
    from src.features.mouse_mapper.logic.mouse_mapper_logic import MouseMapperLogic
    from src.features.mouse_mapper.types.mouse_mapper_types import MouseEvent
    from src.features.mouse_mapper.logic.gesture_recognizer import CARDINAL_NAMES
    from src.features.mouse_mapper.ui.gesture_guide_overlay import GestureGuideOverlay

    assert CARDINAL_NAMES["R"] == "RIGHT"
    assert CARDINAL_NAMES["L"] == "LEFT"
    assert CARDINAL_NAMES["U"] == "UP"
    assert CARDINAL_NAMES["D"] == "DOWN"

    events = {"hold": False, "paths": [], "end": False}

    mapper = MouseMapperLogic()
    mapper.on_hold_start = lambda: events.update({"hold": True})
    mapper.on_sector_change = lambda p: events["paths"].append(list(p))
    mapper.on_gesture_end = lambda: events.update({"end": True})

    # 1. RMB Down should NOT fire on_hold_start immediately — it's a press-and-hold
    # trigger (delayed), not a quick-tap one, so an ordinary right-click (context
    # menu) never shows the guide overlay.
    mapper.handle(MouseEvent(kind="right_down", x=100, y=100))
    assert events["hold"] is False

    # 2. Movement exceeding threshold (18px) to the right is itself proof of real
    # gesture intent, so it fires on_hold_start immediately (bypassing the rest of
    # the delay) and commits RIGHT.
    for x in range(110, 200, 10):
        mapper.handle(MouseEvent(kind="move", x=x, y=100))
    assert events["hold"] is True
    assert len(events["paths"]) > 0
    assert events["paths"][-1] == ["RIGHT"]

    # 3. RMB Up should call on_gesture_end to close overlay
    mapper.handle(MouseEvent(kind="right_up", x=200, y=100))
    assert events["end"] is True

    # 4. GestureGuideOverlay instantiation check
    overlay = GestureGuideOverlay()
    assert overlay._active is False


def test_gesture_asymmetric_d_r_not_hijacked_by_d():
    """Verify D (prtsc) listed before D_R (ctrl+w) never steals asymmetric or short-turn D_R."""
    from src.features.mouse_mapper.logic.gesture_recognizer import GestureRecognizer

    presets = [
        {"shape": "D", "keys": "prtsc", "enabled": True},
        {"shape": "D_R", "keys": "ctrl+w", "enabled": True},
    ]

    # Case A: Asymmetric L-shape (Down 120px, Right 50px -> disp_ratio ~0.76 >= 0.70)
    gr = GestureRecognizer(threshold=18)
    gr.reset()
    gr.feed_point(100, 100)
    for y in range(125, 225, 25):
        gr.feed_point(100, y)
    gr.feed_point(125, 220)
    gr.feed_point(150, 220)
    res_a = gr.finish(presets)
    assert res_a["data"]["matched"] is True
    assert res_a["data"]["keys"] == "ctrl+w"
    assert res_a["data"]["directions"] == ["D", "R"]

    # Case B: Short 1-step orthogonal Right leg (Down 100px, Right 25px)
    gr2 = GestureRecognizer(threshold=18)
    gr2.reset()
    gr2.feed_point(100, 100)
    for y in range(125, 225, 25):
        gr2.feed_point(100, y)
    gr2.feed_point(125, 200)
    res_b = gr2.finish(presets)
    assert res_b["data"]["matched"] is True
    assert res_b["data"]["keys"] == "ctrl+w"
    assert res_b["data"]["directions"] == ["D", "R"]


def test_mapper_scroll_cancels_hold_timer_and_closes_guide():
    """Verify scrolling cancels pending hold timer and closes guide overlay if already open."""
    from src.features.mouse_mapper.logic.mouse_mapper_logic import MouseMapperLogic
    from src.features.mouse_mapper.types.mouse_mapper_types import MouseEvent, ScrollDirection

    ended = {"count": 0}
    mapper = MouseMapperLogic()
    mapper.on_hold_start = lambda: None
    mapper.on_gesture_end = lambda: ended.__setitem__("count", ended["count"] + 1)

    mapper.handle(MouseEvent(kind="right_down", x=100, y=100))
    mapper._fire_hold_start()
    assert mapper._hold_fired is True

    # Scrolling must close the guide overlay immediately and clear _hold_fired
    mapper.handle(MouseEvent(kind="scroll", scroll_dir=ScrollDirection.UP))
    assert ended["count"] == 1
    assert mapper._hold_fired is False

    # Calling _fire_hold_start during SCROLLING must be ignored
    mapper._fire_hold_start()
    assert mapper._hold_fired is False

    mapper.handle(MouseEvent(kind="right_up", x=100, y=100))


def test_store_winrt_iap_and_msix_log_dir(tmp_path, monkeypatch):
    """Verify WinRT StoreContext license/purchase mocks and MSIX-safe writable log path."""
    import subprocess
    import sys

    # 1. MSIX WindowsApps read-only executable path must route logs to LOCALAPPDATA
    fake_local = tmp_path / "LocalAppData"
    monkeypatch.setenv("LOCALAPPDATA", str(fake_local))
    monkeypatch.setattr(sys, "frozen", True, raising=False)
    monkeypatch.setattr(sys, "executable", r"C:\Program Files\WindowsApps\ChauTran.RightWheel_1.0.0.0_x64\RightWheel.exe")
    log_dir = app_paths._get_writable_log_dir()
    assert log_dir == fake_local / "RightWheel" / "data"

    # 2. WinRT license verification mock
    state_file = tmp_path / "store_license.json"
    svc = store_license_service.StoreLicenseService(state_file_override=state_file)
    monkeypatch.setattr(svc, "has_msix_package_identity", lambda: True)

    class _FakeRes:
        def __init__(self, stdout: str):
            self.stdout = stdout

    monkeypatch.setattr(subprocess, "run", lambda *a, **kw: _FakeRes("PRO_ADDON_ACTIVE\n"))
    st = svc.verify_store_license()
    assert st["is_pro"] is True
    assert st["status"] == "PRO_ACTIVATED"

    # 3. WinRT purchase_pro mock
    svc2 = store_license_service.StoreLicenseService(state_file_override=tmp_path / "store_license2.json")
    monkeypatch.setattr(svc2, "has_msix_package_identity", lambda: True)
    monkeypatch.setattr(subprocess, "run", lambda *a, **kw: _FakeRes("Succeeded\n"))
    assert svc2.purchase_pro(addon_id="9NQ_TEST_ADDON") is True
    assert svc2.get_status()["is_pro"] is True





