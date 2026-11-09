## Elicitation — 2026-11-09

Problem: Giao diện hiện tại của RightWheel (Shortcut Panel, Settings Window, Volume HUD) mang phong cách Tkinter cổ điển, thô cứng và chưa tối ưu không gian hiển thị. Tính năng điều khiển âm lượng (Volume) vừa được bổ sung ở F-006 vẫn bị giấu sâu trong thư mục con "📁 App", khiến người dùng khó tiếp cận nhanh.
Goal: Hiện đại hóa toàn diện giao diện RightWheel theo phong cách Modern Dark Minimalist (Fluent/Raycast UI), đồng thời đưa chức năng điều khiển âm lượng ra vị trí trung tâm (Volume Bar tích hợp trên Shortcut Panel và Capsule HUD nổi bật).
Scope IN:
- Tích hợp thanh trượt Volume Quick-Widget trực tiếp tại đỉnh Panel (hiển thị % và thanh trượt, hỗ trợ cuộn chuột chỉnh volume ngay trên widget).
- Thiết kế lại panel item: bo góc, typography Segoe UI Variable, badge số tắt [0-9] tinh tế, highlight hover mềm mại, khoảng cách thoáng đãng.
- Đưa action Volume Control ra ngoài root shortcuts mặc định thay vì nằm trong folder con.
- Nâng cấp Volume Overlay thành dạng Capsule/Pill HUD hiện đại (phong cách Windows 11 Flyout / macOS) với icon loa động (🔇/🔈/🔉/🔊), thanh tiến trình bo cong, nhãn %.
- Chuyển đổi Settings Window từ bố cục tab Notebook truyền thống sang Modern Sidebar Navigation + card containers bo góc phong cách Slate/Zinc tối giản.
- Thiết lập khu vực quản lý Volume chuyên biệt trong Settings (cấu hình bước nhảy % khi cuộn, bật/tắt hiển thị Volume bar trên Shortcut Panel).
- Đảm bảo tuân thủ SYSTEM LOCK (tất cả các file UI ≤ 250 dòng).
Scope OUT:
- Không thay đổi State Machine cốt lõi trong mouse_mapper_logic.py (LOCKED).
- Không thay đổi Gesture Engine và cơ chế hook chuột WH_MOUSE_LL (LOCKED).
- Không thêm dependency bên ngoài (giữ nguyên chuẩn tkinter, ctypes, pystray).
Users: Power-user Windows — When đang làm việc hoặc giải trí, I want điều chỉnh âm lượng và mở phím tắt trên một giao diện hiện đại, tối giản, đẹp mắt, so I can thao tác nhanh mà không bị phân tâm bởi giao diện thô cứng.
Stories: US-020, US-021, US-022, US-023
Constraints: Bắt buộc tuân thủ CLAUDE.md Rules: Rule 4b (thứ tự lift/focus/position của Toplevel), Rule 6 (Tkinter threading single-root). Giới hạn dòng mã nguồn ≤ 250 dòng/file.
NFR: Hiệu năng mượt mà, phản hồi tức thì với thao tác cuộn chuột, không gây giật lag hoặc leak memory/threads.


---

## PRD — 2026-11-09

Path: docs/prd/f007-modern-ui-volume-front.md
Version: 1.0
Summary: Tái thiết kế toàn diện giao diện RightWheel (Shortcut Panel, Volume Overlay HUD, Settings Window) theo phong cách Modern Dark Minimalist, tích hợp Volume Bar trực tiếp trên Shortcut Panel và nâng cấp Capsule HUD với icon loa động và nhãn %.

---

## Architecture — 2026-11-09

Pattern: Component Modularization + Canvas Custom Widgets + Two-Column Sidebar Navigation
ADR-006: Kiến trúc Tái thiết kế Giao diện Modern Minimalist & Tích hợp Quản lý Volume Phía trước → docs/adr/ADR-006-modern-ui-volume-front-architecture.md


---

## Tasks — 2026-11-09

Total: 6 tasks, 4h estimate
Path: docs/planning/f007-modern-ui-volume-front.tasks.md
Batch 1: TSK-036, TSK-037, TSK-038
Batch 2: TSK-039, TSK-040, TSK-041
