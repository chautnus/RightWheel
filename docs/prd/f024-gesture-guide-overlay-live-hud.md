# PRD — f024-gesture-guide-overlay-live-hud

## 1. Mục tiêu (Objective)
Cung cấp cửa sổ hướng dẫn cử chỉ trực tiếp (Gesture Guide Overlay HUD) hiển thị ngay tại góc dưới màn hình khi người dùng nhấn giữ chuột phải, nhằm loại bỏ rào cản ghi nhớ cử chỉ vẽ và hỗ trợ người dùng nhận diện ngay lập tức hành động được gán cho từng hướng di chuyển của chuột.

---

## 2. Yêu cầu Người dùng (User Stories)
- **US-062**: Khi tôi nhấn giữ chuột phải (`RMB Down`), tôi muốn thấy ngay một HUD tinh tế ở góc dưới bên phải màn hình hiển thị 4 hướng mũi tên (Lên, Xuống, Trái, Phải) kèm theo tên lệnh hoặc mô tả hành động tương ứng, để tôi biết mình có thể vẽ những cử chỉ nào mà không cần mở cài đặt.
- **US-063**: Khi tôi bắt đầu kéo chuột theo một hướng (ví dụ: kéo Xuống `D`), tôi muốn HUD tự động cập nhật để hiển thị các hướng rẽ tiếp theo khả dụng (ví dụ: rẽ Phải `R` để Đóng tab) theo thời gian thực.
- **US-064**: Khi tôi nhả chuột phải (`RMB Up`), HUD phải biến mất ngay lập tức mà không gây trễ, không cướp focus của ứng dụng đang làm việc và không cản trở việc click chuột thông thường.

---

## 3. Tiêu chí Chấp nhận (Acceptance Criteria)
1. **Hiển thị tức thì khi Giữ Chuột Phải:**
   - Khi `WM_RBUTTONDOWN` được kích hoạt, `MouseMapperLogic.on_hold_start` phát lệnh mở `GestureGuideOverlay` ngay lập tức mà không cần chờ chuột di chuyển vượt ngưỡng `move_threshold`.
2. **Định vị & Giao diện HUD:**
   - Panel kích thước cố định `480x480px`, đặt cách mép dưới bên phải màn hình 24px trên mọi độ phân giải và đa màn hình.
   - Nền tối bo tròn `36px`, trong suốt (`-transparentcolor`), icon trung tâm thể hiện nút chuột phải đang được giữ (`RMB Glyph`).
   - 4 mũi tên hướng chính (`UP`, `DOWN`, `LEFT`, `RIGHT`) kèm nhãn text đậm màu xanh nhạt `#CFE6FF`.
3. **Cập nhật Live theo Nét vẽ:**
   - Mỗi khi một sector hướng chính được ghi nhận, HUD cập nhật `on_sector_change(path)`, loại bỏ nhánh ngược chiều và hiển thị các gợi ý cử chỉ khớp với tiền tố vừa vẽ.
4. **Không Cản trở & Click-Through:**
   - Gán cờ Win32 `WS_EX_TRANSPARENT | WS_EX_NOACTIVATE | WS_EX_LAYERED | WS_EX_TOOLWINDOW`. Cửa sổ không bao giờ cướp focus và cho phép click xuyên thấu 100%.
5. **Dọn dẹp Bộ nhớ:**
   - Đóng HUD khi `WM_RBUTTONUP`, gọi `trim_memory()` sau 300ms để giữ mức tiêu thụ RAM luôn tối ưu (~40MB).
6. **Kiểm thử Tự động:**
   - 100% test suite `pytest tests/` vượt qua, bao gồm test tích hợp luồng callback `on_hold_start` và `on_sector_change`.
