# ADR-012: Sequence Item Type Architecture and Multi-Step Execution

## Status
Accepted

## Context
RightWheel (Mousehotkey) hiện tại chỉ cung cấp các mục thao tác đơn lẻ (`ShortcutItem`, `AppItem`, `UrlItem`, `CommandItem`). Người dùng có nhu cầu kích hoạt các chuỗi hành động phối hợp liên hoàn (ví dụ: `Ctrl+C` copy dữ liệu, delay 150ms để clipboard cập nhật, sau đó mở URL tra cứu hoặc khởi động ứng dụng ghi chú).

Để đáp ứng PRD F-014 (US-039..043), hệ thống cần một loại item mới `SequenceItem` quản lý danh sách các bước có thứ tự (`steps`), cho phép cấu hình thời gian trễ giữa các bước và cung cấp giao diện biên tập trực quan mà vẫn tuân thủ nghiêm ngặt:
1. Tính tương thích ngược 100% với cấu trúc cấu hình JSON hiện hữu (`config.json`).
2. Quy tắc giới hạn kích thước tệp tin SYSTEM LOCK (≤ 250 dòng/file).
3. Kiến trúc phân tầng rõ ràng giữa UI biên tập, Data Model và Execution Engine.

---

## Decisions

### 1. Cấu trúc Dữ liệu `steps`: Dùng `list[dict]` Thô trong `SequenceItem`
- **Quyết định**:
  - `SequenceItem` được định nghĩa trong `src/features/shortcut_panel/types/panel_types.py`:
    ```python
    @dataclass
    class SequenceItem:
        label: str
        steps: list[dict] = field(default_factory=list)
        type:  str = "sequence"
    ```
  - Mỗi phần tử trong `steps` là một dictionary thô chứa `type` (`"shortcut"` | `"app"` | `"url"` | `"command"`), các thuộc tính tương ứng với loại đó (`keys` / `path` + `args` / `url` / `cmd` + `cwd`), và `delay_ms: int`.
- **Lý do & So sánh**:
  - *Phương án A (Dùng dataclass `SequenceStep` riêng)*: Tạo thêm nhiều class con hoặc polymorphic schema. Tuy type-safe hơn nhưng gây cồng kềnh, phức tạp hóa việc serialize/deserialize JSON hai chiều và làm tăng số dòng code trong `panel_types.py`.
  - *Phương án B (Dùng `list[dict]` thô - Được chọn)*: Nhất quán hoàn toàn với pattern `FolderItem.children` hiện có. Cấu hình JSON nạp và lưu trực tiếp qua `config_service.py` mà không cần chuyển đổi trung gian. Tầng UI và Executor truy cập dictionary theo key rõ ràng.

### 2. Thiết kế `SequenceEditorDialog` Tự Chủ (Standalone Step CRUD)
- **Quyết định**:
  - Tạo hộp thoại modal mới `SequenceEditorDialog` (`src/features/shortcut_panel/ui/sequence_editor_dialog.py`) kế thừa `tk.Toplevel` và gọi `grab_set()`.
  - `SequenceEditorDialog` tự chứa 4 phương thức thêm bước riêng biệt (`_step_add_shortcut`, `_step_add_app`, `_step_add_url`, `_step_add_command`), không phụ thuộc hay kế thừa `DefaultTabCRUDMixin`.
- **Lý do & Trade-off**:
  - `DefaultTabCRUDMixin` thao tác trực tiếp với persistent storage (`config_service.load()`, cập nhật mảng gốc, `config_service.save()`). Nếu cố tái sử dụng sẽ gây side-effect ngoài ý muốn lên cấu hình khi người dùng chưa nhấn "Lưu" trong dialog.
  - `SequenceEditorDialog` thao tác trên một danh sách tạm thời (`in-memory list[dict]`). Việc tách biệt giúp dialog hoạt động như một pure editor component: nhận `init_steps`, chỉnh sửa cục bộ, và chỉ trả về kết quả khi người dùng nhấn "Lưu" (hoặc `None` nếu "Hủy").
  - Tái sử dụng các UI primitive độc lập đã kiểm chứng: `KeyRecorderDialog` (bắt phím tắt), `filedialog.askopenfilename` (chọn file exe), và `_AskDialog` (nhập text URL/Command).

### 3. Khả năng Phục hồi Lỗi Thực thi trong `execute_sequence()`
- **Quyết định**:
  - Trong `src/features/shortcut_panel/services/shortcut_executor.py`, hàm `execute_sequence(steps: list[dict]) -> None` bọc khối `try...except Exception as exc:` độc lập quanh **từng bước đơn lẻ**.
  - Nếu một bước gặp lỗi (ví dụ file app bị xóa, URL không hợp lệ, script command trả về lỗi):
    - Ghi log warning: `_log.warning(f"execute_sequence() step {idx} ({step_type}) failed: {exc}")`.
    - **Không dừng chuỗi**: Hệ thống vẫn ngủ đúng `delay_ms` (nếu không phải bước cuối) và tiếp tục thực thi bước tiếp theo.
- **Lý do**:
  - Ngăn ngừa hiện tượng một lỗi cục bộ ở bước trung gian làm gián đoạn toàn bộ luồng tự động hóa của người dùng (ví dụ: copy clipboard vẫn cần hoàn tất kể cả khi app phụ khởi động chậm).

### 4. Chuẩn hóa và Kiểm định `delay_ms` (Robust Input Fallback)
- **Quyết định**:
  - Sau khi thêm hoặc sửa một bước, hộp thoại yêu cầu nhập thời gian chờ kế tiếp qua `_AskDialog.ask("Delay (ms)", init=str(current_delay))`.
  - Giá trị nhập vào được parse và validate:
    ```python
    try:
        delay = int(val_str.strip())
        delay = delay if delay >= 0 else 100
    except (ValueError, TypeError, AttributeError):
        delay = 100  # Fallback mặc định an toàn
    ```
  - Áp dụng cơ chế fallback im lặng về `100ms` nếu người dùng nhập sai định dạng hoặc số âm, tránh hiển thị error popup gây ngắt quãng trải nghiệm nhập liệu.

### 5. Định dạng Trực quan Hàng Danh sách trong Sequence Editor
- **Quyết định**:
  - Danh sách `Listbox` trong `SequenceEditorDialog` hiển thị từng bước theo định dạng chuẩn hóa, đồng bộ với nhãn `_TYPE_LABEL`:
    - `[1] Keys: {keys}  ({delay_ms}ms)`
    - `[2] App: {os.path.basename(path)}  ({delay_ms}ms)`
    - `[3] Web: {url}  ({delay_ms}ms)`
    - `[4] Script: {cmd}  ({delay_ms}ms)`
  - Định dạng hiển thị item Sequence tại `DefaultTab`: `⛓ {label}  ({n} steps)`.

---

## Consequences
- **Ưu điểm**:
  - Đáp ứng trọn vẹn nhu cầu tự động hóa chuỗi thao tác của người dùng mà không cần cài đặt thêm phần mềm macro bên thứ ba.
  - Tương thích ngược tuyệt đối: các mục cấu hình cũ không bị ảnh hưởng, không cần cơ chế migrate dữ liệu.
  - Kiến trúc phân tách rõ ràng, các file đều duy trì độ dài dưới 250 dòng (SYSTEM LOCK).
- **Hạn chế & Đánh đổi**:
  - `SequenceEditorDialog` có một số đoạn code gọi dialog con tương tự `default_tab_crud.py`, nhưng đánh đổi này là cần thiết để bảo vệ tính toàn vẹn của cấu hình và giữ code đơn giản, dễ bảo trì.
=== HẾT DRAFT ===
EVIDENCE:
- C:\dev\Mousehotkey\src\features\shortcut_panel\types\panel_types.py#L30-L75 (Pattern FolderItem.children dùng list[dict] thô)
- C:\dev\Mousehotkey\src\features\shortcut_panel\services\shortcut_executor.py#L140-L195 (Mẫu execute đơn lẻ và log exception)
- C:\dev\Mousehotkey\src\features\shortcut_panel\ui\default_tab_crud.py#L1-L194 (DefaultTabCRUDMixin trực tiếp ghi config_service)
OPEN_QUESTIONS: không có
SUMMARY: Đã hoàn thành phân tích kiến trúc và soạn thảo ADR-012 cho tính năng Sequence Item Type (F-014). Chốt 5 quyết định kiến trúc then chốt: (1) steps dùng list[dict] thô, (2) SequenceEditorDialog độc lập với in-memory state, (3) execute_sequence bắt lỗi từng bước và tiếp tục chuỗi, (4) delay_ms validate an toàn fallback 100ms, (5) format hiển thị listbox đồng bộ badge. Tuân thủ 100% SYSTEM LOCK <= 250 dòng.