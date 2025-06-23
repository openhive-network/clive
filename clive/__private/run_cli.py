from __future__ import annotations

import asyncio


def run_cli() -> None:
    from clive.__private.before_launch import prepare_before_launch  # noqa: PLC0415
    from clive.__private.cli.main import cli  # noqa: PLC0415

    prepare_before_launch(enable_textual_logger=False)
    asyncio.run(cli())
