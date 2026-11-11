# Memory: Architecture & Implementation Notes for F-014 Sequence Item Type

## Core Architecture Decisions
- **SequenceItem**: Kế thừa `MenuItem`, chứa `steps: list[dict]`. Sử dụng primitive `list[dict]` để serialize tự nhiên ra JSON, không sinh dataclass con gây phình code.
- **SequenceEditorDialog**: Hộp thoại modal độc lập, sở hữu `_steps: list[dict]` in-memory buffer riêng biệt. Có 4 hàm thêm bước con (`_step_add_shortcut`, `_step_add_app`, `_step_add_url`, `_step_add_command`) tự quản lý, không phụ thuộc và không kế thừa `DefaultTabCRUDMixin`.
- **Execution Resilience**: `execute_sequence()` trong `shortcut_executor.py` bọc `try/except` quanh từng bước với `time.sleep(delay_ms / 1000.0)`. Lỗi ở một bước sẽ ghi log warning và tiếp tục thực thi các bước còn lại.
- **Tkinter Integration**: `DefaultTab` bổ sung nút `+ Sequence`. `default_tab_crud.py` định tuyến mở `SequenceEditorDialog` cho cả luồng Add và Edit.
- **SYSTEM LOCK 250 dòng**: Giữ tất cả các file UI và Service dưới 250 dòng.

## Vòng validate (Claude, 2026-11-11)
- FAIL lần 1: draft ban đầu dùng `tkinter.simpledialog.askstring` thô cho bước +Keys (bắt gõ tay "ctrl+win+d") và cho App Args/URL/Command, thay vì `KeyRecorderDialog`/`_AskDialog` nội bộ đã có — tái lập đúng bug "phím Win bị Windows giành" từng fix ở GesturesTab (F-010 follow-up), và lệch theme dark mode. Đã fix lại đúng spec PRD/ADR-012, re-run PASS toàn bộ.
- **BÀI HỌC**: khi task yêu cầu "tái dùng dialog X đã có" (KeyRecorderDialog/_AskDialog), verify-cmd chỉ test `import` thành công KHÔNG đủ để bắt lỗi "dùng nhầm thành simpledialog thô" — phải đọc code thật (grep tên class dialog được gọi) mới phát hiện được, không thể chỉ tin verify-output.
