# Screen Patterns & Anti-AI UI Guide

Tài liệu hướng dẫn mẫu bố cục màn hình (screen patterns), quy tắc thiết kế responsive mobile-first và so sánh trực quan giữa phong cách AI generic template và UI sản phẩm chuyên nghiệp.

---

## 1. Mobile-First Responsive Layouts

Mọi layout đều phải bắt đầu từ màn hình nhỏ nhất (375px), sau đó mở rộng có chủ đích sang tablet (768px) và desktop (1024px / 1280px).

### Pattern: Dashboard Shell với Collapsible Sidebar & Header
```tsx
import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Sheet, SheetContent, SheetTrigger } from "@/components/ui/sheet";
import { Menu, Home, Settings, Users, Bell } from "lucide-react";

export function DashboardLayout({ children }: { children: React.ReactNode }) {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <div className="flex min-h-screen flex-col bg-background text-foreground md:flex-row">
      {/* Mobile Topbar */}
      <header className="flex h-14 items-center justify-between border-b border-border px-4 md:hidden">
        <Sheet open={isOpen} onOpenChange={setIsOpen}>
          <SheetTrigger asChild>
            <Button variant="ghost" size="icon" className="h-10 w-10">
              <Menu className="h-5 w-5" />
              <span className="sr-only">Toggle menu</span>
            </Button>
          </SheetTrigger>
          <SheetContent side="left" className="w-64 p-0">
            <nav className="flex flex-col gap-1 p-4">
              <span className="px-2 py-1 text-sm font-semibold tracking-tight">App Brand</span>
              <a href="#" className="flex items-center gap-3 rounded-md px-3 py-2 text-sm font-medium hover:bg-accent">
                <Home className="h-4 w-4" /> Overview
              </a>
              <a href="#" className="flex items-center gap-3 rounded-md px-3 py-2 text-sm font-medium hover:bg-accent">
                <Users className="h-4 w-4" /> Team
              </a>
              <a href="#" className="flex items-center gap-3 rounded-md px-3 py-2 text-sm font-medium hover:bg-accent">
                <Settings className="h-4 w-4" /> Settings
              </a>
            </nav>
          </SheetContent>
        </Sheet>
        <span className="font-semibold">Dashboard</span>
        <Button variant="ghost" size="icon" className="h-10 w-10">
          <Bell className="h-4 w-4" />
        </Button>
      </header>

      {/* Desktop Persistent Sidebar */}
      <aside className="hidden w-64 flex-col border-r border-border bg-card p-4 md:flex">
        <div className="mb-6 px-2 text-base font-semibold tracking-tight">App Brand</div>
        <nav className="flex flex-col gap-1">
          <a href="#" className="flex items-center gap-3 rounded-md bg-accent px-3 py-2 text-sm font-medium text-accent-foreground">
            <Home className="h-4 w-4" /> Overview
          </a>
          <a href="#" className="flex items-center gap-3 rounded-md px-3 py-2 text-sm font-medium text-muted-foreground hover:bg-accent hover:text-accent-foreground">
            <Users className="h-4 w-4" /> Team
          </a>
          <a href="#" className="flex items-center gap-3 rounded-md px-3 py-2 text-sm font-medium text-muted-foreground hover:bg-accent hover:text-accent-foreground">
            <Settings className="h-4 w-4" /> Settings
          </a>
        </nav>
      </aside>

      {/* Main Content Area */}
      <main className="flex-1 p-4 md:p-8">
        <div className="mx-auto max-w-6xl">{children}</div>
      </main>
    </div>
  );
}
```

---

## 2. Empty States: Good vs Bad

Một empty state chất lượng cao phải gồm:
1. Icon trung tính, tinh tế (không dùng emoji hay hình 3D sặc sỡ).
2. Tiêu đề rõ ràng nêu trạng thái.
3. Đúng **một câu** giải thích lý do hoặc giá trị mang lại.
4. Đúng **một action liên quan** để bắt đầu.

### So sánh:
```tsx
// ❌ BAD: Trống trải, vô cảm, cụt lủn, không có định hướng tiếp theo
<div className="p-8 text-center">
  <div className="text-4xl">📭</div>
  <p className="text-gray-400">No data found</p>
</div>

// ✅ GOOD: Rõ ràng, có ngữ cảnh và primary action kích hoạt
<div className="flex min-h-[320px] flex-col items-center justify-center rounded-lg border border-dashed border-border p-8 text-center">
  <div className="flex h-12 w-12 items-center justify-center rounded-full bg-muted">
    <FolderPlus className="h-6 w-6 text-muted-foreground" />
  </div>
  <h3 className="mt-4 text-base font-semibold text-foreground">No repositories connected</h3>
  <p className="mt-1 text-sm text-muted-foreground max-w-sm">
    Connect your GitHub repository to enable automatic deployment and continuous delivery.
  </p>
  <div className="mt-6">
    <Button variant="default" size="sm">
      <Github className="mr-2 h-4 w-4" />
      Connect Repository
    </Button>
  </div>
</div>
```

---

## 3. Loading States: Skeleton vs Spinner

Nguyên tắc:
- **Skeleton** phải mô phỏng chính xác khung xương (shape) của dữ liệu sẽ xuất hiện (chiều cao, độ rộng, vị trí).
- **Không bao giờ trộn lẫn** spinner và skeleton trong cùng một khu vực hiển thị.

```tsx
// ✅ Chuẩn Skeleton cho danh sách thẻ sản phẩm
export function ProductListSkeleton() {
  return (
    <div className="space-y-3">
      {Array.from({ length: 3 }).map((_, i) => (
        <div key={i} className="flex items-center justify-between rounded-lg border border-border p-4">
          <div className="space-y-2">
            <Skeleton className="h-4 w-40" />
            <Skeleton className="h-3 w-64" />
          </div>
          <Skeleton className="h-8 w-20 rounded-md" />
        </div>
      ))}
    </div>
  );
}
```

---

## 4. Anti-Patterns & Professional Solutions

### Anti-Pattern 1: Equal-width 3-Card Grid vô vị vs Hierarchy-Driven Layout
```tsx
// ❌ AI Generic: 3 card giống hệt nhau, không có điểm nhấn trọng tâm
<div className="grid grid-cols-1 md:grid-cols-3 gap-6">
  <div className="rounded-xl p-6 bg-white shadow-lg border border-purple-100">
    <h3>Feature 1</h3><p>Desc 1</p>
  </div>
  <div className="rounded-xl p-6 bg-white shadow-lg border border-purple-100">
    <h3>Feature 2</h3><p>Desc 2</p>
  </div>
  <div className="rounded-xl p-6 bg-white shadow-lg border border-purple-100">
    <h3>Feature 3</h3><p>Desc 3</p>
  </div>
</div>

// ✅ Professional: Phân tầng thông tin rõ ràng - Highlight khối trọng yếu (2/3 + 1/3)
<div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
  {/* Khối chính chiếm 2 cột */}
  <div className="rounded-lg border border-border bg-card p-6 lg:col-span-2">
    <div className="flex items-center justify-between">
      <h3 className="text-base font-semibold text-foreground">Traffic Analytics</h3>
      <span className="text-xs text-muted-foreground">Past 30 days</span>
    </div>
    <div className="mt-4 h-64 rounded bg-muted/30" />
  </div>

  {/* Khối tóm tắt chiếm 1 cột */}
  <div className="flex flex-col justify-between rounded-lg border border-border bg-card p-6">
    <div>
      <h3 className="text-base font-semibold text-foreground">Quick Actions</h3>
      <p className="mt-1 text-sm text-muted-foreground">Manage your quota and alerts.</p>
    </div>
    <Button variant="default" className="w-full mt-6">Upgrade Plan</Button>
  </div>
</div>
```

### Anti-Pattern 2: Nút Gradient lòe loẹt vs Nút Semantic
```tsx
// ❌ AI Generic: Gradient tím xanh, hiệu ứng phát sáng neon
<button className="bg-gradient-to-r from-purple-500 via-pink-500 to-blue-500 hover:shadow-cyan-500/50 text-white font-bold py-3 px-6 rounded-full shadow-2xl animate-pulse">
  ✨ Get Started Free ✨
</button>

// ✅ Professional: Trực diện, tin cậy, rõ nét
<Button variant="default" size="default">
  Get started
  <ArrowRight className="ml-2 h-4 w-4" />
</Button>
```

### Anti-Pattern 3: Lạm dụng Card lồng Card (Nested Cards)
```tsx
// ❌ AI Generic: Card lồng trong Card tạo viền và bóng tầng tầng lớp lớp
<div className="bg-card p-6 border rounded-xl shadow-sm">
  <h2 className="text-lg">Section</h2>
  <div className="bg-muted p-4 border rounded-lg mt-4 shadow-inner">
    <div className="bg-background p-3 border rounded shadow-sm">
      <p>Over-encapsulated content</p>
    </div>
  </div>
</div>

// ✅ Professional: Phẳng hóa cấu trúc, dùng divider 1px hoặc khoảng trắng để phân cách
<div className="rounded-lg border border-border bg-card">
  <div className="p-6 border-b border-border">
    <h2 className="text-base font-semibold text-foreground">Security Settings</h2>
    <p className="text-sm text-muted-foreground">Manage password and two-factor authentication.</p>
  </div>
  <div className="divide-y divide-border">
    <div className="flex items-center justify-between p-6">
      <div>
        <p className="text-sm font-medium text-foreground">Two-factor Authentication</p>
        <p className="text-xs text-muted-foreground">Add an extra layer of security to your account.</p>
      </div>
      <Button variant="outline" size="sm">Enable</Button>
    </div>
  </div>
</div>
```

### Anti-Pattern 4: Text xám nhạt khó đọc vs WCAG AA Compliant
```tsx
// ❌ AI Generic: Chữ xám nhợt nhạt mất nét
<p className="text-gray-300 dark:text-gray-600 text-xs font-light">
  Last synced 2 hours ago
</p>

// ✅ Professional: Token ngữ nghĩa đảm bảo tương phản tối thiểu 4.5:1
<p className="text-xs text-muted-foreground font-normal">
  Last synced 2 hours ago
</p>
```
