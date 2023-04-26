from __future__ import annotations

from datetime import datetime
from typing import Any, Generic, TypeVar

from pydantic import BaseModel, Field, validator


class BeekeeperResponse(BaseModel):
    pass


class EmptyResponse(BeekeeperResponse):
    pass


class Create(BeekeeperResponse):
    password: str


class CreateKey(BeekeeperResponse):
    public_key: str


class ImportKey(CreateKey):
    pass


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


T = TypeVar("T", Create, CreateKey, ImportKey, ListWallets, ListKeys, GetPublicKeys, SignDigest, GetInfo, EmptyResponse)


class JSONRPCProtocol(BaseModel):
    id_: int | None = Field(0, alias="id")
    jsonrpc: str = "2.0"


class JSONRPCRequest(JSONRPCProtocol):
    method: str
    params: dict[str, Any]


class JSONRPCResponse(JSONRPCProtocol, Generic[T]):
    result: T
