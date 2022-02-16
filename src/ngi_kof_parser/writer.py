from typing import List
from datetime import datetime
from uuid import UUID

from ngi_kof_parser.model import Location
from ngi_kof_parser.model import MethodTypeEnum


class KOFWriter:

    method_type_to_temakode = {
        MethodTypeEnum.RWS.name: "2401",
        MethodTypeEnum.SA.name: "2402",
        MethodTypeEnum.TP.name: "2403",
        MethodTypeEnum.SS.name: "2405",
        MethodTypeEnum.RP.name: "2406",
        MethodTypeEnum.CPT.name: "2407",
        MethodTypeEnum.RS.name: "2409",
        MethodTypeEnum.SR.name: "2410",
        MethodTypeEnum.SPT.name: "2411",
        MethodTypeEnum.RCD.name: "2412",
        MethodTypeEnum.PZ.name: "2413",
        MethodTypeEnum.PT.name: "2414",
        MethodTypeEnum.SVT.name: "2415",
        MethodTypeEnum.INC.name: "2417",
        MethodTypeEnum.TOT.name: "2418",
    }

    @staticmethod
    def create_kof_coordinate_block(id: str, temakode: str, x: float, y: float, z: float) -> str:
        coord_block = ""
        coord_block += " "
        coord_block += f"05"
        coord_block += " "
        coord_block += f"{id[0:10]:<10}"
        coord_block += " "
        coord_block += f"{temakode:<8}"
        coord_block += " "
        coord_block += f"{x:<12.3f}"
        coord_block += " "
        coord_block += f"{y:<11.3f}"
        coord_block += " "
        coord_block += f"{z:<8.3f}"
        coord_block += " "
        coord_block = f"{coord_block:<70}"
        coord_block += "\n"
        return coord_block

    @staticmethod
    def create_kof_header_lines(project_id: UUID, project_name, srid: int) -> str:
        header = ""
        header += f" 00 KOF Export from NGI Field Manager"
        header += "\n"
        header += f" 00 Project: {project_id}. Name: {project_name}"
        header += "\n"
        header += f" 00 Spatial Reference ID (SRID): {srid}"
        header += "\n"
        header += f" 00 Export date (UTC): {datetime.utcnow()}"
        header += "\n"

        return header

    def writeKOF(
        self,
        project_id: UUID,
        project_name: str,
        locations: List[Location],
        srid: int,
    ) -> str:
        """For now, we do not do any transformation of locations positions"""

        kof_string = self.create_kof_header_lines(project_id=project_id, project_name=project_name, srid=srid)
        for loc in locations:

            z = loc.point_z or 0
            x = loc.point_easting or 0
            y = loc.point_northing or 0

            if len(loc.methods) > 0:
                for method in loc.methods:
                    kof_string += self.create_kof_coordinate_block(
                        id=loc.name,
                        temakode=self.method_type_to_temakode[method],
                        x=x,
                        y=y,
                        z=z,
                    )
            else:
                kof_string += self.create_kof_coordinate_block(
                    id=loc.name,
                    temakode="",
                    x=x,
                    y=y,
                    z=z,
                )

        return kof_string
