from __future__ import annotations

import asyncio
import traceback

"""
STEPS BEFORE RUNNING THIS SCRIPT:
1. Run clive beekeeper
2. Export env variables in active console
3. Create profile "alice"
4. Unlock profile "alice"
5. Import on alice two keys sets:
"""


"""Example of multi-operation chaining."""
from rich import print

from clive.__private.si.base import CliveSi


async def example_double_transfer():
    """Example 1: Two transfers in one transaction."""
    print("\n=== Example 1: Double Transfer ===")

    async with CliveSi().use_unlocked_profile() as clive:
        double_transfer = (
            await clive.process.transfer(
                from_account="alice",
                to_account="gtg",
                amount="1.000 HIVE",
                memo="Test transfer",
            )
            .process.transfer(
                from_account="alice",
                to_account="bob",
                amount="2.000 HIVE",
                memo="Test transfer2",
            )
            .sign_with(key="alice_key")
            .as_transaction_object()
        )

        print(f"✓ Created transaction with {len(double_transfer.operations)} operations")
        print(f"  Operations: {[op.__class__.__name__ for op in double_transfer.operations]}")


async def example_transaction_with_transfer():
    """Example 2: Transaction with Transfer."""
    print("\n=== Example 2: Transaction + Transfer ===")
    trx_filepath = "/tmp/transfer_autosign.json"

    async with CliveSi().use_unlocked_profile() as clive:
        await (
            clive.process.transfer(
                from_account="alice",
                to_account="gtg",
                amount="1.000 HIVE",
                memo="Test transfer",
            ).save_file(path=trx_filepath)
        )

        combined_ops = (
            await clive.process.transaction(
                from_file=trx_filepath,
                force_unsign=True,
            )
            .process.transfer(
                from_account="alice",
                to_account="alice",
                amount="1.000 HIVE",
                memo="Second transfer",
            )
            .sign_with(key="alice_key")
            .as_transaction_object()
        )

        print(f"✓ Created transaction with {len(combined_ops.operations)} operations")
        print(f"  Operations: {[op.__class__.__name__ for op in combined_ops.operations]}")


async def example_triple_transfer():
    """Example 3: Three transfers in one transaction."""
    print("\n=== Example 3: Triple Transfer ===")

    async with CliveSi().use_unlocked_profile() as clive:
        triple_transfer = (
            await clive.process.transfer(
                from_account="alice",
                to_account="bob",
                amount="1.000 HIVE",
                memo="First transfer",
            )
            .process.transfer(
                from_account="alice",
                to_account="gtg",
                amount="2.000 HIVE",
                memo="Second transfer",
            )
            .process.transfer(
                from_account="alice",
                to_account="charlie",
                amount="3.000 HIVE",
                memo="Third transfer",
            )
            .sign_with(key="alice_key")
            .as_transaction_object()
        )

        print(f"✓ Created transaction with {len(triple_transfer.operations)} operations")
        print(f"  Operations: {[op.__class__.__name__ for op in triple_transfer.operations]}")


async def example_authority_with_transfer():
    """Example 4: Authority update combined with transfer."""
    print("\n=== Example 4: Authority Update + Transfer ===")

    async with CliveSi().use_unlocked_profile() as clive:
        combined = (
            await clive.process.update_active_authority(
                account_name="alice",
                threshold=2,
            )
            .add_key(
                key="STM5tE6iiVkizDrhPU6pAGxFuW38gWJS2Vemue1nYtZ3Zn9zh4Dhn",
                weight=1,
            )
            .process.transfer(
                from_account="alice",
                to_account="bob",
                amount="5.000 HIVE",
                memo="Transfer after authority update",
            )
            .as_transaction_object()
        )

        print(f"✓ Created transaction with {len(combined.operations)} operations")
        print(f"  Operations: {[op.__class__.__name__ for op in combined.operations]}")


async def example_sign_with_and_unsign():
    """Example 5: Sign with and unsign."""
    print("\n=== Example 5: Sign with and unsign ===")

    async with CliveSi().use_unlocked_profile() as clive:
        transfer0 = await clive.process.transfer(
            from_account="alice",
            to_account="gtg",
            amount="1.000 HIVE",
            memo="Test transfer",
        ).as_transaction_object()

        transfer1 = (
            await clive.process.transfer(
                from_account="alice",
                to_account="gtg",
                amount="1.000 HIVE",
                memo="Test transfer",
            )
            .sign_with("alice_key")
            .as_transaction_object()
        )

        print(f"✓ Created transaction: {transfer0} and {transfer1}")


async def example_multisign():
    """Example 6: Multi-signature transaction."""
    print("\n=== Example 6: Multi-signature transaction ===")

    async with CliveSi().use_unlocked_profile() as clive:
        transfer_to_load = (
            await clive.process.transfer(
                from_account="alice",
                to_account="gtg",
                amount="1.000 HIVE",
                memo="Test transfer",
            )
            .sign_with(key="alice_key")
            .as_transaction_object()
        )

        multisigned_transfer = (
            await clive.process.transaction_from_object(
                from_object=transfer_to_load,
                already_signed_mode="multisign",
            )
            .sign_with("STM5P8syqoj7itoDjbtDvCMCb5W3BNJtUjws9v7TDNZKqBLmp3pQW")
            .as_transaction_object()
        )

        print(f"✓ Created transaction: {multisigned_transfer}")


async def example_all_finalizations():
    """Example 7: All finalizations."""
    print("\n=== Example 7: All finalizations ===")
    trx_filepath2 = "/tmp/test_alice.json"

    async with CliveSi().use_unlocked_profile() as clive:
        await (
            clive.process.transfer(
                from_account="alice",
                to_account="mary",
                amount="0.001 HIVE",
                memo="Test transfer",
            )
            .sign_with(key="alice_key")
            .save_file(path=trx_filepath2)
        )

        await (
            clive.process.transfer(
                from_account="alice",
                to_account="mary",
                amount="0.001 HIVE",
                memo="Test transfer",
            )
            .sign_with(key="alice_key")
            .save_file(path=trx_filepath2)
        )
        try:
            await (
                clive.process.transfer(
                    from_account="alice",
                    to_account="mary",
                    amount="0.001 HIVE",
                    memo="Test transfer",
                )
                .sign_with(key="alice_key")
                .broadcast()
            )
        except Exception as e:
            assert (
                "Missing Active Authority aliceTransaction failed to validate using both new (hf26) and legacy serialization'"
                in str(e)
            )
        transfer = (
            await clive.process.transfer(
                from_account="alice",
                to_account="mary",
                amount="0.001 HIVE",
                memo="Test transfer",
            )
            .sign_with(key="alice_key")
            .as_transaction_object()
        )

        print("✓ All finalizations executed.")


async def example_update_active_authority_with_add_and_remove_key():
    """Example 8: Update active authority with add and remove key."""
    print("\n=== Example 8: Update active authority with add and remove key ===")

    async with CliveSi().use_unlocked_profile() as clive:
        update_authority = (
            await clive.process.update_active_authority(account_name="alice", threshold=11)
            .add_account(account_name="bob", weight=12)
            .remove_account(account_name="bob")
            .remove_key(key="STM5P8syqoj7itoDjbtDvCMCb5W3BNJtUjws9v7TDNZKqBLmp3pQW")
            .add_key(key="STM5P8syqoj7itoDjbtDvCMCb5W3BNJtUjws9v7TDNZKqBLmp3pQW", weight=13)
            .sign_with(key="alice_key")
            .as_transaction_object()
        )

        print(f"✓ Created transaction: {update_authority}")


async def example_update_active_authority_autosign():
    """Example 9: Update active authority with autosign."""
    print("\n=== Example 8: Update active authority with autosign ===")

    async with CliveSi().use_unlocked_profile() as clive:
        update_authority = (
            await clive.process.update_active_authority(account_name="alice", threshold=11)
            .add_account(account_name="bob", weight=12)
            .remove_account(account_name="bob")
            .remove_key(key="STM5P8syqoj7itoDjbtDvCMCb5W3BNJtUjws9v7TDNZKqBLmp3pQW")
            .add_key(key="STM5P8syqoj7itoDjbtDvCMCb5W3BNJtUjws9v7TDNZKqBLmp3pQW", weight=13)
            .autosign()
            .as_transaction_object()
        )

        print(f"✓ Created transaction: {update_authority}")


async def example_show_balances():
    """Example 10: Update active authority with autosign."""
    print("\n=== Example 8: Update active authority with autosign ===")

    async with CliveSi().use_unlocked_profile() as clive:
        balances = (
            await clive.show.balances(account_name="alice")
        )

        print(f"✓ Show balances: {balances}")


class Printer:
    def __init__(self) -> None:
        self._ok = []
        self._fail = []
        self._example_number = 1

    def print_ok(self) -> None:
        print(f"[bold green]✓ Example {self._example_number} ok [/bold green]")
        self._ok.append(self._example_number)
        self._example_number += 1

    def print_fail(self, error: Exception) -> None:
        print(f"[bold red]✗ Example {self._example_number} fail\n{error} [/bold red]")
        self._fail.append(self._example_number)
        self._example_number += 1

    def print_summary(self) -> None:
        print(f"[bold yellow]✗ {len(self._ok) + len(self._fail)} examples run [/bold yellow]")
        print(f"[bold green]✓ ok are {self._ok} [/bold green]")
        print(f"[bold red]✗ fail are {self._fail} [/bold red]")



async def main():
    """Run all examples."""
    print("=" * 60)
    print("Multi-Operation Chaining Examples")
    print("=" * 60)

    printer = Printer()
    callables = [
        example_double_transfer,
        example_transaction_with_transfer,
        example_triple_transfer,
        example_authority_with_transfer,
        example_sign_with_and_unsign,
        example_multisign,
        example_all_finalizations,
        example_update_active_authority_with_add_and_remove_key,
        example_update_active_authority_autosign,
        example_show_balances,
    ]
    number = int(input(f"Enter example number (1-{len(callables)}) or 0 for all examples: "))

    for i, callable in enumerate(callables):
        if number == i+1 or number == 0:
            try:
                await callable()
                printer.print_ok()
            except Exception as e:
                traceback.print_exc()
                printer.print_fail(e)

    print("\n" + "=" * 60)
    print("Examples completed!")
    printer.print_summary()
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
