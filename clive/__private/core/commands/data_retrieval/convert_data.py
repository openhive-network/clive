from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Final

import beekeepy.exceptions as bke

from clive.__private.core.commands.abc.command_data_retrieval import CommandDataRetrieval
from clive.exceptions import RequestIdError

if TYPE_CHECKING:
    from datetime import datetime

    from clive.__private.core.node import Node
    from clive.__private.models.schemas import AssetHbd, AssetHive
    from schemas.apis.database_api import FindCollateralizedConversionRequests, FindHbdConversionRequests
    from schemas.apis.database_api.fundaments_of_reponses import (
        FindCollateralizedConversionRequestsFundament,
        HbdConversionRequestsFundament,
    )


@dataclass
class HarvestedDataRaw:
    hbd_conversion_requests: FindHbdConversionRequests | None = None
    collateralized_conversion_requests: FindCollateralizedConversionRequests | None = None


@dataclass
class SanitizedData:
    hbd_conversion_requests: list[HbdConversionRequestsFundament]
    collateralized_conversion_requests: list[FindCollateralizedConversionRequestsFundament]


@dataclass
class HbdConversionRequest:
    """HBD → HIVE conversion request (standard conversion)."""

    request_id: int
    amount: AssetHbd
    conversion_date: datetime


@dataclass
class CollateralizedConversionRequest:
    """HIVE → HBD conversion request (collateralized conversion)."""

    request_id: int
    collateral_amount: AssetHive
    converted_amount: AssetHbd
    conversion_date: datetime


@dataclass
class ConvertData:
    """Data about pending conversions for an account."""

    hbd_conversions: list[HbdConversionRequest]
    """HBD → HIVE conversions (standard)."""

    collateralized_conversions: list[CollateralizedConversionRequest]
    """HIVE → HBD conversions (collateralized)."""

    def create_request_id(self) -> int:
        """
        Calculate the next available request id for convert operations.

        Both convert and collateralized_convert operations share the same request_id namespace per account.

        Raises:
            RequestIdError: If the maximum number of request ids is exceeded.

        Returns:
            The next available request id.
        """
        max_number_of_request_ids: Final[int] = 100

        all_request_ids = [req.request_id for req in self.hbd_conversions] + [
            req.request_id for req in self.collateralized_conversions
        ]

        if not all_request_ids:
            return 0

        if len(all_request_ids) >= max_number_of_request_ids:
            raise RequestIdError("Maximum quantity of request ids is 100")

        last_occupied_id = max(all_request_ids)
        return last_occupied_id + 1


@dataclass(kw_only=True)
class ConvertDataRetrieval(CommandDataRetrieval[HarvestedDataRaw, SanitizedData, ConvertData]):
    node: Node
    account_name: str

    async def _harvest_data_from_api(self) -> HarvestedDataRaw:
        async with await self.node.batch() as node:
            return HarvestedDataRaw(
                await node.api.database_api.find_hbd_conversion_requests(account=self.account_name),
                await node.api.database_api.find_collateralized_conversion_requests(account=self.account_name),
            )
        raise bke.UnknownDecisionPathError(f"{self.__class__.__name__}:_harvest_data_from_api")

    async def _sanitize_data(self, data: HarvestedDataRaw) -> SanitizedData:
        return SanitizedData(
            hbd_conversion_requests=self.__assert_hbd_conversion_requests(data.hbd_conversion_requests),
            collateralized_conversion_requests=self.__assert_collateralized_conversion_requests(
                data.collateralized_conversion_requests
            ),
        )

    async def _process_data(self, data: SanitizedData) -> ConvertData:
        hbd_conversions = [
            HbdConversionRequest(
                request_id=req.requestid,
                amount=req.amount,
                conversion_date=req.conversion_date,
            )
            for req in data.hbd_conversion_requests
        ]

        collateralized_conversions = [
            CollateralizedConversionRequest(
                request_id=req.requestid,
                collateral_amount=req.collateral_amount,
                converted_amount=req.converted_amount,
                conversion_date=req.conversion_date,
            )
            for req in data.collateralized_conversion_requests
        ]

        return ConvertData(
            hbd_conversions=hbd_conversions,
            collateralized_conversions=collateralized_conversions,
        )

    def __assert_hbd_conversion_requests(
        self, data: FindHbdConversionRequests | None
    ) -> list[HbdConversionRequestsFundament]:
        assert data is not None, "FindHbdConversionRequests data is missing"
        return list(data.requests)

    def __assert_collateralized_conversion_requests(
        self, data: FindCollateralizedConversionRequests | None
    ) -> list[FindCollateralizedConversionRequestsFundament]:
        assert data is not None, "FindCollateralizedConversionRequests data is missing"
        return list(data.requests)
