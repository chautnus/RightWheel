# Memory: Architecture & Implementation Notes for F-015 (Gemini Step + Sequence Step Editing)

## Core Architecture Decisions
- **Step mới `"gemini"`**: schema `{"type": "gemini", "prompt": str, "delay_ms": int}`. Executor (`clipboard_web_actions.execute_gemini`) tự ghép `f"{prompt} {text}"` (text = clipboard thật đọc tại thời điểm chạy) rồi `urllib.parse.quote()` toàn bộ, mở `https://gemini.google.com/app?prompt=<encoded>`. Không yêu cầu người dùng tự gõ `{text}`/encode — loại bỏ lớp lỗi "gõ nhầm `%7B%7D` thay vì `{}`" đã gặp thực tế.
- **Edit cho step đã tạo**: `sequence_editor_dialog.py` thêm nút "Edit" + double-click trên Listbox. Add và Edit dùng **chung** 1 hàm `ask_<type>(parent, init=None)` mỗi loại — Edit chỉ khác ở truyền `init=step` để pre-fill (kể cả `delay_ms`) và ghi đè theo index thay vì `append`.
- **Tách file để giữ SYSTEM LOCK**:
  - `ui/sequence_step_dialogs.py` (98 dòng) — chứa 6 hàm `ask_shortcut/ask_app/ask_url/ask_command/ask_url_clipboard/ask_gemini` + `ask_delay` + dict `STEP_KINDS` (map type → label + ask-fn, dùng để dựng nút Add động và tra loại khi Edit).
  - `services/clipboard_web_actions.py` (65 dòng) — chứa `get_clipboard_text()` (raw Win32, tách từ `_get_clipboard_text()` cũ), `execute_url_clipboard()`, `execute_gemini()`. Tự `webbrowser.open()` trực tiếp, KHÔNG import `shortcut_executor` (tránh circular import).
  - `sequence_editor_dialog.py`: 249 → 211 dòng (giờ chỉ còn vai trò điều phối list/nút/save).
  - `shortcut_executor.py`: 237 → 251 (sau khi thêm execute_gemini, VƯỢT 250) → 198 dòng sau khi tách `clipboard_web_actions.py`. Dispatch `"url_clipboard"`/`"gemini"` giờ gọi `clipboard_web_actions.execute_url_clipboard()`/`execute_gemini()`.

## Bug ngầm phát hiện trong lúc debug (chưa fix — ghi nhận để tránh lặp lại điều tra)
- `RightWheel.spec` → `hiddenimports` vẫn còn `features.shortcut_panel.services.volume_service` — module này đã bị xoá hoàn toàn ở **F-013** (xem `[[f013-remove-volume-fix-render-flicker-arch]]`/ADR-011). PyInstaller log `ERROR: Hidden import 'features.shortcut_panel.services.volume_service' not found` ở mỗi lần build — KHÔNG chặn build (chỉ warning), nhưng là dọn dẹp còn thiếu của F-013. Chưa sửa trong session này vì ngoài phạm vi yêu cầu.

## Vòng debug thực tế (Claude, 2026-11-12)
- Root cause ban đầu bị chẩn đoán sai 1 lần: nghĩ là thiếu bước Ctrl+C trong sequence. User xác nhận đã thêm Ctrl+C và copy hoạt động tốt (verify qua Notepad paste) — loại trừ được hướng đó bằng cách yêu cầu user tự kiểm tra Bước 1 (Ctrl+C) tách biệt khỏi Bước 2 (URL), đúng rule "sau 1 lần sửa mù không thành, không sửa mù lần 2".
- Root cause thật: `url_clipboard` template của user chứa `%7Btext%7D` (dấu `{`/`}` đã bị percent-encode) thay vì `{text}` thật — `.replace("{text}", encoded)` không khớp vì so khớp chuỗi đúng ký tự, không decode trước. Chỉ xác định được chắc chắn sau khi user gửi nguyên văn chuỗi đang lưu — không đoán mò thêm lần nữa.
- Build exe: `dist/RightWheel.exe` đang chạy (2 process khoá file) từng làm `pyinstaller` fail với `PermissionError: Access is denied` — phải xin phép user `taskkill` trước khi build lại (killing process nằm trong danh sách hành động cần xác nhận).
