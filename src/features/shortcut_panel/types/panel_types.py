from __future__ import annotations
from dataclasses import dataclass, field
from typing import Union


@dataclass
class MatchRule:
    by:    str   # "exe" | "title_contains" | "class_name"
    value: str


@dataclass
class Profile:
    name:      str
    match:     list   # list[MatchRule]
    shortcuts: list   # list[MenuItem]


@dataclass
class ShortcutItem:
    label: str
    keys:  str
    type:  str = "shortcut"


@dataclass
class AppItem:
    label: str
    path:  str          # full path to exe, e.g. C:\Windows\notepad.exe
    args:  str = ""     # optional command-line arguments
    type:  str = "app"


@dataclass
class UrlItem:
    label: str
    url:   str          # e.g. https://example.com
    type:  str = "url"


@dataclass
class ActionItem:
    label:  str
    action: str         # "open_settings" | "toggle_pause"
    type:   str = "action"


@dataclass
class CommandItem:
    label: str
    cmd:   str          # shell command, e.g. "cd C:\proj && git pull"
    cwd:   str = ""     # working directory (optional)
    type:  str = "command"


@dataclass
class FolderItem:
    label:    str
    children: list = field(default_factory=list)  # list[MenuItem]
    type:     str  = "folder"


MenuItem = Union[ShortcutItem, AppItem, UrlItem, ActionItem, CommandItem, FolderItem]


@dataclass
class NavState:
    items:      list        # current level MenuItem list
    breadcrumb: list[str]   # folder path labels
    index:      int         # highlighted row
