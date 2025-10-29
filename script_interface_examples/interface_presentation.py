from __private.si.base import clive_use_unlocked_profile


async def interface_presentation() -> str:
    async with clive_use_unlocked_profile() as clive:
        transfer = await clive.process.transfer(
            from_account="alice",
            to_account="gtg",
            amount="1.000 HIVE",
            memo="Test transfer",
        ).autosign().broadcast()

        transfer = await clive.process.transfer(
            from_account="alice",
            to_account="gtg",
            amount="1.000 HIVE",
            memo="Test transfer",
        ).no_sign().broadcast()

        transfer = await clive.process.transfer(
            from_account="alice",
            to_account="gtg",
            amount="1.000 HIVE",
            memo="Test transfer",
        ).sign_with("alice").broadcast()

        transfer = await clive.process.transfer(
            from_account="alice",
            to_account="gtg",
            amount="1.000 HIVE",
            memo="Test transfer",
        ).autosign().save_to(path="transfer1.json", force_save_format="json")

        transfer = await clive.process.transfer(
            from_account="alice",
            to_account="gtg",
            amount="1.000 HIVE",
            memo="Test transfer",
        ).autosign().get_transaction()

        transfer = await clive.process.transfer(
            from_account="alice",
            to_account="gtg",
            amount="1.000 HIVE",
            memo="Test transfer",
        ).autosign().get_transaction()
        transfer2 = await transfer.broadcast()
        transfer3 = await transfer2.save_to("transfer2.json", force_save_format="json")

        transfer4 = await clive.process.transfer(
            from_account="alice",
            to_account="gtg",
            amount="1.000 HIVE",
            memo="Test transfer",
        ).autosign().save_to(path="transfer1.json", force_save_format="json")
        transfer5 = await transfer4.get_transaction()
        transfer6 = await transfer5.broadcast()

        transfer7 = await (
            await (
                await clive.process.transfer(
                    from_account="alice",
                    to_account="gtg",
                    amount="1.000 HIVE",
                    memo="Test transfer",
                )
                .autosign()
                .save_to(path="transfer1.json", force_save_format="json")
            ).get_transaction()
        ).broadcast()

        transaction = await clive.process.transaction(
            from_file="/workspace/clive_workspace/clive/script_interface_examples/transfer.json", already_signed_mode="override"
        ).autosign().broadcast()

        update_authority = await clive.process.update_active_authority(
            account_name="alice",
            threshold=2,
        ).add_account(account_name="bob", weight=1).add_key(key="STM5iuVuYcsZmCzXHJT9VbVvHATPa28cLMrf5zKEkzqKc73e22Jtr", weight=1).no_sign().get_transaction()
