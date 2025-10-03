from __future__ import annotations

import asyncio

from clive.__private.si.base import CliveSi


async def first_script() -> None:
    async with CliveSi() as clive:
        clive.generate.random_key(1)
        await clive.show.profiles()
        clive.generate.secret_phrase()


if __name__ == "__main__":
    asyncio.run(first_script())
