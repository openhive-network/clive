from __future__ import annotations

from datetime import datetime
from typing import Any, Generic, TypeVar

from pydantic import BaseModel, validator


class EmptyResponse(BaseModel):
    pass


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

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat(),
        }

    @validator("now", "timeout_time", pre=True)
    @classmethod
    def time_validate(cls, v: str) -> datetime:
        return datetime.fromisoformat(v)


T = TypeVar("T", Create, CreateKey, ListWallets, ListKeys, GetPublicKeys, SignDigest, GetInfo, EmptyResponse)


class HiveResponse(BaseModel, Generic[T]):
    id: Any  # noqa: A003
    jsonrpc: str
    result: T
