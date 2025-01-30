from __future__ import annotations

from clive.__private.cli.completion import is_tab_completion_active
from clive.__private.settings import safe_settings


def get_default_beekeeper_remote() -> str | None:
    if not is_tab_completion_active():
        address = safe_settings.beekeeper.settings_factory().http_endpoint
        return str(address) if address is not None else None
    return None
