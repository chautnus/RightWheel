# Feature: Context-Aware Profiles

## Mục tiêu
Hiển thị bộ shortcut khác nhau tùy theo ứng dụng đang active (Word, Canva, Chrome...).

## Cây thư mục & trách nhiệm

```
shortcut_panel/
├── types/
│   └── panel_types.py          ← THÊM: MatchRule, Profile dataclasses
│
├── services/
│   ├── window_service.py       ← MỚI: lấy exe + title + class từ HWND (ctypes only)
│   ├── config_service.py       ← CẬP NHẬT: schema v2, resolve_profile(), migration v1→v2
│   └── shortcut_executor.py    ← không đổi
│
├── logic/
│   └── panel_logic.py          ← CẬP NHẬT: show() gọi window_service + resolve_profile
│                                            lưu active_profile_name để hiển thị header
│
└── ui/
    ├── settings_window.py      ← CẬP NHẬT: ttk.Notebook (tab Default + tab Profiles)
    └── profile_editor.py       ← MỚI: toàn bộ UI CRUD cho profiles
                                         ProfileListPanel + ProfileDetailPanel
```

## Luồng dữ liệu

```
[Mouse Hook] → panel_logic.show()
                   │
                   ├─ window_service.get_hwnd_info(hwnd)
                   │        → (exe: str, title: str, class_name: str)
                   │
                   ├─ config_service.resolve_profile(exe, title, class_name, data)
                   │        → list[MenuItem]  (profile match hoặc default)
                   │
                   └─ self._items = resolved items
                      self._active_profile = profile_name | "Default"

[User opens Settings] → settings_window.py
    ├── Tab "Default"  → ShortcutListPanel (code hiện tại)
    └── Tab "Profiles" → profile_editor.py
            ├── ProfileListPanel  (danh sách profiles, + Add, ✕ Delete)
            └── ProfileDetailPanel (tên, match rules, shortcut list)
```

## Schema config v2

```json
{
  "version": 2,
  "default": [ ...shortcuts... ],
  "profiles": [
    {
      "name": "Microsoft Word",
      "match": [
        { "by": "exe", "value": "WINWORD.EXE" }
      ],
      "shortcuts": [ ...word shortcuts... ]
    },
    {
      "name": "Canva (Chrome)",
      "match": [
        { "by": "exe",            "value": "chrome.exe" },
        { "by": "title_contains", "value": "Canva" }
      ],
      "shortcuts": [ ...canva shortcuts... ]
    }
  ]
}
```

## Match rules

| `by`            | Logic                              | Ví dụ value       |
|-----------------|------------------------------------|-------------------|
| `exe`           | basename EXE, case-insensitive     | `WINWORD.EXE`     |
| `title_contains`| window title chứa chuỗi (lower)    | `Canva`           |
| `class_name`    | Win32 class name (exact)           | `OpusApp`         |

Một profile match khi **tất cả rules** đều đúng (AND).  
Profile đầu tiên match thắng → fallback về `default`.

## Giới hạn thiết kế

- Mỗi file ≤ 150 dòng → `profile_editor.py` tách thành 2 class
- `window_service.py` chỉ dùng ctypes — không cần psutil
- Migration v1→v2 tự động trong `config_service.load()`
- `panel_window.py` hiển thị tên profile active ở header panel (nếu ≠ Default)
