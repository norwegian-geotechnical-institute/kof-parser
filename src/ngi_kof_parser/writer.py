from typing import List
from datetime import datetime
from uuid import UUID

from ngi_kof_parser import Kof
from ngi_kof_parser import Location
from ngi_kof_parser import MethodTypeEnum


class KOFWriter(Kof):

    method_type_to_temakode = {
        MethodTypeEnum.RO.name: "2251",
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

    def __init__(self):
        super().__init__()

    def create_admin_block(self, project_name: str, srid: int) -> str:
        """
        # 00 Oppdrag Dato Ver K.sys Komm $11100000000 Observatør
        # 01 EXP          31012022   2      22 0000 $22100000000           NN
        """
        date = datetime.utcnow().strftime("%d%m%Y")
        version = "1"
        code = self.get_code(srid=srid)
        municipality = ""
        units = "$21100000000"
        observer = ""

        #             "-01 OOOOOOOOOOOO DDMMYYYY VVV KKKKKKK KKKK $RVAllllllll OOOOOOOOOOOO"
        admin_block = " 00 Oppdrag      Dato     Ver K.sys   Komm $21100000000 Observer    \n"
        admin_block += (
            f" 01 {project_name[:12]:<12} {date[:8]:>8} {version[:3]:>3} {code:>7} "
            f"{municipality:>4} {units[:12]:<12} {observer[:12]:<12}\n"
        )
        return admin_block

    @staticmethod
    def create_kof_coordinate_block(id: str, temakode: str, x: float, y: float, z: float) -> str:
        coord_block = f" 05 {id[0:10]:<10} {temakode:<8} {x:<12.3f} {y:<11.3f} {z:<8.3f} "
        coord_block = f"{coord_block:<70}\n"
        return coord_block

    @staticmethod
    def create_kof_header_lines(project_id: UUID, project_name, srid: int) -> str:
        header = f" 00 KOF Export from NGI Field Manager\n"
        header += f" 00 Project: {project_id}. Name: {project_name}\n"
        header += f" 00 Spatial Reference ID (SRID): {srid}\n"
        header += f" 00 Export date (UTC): {datetime.utcnow()}\n"

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
        kof_string += self.create_admin_block(project_name, srid=srid)
        for loc in locations:

            z = loc.point_z or 0
            x = loc.point_easting or 0
            y = loc.point_northing or 0

            if len(loc.methods) > 0:
                for method in loc.methods:
                    kof_string += self.create_kof_coordinate_block(
                        id=loc.name,
                        temakode=self.method_type_to_temakode.get(method, ""),
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
