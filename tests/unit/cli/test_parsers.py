from __future__ import annotations

import pytest
import typer

from clive.__private.cli.common.parsers import account_name, hbd_asset, liquid_asset, voting_asset
from clive.__private.core.constants.cli import PERFORM_WORKING_ACCOUNT_LOAD
from clive.__private.models.asset import Asset


@pytest.mark.parametrize(
    "raw",
    [
        "alice",
        "alice123",
        "alice.bob",
        "alice-bob",
        PERFORM_WORKING_ACCOUNT_LOAD,
    ],
)
def test_account_name_valid(raw: str) -> None:
    assert account_name(raw) == raw


@pytest.mark.parametrize(
    "raw",
    [
        "ab",
        "a" * 17,
        "Alice",
        "1alice",
        "alice@bob",
    ],
)
def test_account_name_invalid(raw: str) -> None:
    with pytest.raises(typer.BadParameter):
        account_name(raw)


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("1.000 HIVE", Asset.hive(1)),
        ("2.500 hbd", Asset.hbd("2.5")),
    ],
)
def test_liquid_asset_valid(raw: str, expected: Asset.LiquidT) -> None:
    # ACT
    parsed = liquid_asset(raw)

    # ASSERT
    assert parsed == expected
    assert Asset.get_kind(parsed) == Asset.get_kind(expected)


@pytest.mark.parametrize(
    ("raw", "expected_message"),
    [
        ("1.000000 VESTS", "Only ['HIVE', 'HBD'] are allowed."),
        ("1.000 NOTEXISTING", "Unknown asset type: 'NOTEXISTING'. Only ['HIVE', 'HBD'] are allowed."),
        ("1.0000 HIVE", "Invalid asset amount format: '1.0000'."),
    ],
)
def test_liquid_asset_invalid(raw: str, expected_message: str) -> None:
    # ACT & ASSERT
    with pytest.raises(typer.BadParameter) as error:
        liquid_asset(raw)

    assert expected_message in str(error.value)


def test_voting_asset_accepts_hive_power() -> None:
    # ACT
    parsed = voting_asset("1.000 HP")

    # ASSERT
    assert parsed == Asset.hive(1)


def test_hbd_asset_rejects_hive() -> None:
    # ACT & ASSERT
    with pytest.raises(typer.BadParameter, match=r"Only \['HBD'\] are allowed."):
        hbd_asset("1.000 HIVE")
