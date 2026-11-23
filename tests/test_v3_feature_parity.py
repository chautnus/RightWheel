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
