from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Iterable, Literal

import msgspec

from clive.__private.core.constants.date import TIME_FORMAT_WITH_SECONDS
from clive.__private.models.schemas import Serializable
from schemas.decoders import DecoderFactory
from schemas.encoders import enc_hook_base

DictStrAny = dict[str, Any]


class CliveBaseModel(msgspec.Struct):
    class Config:
        allow_population_by_field_name = True
        json_encoders = {
            datetime: lambda d: d.strftime(TIME_FORMAT_WITH_SECONDS),
            Serializable: lambda x: x.serialize(),
        }

    def json(
        self,
        *,
        str_keys: bool = False,
        builtin_types: Iterable[type] | None = None,
        order: Literal[None, "deterministic", "sorted"] = None,
    ) -> DictStrAny:
        return json.dumps(
            msgspec.to_builtins(
                obj=self, enc_hook=enc_hook_base, str_keys=str_keys, builtin_types=builtin_types, order=order
            )
        )

    def dict(
        self,
        *,
        str_keys: bool = False,
        builtin_types: Iterable[type] | None = None,
        order: Literal[None, "deterministic", "sorted"] = None,
    ) -> DictStrAny:
        return msgspec.to_builtins(
            obj=self, enc_hook=enc_hook_base, str_keys=str_keys, builtin_types=builtin_types, order=order
        )

    @classmethod
    def parse_file(cls, path: Path, decoder_factory: DecoderFactory) -> str:
        with open(path, encoding="utf-8") as file:
            raw = file.read()
            return cls.parse_raw(raw, decoder_factory)

    @classmethod
    def parse_raw(cls, raw: str, decoder_factory: DecoderFactory) -> str:
        decoder = decoder_factory(cls)
        return decoder.decode(raw)
