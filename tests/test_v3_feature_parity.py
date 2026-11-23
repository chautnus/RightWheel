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

    # Test save settings
    patch_res = api.save_general_settings({"ui_engine": "webview", "language": "vi"})
    assert patch_res["ok"] is True
    assert patch_res["data"]["ui_engine"] == "webview"

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
    assert user32.SetWindowsHookExW.restype == ctypes.c_void_p
    assert len(user32.SetWindowsHookExW.argtypes) == 4

    hook_svc = MouseHookService(on_event=lambda ev: False)
    assert hook_svc.is_hook_alive is False
    assert "rmb_down" in hook_svc.stats
    assert "rmb_up" in hook_svc.stats
    assert "moves" in hook_svc.stats


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
