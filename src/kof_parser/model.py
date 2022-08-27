from enum import Enum
from typing import Optional, List

from pydantic import BaseModel, Field


class Location(BaseModel):
    name: str = ""
    methods: Optional[List[str]] = []
    point_easting: Optional[float]
    point_northing: Optional[float]
    point_z: Optional[float] = Field(None, ge=-10000, le=10000)
    srid: Optional[int]
