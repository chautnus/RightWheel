"""Profile editor widget — left list panel + right detail panel."""
from __future__ import annotations

import tkinter as tk

from ..services import config_service

_BG  = "#1e1e1e"
_BG2 = "#2d2d2d"
_FG  = "#cccccc"
_ACC = "#0078d4"
_RED = "#c0392b"
_SAV = "#16825d"


def _btn(p, text, cmd, bg=_ACC):
    return tk.Button(p, text=text, command=cmd, bg=bg, fg="white",
                     font=("Segoe UI", 9), relief="flat", padx=6, pady=3,
                     cursor="hand2", activebackground=bg)


def _ask(parent, title, prompt, init=""):
    r = [None]
    d = tk.Toplevel(parent)
    d.title(title); d.configure(bg=_BG); d.grab_set(); d.resizable(False, False)
    d.attributes("-topmost", True)
    tk.Label(d, text=prompt, bg=_BG, fg=_FG,
             font=("Segoe UI", 10)).pack(padx=16, pady=(12, 4))
    v = tk.StringVar(value=init)
    e = tk.Entry(d, textvariable=v, bg=_BG2, fg="#fff", insertbackground="#fff",
                 font=("Segoe UI", 11), width=26, relief="flat", bd=4)
    e.pack(padx=16, pady=4); e.focus_set(); e.select_range(0, "end")
    def ok(): r[0] = v.get().strip(); d.destroy()
    def cancel(): d.destroy()
    e.bind("<Return>", lambda _: ok()); e.bind("<Escape>", lambda _: cancel())
    bf = tk.Frame(d, bg=_BG); bf.pack(pady=8)
    _btn(bf, "OK", ok, _SAV).pack(side="left", padx=4)
    _btn(bf, "Cancel", cancel, _RED).pack(side="left", padx=4)
    d.protocol("WM_DELETE_WINDOW", cancel)
    parent.wait_window(d)
    return r[0] if r[0] else None


class ProfileEditor(tk.Frame):
    """Left = profile list, Right = profile detail (name + match rules + shortcuts)."""

    def __init__(self, parent) -> None:
        super().__init__(parent, bg=_BG)
        self._idx = -1

        # ── Left pane: list ──────────────────────────────────────────────
        lf = tk.Frame(self, bg=_BG2, width=160)
        lf.pack(side="left", fill="y"); lf.pack_propagate(False)
        tk.Label(lf, text="Profiles", bg=_BG2, fg=_FG,
                 font=("Segoe UI", 10, "bold")).pack(pady=(8, 2))
        self._lb = tk.Listbox(lf, bg=_BG2, fg=_FG, selectbackground=_ACC,
                              relief="flat", bd=0, activestyle="none",
                              font=("Segoe UI", 10))
        self._lb.pack(fill="both", expand=True, padx=4)
        self._lb.bind("<<ListboxSelect>>", self._on_select)
        bf = tk.Frame(lf, bg=_BG2); bf.pack(fill="x", padx=4, pady=6)
        _btn(bf, "+ Add", self._add,    _ACC).pack(side="left", padx=2)
        _btn(bf, "✕ Del", self._delete, _RED).pack(side="left", padx=2)

        # ── Right pane: detail ───────────────────────────────────────────
        self._rf = tk.Frame(self, bg=_BG)
        self._rf.pack(side="left", fill="both", expand=True)
        self._ph = tk.Label(self._rf, text="← Select a profile", bg=_BG, fg="#555",
                            font=("Segoe UI", 11))
        self._ph.pack(pady=30)

        self._df = tk.Frame(self._rf, bg=_BG)
        # name row
        nr = tk.Frame(self._df, bg=_BG); nr.pack(fill="x", padx=8, pady=(8, 4))
        tk.Label(nr, text="Name:", bg=_BG, fg=_FG,
                 font=("Segoe UI", 10)).pack(side="left")
        self._name = tk.StringVar()
        tk.Entry(nr, textvariable=self._name, bg=_BG2, fg="#fff",
                 insertbackground="#fff", font=("Segoe UI", 10),
                 relief="flat", bd=4, width=22).pack(side="left", padx=6)
        _btn(nr, "💾", self._save_name, _SAV).pack(side="left")

        # match rules
        tk.Label(self._df, text="Match Rules  (ALL must match — AND logic):",
                 bg=_BG, fg=_FG, font=("Segoe UI", 9)).pack(anchor="w", padx=8, pady=(6, 0))
        self._rlb = tk.Listbox(self._df, bg=_BG2, fg=_FG, selectbackground=_ACC,
                               relief="flat", bd=0, height=4, font=("Segoe UI", 9))
        self._rlb.pack(fill="x", padx=8)
        rf2 = tk.Frame(self._df, bg=_BG); rf2.pack(anchor="w", padx=8, pady=2)
        _btn(rf2, "+ Rule", self._add_rule, _ACC).pack(side="left", padx=2)
        _btn(rf2, "✕ Rule", self._del_rule, _RED).pack(side="left", padx=2)
        tk.Label(rf2, text="by: exe | title_contains | class_name",
                 bg=_BG, fg="#444", font=("Segoe UI", 8)).pack(side="left", padx=6)

        # shortcuts
        tk.Label(self._df, text="Shortcuts:", bg=_BG, fg=_FG,
                 font=("Segoe UI", 9)).pack(anchor="w", padx=8, pady=(8, 0))
        self._slb = tk.Listbox(self._df, bg=_BG2, fg=_FG, selectbackground=_ACC,
                               relief="flat", bd=0, height=7, font=("Segoe UI", 9))
        self._slb.pack(fill="x", padx=8)
        sf2 = tk.Frame(self._df, bg=_BG); sf2.pack(anchor="w", padx=8, pady=2)
        _btn(sf2, "+ Add", self._add_sc, _ACC).pack(side="left", padx=2)
        _btn(sf2, "✕ Del", self._del_sc, _RED).pack(side="left", padx=2)

        self._refresh()

    # ── list panel ────────────────────────────────────────────────────────

    def _refresh(self, sel: int | None = None) -> None:
        data = config_service.load()
        self._lb.delete(0, "end")
        for p in data.get("profiles", []):
            self._lb.insert("end", f"  {p['name']}")
        if sel is not None and sel >= 0:
            self._lb.selection_set(sel)
            self._load_detail(sel)

    def _on_select(self, _=None) -> None:
        s = self._lb.curselection()
        if s:
            self._load_detail(s[0])

    def _add(self) -> None:
        name = _ask(self, "New Profile", "Profile name:")
        if not name:
            return
        data = config_service.load()
        data.setdefault("profiles", []).append(
            {"name": name, "match": [], "shortcuts": []})
        config_service.save(data)
        self._refresh(len(data["profiles"]) - 1)

    def _delete(self) -> None:
        s = self._lb.curselection()
        if not s:
            return
        data = config_service.load()
        data["profiles"].pop(s[0])
        config_service.save(data)
        self._idx = -1
        self._df.pack_forget(); self._ph.pack(pady=30)
        self._refresh()

    # ── detail panel ──────────────────────────────────────────────────────

    def _load_detail(self, idx: int) -> None:
        self._idx = idx
        self._ph.pack_forget()
        self._df.pack(fill="both", expand=True)
        data = config_service.load()
        p = data["profiles"][idx]
        self._name.set(p["name"])
        self._rlb.delete(0, "end")
        for r in p.get("match", []):
            self._rlb.insert("end", f"  {r['by']} = {r['value']}")
        self._slb.delete(0, "end")
        for sc in p.get("shortcuts", []):
            self._slb.insert("end", f"  {sc.get('label', '')}   →   {sc.get('keys', '')}")

    def _save_name(self) -> None:
        if self._idx < 0:
            return
        data = config_service.load()
        data["profiles"][self._idx]["name"] = self._name.get().strip()
        config_service.save(data)
        self._refresh(self._idx)

    def _add_rule(self) -> None:
        if self._idx < 0:
            return
        by = _ask(self, "Match Rule", "by  (exe / title_contains / class_name):")
        if not by:
            return
        val = _ask(self, "Match Rule", f"value  for '{by}':")
        if val is None:
            return
        data = config_service.load()
        data["profiles"][self._idx]["match"].append({"by": by, "value": val})
        config_service.save(data); self._load_detail(self._idx)

    def _del_rule(self) -> None:
        s = self._rlb.curselection()
        if not s or self._idx < 0:
            return
        data = config_service.load()
        data["profiles"][self._idx]["match"].pop(s[0])
        config_service.save(data); self._load_detail(self._idx)

    def _add_sc(self) -> None:
        if self._idx < 0:
            return
        label = _ask(self, "Add Shortcut", "Label:")
        if not label:
            return
        keys = _ask(self, "Add Shortcut", "Keys  (e.g. ctrl+shift+v):")
        if keys is None:
            return
        data = config_service.load()
        data["profiles"][self._idx]["shortcuts"].append(
            {"type": "shortcut", "label": label, "keys": keys.lower()})
        config_service.save(data); self._load_detail(self._idx)

    def _del_sc(self) -> None:
        s = self._slb.curselection()
        if not s or self._idx < 0:
            return
        data = config_service.load()
        data["profiles"][self._idx]["shortcuts"].pop(s[0])
        config_service.save(data); self._load_detail(self._idx)
