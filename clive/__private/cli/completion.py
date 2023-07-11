from __future__ import annotations

import os


def is_tab_completion_active() -> bool:
    return "_CLIVE_COMPLETE" in os.environ
