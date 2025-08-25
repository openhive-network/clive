from __future__ import annotations

import asyncio
import sys

from clive.__private.core.constants.cli import HELP_FLAGS


def _should_show_help() -> bool:
    return bool(set(sys.argv) & set(HELP_FLAGS))


def run_cli() -> None:
    from clive.__private.cli.main import cli  # noqa: PLC0415

    if not _should_show_help():
        from clive.__private.before_launch import prepare_before_launch  # noqa: PLC0415
        from clive.__private.cli.error_handlers import register_error_handlers  # noqa: PLC0415

        prepare_before_launch(enable_textual_logger=False)
        register_error_handlers(cli)
    asyncio.run(cli())
