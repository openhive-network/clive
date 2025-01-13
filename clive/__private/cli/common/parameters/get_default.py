from __future__ import annotations

from clive.__private.cli.completion import is_tab_completion_active


def get_default_beekeeper_remote() -> str | None:
    if not is_tab_completion_active():
        from clive.__private.core.beekeeper import Beekeeper

        address = Beekeeper.get_remote_address_from_settings() or Beekeeper.get_remote_address_from_connection_file()
        return str(address) if address else None
    return None
