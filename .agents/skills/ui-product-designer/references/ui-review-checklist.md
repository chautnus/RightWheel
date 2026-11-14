# UI Review & Quality Audit Checklist

Bảng kiểm định chất lượng giao diện toàn diện dành cho Antigravity Agent và lập trình viên. Dùng để tự rà soát sau khi code mới hoặc kiểm tra, đánh giá màn hình hiện hữu trước khi bàn giao.

---

## 1. Usability & Hierarchy Checklist

- [ ] **3-Second Comprehension**: Người dùng có hiểu ngay màn hình này dùng để làm gì và trạng thái hiện tại không?
- [ ] **Single Primary Action**: Có đúng **một** primary action duy nhất nổi bật nhất màn hình không?
- [ ] **Action Hierarchy**: Các nút phụ có dùng đúng variant `outline`, `secondary` hoặc `ghost` không?
- [ ] **Visual Anchors**: Điểm nhìn đầu tiên có hướng vào khối thông tin giá trị nhất không (thay vì dàn trải đều)?
- [ ] **Information Density**: Mật độ thông tin có cân đối không? (Không quá thưa như landing page, không quá nghẹt thở như bảng excel cũ).

---

## 2. Responsive & Layout Checklist

- [ ] **Mobile First (375px)**:
  - Có bị tràn chiều ngang (horizontal scrollbar ngoài ý muốn) không?
  - Bảng dữ liệu có giải pháp cuộn ngang êm hoặc chuyển sang dạng card list trên mobile không?
  - Menu chuyển thành Drawer / Sheet mượt mà không?
- [ ] **Tablet (768px)**:
  - Grid phân bổ hợp lý (từ 1 cột mobile lên 2 cột tablet)?
- [ ] **Desktop (1024px - 1440px)**:
  - Nội dung có được giới hạn trong container `max-w-*` không bị kéo giãn quá đà trên màn hình siêu rộng?
- [ ] **Spacing Rhythm**: Có bám sát thang 4px (`gap-2`, `gap-4`, `p-6`, `p-8`) và không chứa arbitrary values (`p-[13px]`) không?

---

## 3. Complete State Coverage Checklist

Mọi component/màn hình tương tác phải có đủ 10 trạng thái:

1. [ ] **Default**: Trạng thái nghỉ bình thường.
2. [ ] **Hover**: Phản hồi đổi màu nhẹ nhàng (`hover:bg-accent` hoặc `hover:opacity-90`).
3. [ ] **Focus-visible**: Đường viền focus sắc nét khi dùng phím Tab (`focus-visible:ring-2 focus-visible:ring-ring`).
4. [ ] **Active**: Hiệu ứng nhấn xuống (`active:scale-[0.98]` hoặc đổi màu nền).
5. [ ] **Disabled**: Mờ và chặn click (`disabled:opacity-50 disabled:pointer-events-none`).
6. [ ] **Loading**: Skeleton tương ứng shape thật hoặc spinner tích hợp trong button (không che toàn màn hình nếu không cần thiết).
7. [ ] **Empty**: Thông báo cụ thể + 1 action bắt đầu (không để bảng trống không chữ).
8. [ ] **Error**: Thông báo lỗi cụ thể, có cách khắc phục hoặc nút Retry.
9. [ ] **Success**: Phản hồi lưu thành công qua toast hoặc inline indicator.
10. [ ] **No Results**: Khi filter/search trả về rỗng, có nút xóa bộ lọc.

---

## 4. Theme & Dark Mode Checklist

- [ ] **Zero Hardcoded Colors**: Không có bất kỳ mã `#hex`, `rgb()`, `hsl()` nào trong file code.
- [ ] **Semantic Tokens**: Sử dụng chuẩn xác `bg-background`, `bg-card`, `text-foreground`, `text-muted-foreground`, `border-border`.
- [ ] **Dark Mode Contrast**: Kiểm tra trong dark mode nền không bị đen tuyền tuyệt đối (OLED pitch black) gây chói lóa, các đường border vẫn giữ độ phân cách rõ ràng.

---

## 5. Accessibility (WCAG AA) Checklist

- [ ] **Contrast Ratio**:
  - Chữ thường đạt tối thiểu **4.5:1** so với nền.
  - Chữ lớn / UI controls đạt tối thiểu **3:1**.
- [ ] **Touch Target Size**: Các vùng bấm trên màn cảm ứng tối thiểu **44 x 44px**.
- [ ] **Form Labels**: Mỗi ô input đều có `<Label htmlFor="...">` hoặc `aria-label` tương ứng.
- [ ] **Keyboard Navigation**: Mọi nút bấm, link, dialog có thể đóng/mở/chọn hoàn toàn bằng bàn phím (Tab, Enter, Escape).
- [ ] **Motion Sensitivity**: Có hỗ trợ `motion-reduce:transition-none` cho người dùng nhạy cảm chuyển động.

---

## 6. Anti-AI Template Checklist

- [ ] KHÔNG có gradient tím/xanh trang trí.
- [ ] KHÔNG có hiệu ứng phát sáng neon glow.
- [ ] KHÔNG có glassmorphism mờ đục vô nghĩa (`backdrop-blur`).
- [ ] KHÔNG có biểu tượng lấp lánh (sparkles ✨) làm icon chính.
- [ ] KHÔNG có emoji thay thế cho icon SVG chuyên nghiệp (Lucide).
- [ ] KHÔNG có layout 3 thẻ card chia đều bằng nhau thiếu phân cấp.
- [ ] KHÔNG có animation lặp lại liên tục gây xao nhãng.

---

## 7. Review Report Template

Khi thực hiện review một giao diện hiện có, trình bày kết quả theo đúng cấu trúc sau:

```markdown
# UI Audit Report: [Tên trang / Component]

### 1. Critical Issues
*Các lỗi làm hỏng trải nghiệm người dùng, vi phạm a11y nghiêm trọng hoặc vỡ giao diện.*
- **[A11y/Contrast]**: Chữ caption tại `ProjectCard` dùng `text-gray-300` trên nền trắng chỉ đạt 1.8:1 (yêu cầu 4.5:1).
- **[Broken State]**: Bảng dữ liệu chưa có empty state khi API trả về mảng rỗng `[]`.

### 2. Consistency Issues
*Các điểm lệch chuẩn design system, dùng sai token hoặc component variant.*
- **[Color Token]**: Phát hiện hardcode mã màu `#1E293B` tại dòng 42 thay vì dùng `bg-card`.
- **[Button Variant]**: Nút "Delete User" đang dùng variant `default`, cần đổi sang `destructive`.

### 3. Polish Suggestions
*Đề xuất nâng tầm thẩm mỹ, nhịp điệu khoảng trắng và độ mượt mà.*
- **[Hierarchy]**: Thay vì chia 3 cột đều nhau, nên mở rộng biểu đồ chính lên 2 cột để tạo điểm nhấn thị giác.
- **[Density]**: Giảm padding từ `p-8` xuống `p-6` trên desktop để tăng mật độ thông tin hữu ích.

### 4. Concrete Changes (Code Diff)
*Mã nguồn hoặc class cụ thể cần thay thế:*
```diff
- <button className="bg-blue-600 text-white p-[10px] rounded-lg">
-   Save
- </button>
+ <Button variant="default" size="sm">
+   Save changes
+ </Button>
```
