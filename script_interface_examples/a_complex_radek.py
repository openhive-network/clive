from __future__ import annotations

import asyncio

"""
STEPS BEFORE RUNNING THIS SCRIPT:
1. Run clive beekeeper
2. Export env variables in active console
3. Create profile "radek"
4. Unlock profile "radek"
"""


"""Example of multi-operation chaining."""
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
            .autosign()
            .as_transaction_object()
        )

        print(f"✓ Created transaction with {len(double_transfer.operations)} operations")
        print(f"  Operations: {[op.__class__.__name__ for op in double_transfer.operations]}")


async def example_transaction_with_transfer():
    """Example 2: Transaction with Transfer."""
    print("\n=== Example 2: Transaction + Transfer ===")

    async with CliveSi().use_unlocked_profile() as clive:
        combined_ops = (
            await clive.process.transaction(
                from_file="/workspace/clive_workspace/clive/script_interface_examples/transfer_autosign.json"
            )
            .process.transfer(
                from_account="alice",
                to_account="alice",
                amount="1.000 HIVE",
                memo="Second transfer",
            )
            .autosign()
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
            .autosign()
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
                key="STM5iuVuYcsZmCzXHJT9VbVvHATPa28cLMrf5zKEkzqKc73e22Jtr",
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


async def example_autosign_and_unsign():
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
            .autosign()
            .as_transaction_object()
        )

        print(f"✓ Created transaction: {transfer0} and {transfer1}")


async def example_all_finalizations():
    """Example 6: All finalizations."""
    print("\n=== Example 6: All finalizations ===")

    async with CliveSi().use_unlocked_profile() as clive:
        await (
            clive.process.transfer(
                from_account="alice",
                to_account="gtg",
                amount="1.000 HIVE",
                memo="Test transfer",
            )
            .autosign()
            .save_file(path="/workspace/clive_workspace/clive/script_interface_examples/test_radek.json")
        )

        await (
            clive.process.transfer(
                from_account="alice",
                to_account="gtg",
                amount="1.000 HIVE",
                memo="Test transfer",
            )
            .autosign()
            .save_file(path="/workspace/clive_workspace/clive/script_interface_examples/test_radek.bin")
        )
        try:
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
        except Exception as e:
            assert (
                "Missing Active Authority aliceTransaction failed to validate using both new (hf26) and legacy serialization'"
                in str(e)
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

        print("✓ All finalizations executed.")


async def example_update_active_authority_with_add_and_remove_key():
    """Example 8: Update active authority with add and remove key."""
    print("\n=== Example 8: Update active authority with add and remove key ===")

    async with CliveSi().use_unlocked_profile() as clive:
        update_authority = (
            await clive.process.update_active_authority(account_name="alice", threshold=11)
            .add_account(account_name="bob", weight=12)
            .add_key(key="STM5iuVuYcsZmCzXHJT9VbVvHATPa28cLMrf5zKEkzqKc73e22Jtr", weight=13)
            .remove_key(key="STM5iuVuYcsZmCzXHJT9VbVvHATPa28cLMrf5zKEkzqKc73e22Jtr")
            .autosign()
            .as_transaction_object()
        )

        print(f"✓ Created transaction: {update_authority}")


async def main():
    """Run all examples."""
    print("=" * 60)
    print("Multi-Operation Chaining Examples")
    print("=" * 60)

    try:
        await example_double_transfer()
    except Exception as e:
        print(f"✗ Example 1 failed: {e}")

    try:
        await example_transaction_with_transfer()
    except Exception as e:
        print(f"✗ Example 2 failed: {e}")

    try:
        await example_triple_transfer()
    except Exception as e:
        print(f"✗ Example 3 failed: {e}")

    try:
        await example_authority_with_transfer()
    except Exception as e:
        print(f"✗ Example 4 failed: {e}")

    try:
        await example_autosign_and_unsign()
    except Exception as e:
        print(f"✗ Example 5 failed: {e}")

    try:
        await example_all_finalizations()
    except Exception as e:
        print(f"✗ Example 6 failed: {e}")

    try:
        await example_update_active_authority_with_add_and_remove_key()
    except Exception as e:
        print(f"✗ Example 7 failed: {e}")

    print("\n" + "=" * 60)
    print("Examples completed!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
