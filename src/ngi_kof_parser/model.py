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
    SS = "SS"
    RWS = "RWS"
    RCD = "RCD"
    RS = "RS"
    SVT = "SVT"
    SPT = "SPT"
    CD = "CD"
    TP = "TP"
    PT = "PT"
    ESA = "ESA"
    EP = "EP"
    AD = "AD"
    RO = "RO"
    INC = "INC"
    SR = "SR"
    IW = "IW"
    DT = "DT"
    OTHER = "OTHER"


class Location(LocationBase):

    methods: List[str] = []
