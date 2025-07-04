from __future__ import annotations

import os


def is_tab_completion_active() -> bool:
    """
    Check if tab completion is active by looking for a specific environment variable.

    Returns:
        bool: True if tab completion is active, False otherwise.
    """
    return "_CLIVE_COMPLETE" in os.environ
