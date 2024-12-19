from __future__ import annotations

from clive.__private.cli.completion import is_tab_completion_active

if not is_tab_completion_active():
    from clive.__private.core.world import World

__version__ = "0.0.0"

__all__ = ["World", "__version__"]
