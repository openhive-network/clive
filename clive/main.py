from __future__ import annotations

import asyncio
import sys

from pydantic import Extra

from clive.__private.cli import cli
from clive.__private.cli.completion import is_tab_completion_active
from clive.__private.core._thread import thread_pool
from clive.__private.run_cli import run_cli
from clive.__private.run_tui import run_tui
from schemas.policies import ExtraFields, set_policies


def __disable_schemas_extra_fields_check() -> None:
    set_policies(ExtraFields(policy=Extra.allow))


def __any_arguments_given() -> bool:
    return len(sys.argv) > 1


async def _main() -> None:
    __disable_schemas_extra_fields_check()
    with thread_pool:
        if is_tab_completion_active():
            cli()
            return

        if not __any_arguments_given():
            await run_tui()
            return

        run_cli()


def main() -> None:
    asyncio.run(_main())


if __name__ == "__main__":
    main()
