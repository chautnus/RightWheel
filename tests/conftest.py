import os
import sys

root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
src_dir = os.path.join(root_dir, "src")

if root_dir not in sys.path:
    sys.path.insert(0, root_dir)
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)

# Ensure Tcl/Tk paths are set if available in python prefix (using forward slashes for Tcl interpreter)
tcl_dir = os.path.join(sys.prefix, "tcl", "tcl8.6").replace("\\", "/")
tk_dir = os.path.join(sys.prefix, "tcl", "tk8.6").replace("\\", "/")
if os.path.isdir(tcl_dir) and "TCL_LIBRARY" not in os.environ:
    os.environ["TCL_LIBRARY"] = tcl_dir
if os.path.isdir(tk_dir) and "TK_LIBRARY" not in os.environ:
    os.environ["TK_LIBRARY"] = tk_dir
