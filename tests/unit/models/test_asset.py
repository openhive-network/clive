from __future__ import annotations

import pytest

from clive.__private.models.asset import Asset, UnknownAssetTypeError


@pytest.mark.parametrize(
    ("symbol", "expected_kind"),
    [
        ("HIVE", Asset.HIVE_KIND),
        ("hbd", Asset.HBD_KIND),
        ("Vests", Asset.VESTS_KIND),
    ],
)
def test_resolve_symbol(symbol: str, expected_kind: Asset.Kind) -> None:
    # ACT
    kind = Asset.resolve_symbol(symbol)

    # ASSERT
    assert kind == expected_kind


def test_resolve_unknown_symbol() -> None:
    # ACT & ASSERT
    with pytest.raises(UnknownAssetTypeError):
        Asset.resolve_symbol("NOTEXISTING")


@pytest.mark.parametrize(
    ("asset", "expected_kind"),
    [
        (Asset.hive(1), Asset.HIVE_KIND),
        (Asset.hbd(1), Asset.HBD_KIND),
        (Asset.vests(1), Asset.VESTS_KIND),
    ],
)
def test_get_kind(asset: Asset.AnyT, expected_kind: Asset.Kind) -> None:
    # ACT
    kind = Asset.get_kind(asset)

    # ASSERT
    assert kind == expected_kind


@pytest.mark.parametrize(
    ("asset", "expected"),
    [
        (Asset.hive(1), (True, False, False)),
        (Asset.hbd(1), (False, True, False)),
        (Asset.vests(1), (False, False, True)),
        (Asset.HIVE_KIND, (True, False, False)),
        (Asset.HBD_KIND, (False, True, False)),
        (Asset.VESTS_KIND, (False, False, True)),
    ],
)
def test_is_kind_of_asset_and_kind(asset: Asset.AnyT | Asset.Kind, expected: tuple[bool, bool, bool]) -> None:
    # ACT
    actual = (Asset.is_hive(asset), Asset.is_hbd(asset), Asset.is_vests(asset))

    # ASSERT
    assert actual == expected


@pytest.mark.parametrize("kind", [Asset.HIVE_KIND, Asset.HBD_KIND])
def test_ensure_liquid_type_accepts_liquid_kind(kind: Asset.Kind) -> None:
    # ACT
    ensured = Asset.ensure_liquid_type(kind)

    # ASSERT
    assert ensured == kind


def test_ensure_liquid_type_rejects_vests() -> None:
    # ACT & ASSERT
    with pytest.raises(AssertionError, match="not liquid type"):
        Asset.ensure_liquid_type(Asset.VESTS_KIND)


@pytest.mark.parametrize("kind", [Asset.HIVE_KIND, Asset.VESTS_KIND])
def test_ensure_voting_type_accepts_voting_kind(kind: Asset.Kind) -> None:
    # ACT
    ensured = Asset.ensure_voting_type(kind)

    # ASSERT
    assert ensured == kind


def test_ensure_voting_type_rejects_hbd() -> None:
    # ACT & ASSERT
    with pytest.raises(AssertionError, match="not voting type"):
        Asset.ensure_voting_type(Asset.HBD_KIND)
