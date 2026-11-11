# Design Blueprint: F-010 Raycast Command Palette

## 1. Modules & Components

### Existing touched:
- `src/features/shortcut_panel/ui/panel_window.py` (~150 dòng sau refactor)
  - Trách nhiệm: Window Coordinator, định vị con trỏ chuột, bàn phím điều hướng, gắn kết volume widget và item renderer, render header/footer.

### New modules (Skeleton created):
- `src/features/shortcut_panel/ui/panel_volume_widget.py` (~115 dòng)
  - Trách nhiệm: Inline Canvas Volume Slider, dynamic speaker icon, master volume real-time track drag/click/wheel.
  - Colors:
    - bg: `#18181b`
    - track: `#27272a`
    - fill: `#0078d4` (contrast on dark ~4.8:1)
    - text: `#ffffff` (contrast on #18181b ~15.2:1)
    - muted: `#a1a1aa` (contrast on #18181b ~7.2:1)
- `src/features/shortcut_panel/ui/panel_item_renderer.py` (~125 dòng)
  - Trách nhiệm: Render danh sách shortcut, mechanical kbd badges, section headers, hover/selected row.
  - Colors:
    - row unselected bg: `#121214` / text: `#a1a1aa` (ratio ~7.8:1)
    - row selected bg: `#27272a` / text: `#f4f4f5` (ratio ~11.8:1)
    - kbd badge bg: `#27272a` / border: `#3f3f46` / text: `#ffffff` (ratio ~11.8:1)
    - accent indicator: `#0078d4`
    - section header text: `#71717a` trên bg `#121214` (ratio ~4.6:1)

---

## 2. Variables & Functions Impact Analysis

### New variables/constants/classes:
- `PanelVolumeWidget` in `panel_volume_widget.py`
  - `_BG`, `_TRACK_BG`, `_TRACK_FILL`, `_FG_TEXT`, `_FG_MUTED`
  - `get_speaker_glyph(level: float) -> str`
  - Methods: `refresh()`, `_on_click()`, `_on_drag()`, `_on_wheel()`, `_update_from_x()`
- `PanelItemRenderer` in `panel_item_renderer.py`
  - `_BG_BASE`, `_BG_SELECTED`, `_BORDER_KBD`, `_FG_SELECTED`, `_FG_NORMAL`, `_FG_SECTION`, `_ACCENT_BAR`
  - Methods: `render_items()`, `_render_kbd_badge()`, `_render_row()`

### Modified in `panel_window.py`:
- Thêm `self._volume_widget`, `self._item_renderer`
- Thay thế hàm `_render()` thành các lời gọi ủy quyền sạch sẽ, thêm `_render_footer()`
- Xóa các biến style cục bộ không còn dùng
- Giữ nguyên các binding sự kiện và logic bên ngoài.
