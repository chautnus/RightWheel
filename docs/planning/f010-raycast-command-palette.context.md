## Elicitation — 2026-11-11

Problem: Floating Shortcut Panel hiện tại có giao diện phẳng cổ điển, các item hiển thị đơn điệu, thiếu phân cấp thị giác hiện đại (visual hierarchy), phím số tắt đơn giản, thanh volume vẫn phải mở popup riêng hoặc hiển thị dạng text label khô khan.
Goal: Hiện đại hóa toàn diện giao diện Shortcut Panel theo ngôn ngữ thiết kế Raycast / Linear Command Palette — tối giản, thanh lịch, phím tắt dạng kbd badge nổi bật, thanh trượt volume inline trực tiếp, phân khu danh mục rõ ràng, thời gian render < 30ms.
Scope IN:
- Tái cấu trúc giao diện `panel_window.py` theo phong cách Raycast / Linear Command Palette.
- Phím tắt dạng kbd badge cơ học (`#27272a` nền, viền `#3f3f46`, chữ `#ffffff` đậm).
- Inline Volume Slider trực quan tại dòng Volume: hiển thị icon loa biến thiên (`🔇`, `🔈`, `🔉`, `🔊`), thanh trượt tiến trình thực tế của Windows, hỗ trợ kéo thả chuột và cuộn chuột ngay tại dòng đó.
- Phân vùng nội dung (Section Headers: `PINNED / FREQUENT`, `SYSTEM ACTIONS`).
- Thanh Footer Status / Navigation hints tinh tế (`◈ Profile • ↑↓ Navigate • Enter Select • Esc Close`).
- Tách nhỏ module (ví dụ `panel_volume_widget.py`, `panel_item_renderer.py`) để tuân thủ triệt để SYSTEM LOCK (mọi file ≤ 250 dòng).
Scope OUT:
- Không thay đổi máy trạng thái RMB Hook (`mouse_hook_service.py`), không đụng vào `volume_service.py` COM backend (đã hoàn thiện ở F-008).
- Không nhúng Chromium/Electron hay web engine cồng kềnh — 100% native Tkinter Canvas & Widgets.
Users: Power user sử dụng chuột phải + cuộn chuột muốn một menu phím tắt đẹp mắt, hiện đại như Raycast trên macOS/Windows, điều khiển âm lượng và mở app tức thời không có độ trễ.
Stories:
- US-028: Người dùng nhìn thấy Shortcut Panel mang phong cách Raycast tối giản, viền sắc nét, bo góc và badge kbd nổi bật.
- US-029: Người dùng có thể điều chỉnh âm lượng Windows ngay trên dòng Volume của Panel bằng cách cuộn chuột hoặc kéo chuột trên thanh slider inline.
- US-030: Người dùng nhìn thấy phân cấp danh mục rõ ràng và footer hướng dẫn thao tác tinh tế.
Constraints:
- Tkinter native thread, single root.
- Mọi file mã nguồn ≤ 250 dòng.
- Không mở trình duyệt test (`NGHIÊM CẤM test bằng browser`).

---

## PRD — 2026-11-11

Path: docs/prd/f010-raycast-command-palette.md
Version: 1.0
Summary: Đặc tả kỹ thuật và yêu cầu giao diện Raycast / Linear Command Palette cho RightWheel Shortcut Panel.

---

## Architecture — 2026-11-11

Pattern: Modular Component Architecture (Tkinter Canvas + Custom Widgets)
ADR-009: Modular Raycast Palette UI Architecture → docs/adr/ADR-009-raycast-palette-modular-ui.md
## Tasks — 2026-11-11

Total: 4 tasks (T-055 to T-058), path: docs/planning/f010-raycast-command-palette.tasks.md
- T-055: Create `panel_volume_widget.py` for inline interactive volume control
- T-056: Create `panel_item_renderer.py` for Raycast item styling and kbd badges
- T-057: Refactor `panel_window.py` with modular coordination and footer hints
- T-058: Validation, PyInstaller build check, and changelog update
