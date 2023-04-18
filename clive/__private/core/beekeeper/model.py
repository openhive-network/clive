from __future__ import annotations

from typing import TYPE_CHECKING, Any, Generic, TypeVar

from pydantic import BaseModel

if TYPE_CHECKING:
    from datetime import datetime


class BeekeeperResponse(BaseModel):
    pass


class Create(BeekeeperResponse):
    password: str


class CreateKey(BeekeeperResponse):
    public_key: str


class ListKeys(BeekeeperResponse):
    keys: dict[str, str]


class ListWallets(BeekeeperResponse):
    class WalletDetails(BaseModel):
        name: str
        unlocked: bool

    wallets: list[ListWallets.WalletDetails]


class GetPublicKeys(BeekeeperResponse):
    keys: list[str]


class SignDigest(BeekeeperResponse):
    signature: str


class GetInfo(BeekeeperResponse):
    now: datetime
    timeout_time: datetime


T = TypeVar("T", Create, CreateKey, ListWallets, ListKeys, GetPublicKeys, SignDigest, GetInfo, None)


class HiveResponse(BaseModel, Generic[T]):
    id: Any  # noqa: A003
    jsonrpc: str
    result: T
    error: dict[str, Any] | None = None
