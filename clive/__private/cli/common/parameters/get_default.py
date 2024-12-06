from __future__ import annotations

import contextlib

from clive.__private.cli.completion import is_tab_completion_active


def get_default_profile_name() -> str | None:
    if not is_tab_completion_active():
        from clive.__private.core.profile import Profile
        from clive.__private.storage.service import NoDefaultProfileToLoadError

        with contextlib.suppress(NoDefaultProfileToLoadError):
            return Profile.get_default_profile_name()
    return None


def get_default_beekeeper_remote() -> str | None:
    if not is_tab_completion_active():
        from clive.__private.core.beekeeper import Beekeeper

        address = Beekeeper.get_remote_address_from_settings() or Beekeeper.get_remote_address_from_connection_file()
        return str(address) if address else None
    return None
