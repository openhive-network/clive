from __future__ import annotations

from clive.__private.core.constants.setting_identifiers import IS_DEV
from clive.__private.settings.clive_prefixed_envvar import clive_prefixed_envvar


def is_in_dev_mode() -> bool:
    from clive.__private.settings import safe_settings  # noqa: PLC0415

    return safe_settings.dev.is_set


def main() -> None:
    import os  # noqa: PLC0415

    from rich.console import Console  # noqa: PLC0415
    from rich.style import Style  # noqa: PLC0415

    from clive.main import _is_cli_requested  # noqa: PLC0415

    Console().print(
        "-- Running in development mode (NOT FOR DIRECT USAGE!) --",
        style=Style(bgcolor="red", blink=True),
    )

    if _is_cli_requested():  # don't run via textual_dev.run_app when CLI is requested (saves around 1s)
        from clive.__private.settings import get_settings  # noqa: PLC0415
        from clive.main import main as production_main  # noqa: PLC0415

        get_settings().setenv("dev")

        production_main()
        return

    from textual.features import parse_features  # noqa: PLC0415
    from textual_dev.tools.run import run_app  # noqa: PLC0415

    environment = dict(os.environ)

    features = set(parse_features(environment.get("TEXTUAL", "")))
    features.add("debug")
    features.add("devtools")

    environment["TEXTUAL"] = ",".join(sorted(features))
    environment[clive_prefixed_envvar(IS_DEV)] = "1"

    run_app("clive/main.py", [], environment)


if __name__ == "__main__":
    main()
