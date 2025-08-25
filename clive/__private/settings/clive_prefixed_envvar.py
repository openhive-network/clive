from __future__ import annotations

from clive.__private.core.constants.env import ENVVAR_PREFIX


def clive_prefixed_envvar(setting_name: str) -> str:
    underscored_setting_name = setting_name.replace(".", "__")
    return f"{ENVVAR_PREFIX}_{underscored_setting_name}"
