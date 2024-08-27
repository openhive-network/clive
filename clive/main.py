from __future__ import annotations

import asyncio
import sys

from pydantic import Extra

from clive.__private.cli.completion import is_tab_completion_active
from clive.__private.cli.main import cli
from clive.__private.core._thread import thread_pool
from clive.__private.models.schemas import ExtraFieldsPolicy, MissingFieldsInGetConfigPolicy, set_policies
from clive.__private.run_cli import run_cli
from clive.__private.run_tui import run_tui


def __disable_schemas_extra_fields_check() -> None:
    set_policies(ExtraFieldsPolicy(policy=Extra.allow), MissingFieldsInGetConfigPolicy(allow=True))


def _is_cli_requested() -> bool:
    return len(sys.argv) > 1


async def _main() -> None:
    with thread_pool:
        if is_tab_completion_active():
            cli()
            return

        __disable_schemas_extra_fields_check()

        if not _is_cli_requested():
            await run_tui()
            return

        run_cli()


def main() -> None:
    asyncio.run(_main())


if __name__ == "__main__":
    main()
