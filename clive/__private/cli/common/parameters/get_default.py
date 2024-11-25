from __future__ import annotations

import contextlib
from typing import Any

from clive.__private.cli.completion import is_tab_completion_active
from clive.__private.settings import safe_settings


def get_default_profile_name() -> str | None:
    if not is_tab_completion_active():
        from clive.__private.core.profile import Profile
        from clive.__private.storage.service import NoDefaultProfileToLoadError

        with contextlib.suppress(NoDefaultProfileToLoadError):
            return Profile.get_default_profile_name()
    return None


def get_default_beekeeper_remote() -> str | None:
    if not is_tab_completion_active():
        address = safe_settings.beekeeper.settings_factory().http_endpoint
        return address.as_string() if address else None
    return None


def get_default_or_make_required(value: Any) -> Any:  # noqa: ANN401
    return ... if value is None else value


def get_default_or_make_optional(value: Any) -> Any:  # noqa: ANN401
    return value if value else None
