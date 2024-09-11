from __future__ import annotations

import contextlib
from copy import deepcopy
from typing import TYPE_CHECKING, Any

from clive.__private.cli.completion import is_tab_completion_active

if TYPE_CHECKING:
    from typer.models import OptionInfo


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


def get_default_or_make_required(value: Any) -> Any:  # noqa: ANN401
    return ... if value is None else value


def modified_option(option: OptionInfo, **kwargs: Any) -> Any:  # noqa: ANN401
    """
    Create option based on another option, but with some attributes modified.

    Args:
    ----
    option: The option to modify.
    kwargs: The attributes to modify.
    """
    new_option = deepcopy(option)
    for key, value in kwargs.items():
        if not hasattr(new_option, key):
            raise ValueError(f"Unknown option attribute: {key}\navailable attributes: {list(option.__dict__)}")
        setattr(new_option, key, value)
    return new_option
