
from clive.__private.si.base import CliveSi

async def test_second() -> None:
    clive = CliveSi()
    await clive.setup()
    await clive.create_new_profile("alice")
    clive.world.profile
    balances = await clive.show.balances("alice")
    transfer = await clive.process.transfer(
        from_account="alice",
        to="gtg",
        amount="1.000 HIVE",
        memo="Test transfer",
        broadcast=False,
    )
