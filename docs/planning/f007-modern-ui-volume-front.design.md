# Design Blueprint: Modern Minimalist UI & Volume Fronting (F-007)

## 1. Modules bị chạm (Existing Modules)
- `src/features/shortcut_panel/services/config_service.py` (~187 dòng)
- `src/features/shortcut_panel/ui/volume_overlay.py` (~145 dòng)
- `src/features/shortcut_panel/ui/panel_window.py` (~199 dòng)
- `src/features/shortcut_panel/ui/settings_window.py` (~163 dòng)

## 2. File mới (New Module)
- `src/features/shortcut_panel/ui/general_volume_tab.py` (~130 dòng)
  - Trách nhiệm: Render thẻ General & Volume trong Settings Window (tách riêng từ `settings_window.py` để giữ `settings_window.py` < 180 dòng).
  - Exports: `class GeneralVolumeTab(tk.Frame)`
  - Colors:
    - Text: `#ffffff` trên Background: `#18181b` (contrast ratio ~16:1 ✓)
    - Subtext/Labels: `#a1a1aa` trên Background: `#18181b` (contrast ratio ~7:1 ✓)
    - Card containers: `#1e1e24` với viền `#27272a` trên Background: `#18181b`
    - Accent elements: `#0078d4` (text `#ffffff` trên `#0078d4` ratio ~4.6:1 ✓)

## 3. Quy chuẩn màu sắc UI (WCAG AA Contrast Check)
- **Shortcut Panel (`panel_window.py`)**:
  - Panel Background: `#121214`
  - Item Normal: Text `#a1a1aa` trên Background `#121214` (contrast ~7:1 ✓)
  - Item Selected: Text `#ffffff` trên Background `#27272a` (contrast ~13:1 ✓)
  - Badge [0-9]: Text `#71717a` trên Background `#1e1e24` (contrast ~4.5:1 ✓)
  - Volume Bar Fill: `#0078d4` trên Background `#18181b`
- **Volume Overlay HUD (`volume_overlay.py`)**:
  - Capsule Background: `#18181b` viền `#27272a`
  - Icon & Text %: Text `#ffffff` trên Background `#18181b` (contrast ~16:1 ✓)
  - Progress Track: `#27272a`, Fill: `#0078d4`
- **Settings Window (`settings_window.py`)**:
  - Sidebar Background: `#121214`
  - Sidebar Nav Inactive: Text `#a1a1aa` trên Background `#121214` (contrast ~7:1 ✓)
  - Sidebar Nav Active: Text `#ffffff` trên Background `#27272a` (contrast ~13:1 ✓)
  - Content Background: `#18181b`

## 4. Thứ tự triển khai (Implementation Order)
1. `config_service.py` (bổ sung fields volume + di chuyển volume action ra root `_DEFAULT`)
2. `general_volume_tab.py` (tạo mới component thẻ cấu hình General & Volume)
3. `volume_overlay.py` (nâng cấp Capsule HUD, icon động, nhãn %)
4. `panel_window.py` (tích hợp Volume Quick-Widget và modern minimalist item styling)
5. `settings_window.py` (tái cấu trúc sang Sidebar Navigation layout 2 cột)
6. Kiểm tra tĩnh cú pháp và giới hạn độ dài file (≤ 250 dòng).
