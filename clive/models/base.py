from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel

from clive.__private.core.communication import CustomJSONEncoder


class CliveBaseModel(BaseModel):
    class Config:
        allow_population_by_field_name = True
        json_encoders = {  # noqa: RUF012; pydantic convention
            datetime: lambda d: d.strftime(CustomJSONEncoder.TIME_FORMAT_WITH_MILLIS)
        }
