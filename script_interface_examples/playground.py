from __future__ import annotations

import asyncio
from functools import partial


from clive.__private.cli.commands.process.process_account_update import ProcessAccountUpdate, add_key, update_authority
from clive.__private.si.base import CliveSi, clive_use_unlocked_profile


async def first_script() -> None:
    async with clive_use_unlocked_profile() as clive:

        add_key_function = partial(add_key, key="STM5iuVuYcsZmCzXHJT9VbVvHATPa28cLMrf5zKEkzqKc73e22Jtr", weight=1)
        update_function = partial(update_authority, attribute="owner", callback=add_key_function)

        operation = ProcessAccountUpdate(force=True, account_name="alice", broadcast=True)
        operation.add_callback(update_function)
        dupa = await operation._run_in_context_manager()
        breakpoint()
        # await operation.run()
        # await operation.fetch_data()
        # print(await operation._create_operation())

if __name__ == "__main__":
    asyncio.run(first_script())
