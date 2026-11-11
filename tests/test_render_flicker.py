import sys
import os
import unittest
from unittest.mock import patch

# Add src to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

import tkinter as tk
from features.shortcut_panel.logic.panel_logic import PanelLogic
from features.shortcut_panel.types.panel_types import ShortcutItem
from features.shortcut_panel.ui.panel_window import PanelWindow


class TestRenderFlicker(unittest.TestCase):
    def setUp(self):
        self.root = tk.Tk()
        self.root.withdraw()

    def tearDown(self):
        try:
            self.root.destroy()
        except Exception:
            pass

    def test_navigate_does_not_re_render_or_destroy_children(self):
        # 1. Initialize PanelLogic with 5 items
        items = [
            ShortcutItem(label=f"Item {i}", keys=f"ctrl+{i}")
            for i in range(5)
        ]

        logic = PanelLogic()
        logic._root = list(items)
        logic._items = list(items)
        logic._index = 0
        logic.visible = True

        # 2. Initialize PanelWindow without starting background thread
        with patch.object(PanelWindow, "_run", return_value=None):
            window = PanelWindow(logic)
            window._root = self.root
            window._win = tk.Toplevel(self.root)

            # Spy on _render
            orig_render = window._render
            render_count = 0

            def tracked_render():
                nonlocal render_count
                render_count += 1
                return orig_render()

            window._render = tracked_render

            # Initial render
            window._render()
            self.assertEqual(render_count, 1)

            renderer = window._item_renderer
            self.assertIsNotNone(renderer)

            # Record widget children in renderer container and window
            initial_win_children = list(window._win.winfo_children())
            initial_renderer_children = list(renderer._container.winfo_children())
            self.assertGreater(len(initial_renderer_children), 0)

            # Spy on update_selection
            orig_update_sel = renderer.update_selection
            update_sel_calls = []

            def tracked_update_selection(old_idx, new_idx):
                update_sel_calls.append((old_idx, new_idx))
                return orig_update_sel(old_idx, new_idx)

            renderer.update_selection = tracked_update_selection

            # Spy on clear
            clear_count = 0
            orig_clear = renderer.clear

            def tracked_clear():
                nonlocal clear_count
                clear_count += 1
                return orig_clear()

            renderer.clear = tracked_clear

            # 3. Call navigate(1) 3 times consecutively
            for _ in range(3):
                logic.navigate(1)
                window._do_update()

            # 4. Assertions
            # _render() should still only have been called ONCE initially
            self.assertEqual(render_count, 1, f"_render was called {render_count} times, expected 1")

            # update_selection should have been called 3 times with correct indices
            self.assertEqual(len(update_sel_calls), 3)
            self.assertEqual(update_sel_calls, [(0, 1), (1, 2), (2, 3)])

            # clear() should NEVER have been called during navigate
            self.assertEqual(clear_count, 0, f"clear() was called {clear_count} times during navigate")

            # DOM children should remain identical (not destroyed or recreated)
            current_win_children = list(window._win.winfo_children())
            current_renderer_children = list(renderer._container.winfo_children())
            self.assertEqual(initial_win_children, current_win_children)
            self.assertEqual(initial_renderer_children, current_renderer_children)

            print("AI-Test Flicker Check PASS: 0 full re-renders, in-place updates only, DOM children preserved.")


if __name__ == "__main__":
    unittest.main()
