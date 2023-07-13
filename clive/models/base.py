from __future__ import annotations

from pydantic import BaseModel


class CliveBaseModel(BaseModel):
    class Config:
        allow_population_by_field_name = True
