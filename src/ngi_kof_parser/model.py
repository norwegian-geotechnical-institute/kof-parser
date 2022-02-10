from enum import Enum
from typing import Optional, List

from pydantic import BaseModel, Field


class LocationBase(BaseModel):
    name: str

    point_easting: Optional[float]
    point_northing: Optional[float]
    point_z: Optional[float] = Field(None, ge=-10000, le=10000)
    srid: Optional[int]

    # point_x_wgs84_pseudo: Optional[float]
    # point_y_wgs84_pseudo: Optional[float]
    # point_x_wgs84_web: Optional[float]
    # point_y_wgs84_web: Optional[float]


class MethodTypeEnum(str, Enum):
    CPT = "CPT"
    TOT = "TOT"
    RP = "RP"
    SA = "SA"
    PZ = "PZ"
    ESA = "ESA"
    SS = "SS"
    RWS = "RWS"
    TP = "TP"
    RS = "RS"
    SR = "SR"
    SPT = "SPT"
    RCD = "RCD"
    PT = "PT"
    SVT = "SVT"
    INC = "INC"


class Location(LocationBase):

    methods: List[Optional[str]] = []
