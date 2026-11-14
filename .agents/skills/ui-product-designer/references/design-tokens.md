# Design Tokens & Theme Standards

Tài liệu quy định hệ thống tokens dùng chung cho toàn bộ dự án React/Next.js sử dụng Tailwind CSS và shadcn/ui. Mọi component đều phải tuân thủ nghiêm ngặt các quy tắc này.

---

## 1. Semantic Color Tokens

Tuyệt đối **không** sử dụng mã màu trực tiếp (hex `#...`, `rgb()`, `hsl(...)`) trong code JSX/TSX. Sử dụng 100% token ngữ nghĩa do shadcn định nghĩa:

| Token Class | Ý nghĩa / Ngữ cảnh sử dụng | Ví dụ sử dụng |
| :--- | :--- | :--- |
| `bg-background`, `text-foreground` | Nền chính của toàn trang và màu chữ mặc định | `min-h-screen bg-background text-foreground` |
| `bg-card`, `text-card-foreground` | Nền khối thông tin nổi (thẻ, panel, widget) | `rounded-lg border bg-card p-6 text-card-foreground` |
| `bg-popover`, `text-popover-foreground` | Nền cho dropdown menu, tooltip, popover | `z-50 bg-popover text-popover-foreground shadow-md` |
| `bg-primary`, `text-primary-foreground` | Nhận diện thương hiệu & primary action duy nhất | `<Button className="bg-primary text-primary-foreground">` |
| `bg-secondary`, `text-secondary-foreground` | Nền các phần tử phụ trợ, badge nhẹ | `rounded-md bg-secondary text-secondary-foreground` |
| `bg-muted`, `text-muted-foreground` | Nền thứ cấp, nhãn metadata, helper text | `<p className="text-sm text-muted-foreground">` |
| `bg-accent`, `text-accent-foreground` | Trạng thái hover/active của menu, item list | `hover:bg-accent hover:text-accent-foreground` |
| `bg-destructive`, `text-destructive-foreground` | Thao tác hủy, lỗi hệ thống, xóa dữ liệu | `bg-destructive text-destructive-foreground` |
| `border-border` | Đường kẻ phân tách (1px) | `border-b border-border` |
| `border-input` | Viền của form input, select, textarea | `border border-input` |
| `ring-ring` | Viền sáng khi bàn phím focus (`focus-visible`) | `focus-visible:ring-2 focus-visible:ring-ring` |

---

## 2. Light & Dark Mode Configuration

Định cấu hình qua CSS Variables trong `globals.css` để giao diện tự thích ứng mà không cần viết các class `dark:...` cục bộ cho từng element.

### Ví dụ chuẩn cấu hình `globals.css`:
```css
@layer base {
  :root {
    --background: 0 0% 100%;
    --foreground: 222.2 84% 4.9%;

    --card: 0 0% 100%;
    --card-foreground: 222.2 84% 4.9%;

    --popover: 0 0% 100%;
    --popover-foreground: 222.2 84% 4.9%;

    --primary: 222.2 47.4% 11.2%;
    --primary-foreground: 210 40% 98%;

    --secondary: 210 40% 96.1%;
    --secondary-foreground: 222.2 47.4% 11.2%;

    --muted: 210 40% 96.1%;
    --muted-foreground: 215.4 16.3% 46.9%;

    --accent: 210 40% 96.1%;
    --accent-foreground: 222.2 47.4% 11.2%;

    --destructive: 0 84.2% 60.2%;
    --destructive-foreground: 210 40% 98%;

    --border: 214.3 31.8% 91.4%;
    --input: 214.3 31.8% 91.4%;
    --ring: 222.2 84% 4.9%;

    --radius: 0.5rem;
  }

  .dark {
    --background: 224 71.4% 4.1%;
    --foreground: 210 20% 98%;

    --card: 224 71.4% 4.1%;
    --card-foreground: 210 20% 98%;

    --popover: 224 71.4% 4.1%;
    --popover-foreground: 210 20% 98%;

    --primary: 210 20% 98%;
    --primary-foreground: 222.2 47.4% 11.2%;

    --secondary: 217.2 32.6% 17.5%;
    --secondary-foreground: 210 20% 98%;

    --muted: 217.2 32.6% 17.5%;
    --muted-foreground: 215 20.2% 65.1%;

    --accent: 217.2 32.6% 17.5%;
    --accent-foreground: 210 20% 98%;

    --destructive: 0 62.8% 30.6%;
    --destructive-foreground: 210 20% 98%;

    --border: 217.2 32.6% 17.5%;
    --input: 217.2 32.6% 17.5%;
    --ring: 212.8 100% 47%;
  }
}
```

### So sánh cách viết đúng vs sai:
```tsx
// ❌ SAI: Hardcode màu hex, lạm dụng dark:bg-black, gradient trang trí
<div className="bg-[#ffffff] dark:bg-[#121212] p-4 text-[#333333] dark:text-[#f0f0f0] border border-gray-200">
  <button className="bg-gradient-to-r from-blue-500 to-indigo-600 text-white shadow-lg">
    Submit
  </button>
</div>

// ✅ ĐÚNG: Dùng 100% semantic tokens tự tương thích light/dark mode
<div className="rounded-lg border border-border bg-card p-4 text-card-foreground">
  <Button variant="default">
    Submit
  </Button>
</div>
```

---

## 3. Spacing Scale (4px System)

Chỉ sử dụng spacing scale 4px chuẩn của Tailwind. Tuyệt đối cấm các giá trị tùy tiện (arbitrary values) như `p-[17px]`, `gap-[13px]`, `mt-[23px]`.

| Tailwind Class | Pixel tương ứng | Ngữ cảnh sử dụng |
| :--- | :--- | :--- |
| `p-0.5` / `gap-0.5` | 2px | Khoảng cách siêu nhỏ giữa icon và badge, viền kép |
| `p-1` / `gap-1` | 4px | Khoảng cách icon nhỏ, tag inline, padding button siêu gọn |
| `p-2` / `gap-2` | 8px | Khoảng cách giữa các form controls liên quan, padding dropdown item |
| `p-3` / `gap-3` | 12px | Padding của input field, button kích thước chuẩn |
| `p-4` / `gap-4` | 16px | Padding card cơ bản trên mobile, khoảng cách giữa các trường trong form |
| `p-6` / `gap-6` | 24px | Padding card desktop, grid gap giữa các cụm tính năng |
| `p-8` / `gap-8` | 32px | Khoảng cách giữa các section trong một trang |
| `p-12` / `gap-12` | 48px | Padding hero section, khoảng cách lớn giữa các nhóm nội dung chính |
| `p-16` / `gap-16` | 64px | Khoảng cách margin top/bottom cho page layout |

---

## 4. Border Radius Tokens

Hệ thống bo góc phải đồng nhất, tránh tình trạng nút bấm bo tròn hoàn toàn (`rounded-full`) trong khi card lại vuông vức (`rounded-none`).

- `rounded-sm`: (2px) Dành cho badge siêu nhỏ, checkbox, slider thumb.
- `rounded-md`: (6px) Dành cho form input, button kích thước vừa, dropdown menu.
- `rounded-lg`: (8px - `--radius`) Dành cho container card, dialog modal, panel nội dung.
- `rounded-full`: Chỉ dùng cho avatar tròn hoặc status indicator badge hình tròn.

---

## 5. Typography Scale & Hierarchy

Mỗi màn hình không được có quá 4 cấp độ font.

```tsx
// Level 1: Page Title (Tối đa 1 cái trên một trang)
<h1 className="text-2xl font-semibold tracking-tight text-foreground md:text-3xl">
  Project Settings
</h1>

// Level 2: Section Header / Card Title
<h2 className="text-lg font-medium text-foreground">
  API Authentication
</h2>

// Level 3: Body Text
<p className="text-sm font-normal leading-relaxed text-foreground">
  Use this API key to authenticate requests from your backend server.
</p>

// Level 4: Meta, Helper, Caption
<span className="text-xs text-muted-foreground">
  Created on Oct 14, 2026 • Never expires
</span>
```

---

## 6. Contrast & Accessibility Rules (WCAG AA)

1. **Text contrast**:
   - Chữ thông thường (`< 18pt` hoặc `< 14pt bold`): Tỷ lệ tương phản tối thiểu **4.5:1** so với nền.
   - Chữ lớn (`>= 18pt` hoặc `>= 14pt bold`): Tỷ lệ tương phản tối thiểu **3:1**.
   - UI components & borders: Tối thiểu **3:1** so với màu nền xung quanh.
2. **Focus Visible**:
   - Mọi phần tử tương tác (button, link, input) phải có viền focus rõ ràng khi tab bằng bàn phím:
   ```tsx
   className="focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 focus-visible:ring-offset-background"
   ```
3. **Touch Targets**:
   - Trên mobile/tablet, vùng chạm tối thiểu là **44 x 44px**. Nếu icon chỉ có 16x16px, bọc trong button có padding để đảm bảo diện tích:
   ```tsx
   <Button variant="ghost" size="icon" className="h-11 w-11">
     <MoreHorizontal className="h-4 w-4" />
     <span className="sr-only">Open options</span>
   </Button>
   ```
