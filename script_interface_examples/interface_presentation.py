from __future__ import annotations

from __private.si.base import clive_use_unlocked_profile

"""
1. Usunięcie metody no_sign()
2. Zmiana get_transaction() na as_transaction_object()
3. Dodano przykład na pakowanie dodatkowych operacji do transakcji
4. Dodano przykład na możliwość zrobienia multisignu, wzorowany na mechaniźmie z cli
5. Ograniczenie występowania po sobie method finalizujących (broadcast, save_fie, as_transaction_object)
6. Możliwość łańcuchowego sign()
7. Zmiana działania ładowania transakcji:
    - jeżeli załadowana transakcja jest już podpisana to można ją podpisać kolejnym kluczem (z opcją multisign), nadpisać podpis albo broadcastować z istniejącym podpisem
    - jeżeli załadowana transakcja nie jest podpisana to można ją podpisać jednym lub wieloma kluczami oraz można dodać do niej kolejne operacje przed finalizacją
8. Do opcji "save_file" dodano dwa arguemnty: file_format (json/bin) oraz serialization_mode (hf26/hf25)
"""


async def interface_presentation() -> str:
    async with clive_use_unlocked_profile() as clive:
        ### Opcje podpisywania
        await (
            clive.process.transfer(
                from_account="alice",
                to_account="gtg",
                amount="1.000 HIVE",
                memo="Test transfer",
            )
            .autosign()
            .broadcast()
        )

        await clive.process.transfer(
            from_account="alice",
            to_account="gtg",
            amount="1.000 HIVE",
            memo="Test transfer",
        ).broadcast()

        (
            await clive.process.transfer(
                from_account="alice",
                to_account="gtg",
                amount="1.000 HIVE",
                memo="Test transfer",
            )
            .sign_with("alice_alias")
            .broadcast()
        )

        # Podpisywanie wielokrotne, wzorowane na mechaniźmie, który mamy w "cli"
        await (
            clive.process.transfer(
                from_account="alice",
                to_account="gtg",
                amount="1.000 HIVE",
                memo="Test transfer",
            )
            .sign_with("alice_alias")
            .as_transaction_object()
        )
        await (
            clive.process.transaction_from_object(from_object=transfer_transaction, already_signed_mode="multisign")
            .sign_with("bob_alias")
            .broadcast()
        )

        transfer = await clive.process.transfer(
                from_account="alice",
                to_account="gtg",
                amount="1.000 HIVE",
                memo="Test transfer",
            ).sign_with("alice_alias").sign_with("bob_alias").as_transaction_object()
        

        ### Wszystkie opcje finalizujące
        await (
            clive.process.transfer(
                from_account="alice",
                to_account="gtg",
                amount="1.000 HIVE",
                memo="Test transfer",
            )
            .autosign()
            .save_file(path="transfer1.json", file_format="json", serialization_mode="hf26")
        )

        await (
            clive.process.transfer(
                from_account="alice",
                to_account="gtg",
                amount="1.000 HIVE",
                memo="Test transfer",
            )
            .autosign()
            .broadcast()
        )

        transfer = (
            await clive.process.transfer(
                from_account="alice",
                to_account="gtg",
                amount="1.000 HIVE",
                memo="Test transfer",
            )
            .autosign()
            .as_transaction_object()
        )
        await transfer.broadcast()
        await transfer.save_file("transfer2.json")

        ### Przykład update_authority
        update_active_authority = (
            await clive.process.update_active_authority(
                account_name="alice",
                threshold=2,
            )
            .add_account(account_name="bob", weight=1)
            .add_key(key="STM5iuVuYcsZmCzXHJT9VbVvHATPa28cLMrf5zKEkzqKc73e22Jtr", weight=1)
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
            .sign_with("alice_alias")
            .as_transaction_object()
        )
        await (
            clive.process.transaction_from_object(from_object=transfer_transaction, force_unsign=True)
            .process.update_active_authority(account_name="alice", threshold=2)
            .autosign()
            .broadcast()
        )

        await (
            clive.process.transfer(
                from_account="alice",
                to_account="gtg",
                amount="1.000 HIVE",
                memo="Test transfer",
            )
            .process.update_active_authority(
                account_name="alice",
                threshold=2,
            )
            .sign_with("alice_alias")
            .save_file("transfer_and_update_active_authority2.json")
        )
