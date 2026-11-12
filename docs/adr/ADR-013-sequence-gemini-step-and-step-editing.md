# ADR-013: Gemini Sequence Step, Step Editing, and Clipboard/Dialog File Split

## Status
Accepted

## Context
F-014 (Sequence) chỉ hỗ trợ **thêm** bước (`+Keys/+App/+Web/+Script/+Web(Clip)`), **xoá**, và **đổi thứ tự** (▲▼) — không có cách **sửa lại** một bước đã tạo (kể cả riêng `delay_ms`). Người dùng phát hiện điều này khi debug một step "Web (Clip)" nhập sai: không sửa được, phải xoá rồi tạo lại từ đầu mỗi lần thử.

Trong lúc debug cùng một step đó, người dùng muốn dùng Gemini (qua extension "Gemini Url Prompt", tham số `?prompt=`) để dịch văn bản đã chọn, nhưng việc tự ghép `prompt` cố định + `{text}` + URL-encode thủ công trong ô "Web template" liên tục bị lỗi gõ dấu `{` `}` (có lúc gõ nhầm percent-encode `%7B%7D` thay vì ký tự thật) — chỉ ra nhu cầu một step chuyên biệt chỉ hỏi "Prompt", còn việc ghép + encode để app làm.

Đồng thời, thêm `execute_gemini()` vào `shortcut_executor.py` (vốn đã mang `_get_clipboard_text()`/`execute_url_clipboard()`) đẩy file từ 237 lên 251 dòng — vượt ngưỡng SYSTEM LOCK (250). Và việc thêm Edit cho 5 loại bước nếu viết trực tiếp trong `sequence_editor_dialog.py` (249 dòng, đã ở mức WARNING) chắc chắn cũng vượt ngưỡng.

---

## Decisions

### 1. Step mới `"gemini"` — chỉ hỏi Prompt, tự ghép + encode
- **Quyết định**: thêm step type `gemini` với schema `{"type": "gemini", "prompt": str, "delay_ms": int}`. Executor (`clipboard_web_actions.execute_gemini`) đọc clipboard thật tại thời điểm chạy, ghép `f"{prompt} {text}"`, `urllib.parse.quote()` toàn bộ, rồi mở `https://gemini.google.com/app?prompt=<encoded>`.
- **Lý do & so sánh**:
  - *Phương án A (dùng lại `"url_clipboard"` với URL template dựng sẵn)*: tái dùng executor có sẵn, nhưng người dùng vẫn phải thấy/sửa một URL đầy đủ, dễ lặp lại lỗi gõ `{text}`/encode thủ công đã từng xảy ra.
  - *Phương án B (step riêng `"gemini"`, chỉ lưu `prompt` — ĐƯỢC CHỌN)*: UI chỉ hỏi 1 câu "Prompt", không có chỗ cho người dùng tự gõ sai cú pháp placeholder; đồng thời giữ được khả năng sửa lại (Edit) đúng 1 field "prompt" sau này, không phải sửa cả URL.
  - Endpoint `gemini.google.com/app?prompt=` không phải API chính thức của Google (hành vi quan sát được từ extension/cộng đồng, có thể ngừng hoạt động) — đã nói rõ với người dùng, không coi là cam kết lâu dài của Google.

### 2. Thêm khả năng Edit cho step đã tạo (double-click hoặc nút "Edit")
- **Quyết định**: thêm nút **"Edit"** + binding `<Double-Button-1>` trên Listbox trong `sequence_editor_dialog.py`. Cả Add và Edit gọi **cùng một hàm hỏi giá trị** theo từng loại step (xem Decision 3); Edit truyền thêm `init=step` để pre-fill giá trị cũ (bao gồm `delay_ms`), rồi ghi đè `self._steps[idx]` thay vì `append`.
- **Lý do**: tái dùng 100% logic Add hiện có, không tạo đường dẫn code thứ hai dễ lệch nhau; sửa 1 chỗ (hàm `ask_*`) là cả Add và Edit đều nhận thay đổi.

### 3. Tách `sequence_step_dialogs.py` — logic hỏi giá trị từng loại step
- **Quyết định**: chuyển toàn bộ 5 hàm `_step_add_*` (và `_ask_delay`) từ `sequence_editor_dialog.py` ra file mới `ui/sequence_step_dialogs.py`, đổi API thành `ask_<type>(parent, init: dict | None = None) -> dict | None` — nhận `init` để pre-fill (phục vụ Edit ở Decision 2), trả `None` nếu người dùng Cancel. Thêm dict `STEP_KINDS: {type: (button_label, ask_fn)}` để `sequence_editor_dialog.py` dựng nút Add động và tra loại step khi Edit, không hard-code từng nhánh `if/elif` cho nút.
- **Lý do & so sánh**:
  - *Phương án A (giữ nguyên 1 file, chấp nhận vượt 250 dòng, chạy `/split-plan` sau)*: đúng rule nhưng tốn thêm 1 vòng lập kế hoạch cho một việc tách cơ học rõ ràng, không có quyết định kiến trúc mới cần tranh luận.
  - *Phương án B (tách ngay thành `sequence_step_dialogs.py` — ĐƯỢC CHỌN)*: giảm `sequence_editor_dialog.py` từ 249 → 211 dòng *trong khi vẫn thêm_ Edit + nút Gemini*, vì dialog file giờ chỉ còn vai trò điều phối (list, nút, save), không còn chứa logic hỏi giá trị từng loại.
- **Hệ quả phụ có lợi**: Add và Edit dùng chung đúng 1 hàm/loại step — không thể lệch field giữa 2 luồng như từng xảy ra ở F-014/v2.20.1 (rename sequence không lưu vì luồng Edit tự ý `config_service.load()` lại).

### 4. Tách `clipboard_web_actions.py` — đọc clipboard + build URL
- **Quyết định**: chuyển `_get_clipboard_text()`, `execute_url_clipboard()`, và `execute_gemini()` mới ra file riêng `services/clipboard_web_actions.py`. File này tự mở URL qua `webbrowser.open` trực tiếp (không gọi `shortcut_executor.execute_url()`) để tránh import vòng (`shortcut_executor` → `clipboard_web_actions` → `shortcut_executor`). `execute_sequence()` dispatch `"url_clipboard"`/`"gemini"` qua `clipboard_web_actions.execute_url_clipboard()`/`execute_gemini()`.
- **Lý do**: `shortcut_executor.py` đã chạm 251/250 dòng ngay khi thêm `execute_gemini()`; tách theo đúng ranh giới chức năng (mọi thứ đọc clipboard sống trong 1 file) thay vì cắt tùy ý theo số dòng. Kết quả: `shortcut_executor.py` 198 dòng, `clipboard_web_actions.py` 65 dòng — cả hai xa ngưỡng SYSTEM LOCK.

---

## Consequences
- **Ưu điểm**:
  - Sửa được lỗi UX "không sửa lại được step/delay đã tạo" tồn tại từ F-014 tới giờ — không phải xoá-tạo-lại mỗi lần chỉnh.
  - Step "Gemini" loại bỏ hoàn toàn lớp lỗi gõ `{text}`/percent-encode nhầm đã gặp thực tế trong session debug.
  - Cả 4 file service/UI liên quan (`shortcut_executor.py` 198, `clipboard_web_actions.py` 65, `sequence_editor_dialog.py` 211, `sequence_step_dialogs.py` 98) đều dưới ngưỡng SYSTEM LOCK với biên độ an toàn cho các bước kế tiếp.
- **Hạn chế & đánh đổi**:
  - Step "shortcut" khi Edit yêu cầu người dùng **bấm lại tổ hợp phím** qua `KeyRecorderDialog` (không có cách hiển thị lại combo cũ để chỉnh từng phím) — chấp nhận được vì đây là hành vi gốc của `KeyRecorderDialog.ask()`, không phải hạn chế mới do ADR này gây ra.
  - `gemini.google.com/app?prompt=` là hành vi không chính thức của Google/extension bên thứ ba — ghi rõ trong tooltip/hint để người dùng không nhầm là tích hợp được Google đảm bảo.
=== HẾT DRAFT ===
EVIDENCE:
- C:\dev\Mousehotkey\src\features\shortcut_panel\services\shortcut_executor.py (trước sửa: 237→251 dòng sau khi thêm execute_gemini, vượt SYSTEM LOCK)
- C:\dev\Mousehotkey\src\features\shortcut_panel\ui\sequence_editor_dialog.py (trước sửa: 249 dòng, không có Edit, chỉ Add/Delete/▲▼)
- C:\dev\Mousehotkey\src\features\shortcut_panel\ui\ask_dialog.py#L62-L67 (`_AskDialog.ask()` đã sẵn có tham số `init` dùng để pre-fill)
- Test thực tế qua Windows clipboard API (không mock): `execute_gemini("Translate to English:")` với clipboard="Xin chao the gioi" → `https://gemini.google.com/app?prompt=Translate%20to%20English%3A%20Xin%20chao%20the%20gioi`
OPEN_QUESTIONS: không có
SUMMARY: ADR-013 — thêm step "gemini" (chỉ hỏi prompt, tự ghép+encode clipboard), thêm Edit cho mọi loại step (double-click/nút Edit, dùng chung hàm ask_* với Add), tách sequence_step_dialogs.py (logic hỏi giá trị) và clipboard_web_actions.py (đọc clipboard + build URL) để giữ 4 file liên quan dưới ngưỡng SYSTEM LOCK 250 dòng.
