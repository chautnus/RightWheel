# Component Rules & Implementation Guide

Quy chuẩn triển khai các component cốt lõi trong hệ sinh thái React + Tailwind CSS + shadcn/ui. Đảm bảo tính nhất quán, khả năng truy cập (a11y) và trải nghiệm tương tác tự nhiên.

---

## 1. Button Usage & Action Hierarchy

Mỗi màn hình chỉ có **một** primary action duy nhất. Các hành động khác phải dùng variant phù hợp để không phân tán sự chú ý của người dùng.

| Variant | Mục đích sử dụng | Vị trí khuyến nghị |
| :--- | :--- | :--- |
| `default` | Primary Action: Lưu thay đổi, Tạo mới, Tiếp tục | Góc phải trên của trang, hoặc cuối form |
| `secondary` / `outline` | Secondary Action: Hủy, Quay lại, Xuất dữ liệu | Đứng cạnh Primary Button |
| `ghost` | Tertiary Action: Nút menu 3 chấm, action icon trong table | Bảng dữ liệu, header card, icon phụ |
| `destructive` | Hành động nguy hiểm: Xóa tài khoản, Hủy dự án | Phải đi kèm Confirmation Dialog |

### Ví dụ chuẩn Button Group:
```tsx
import { Button } from "@/components/ui/button";
import { Loader2, Plus, Trash2 } from "lucide-react";

export function ActionToolbar({ isSubmitting = false }: { isSubmitting?: boolean }) {
  return (
    <div className="flex items-center gap-2">
      {/* Secondary Action */}
      <Button variant="outline" size="sm" disabled={isSubmitting}>
        Cancel
      </Button>

      {/* Primary Action duy nhất */}
      <Button variant="default" size="sm" disabled={isSubmitting}>
        {isSubmitting ? (
          <>
            <Loader2 className="mr-2 h-4 w-4 animate-spin motion-reduce:hidden" />
            Saving...
          </>
        ) : (
          <>
            <Plus className="mr-2 h-4 w-4" />
            Create Project
          </>
        )}
      </Button>

      {/* Destructive Action tách biệt */}
      <Button variant="ghost" size="icon" className="text-destructive hover:bg-destructive/10">
        <Trash2 className="h-4 w-4" />
        <span className="sr-only">Delete item</span>
      </Button>
    </div>
  );
}
```

---

## 2. Form Implementation Standard

Mọi form phải đáp ứng đủ 5 yếu tố:
1. **Label hiển thị rõ ràng** (không dùng placeholder thay thế cho label).
2. **Helper text** khi cần giải thích định dạng hoặc điều kiện.
3. **Validation error cụ thể** ngay dưới input vi phạm.
4. **Trạng thái disabled & loading** khi đang submit dữ liệu.
5. **Nút Submit & Cancel rõ ràng**, phân biệt cấp độ bằng variant.

### Ví dụ chuẩn Form Field với react-hook-form / shadcn:
```tsx
import { Label } from "@/components/ui/label";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Loader2 } from "lucide-react";

interface FormFieldProps {
  id: string;
  label: string;
  helperText?: string;
  error?: string;
  isLoading?: boolean;
}

export function ProjectNameForm({ id, label, helperText, error, isLoading }: FormFieldProps) {
  return (
    <form className="space-y-4 max-w-md">
      <div className="space-y-1.5">
        <Label htmlFor={id} className="text-sm font-medium text-foreground">
          {label} <span className="text-destructive">*</span>
        </Label>
        
        <Input
          id={id}
          disabled={isLoading}
          aria-invalid={!!error}
          aria-describedby={error ? `${id}-error` : helperText ? `${id}-desc` : undefined}
          className="border-input bg-background"
        />

        {helperText && !error && (
          <p id={`${id}-desc`} className="text-xs text-muted-foreground">
            {helperText}
          </p>
        )}

        {error && (
          <p id={`${id}-error`} className="text-xs font-medium text-destructive">
            {error}
          </p>
        )}
      </div>

      <div className="flex items-center justify-end gap-3 pt-2">
        <Button type="button" variant="outline" disabled={isLoading}>
          Cancel
        </Button>
        <Button type="submit" variant="default" disabled={isLoading}>
          {isLoading && <Loader2 className="mr-2 h-4 w-4 animate-spin motion-reduce:hidden" />}
          Save Changes
        </Button>
      </div>
    </form>
  );
}
```

---

## 3. Data Table Standards

Data table là trung tâm của các màn hình quản trị. Bắt buộc xử lý trọn vẹn 6 trạng thái:
- **Sticky header** khi cuộn danh sách dài.
- **Row actions** dùng variant `ghost` gọn gàng.
- **Loading state**: Hiển thị Skeleton rows mô phỏng cấu trúc bảng (không dùng spinner chung chung).
- **Empty state**: Thông báo rõ ràng chưa có dữ liệu và action khởi tạo.
- **No-results state**: Khi bộ lọc hoặc tìm kiếm không trả về kết quả kèm nút Clear Filter.
- **Error state**: Báo lỗi tải dữ liệu kèm nút Retry.

### Ví dụ Data Table chuẩn:
```tsx
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { MoreHorizontal, ArrowUpDown, AlertCircle, Inbox } from "lucide-react";

interface Item {
  id: string;
  name: string;
  status: "active" | "inactive";
  updatedAt: string;
}

interface TableProps {
  data: Item[];
  isLoading: boolean;
  isError: boolean;
  onRetry: () => void;
  onResetFilter: () => void;
  isFiltered: boolean;
}

export function DataTable({ data, isLoading, isError, onRetry, onResetFilter, isFiltered }: TableProps) {
  return (
    <div className="rounded-md border border-border bg-card">
      <Table>
        <TableHeader className="sticky top-0 bg-muted/50">
          <TableRow>
            <TableHead className="w-[300px]">
              <Button variant="ghost" size="sm" className="-ml-3 h-8 text-xs font-medium">
                Name <ArrowUpDown className="ml-2 h-3.5 w-3.5" />
              </Button>
            </TableHead>
            <TableHead>Status</TableHead>
            <TableHead>Updated</TableHead>
            <TableHead className="w-[60px] text-right">Actions</TableHead>
          </TableRow>
        </TableHeader>

        <TableBody>
          {/* 1. Loading State */}
          {isLoading &&
            Array.from({ length: 4 }).map((_, i) => (
              <TableRow key={i}>
                <TableCell><Skeleton className="h-4 w-48" /></TableCell>
                <TableCell><Skeleton className="h-4 w-16" /></TableCell>
                <TableCell><Skeleton className="h-4 w-24" /></TableCell>
                <TableCell className="text-right"><Skeleton className="h-8 w-8 ml-auto" /></TableCell>
              </TableRow>
            ))}

          {/* 2. Error State */}
          {!isLoading && isError && (
            <TableRow>
              <TableCell colSpan={4} className="h-32 text-center">
                <div className="flex flex-col items-center justify-center gap-2 text-destructive">
                  <AlertCircle className="h-5 w-5" />
                  <p className="text-sm font-medium">Failed to load data.</p>
                  <Button variant="outline" size="sm" onClick={onRetry}>
                    Try again
                  </Button>
                </div>
              </TableCell>
            </TableRow>
          )}

          {/* 3. Empty State / No Results State */}
          {!isLoading && !isError && data.length === 0 && (
            <TableRow>
              <TableCell colSpan={4} className="h-40 text-center">
                <div className="flex flex-col items-center justify-center gap-2">
                  <Inbox className="h-8 w-8 text-muted-foreground" />
                  <p className="text-sm font-medium text-foreground">
                    {isFiltered ? "No matching records found" : "No items created yet"}
                  </p>
                  <p className="text-xs text-muted-foreground max-w-xs">
                    {isFiltered
                      ? "Try adjusting your search criteria or resetting filters."
                      : "Get started by creating your first project."}
                  </p>
                  {isFiltered ? (
                    <Button variant="outline" size="sm" onClick={onResetFilter}>
                      Clear filters
                    </Button>
                  ) : (
                    <Button variant="default" size="sm">
                      Create Project
                    </Button>
                  )}
                </div>
              </TableCell>
            </TableRow>
          )}

          {/* 4. Normal Data Rows */}
          {!isLoading &&
            !isError &&
            data.map((item) => (
              <TableRow key={item.id} className="hover:bg-muted/50">
                <TableCell className="font-medium text-foreground">{item.name}</TableCell>
                <TableCell>
                  <span className="inline-flex items-center rounded-full px-2 py-0.5 text-xs font-medium bg-secondary text-secondary-foreground">
                    {item.status}
                  </span>
                </TableCell>
                <TableCell className="text-sm text-muted-foreground">{item.updatedAt}</TableCell>
                <TableCell className="text-right">
                  <Button variant="ghost" size="icon" className="h-8 w-8">
                    <MoreHorizontal className="h-4 w-4" />
                    <span className="sr-only">Row actions</span>
                  </Button>
                </TableCell>
              </TableRow>
            ))}
        </TableBody>
      </Table>
    </div>
  );
}
```

---

## 4. Feedback System (Toast vs Inline vs Modal)

Áp dụng đúng phương thức phản hồi theo mức độ nghiêm trọng và ngữ cảnh:

```
+-------------------+----------------------------+-------------------------------------+
| Mức độ            | Cơ chế khuyến nghị         | Ví dụ                               |
+-------------------+----------------------------+-------------------------------------+
| Non-blocking      | Toast (Sonner / shadcn)    | "File uploaded successfully"        |
| Inline Context    | Error message dưới Input   | "Email is already registered"       |
| Destructive/Focus | Modal / Dialog / Sheet     | "Delete database 'prod-db'?"        |
+-------------------+----------------------------+-------------------------------------+
```

- **Toast**: Thông báo kết quả thao tác bất đồng bộ mà người dùng không cần hành động ngay lập tức.
- **Inline message**: Phản hồi trực tiếp tại trường dữ liệu, giúp người dùng định vị ngay vị trí cần sửa.
- **Modal / Alert Dialog**: Buộc người dùng tập trung giải quyết một thao tác quan trọng hoặc có tính rủi ro cao trước khi quay lại giao diện chính.
