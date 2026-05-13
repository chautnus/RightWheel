# Import Template Feature

## Trách nhiệm từng file

| File | Trách nhiệm | Lines dự kiến |
|------|-------------|---------------|
| `services/import_service.py` | Đọc file JSON, validate schema, trả về list[dict] sạch | ~80 |
| `ui/import_dialog.py` | Dialog chọn file + chọn mode (replace/append) + preview | ~140 |
| `ui/default_tab.py` | Thêm nút "Import" vào toolbar, gọi ImportDialog | +10 lines |
| `ui/settings_window.py` | Không cần thay đổi | — |

## Data Flow

```
User click "Import" (default_tab.py)
        ↓
ImportDialog mở (import_dialog.py)
        ↓
User chọn file .json + mode (replace / append)
        ↓
import_service.validate_file(path) → list[dict] | error
        ↓
Preview hiển thị danh sách shortcuts sẽ import
        ↓
User confirm → import_service.apply(data, mode, config)
        ↓
config_service.save(updated_config)
        ↓
default_tab._refresh() reload danh sách
```

## Template file format (JSON)

```json
{
  "name": "Developer Setup",
  "description": "Shortcuts for VS Code + Git workflow",
  "shortcuts": [
    {"type": "shortcut", "label": "🔍 Search", "keys": "win+s"},
    {"type": "app",      "label": "🚀 VS Code", "path": "C:\\...\\Code.exe"},
    {"type": "url",      "label": "🌐 GitHub",  "url": "https://github.com"},
    {"type": "folder",   "label": "📁 Git",     "children": [
      {"type": "shortcut", "label": "Pull", "keys": "ctrl+shift+p"}
    ]}
  ]
}
```

## Import modes

| Mode | Hành vi |
|------|---------|
| `append` | Thêm vào cuối danh sách hiện tại |
| `replace` | Xóa toàn bộ danh sách cũ, thay bằng template |

## Validation rules (import_service)

- File phải là JSON hợp lệ
- Phải có key `"shortcuts"` là array
- Mỗi item phải có `"type"` ∈ {shortcut, app, url, folder, action}
- `shortcut` phải có `"keys"`
- `app` phải có `"path"`
- `url` phải có `"url"`
- `folder` phải có `"children"` là array
- Items không hợp lệ bị bỏ qua, không crash
