---
name: f001-shift-scroll-tab-switch-arch
description: Quyết định kiến trúc cho feature F-001 shift-scroll-tab-switch — ADR-001
metadata:
  type: project
---

Feature: F-001 shift-scroll-tab-switch
ADR-001: Dùng GetAsyncKeyState(VK_SHIFT) polling trong callback WM_MOUSEWHEEL hiện có + kỹ thuật blind-release-modifier (inject KEYEVENTF_KEYUP cho VK_SHIFT trước khi gửi Ctrl+Tab) để chuyển tab Chrome/Edge/Chromium — KHÔNG thêm WH_KEYBOARD_LL hook mới (phương án này bị loại vì sẽ phá Shift+Click/gõ chữ HOA/Shift+Tab trong form nếu suppress Shift liên tục).
Không tái dùng pattern begin_switch/cycle/end_switch (đó là cho Alt+Tab có overlay UI) — Ctrl+Tab chuyển ngay, chỉ cần 1 hàm switch_tab(forward) mỗi tick.
Saved: 2026-10-30
