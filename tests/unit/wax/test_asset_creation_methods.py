from __future__ import annotations

from typing import Final, Literal

import pytest

import wax
from tests.unit.wax.consts import ENCODING

INT_32_MIN: Final[int] = -2_147_483_648
INT_32_MAX: Final[int] = 2_147_483_647

INT_64_MIN: Final[int] = -9_223_372_036_854_775_808
INT_64_MAX: Final[int] = 9_223_372_036_854_775_807

ASSET_NAI: Final[dict[str, str]] = {
    "hbd": "@@000000013",
    "hive": "@@000000021",
    "vests": "@@000000037",
}

ASSET_PRECISION: Final[dict[str, int]] = {
    "hbd": 3,
    "hive": 3,
    "vests": 6,
}


def _powers_of_ten(maximum_power: int) -> list[int]:
    return [10**n for n in range(2, maximum_power + 1)]


@pytest.mark.parametrize("asset", ["hbd", "hive", "vests"])
@pytest.mark.parametrize(
    "amount", [INT_64_MIN, INT_32_MIN, -123456, -100, -1, 0, 1, *_powers_of_ten(9), INT_32_MAX, INT_64_MAX]
)
def test_hive(amount: int, asset: Literal["hbd", "hive", "vests"]) -> None:
    # ARRANGE
    expected_precision = ASSET_PRECISION[asset]
    expected_nai = ASSET_NAI[asset]
    wax_function = getattr(wax, asset)

    # ACT
    result = wax_function(amount)

    # ASSERT
    assert result.amount == str(amount).encode()
    assert result.precision == expected_precision
    assert result.nai == expected_nai.encode(ENCODING)


@pytest.mark.parametrize("asset", ["hbd", "hive", "vests"])
def test_general_asset(asset: Literal["hbd", "hive", "vests"]) -> None:
    # ARRANGE
    asset_nums = {
        "hbd": 3200000003,
        "hive": 3200000035,
        "vests": 3200000070,
    }
    amount = 5
    asset_num = asset_nums[asset]
    expected_precision = ASSET_PRECISION[asset]
    expected_nai = ASSET_NAI[asset]

    # ACT
    result = wax.general_asset(asset_num, amount)

    # ASSERT
    assert result.amount == str(amount).encode(ENCODING)
    assert result.precision == expected_precision
    assert result.nai == expected_nai.encode(ENCODING)
