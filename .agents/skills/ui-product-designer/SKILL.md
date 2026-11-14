---
name: ui-product-designer
description: Thiết kế và implement giao diện UI/UX chuyên nghiệp, rõ ràng, giàu cá tính sản phẩm theo chuẩn Tailwind CSS + shadcn/ui (React/Next.js). Kích hoạt khi user yêu cầu tạo mới hoặc chỉnh sửa screen, page, component, form, table, dashboard, modal, empty state, responsive layout, dark mode, hoặc review/cải thiện UI hiện có. Ngăn chặn triệt để phong cách AI generic (gradient tím/xanh, neon glow, glassmorphism, card grid đều nhau).
---

# UI Product Designer Skill

Chuyên gia thiết kế và hiện thực hóa giao diện sản phẩm số (B2B, SaaS, web app) tập trung vào tính rõ ràng, cấu trúc thứ bậc, khả năng truy cập (a11y) và độ tin cậy.

## 1. When to Use
Kích hoạt skill khi thực hiện bất kỳ tác vụ nào sau đây:
- Tạo mới hoặc tái cấu trúc screen, page, layout (dashboard, settings, auth, feed, list/detail).
- Thiết kế hoặc implement component: form, data table, modal, dialog, sheet, drawer, empty state, navigation.
- Cải thiện responsive (mobile, tablet, desktop) và chuyển đổi dark mode.
- Đánh giá (review), refactor hoặc dọn dẹp visual debt của UI hiện có.

## 2. Core Principle
- **Clarity over cleverness**: Giao diện phục vụ hoàn thành nhiệm vụ của người dùng, không phải để trưng bày hiệu ứng.
- **3-Second rule**: Người dùng phải hiểu ngay trong 3 giây: mình đang ở đâu, trạng thái hiện tại là gì, và action chính tiếp theo là gì.
- **Exactly one primary action**: Mỗi viewport/màn hình chỉ có duy nhất một primary action nổi bật.

## 3. Design Direction
- **Phong cách chủ đạo**: Calm, precise, credible, modern.
- **Tập trung**: Khoảng cách có nhịp điệu (spatial rhythm), viền tinh tế (subtle border 1px), typography phân cấp sắc nét, độ tương phản cao.
- **Chi tiết tra cứu**: Xem [design-tokens.md](file:///c:/dev/Mousehotkey/.agents/skills/ui-product-designer/references/design-tokens.md).

## 4. Mandatory Workflow
Trước khi viết mã, agent **bắt buộc** thực hiện 4 bước:
1. **Khảo sát hệ thống (Read first)**: Đọc `DESIGN.md`, `globals.css`, Tailwind config, thư mục components (`@/components/ui`), và các trang tương tự hiện có để kế thừa tokens.
2. **Lập Blueprint UI**: Trình bày cấu trúc màn hình theo quy định tại Mục 11 trước khi code.
3. **Hiện thực hóa (Implementation)**: Dùng semantic tokens, xử lý trọn vẹn 10 trạng thái (xem Mục 11).
4. **Self-Review**: Tự kiểm tra qua [ui-review-checklist.md](file:///c:/dev/Mousehotkey/.agents/skills/ui-product-designer/references/ui-review-checklist.md) trước khi báo cáo hoàn thành.

## 5. Tailwind Rules
- **Spacing scale 4px**: Chỉ dùng `0.5 (2px)`, `1 (4px)`, `2 (8px)`, `3 (12px)`, `4 (16px)`, `6 (24px)`, `8 (32px)`, `12 (48px)`, `16 (64px)`.
- **Tuyệt đối cấm arbitrary values**: Không dùng `p-[17px]`, `w-[343px]`, `text-[13px]` trừ khi xử lý kỹ thuật ngoại lệ đã xác minh.
- **Mobile-first**: Viết class mặc định cho mobile, mở rộng dần với `sm:`, `md:`, `lg:`, `xl:`.

## 6. Typography Rules
- **Phân cấp tối đa 4 tầng/màn hình**: Page title (`text-2xl font-semibold`), Section header (`text-base font-medium`), Body (`text-sm font-normal`), Caption/Meta (`text-xs text-muted-foreground`).
- Không tăng kích thước font để làm nổi bật nếu chỉ cần đổi weight hoặc color token.
- Luôn ghép cặp `leading-*` tương ứng để tránh chồng lấn dòng chữ.

## 7. Color Rules
- **Không hardcode**: CẤM viết mã hex (`#3B82F6`), `rgb()`, `hsl()` trong JSX/TSX.
- **Chỉ dùng shadcn semantic tokens**: `bg-background`, `bg-card`, `text-foreground`, `text-muted-foreground`, `border-border`, `bg-primary`, `text-primary-foreground`, `bg-destructive`, `text-destructive-foreground`.
- **Dark mode tự nhiên**: Màu tối phải điều chỉnh qua biến HSL ở CSS layer, không dùng `dark:bg-black` bừa bãi.

## 8. shadcn/ui Rules
- **Button variants**:
  - `default`: Primary action duy nhất của màn hình.
  - `secondary` / `outline`: Action phụ, thao tác song song.
  - `ghost`: Thao tác thứ cấp, icon actions trong bảng hoặc thanh điều hướng.
  - `destructive`: Thao tác xóa, hủy không thể hoàn tác (cần confirmation dialog).
- **Phản hồi đúng lớp**: Toast cho non-blocking notification, Inline message cho validation lỗi, Modal/Dialog chỉ cho task tập trung hoặc xác nhận nguy hiểm.
- Xem chi tiết triển khai tại [component-rules.md](file:///c:/dev/Mousehotkey/.agents/skills/ui-product-designer/references/component-rules.md).

## 9. Anti-AI UI Rules
Nghiêm cấm tuyệt đối các đặc trưng "AI generic template":
- ❌ Gradient tím/xanh (`from-purple-600 to-blue-500`), nút bấm phát sáng (glow effects).
- ❌ Glassmorphism vô nghĩa (`backdrop-blur-md bg-white/10` trên nền phức tạp).
- ❌ Hiệu ứng 3D bóng bẩy giả tạo, decorative drop-shadows quá đậm.
- ❌ Sparkle icons (✨), icon trang trí tràn lan, emoji dùng làm icon chính.
- ❌ Bố cục chia đều feature cards (equal-width 3-col grid thiếu điểm nhấn).
- ❌ Animation chạy liên tục gây xao nhãng người dùng.

## 10. Accessibility Rules (WCAG AA)
- Đảm bảo contrast ratio tối thiểu 4.5:1 cho text thường, 3:1 cho large text & UI controls.
- Keyboard navigation: Luôn có `focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2`.
- Touch target: Tối thiểu 44x44px trên mobile (`min-h-[44px] min-w-[44px]`).
- Hỗ trợ `motion-reduce:transition-none` hoặc `@media (prefers-reduced-motion)`.

## 11. Output Format

### A. Trước khi code (UI Blueprint)
Agent phải in ngắn gọn khối thông tin sau:
```markdown
### UI Blueprint: [Tên màn hình/Component]
- **Primary Job**: [Mục đích sống còn của màn hình này]
- **Primary User Task**: [Việc chính user muốn làm khi vào đây]
- **Primary Action**: [Nút/Thao tác quan trọng nhất - duy nhất 1]
- **Secondary & Tertiary Actions**: [Các thao tác phụ kèm theo]
- **Information Hierarchy**: [Thứ tự thông tin từ trên xuống dưới]
- **Layout Pattern**: [Ví dụ: Sidebar + Header + Data List / Stacked Form]
- **States Covered**: Mobile/Desktop, Loading, Empty, Error, Success, Disabled
```

### B. Khi implement
- Triển khai bằng Tailwind + shadcn/ui với semantic tokens.
- Liệt kê danh sách file đã tạo/chỉnh sửa kèm diff rõ ràng.

### C. Sau khi code (Self-Review Checklist)
Báo cáo xác nhận đã pass các tiêu chí:
- [x] Responsive: Mobile (375px), Tablet (768px), Desktop (1280px).
- [x] Theme: Light mode & Dark mode đồng bộ qua semantic tokens.
- [x] States: Hover, Focus-visible, Active, Disabled, Loading (skeleton), Empty, Error, Success.
- [x] A11y: WCAG AA contrast, keyboard tab-order, touch target >= 44px, prefers-reduced-motion.
- [x] Anti-AI: Đã loại bỏ hoàn toàn gradient tím, glassmorphism, sparkle icon, card grid đều.

### D. Định dạng khi Review UI hiện có
Khi được yêu cầu review giao diện hiện hữu, trả về đúng 4 mục:
1. **Critical issues**: Vi phạm usability, lỗi a11y, vỡ responsive, thiếu states, contrast thấp.
2. **Consistency issues**: Dùng sai token màu, spacing tùy tiện, sai variant component.
3. **Polish suggestions**: Tối ưu mật độ thông tin, hierarchy, nhịp điệu khoảng trắng.
4. **Concrete changes**: Đưa code diff hoặc hướng dẫn sửa class Tailwind/props shadcn cụ thể.

## 12. Escalation Rules
- **Chưa có DESIGN.md hoặc token config**: Dừng lại hỏi user. Đề xuất design system tối thiểu (font, màu nền/chữ, radius, spacing) và chỉ code sau khi user duyệt.
- **User yêu cầu hiệu ứng nặng (3D, neon, glassmorphism)**: Hỏi rõ mục tiêu trải nghiệm và đề xuất phương án tối giản (restrained) thay thế. Chỉ làm khi user khẳng định yêu cầu.
- **Đã có sẵn design system**: Tuyệt đối tuân thủ, không tự tiện đổi màu brand, font, border-radius. Báo cáo inconsistency thay vì tự ý rewrite.
- **Yêu cầu mâu thuẫn Usability/A11y**: Chỉ rõ điểm nghẽn, đưa ra ít nhất 2 giải pháp cân bằng và đợi user chọn.

---
*Tham khảo chi tiết kỹ thuật:*
- [Design Tokens & Variables](file:///c:/dev/Mousehotkey/.agents/skills/ui-product-designer/references/design-tokens.md)
- [Component Rules & Code Examples](file:///c:/dev/Mousehotkey/.agents/skills/ui-product-designer/references/component-rules.md)
- [Screen Patterns & Layout Guide](file:///c:/dev/Mousehotkey/.agents/skills/ui-product-designer/references/screen-patterns.md)
- [UI Review & Audit Checklist](file:///c:/dev/Mousehotkey/.agents/skills/ui-product-designer/references/ui-review-checklist.md)
