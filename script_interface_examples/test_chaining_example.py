"""Example of multi-operation chaining."""

from __future__ import annotations

import asyncio

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
            .sign_with(key="STM5iuVuYcsZmCzXHJT9VbVvHATPa28cLMrf5zKEkzqKc73e22Jtr")
            .as_transaction_object()
        )

        print(f"✓ Created transaction with {len(double_transfer.operations)} operations")
        print(f"  Operations: {[op.__class__.__name__ for op in double_transfer.operations]}")


async def example_transfer_with_power_up():
    """Example 2: Transfer combined with power up."""
    print("\n=== Example 2: Transfer + Power Up ===")

    async with CliveSi().use_unlocked_profile() as clive:
        try:
            combined_ops = (
                await clive.process.transfer(
                    from_account="alice",
                    to_account="bob",
                    amount="5.000 HIVE",
                    memo="Transfer before power up",
                )
                .process.power_up(
                    from_account="alice",
                    to_account="alice",
                    amount="10.000 HIVE",
                    force=False,
                )
                .sign_with(key="STM5iuVuYcsZmCzXHJT9VbVvHATPa28cLMrf5zKEkzqKc73e22Jtr")
                .as_transaction_object()
            )

            print(f"✓ Created transaction with {len(combined_ops.operations)} operations")
            print(f"  Operations: {[op.__class__.__name__ for op in combined_ops.operations]}")
        except NotImplementedError as e:
            print(f"⚠ Power up not yet implemented: {e}")


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
            .sign_with(key="STM5iuVuYcsZmCzXHJT9VbVvHATPa28cLMrf5zKEkzqKc73e22Jtr")
            .as_transaction_object()
        )

        print(f"✓ Created transaction with {len(triple_transfer.operations)} operations")
        print(f"  Operations: {[op.__class__.__name__ for op in triple_transfer.operations]}")


async def example_authority_with_transfer():
    """Example 4: Authority update combined with transfer."""
    print("\n=== Example 4: Authority Update + Transfer ===")

    async with CliveSi().use_unlocked_profile() as clive:
        try:
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
                .sign_with(key="STM5iuVuYcsZmCzXHJT9VbVvHATPa28cLMrf5zKEkzqKc73e22Jtr")
                .as_transaction_object()
            )

            print(f"✓ Created transaction with {len(combined.operations)} operations")
            print(f"  Operations: {[op.__class__.__name__ for op in combined.operations]}")
        except Exception as e:
            print(f"⚠ Error: {e}")


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
        await example_transfer_with_power_up()
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

    print("\n" + "=" * 60)
    print("Examples completed!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
