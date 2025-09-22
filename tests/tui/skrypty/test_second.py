
from clive.__private.si.base import CliveSi

async def test_second() -> None:
    clive = CliveSi()
    await clive.setup()
    await clive.create_new_profile("alice")
    clive.world.profile
    balances = await clive.show.balances("alice")

    pass
# transfer = clive.process.transfer(from_account: str = options.from_account_name,
#     to: str = typer.Option(..., help="The account to transfer to."),
#     amount: str = options.liquid_amount,
#     memo: str = options.memo_value,
#     sign_with: str | None = options.sign_with,
#     broadcast: bool = options.broadcast,  # noqa: FBT001
#     save_file: str | None = options.save_file,)



