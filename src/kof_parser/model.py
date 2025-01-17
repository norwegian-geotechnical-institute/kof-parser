from pydantic import BaseModel, Field

class Location(BaseModel):
    name: str = ""
    methods: list[str] = Field(default_factory=list)
    point_easting: float| None = None
    point_northing: float| None = None
    point_z: float| None = Field(None, ge=-10000, le=10000)
    srid: int | None = None

    def __repr__(self):
        return f"<{self.__class__.__name__} {self.name} ({self.point_easting}, {self.point_northing}, {self.point_z})>"