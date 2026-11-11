---
id: prd_f014-sequence-item-type_20261111
title: "Sequence Item Type — Chuỗi Nhiều Bước Nối Tiếp (F-014)"
status: draft
version: 1.0
author: chautnus
created: 2026-11-11
updated: 2026-11-11
tags: [shortcut-panel, sequence-item, multi-step, automation, ui]
summary: "Thêm loại item mới 'Sequence' cho phép một shortcut thực thi chuỗi nhiều hành động nối tiếp nhau (shortcut, app, url, command) với khoảng delay cấu hình được giữa các bước."
---

# PRD: Sequence Item Type — Chuỗi Nhiều Bước Nối Tiếp (F-014)

## 1. Overview
**Problem**:
Hiện tại RightWheel (Mousehotkey) chỉ hỗ trợ các mục shortcut đơn lẻ (`ShortcutItem`, `AppItem`, `UrlItem`, `CommandItem`). Người dùng không thể thực hiện một luồng thao tác phức tạp gồm nhiều bước liên tiếp (ví dụ: gửi tổ hợp phím `Ctrl+C` để copy, sau đó mở URL hoặc app Claude/trình duyệt để xử lý nội dung vừa copy) trong một lần chọn duy nhất.

**Solution**:
Bổ sung loại item mới mang tên **Sequence** (`SequenceItem`). Một Sequence item chứa danh sách các bước có thứ tự (`steps`), trong đó mỗi bước thuộc 1 trong 4 loại hành động cơ bản (`shortcut`, `app`, `url`, `command`) kèm theo cấu hình thời gian chờ (`delay_ms`) sau mỗi bước trước khi chuyển sang bước tiếp theo. Cung cấp hộp thoại biên tập trực quan (`SequenceEditorDialog`) cho phép người dùng thêm, sửa, xóa và sắp xếp thứ tự các bước.

**Success Metrics**:
- Người dùng có thể tạo, chỉnh sửa và lưu trữ các item loại Sequence ngay trên tab Default của Settings.
- Hệ thống thực thi tuần tự 100% các bước theo đúng thứ tự và thời gian trễ đã định nghĩa.
- Không gây ảnh hưởng hay hồi quy (regression) đối với các loại item đơn lẻ hiện có.
- Giao diện và mã nguồn tuân thủ giới hạn SYSTEM LOCK (≤ 250 dòng/file).

## 2. Jobs To Be Done (JTBD)
> **When** đang làm việc và cần kích hoạt một chuỗi hành động lặp đi lặp lại (như copy dữ liệu rồi mở công cụ tra cứu hoặc chạy script chuẩn bị), **I want to** chỉ cần chọn một mục shortcut Sequence duy nhất trong Command Panel, **so I can** tự động hóa chuỗi thao tác mà không phải bấm nhiều phím tắt rời rạc hay chuyển đổi thủ công giữa các ứng dụng.

## 3. Stakeholders
| Role | Name/Team | Responsibility |
|------|-----------|----------------|
| Product Owner | chautnus | Phê duyệt PRD và trải nghiệm người dùng |
| Tech Lead | Claude / Antigravity | Thiết kế kiến trúc và data schema |
| Dev | Antigravity | Triển khai mã nguồn và kiểm thử |

## 4. User Stories & Acceptance Criteria

### US-039: Sequence Data Model & Serialization
**As a** nhà phát triển,  
**I want to** định nghĩa dataclass `SequenceItem` và cập nhật parser trong `config_service`,  
**So that** hệ thống có thể lưu trữ, nạp và biểu diễn các mục Sequence trong cấu trúc menu.

**Acceptance Criteria:**
- [ ] `src/features/shortcut_panel/types/panel_types.py` bổ sung dataclass `SequenceItem(label: str, steps: list[dict], type: str = "sequence")`.
- [ ] Union `MenuItem` được cập nhật bao gồm `SequenceItem`.
- [ ] Mỗi dictionary trong `steps` hỗ trợ field `type` ("shortcut" | "app" | "url" | "command") cùng các thuộc tính tương ứng và `delay_ms: int`.
- [ ] `src/features/shortcut_panel/services/config_service.py` parse đúng `SequenceItem` khi nạp từ config JSON.

### US-040: Tuần tự thực thi Sequence Steps trong Executor & Logic
**As a** người dùng RightWheel,  
**I want to** khi chọn một mục Sequence trên Panel, ứng dụng sẽ thực thi lần lượt từng bước với độ trễ tương ứng,  
**So that** các ứng dụng và hệ thống có đủ thời gian phản hồi giữa các thao tác nối tiếp.

**Acceptance Criteria:**
- [ ] `src/features/shortcut_panel/services/shortcut_executor.py` bổ sung hàm `execute_sequence(steps: list[dict]) -> None`.
- [ ] `execute_sequence` duyệt qua từng bước, điều phối gọi đúng hàm thực thi tương ứng: `execute()` cho shortcut, `execute_app()` cho app, `execute_url()` cho url, `execute_command()` cho command.
- [ ] Áp dụng `time.sleep(delay_ms / 1000)` sau mỗi bước (ngoại trừ bước cuối cùng). Nếu không chỉ định `delay_ms`, mặc định là 100ms.
- [ ] `src/features/shortcut_panel/logic/panel_logic.py` nhánh `select_current()` xử lý `isinstance(item, SequenceItem)` bằng cách phục hồi focus cửa sổ trước (`SetForegroundWindow`), ẩn panel (`hide()`), và kích hoạt `execute_sequence` qua `threading.Timer(0.25, ...)`.

### US-041: Hiển thị nhãn Badge và Item Renderer
**As a** người dùng RightWheel,  
**I want to** mục Sequence hiển thị huy hiệu và định dạng rõ ràng trên Shortcut Panel,  
**So that** tôi dễ dàng nhận biết đây là một chuỗi hành động tự động.

**Acceptance Criteria:**
- [ ] `src/features/shortcut_panel/ui/panel_item_renderer.py` bổ sung `"sequence": "Sequence"` vào bảng tra cứu `_TYPE_LABEL`.
- [ ] Panel hiển thị nhãn và huy hiệu đúng quy chuẩn dark mode, không chứa ký tự emoji lỗi.

### US-042: Hộp thoại Sequence Editor Dialog
**As a** người dùng RightWheel,  
**I want to** có một giao diện trực quan để soạn thảo danh sách các bước của Sequence,  
**So that** tôi có thể thêm, chỉnh sửa, xóa và đổi thứ tự các bước một cách thuận tiện.

**Acceptance Criteria:**
- [ ] Tạo file UI mới `src/features/shortcut_panel/ui/sequence_editor_dialog.py` kế thừa `tk.Toplevel`, áp dụng `grab_set()` (modal dialog).
- [ ] Hiển thị `Listbox` liệt kê các bước trong chuỗi kèm kiểu hành động và thời gian trễ.
- [ ] Cung cấp 4 nút thêm bước: `+ Shortcut`, `+ App`, `+ URL`, `+ Command`. Tái sử dụng `KeyRecorderDialog` cho phím tắt, `filedialog.askopenfilename` cho app, `_AskDialog` cho url và command.
- [ ] Sau khi nhập thông tin bước, yêu cầu nhập `delay_ms` (mặc định 100ms, validate số nguyên dương).
- [ ] Cung cấp các nút: `Sửa`, `Xóa`, `Lên`, `Xuống` để sắp xếp thứ tự bước.
- [ ] Nút `Lưu` trả về danh sách các bước đã định nghĩa; nút `Hủy` đóng hộp thoại mà không lưu thay đổi.

### US-043: Tích hợp Quản lý Sequence trên Default Tab Settings
**As a** người dùng RightWheel,  
**I want to** thêm và quản lý các mục Sequence trực tiếp trên tab Default trong cửa sổ Cài đặt,  
**So that** tôi có thể tổ chức và chỉnh sửa Sequence cùng các shortcut khác.

**Acceptance Criteria:**
- [ ] `src/features/shortcut_panel/ui/default_tab.py`: Hàng nút điều khiển bổ sung nút `+ Sequence` (đặt sau Command, trước Edit).
- [ ] `src/features/shortcut_panel/ui/default_tab_crud.py`: Thêm phương thức `_add_sequence()` với re-entrancy guard `self._dialog_open`, hỏi nhãn (`label`), mở `SequenceEditorDialog` và lưu vào `config_service`.
- [ ] Xử lý chỉnh sửa trong `_edit()`: Khi item được chọn có `type == "sequence"`, mở lại `SequenceEditorDialog` với các bước hiện có để người dùng cập nhật.
- [ ] Hàm `_refresh()` hiển thị mục Sequence trong danh sách với định dạng: `⛓ {label}  ({n} steps)`.

## 5. Functional Requirements
| ID | Requirement | Priority | Notes |
|----|-------------|----------|-------|
| FR-001 | Định nghĩa dataclass `SequenceItem` và cập nhật parser `config_service` | Must Have | Core data layer |
| FR-002 | Triển khai `execute_sequence()` điều phối 4 loại action và delay giữa các bước | Must Have | Core execution |
| FR-003 | Tích hợp kích hoạt `SequenceItem` trong `PanelLogic.select_current()` | Must Have | Trigger integration |
| FR-004 | Thêm nhãn loại item "Sequence" vào `panel_item_renderer.py` | Must Have | UI badge |
| FR-005 | Xây dựng hộp thoại `SequenceEditorDialog` quản lý các bước (Thêm/Sửa/Xóa/Đổi vị trí/Delay) | Must Have | New dialog |
| FR-006 | Tích hợp nút thêm và chức năng sửa/hiển thị Sequence trên `DefaultTab` và `DefaultTabCRUDMixin` | Must Have | Settings UI integration |

## 6. Non-Functional Requirements
| Category | Requirement | Metric |
|----------|-------------|--------|
| Performance | Độ trễ kích hoạt và chuyển bước tuân thủ chính xác cấu hình `delay_ms` | Sai số delay < 15ms |
| Reliability | Lỗi ở một bước không làm crash tiến trình chính RightWheel | Catch exception và log warning |
| Backward Compatibility | Tương thích ngược 100% với file cấu hình JSON hiện hữu | 0 migration required |
| Code Quality | Giới hạn độ dài tệp tin tuân thủ quy định hệ thống | Mỗi file ≤ 250 dòng |
| UI/UX | Giao diện đồng bộ phong cách với RightWheel Settings (_BG/_FG/_ACC) | WCAG AA compliant |

## 7. Out of Scope
- Không thay đổi hành vi hoặc cấu trúc của các loại item hiện có (`ShortcutItem`, `AppItem`, `UrlItem`, `CommandItem`, `FolderItem`, `ActionItem`).
- Không can thiệp vào tầng mouse hook (`mouse_hook_service.py`) hoặc gesture recognizer (`mouse_mapper_logic.py`).
- Không hỗ trợ lồng Sequence bên trong Sequence (không hỗ trợ nested sequences).
- Không thêm nút thêm Sequence vào bên trong hộp thoại `FolderEditorDialog` (chỉ quản lý ở cấp cao nhất của Default tab).

## 8. Dependencies
- Mã nguồn nội bộ:
  - `src/features/shortcut_panel/types/panel_types.py`
  - `src/features/shortcut_panel/services/shortcut_executor.py`
  - `src/features/shortcut_panel/services/config_service.py`
  - `src/features/shortcut_panel/logic/panel_logic.py`
  - `src/features/shortcut_panel/ui/panel_item_renderer.py`
  - `src/features/shortcut_panel/ui/default_tab.py`
  - `src/features/shortcut_panel/ui/default_tab_crud.py`
  - `src/features/shortcut_panel/ui/ask_dialog.py` (`_AskDialog`)
  - `src/features/shortcut_panel/ui/key_recorder_dialog.py` (`KeyRecorderDialog`)

## 9. Definition of Done (Feature-level)
- [ ] Tất cả User Stories (US-039 đến US-043) và Functional Requirements đã hoàn thành.
- [ ] Tạo được mục Sequence mới trên Settings và lưu thành công vào file cấu hình.
- [ ] Chọn Sequence trên Shortcut Panel thực thi đúng lần lượt các bước với delay xác định.
- [ ] Kiểm thử unit/smoke test cho `execute_sequence` và `parse_items` đạt kết quả pass.
- [ ] Toàn bộ các file mới và sửa đổi tuân thủ nghiêm ngặt giới hạn ≤ 250 dòng.

## 10. Timeline & Milestone
| Milestone | Description | Notes |
|-----------|------|-------|
| M1: Data & Execution Engine | Bổ sung `SequenceItem`, parser và `execute_sequence()` | US-039, US-040, US-041 |
| M2: Editor Dialog | Xây dựng `SequenceEditorDialog` với CRUD các bước | US-042 |
| M3: Settings UI & Integration | Tích hợp vào `DefaultTab` và kiểm thử toàn diện | US-043 |

## 11. Open Questions
- Không có (Các yêu cầu và phương án kỹ thuật đã được làm rõ hoàn toàn qua bước Elicitation).

## 12. Changelog
| Version | Date | Author | Change |
|---------|------|--------|--------|
| 1.0 | 2026-11-11 | chautnus | Khởi tạo dự thảo PRD cho tính năng Sequence Item Type (F-014) |
=== HẾT DRAFT ===
EVIDENCE:
- C:\dev\Mousehotkey\src\features\shortcut_panel\types\panel_types.py#L30-L75 (Định nghĩa MenuItem và các dataclass item hiện có)
- C:\dev\Mousehotkey\src\features\shortcut_panel\services\shortcut_executor.py#L140-L195 (Các hàm execute, execute_app, execute_command, execute_url)
- C:\dev\Mousehotkey\src\features\shortcut_panel\logic\panel_logic.py#L110-L140 (Dispatch item trong select_current)
- C:\dev\Mousehotkey\src\features\shortcut_panel\ui\panel_item_renderer.py#L20-L35 (_TYPE_LABEL mapping)
- C:\dev\Mousehotkey\src\features\shortcut_panel\ui\default_tab.py#L1-L102 (Default tab UI, 102 lines)
- C:\dev\Mousehotkey\src\features\shortcut_panel\ui\default_tab_crud.py#L1-L194 (DefaultTabCRUDMixin, 194 lines)
OPEN_QUESTIONS: không có
SUMMARY: Đã hoàn thành phân tích và soạn draft PRD cho tính năng Sequence Item Type (F-014) của Mousehotkey. Gồm 5 User Stories (US-039..US-043), 6 Functional Requirements, Scope IN/OUT rõ ràng, tiêu chí đánh giá và kiểm tra file size tuân thủ SYSTEM LOCK <= 250 dòng.