# Design Blueprint: Remove X1/X2 Rocker Gesture & Fix Mouse Button Hangs (F-009)

## 1. Modules bị chạm (Existing Modules to Modify)
- `src/features/mouse_mapper/services/mouse_hook_service.py` (~175 dòng)
  - Xóa: Hằng số `WM_XBUTTONDOWN = 0x020B`, `XBUTTON1 = 0x0001`, `XBUTTON2 = 0x0002`
  - Xóa: Nhánh `elif w_param == WM_XBUTTONDOWN:` trong `_ll_proc`
- `src/features/mouse_mapper/logic/mouse_mapper_logic.py` (~158 dòng)
  - Xóa: Thuộc tính `self._xbutton_used` trong `__init__()`
  - Xóa: Lệnh reset `self._xbutton_used = False` trong `_on_right_down()`
  - Xóa: Nhánh `if event.kind == "xbutton_down": return self._on_xbutton_down(event.button)` trong `handle()`
  - Xóa: Phương thức `_on_xbutton_down(self, button: int) -> bool`
  - Xóa: Khối `if self._xbutton_used: self._xbutton_used = False; return True` trong `_on_right_up()`
- `src/features/mouse_mapper/services/hotkey_service.py` (~150 dòng)
  - Xóa: Hàm `switch_tab_x1x2(forward: bool)`
- `src/features/mouse_mapper/types/mouse_mapper_types.py` (~27 dòng)
  - Dọn dẹp docstring `kind` trong `MouseEvent`
- `src/features/shortcut_panel/ui/reference_tab.py` (~75 dòng)
  - Xóa dòng tra cứu: `("RightWheel", "RMB + X1/X2", "Switch browser tab prev/next")`

## 2. Thứ tự triển khai
1. `mouse_hook_service.py`
2. `mouse_mapper_logic.py`
3. `hotkey_service.py`, `mouse_mapper_types.py`, `reference_tab.py`
4. Kiểm tra cú pháp tĩnh `py_compile`, kiểm tra giới hạn dòng ≤ 250 dòng, đóng tiến trình và build lại `.exe`
