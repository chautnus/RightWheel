# ADR-009: Modular Raycast Palette UI Architecture

## Status
Accepted

## Context
Shortcut Panel hiện tại tập trung toàn bộ code render trong `panel_window.py` (207 dòng). Khi bổ sung phong cách thiết kế Raycast (kbd badges, inline volume slider tương tác kéo thả/cuộn, section headers, footer hints), độ dài file sẽ vượt quá giới hạn SYSTEM LOCK (250 dòng). Đồng thời, tính năng inline volume slider cần khả năng lắng nghe sự kiện kéo thả chuột và cuộn chuột mượt mà trên canvas.

## Decision
1. **Chia nhỏ kiến trúc giao diện Panel (Modular View Decomposition)**:
   - `panel_window.py`: Đóng vai trò Window Coordinator (quản lý `tk.Toplevel`, vòng đời hiển thị/ẩn, định vị tọa độ chuột, bàn phím điều hướng cấp cao).
   - `panel_volume_widget.py`: Module chuyên biệt xử lý widget Volume inline (vẽ canvas thanh trượt, xử lý click/drag/wheel để cập nhật Windows master volume qua `volume_service.py`, đồng bộ hiển thị icon động).
   - `panel_item_renderer.py`: Module chuyên biệt render danh sách các item shortcut, kbd badge, hover/selection state, và section dividers.
2. **Kế thừa và tái sử dụng `volume_service.py`**:
   - Sử dụng trực tiếp API COM Core Audio thực tế từ `volume_service.py` (F-008), đảm bảo thanh slider inline phản ánh 100% âm lượng Windows.
3. **Màu sắc & Phông chữ Raycast**:
   - Palette Zinc Dark (`#121214`, `#18181b`, `#27272a`, `#3f3f46`, `#a1a1aa`, `#ffffff`).
   - Phông chữ mặc định `Segoe UI Variable` hoặc `Segoe UI`.

## Consequences
- Tách biệt rõ ràng trách nhiệm giữa Window Lifecycle, Item Rendering và Volume Widget.
- Mọi file mã nguồn duy trì ở mức 100 - 180 dòng (tuân thủ nghiêm ngặt SYSTEM LOCK ≤ 250 dòng).
- Giao diện đạt độ hoàn thiện cao, hiện đại và phản hồi nhanh.
