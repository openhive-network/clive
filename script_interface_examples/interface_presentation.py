from __private.si.base import clive_use_unlocked_profile

"""
1. Usunięcie metody no_sign()
2. Zmiana get_transaction() na as_transaction_object()
3. Dodaj przykład na pakowanie dodatkowych operacji do transakcji
4. Ograniczenie występowania po sobie metod finalizujących (broadcast, save_to, as_transaction_object)
"""

async def interface_presentation() -> str:

    ### Opcje podpisywania
    async with clive_use_unlocked_profile() as clive:
        await clive.process.transfer(
            from_account="alice",
            to_account="gtg",
            amount="1.000 HIVE",
            memo="Test transfer",
        ).autosign().broadcast()

        await clive.process.transfer(
            from_account="alice",
            to_account="gtg",
            amount="1.000 HIVE",
            memo="Test transfer",
        ).broadcast()

        await clive.process.transfer(
            from_account="alice",
            to_account="gtg",
            amount="1.000 HIVE",
            memo="Test transfer",
        ).sign_with("alice").broadcast()

        ### Wszystkie opcje finalizujące
        await clive.process.transfer(
            from_account="alice",
            to_account="gtg",
            amount="1.000 HIVE",
            memo="Test transfer",
        ).autosign().save_to(path="transfer1.json", force_save_format="json")

        await clive.process.transfer(
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
        ).autosign().as_transaction_object()
        transfer2 = await transfer.broadcast()
        transfer3 = await transfer.save_to("transfer2.json", force_save_format="json")

        ### Przykład update_authority
        update_active_authority = (
            await clive.process.update_active_authority(
                account_name="alice",
                threshold=2,
            )
            .add_account(account_name="bob", weight=1)
            .add_key(
                key="STM5iuVuYcsZmCzXHJT9VbVvHATPa28cLMrf5zKEkzqKc73e22Jtr", weight=1
            )
            .as_transaction_object()
        )

        ### Pakowanie dodatkowych operacji do transakcji
        transfer_transaction = (
            await clive.process.transfer(
                from_account="alice",
                to_account="gtg",
                amount="1.000 HIVE",
                memo="Test transfer",
            )
            .sign_with("alice")
            .as_transaction_object()
        )

        transfer_and_update_active_authority = (
            await clive.process.load_transaction(transaction=transfer_transaction)
            .process.update_active_authority(
                account_name="alice",
                threshold=2,
            )
            .autosign()
            .broadcast()
        )

        transfer_and_update_active_authority2 = (
            await clive.process.transfer(
                from_account="alice",
                to_account="gtg",
                amount="1.000 HIVE",
                memo="Test transfer",
            )
            .process.update_active_authority(
                account_name="alice",
                threshold=2,
            )
            .sign_with("alice")
            .broadcast()
        )
