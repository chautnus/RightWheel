"""Unit tests for IntentService and Reference Tab 1-click import."""
from __future__ import annotations

import os
import sys

# Ensure src/ is on sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

import tkinter as tk
import pytest
from features.shortcut_panel.services.intent_service import IntentService, _normalize_str
from features.shortcut_panel.services import config_service


def test_normalize_str():
    assert _normalize_str("Chụp Màn Hình") == "chup man hinh"
    assert _normalize_str("Task Manager") == "task manager"
    assert _normalize_str("  ĐỔI TAB  ") == "doi tab"
    assert _normalize_str("Đổi tên") == "doi ten"


def test_intent_service_search_task_manager():
    service = IntentService()
    results = service.search("task manager")
    assert len(results) > 0
    top = results[0]
    assert top.intent_id == "task_manager"
    assert top.keys == "ctrl+shift+esc"


def test_intent_service_search_vietnamese_intent():
    service = IntentService()
    # Search 'chup man hinh'
    results = service.search("chup man hinh")
    assert len(results) > 0
    assert any(it.intent_id == "snip_screenshot" for it in results)

    # Search 'doi tab' or 'next tab'
    results_tab = service.search("doi tab")
    assert len(results_tab) > 0
    assert results_tab[0].intent_id in ("next_tab", "prev_tab")


def test_intent_service_categories():
    service = IntentService()
    cats = service.get_all_categories()
    assert "Hệ thống" in cats
    assert "Cửa sổ" in cats
    assert "Trình duyệt" in cats
    assert "File Explorer" in cats

    browser_items = service.get_by_category("Trình duyệt")
    assert len(browser_items) >= 5
    assert any(it.keys == "ctrl+t" for it in browser_items)


def test_reference_tab_add_selected_headless(monkeypatch, tmp_path):
    # Mock config_service paths to temp
    temp_cfg = tmp_path / "shortcuts.json"
    temp_cfg.write_text('{"default": []}', encoding="utf-8")
    monkeypatch.setattr(config_service, "CONFIG_PATH", temp_cfg)

    root = tk.Tk()
    root.withdraw()
    try:
        from features.shortcut_panel.ui.reference_tab import ReferenceTab
        tab = ReferenceTab(root)
        # Select first item in treeview
        children = tab._tree.get_children()
        assert len(children) > 0
        tab._tree.selection_set(children[0])
        vals = tab._tree.item(children[0], "values")

        tab._add_selected()
        loaded = config_service.load().get("default", [])
        if "rmb" in vals[1].lower():
            assert "cử chỉ chuột" in tab._feedback_lbl.cget("text").lower()
        else:
            assert len(loaded) == 1
            assert loaded[0]["label"] == vals[2]
            assert "đã thêm" in tab._feedback_lbl.cget("text").lower()
    finally:
        root.destroy()
