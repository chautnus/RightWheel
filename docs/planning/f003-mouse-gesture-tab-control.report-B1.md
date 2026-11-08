# BATCH 1 — f003-mouse-gesture-tab-control

plan-file: C:\dev\Mousehotkey\docs\planning\f003-mouse-gesture-tab-control.batch-1.md
started: 2026-11-08 19:03
finished: 2026-11-08 19:18
batch-status: done

## REALITY-CHECK
result: n/a (batch đầu)
detail: n/a — batch đầu tiên, không có dependency từ batch khác

## TASK T-006: Thêm switch_tab_x1x2 và inject_right_up vào hotkey_service.py
status: done
files-changed: src/features/mouse_mapper/services/hotkey_service.py
verify-cmd: python -c "from features.mouse_mapper.services import hotkey_service; rf=hotkey_service.switch_tab_x1x2(True); rb=hotkey_service.switch_tab_x1x2(False); assert rf['ok'] and rf['data']['combo']=='ctrl+tab'; assert rb['ok'] and rb['data']['combo']=='ctrl+shift+tab'; assert hasattr(hotkey_service,'inject_right_up'); print('OK T-006')" && grep -n "def switch_tab\b" src/features/mouse_mapper/services/hotkey_service.py
verify-output: |
  OK T-006
  src/features/mouse_mapper/services/hotkey_service.py:121:def switch_tab(forward: bool) -> None:
deviation: none

## TASK T-007: Cập nhật MouseEvent hỗ trợ xbutton trong mouse_mapper_types.py
status: done
files-changed: src/features/mouse_mapper/types/mouse_mapper_types.py
verify-cmd: python -c "from features.mouse_mapper.types.mouse_mapper_types import MouseEvent; ev=MouseEvent('xbutton_down',x=10,y=20,button=1); assert ev.kind=='xbutton_down' and ev.button==1; print('OK T-007')"
verify-output: |
  OK T-007
deviation: none

## TASK T-008: Hook WM_XBUTTONDOWN và giải mã XBUTTON1/XBUTTON2 trong mouse_hook_service.py
status: done
files-changed: src/features/mouse_mapper/services/mouse_hook_service.py
verify-cmd: python -c "import features.mouse_mapper.services.mouse_hook_service as mhs; assert hasattr(mhs,'WM_XBUTTONDOWN') and mhs.WM_XBUTTONDOWN==0x020B; print('OK T-008')"
verify-output: |
  OK T-008
deviation: none

## TASK T-009: Xây dựng GestureRecognizer 8-hướng trong gesture_recognizer.py
status: done
files-changed: src/features/mouse_mapper/logic/gesture_recognizer.py
verify-cmd: python -c "from features.mouse_mapper.logic.gesture_recognizer import GestureRecognizer; g=GestureRecognizer(18); r1=g.feed_point(0,0); r2=g.feed_point(0,30); assert r1['ok'] and r2['ok']; res=g.finish([{'directions':['D'],'keys':'ctrl+w','enabled':True}]); assert res['ok'] and res['data']['matched'] and res['data']['keys']=='ctrl+w'; print('OK T-009')"
verify-output: |
  OK T-009
deviation: none

## TASK T-010: Schema v3, gestures default & migrate_to_v3 trong config_service.py
status: done
files-changed: src/features/shortcut_panel/services/config_service.py
verify-cmd: python -c "from features.shortcut_panel.services import config_service; res=config_service.migrate_to_v3({'version':2,'default':[],'profiles':[]}); assert res['ok'] and res['data']['version']==3 and 'gestures' in res['data']; print('OK T-010')" && grep -rn "config_service.load()" src/features/shortcut_panel/ui/*.py src/features/shortcut_panel/logic/*.py src/features/shortcut_panel/services/import_service.py
verify-output: |
  OK T-010
  src/features/shortcut_panel/FEATURE_PROFILES.md:90:- Migration v1→v2 tự động trong `config_service.load()`
  src/features/shortcut_panel/logic/panel_logic.py:52:        data = config_service.load()
  src/features/shortcut_panel/logic/panel_logic.py:62:        data = config_service.load()
  src/features/shortcut_panel/services/import_service.py:85:    data = config_service.load()
  src/features/shortcut_panel/ui/default_tab.py:81:        for i, it in enumerate(config_service.load().get("default", [])):
  src/features/shortcut_panel/ui/default_tab.py:112:        data = config_service.load()
  src/features/shortcut_panel/ui/default_tab.py:129:        data = config_service.load()
  src/features/shortcut_panel/ui/default_tab.py:142:        data = config_service.load()
  src/features/shortcut_panel/ui/default_tab.py:152:        data = config_service.load()
  src/features/shortcut_panel/ui/default_tab.py:162:        data = config_service.load()
  src/features/shortcut_panel/ui/default_tab.py:203:        data = config_service.load()
  src/features/shortcut_panel/ui/default_tab.py:216:        data = config_service.load()
  src/features/shortcut_panel/ui/default_tab.py:232:        data  = config_service.load()
  src/features/shortcut_panel/ui/folder_editor_dialog.py:38:        folder_label = config_service.load()["default"][self._idx].get("label", "Folder")
  src/features/shortcut_panel/ui/folder_editor_dialog.py:85:        return config_service.load()["default"][self._idx].get("children", [])
  src/features/shortcut_panel/ui/folder_editor_dialog.py:116:        data = config_service.load()
  src/features/shortcut_panel/ui/folder_editor_dialog.py:132:        data = config_service.load()
  src/features/shortcut_panel/ui/folder_editor_dialog.py:146:        data = config_service.load()
  src/features/shortcut_panel/ui/folder_editor_dialog.py:156:        data  = config_service.load()
  src/features/shortcut_panel/ui/folder_editor_dialog.py:188:        data = config_service.load()
  src/features/shortcut_panel/ui/folder_editor_dialog.py:196:        data = config_service.load()
  src/features/shortcut_panel/ui/profile_editor.py:110:        data = config_service.load()
  src/features/shortcut_panel/ui/profile_editor.py:127:        data = config_service.load()
  src/features/shortcut_panel/ui/profile_editor.py:137:        data = config_service.load()
  src/features/shortcut_panel/ui/profile_editor.py:150:        data = config_service.load()
  src/features/shortcut_panel/ui/profile_editor.py:163:        data = config_service.load()
  src/features/shortcut_panel/ui/profile_editor.py:177:        data = config_service.load()
  src/features/shortcut_panel/ui/profile_editor.py:185:        data = config_service.load()
  src/features/shortcut_panel/ui/profile_editor.py:198:        data = config_service.load()
  src/features/shortcut_panel/ui/profile_editor.py:207:        data = config_service.load()
deviation: none

## TASK T-011: X1/X2 tab switch logic & Chromium gate trong mouse_mapper_logic.py
status: done
files-changed: src/features/mouse_mapper/logic/mouse_mapper_logic.py
verify-cmd: python -c "from features.mouse_mapper.logic.mouse_mapper_logic import MouseMapperLogic; from features.mouse_mapper.types.mouse_mapper_types import MouseEvent, MapperState; m=MouseMapperLogic(); assert not m.handle(MouseEvent('xbutton_down',button=1)); m._state=MapperState.RIGHT_HELD; assert m.handle(MouseEvent('xbutton_down',button=1)); print('OK T-011')"
verify-output: |
  OK T-011
deviation: none

## TASK T-012: Fix wants_moves, tích hợp GestureRecognizer & hủy ngược trong mouse_mapper_logic.py
status: done
files-changed: src/features/mouse_mapper/logic/mouse_mapper_logic.py
verify-cmd: python -c "from features.mouse_mapper.logic.mouse_mapper_logic import MouseMapperLogic; from features.mouse_mapper.types.mouse_mapper_types import MapperState, MouseEvent, ScrollDirection; m=MouseMapperLogic(); m._state=MapperState.GESTURE; assert m.wants_moves() is True; m._state=MapperState.RIGHT_HELD; assert m.handle(MouseEvent('scroll',scroll_dir=ScrollDirection.UP)); assert m._state==MapperState.SCROLLING; print('OK T-012')"
verify-output: |
  OK T-012
deviation: none

## TASK T-013: Tạo GestureSettingsDialog UI quản lý preset gestures
status: done
files-changed: src/features/shortcut_panel/ui/gesture_settings_dialog.py
verify-cmd: python -c "from features.shortcut_panel.ui.gesture_settings_dialog import GestureSettingsDialog; assert GestureSettingsDialog is not None; print('OK T-013')"
verify-output: |
  OK T-013
deviation: none

## TASK T-014: Wiring mở GestureSettingsDialog từ TrayUI và main.py
status: done
files-changed: src/features/mouse_mapper/ui/tray_ui.py, src/main.py
verify-cmd: python -c "from features.mouse_mapper.ui.tray_ui import TrayUI; import inspect; sig=inspect.signature(TrayUI.__init__); assert 'on_gestures' in sig.parameters; print('OK T-014')"
verify-output: |
  OK T-014
deviation: none

## SUMMARY
tasks-done: 9/9
blocked-reason: none
notes-for-validator: none
