from dataclasses import dataclass
from enum import Enum, auto


class MapperState(Enum):
    IDLE        = auto()
    RIGHT_HELD  = auto()   # RMB suppressed, waiting to see scroll or move
    GESTURE     = auto()   # Mouse moved enough → injected retroactive right_down
    SCROLLING   = auto()   # Scroll happened → Alt+Tab mode


class ScrollDirection(Enum):
    UP   = auto()
    DOWN = auto()


@dataclass
class HotkeyConfig:
    move_threshold: int = 8   # pixels before we commit to GESTURE mode


@dataclass
class MouseEvent:
    kind:       str                        # "right_down"|"right_up"|"scroll"|"move"
    scroll_dir: ScrollDirection | None = None
    x:          int = 0
    y:          int = 0
