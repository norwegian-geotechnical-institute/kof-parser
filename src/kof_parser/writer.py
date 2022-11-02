from typing import List, Optional
from datetime import datetime
from uuid import UUID

from kof_parser import Kof
from kof_parser import Location
from kof_parser.enums import MethodType
from kof_parser import projector


class KOFWriter(Kof):

    method_type_to_temakode = {
        MethodType.RO.name: "2251",
        MethodType.RWS.name: "2401",
        MethodType.SA.name: "2402",
        MethodType.TP.name: "2403",
        MethodType.SS.name: "2405",
        MethodType.RP.name: "2406",
        MethodType.CPT.name: "2407",
        MethodType.RS.name: "2409",
        MethodType.SR.name: "2410",
        MethodType.SPT.name: "2411",
        MethodType.RCD.name: "2412",
        MethodType.PZ.name: "2413",
        MethodType.PT.name: "2414",
        MethodType.SVT.name: "2415",
        MethodType.INC.name: "2417",
        MethodType.TOT.name: "2418",
    }

    def __init__(self):
        super().__init__()

    def create_admin_block(self, project_name: str, srid: int, swap_easting_northing: Optional[bool] = False) -> str:
        """
        # 00 Oppdrag Dato Ver K.sys Komm $11100000000 Observatør
        # 01 EXP          31012022   2      22 0000 $22100000000           NN
        """
        date = datetime.utcnow().strftime("%d%m%Y")
        version = "1"
        sosi_code = self.get_code(srid=srid) or ""
        municipality = ""
        if swap_easting_northing:
            units = "$21100000000"
        else:
            units = "$11100000000"
        observer = ""

        #             "-01 OOOOOOOOOOOO DDMMYYYY VVV KKKKKKK KKKK $RVAllllllll OOOOOOOOOOOO"
        admin_block = " 00 Oppdrag      Dato     Ver K.sys   Komm $21100000000 Observer    \n"
        admin_block += (
            f" 01 {project_name[:12]:<12} {date[:8]:>8} {version[:3]:>3} {sosi_code:>7} "
            f"{municipality:>4} {units[:12]:<12} {observer[:12]:<12}\n"
        )
        return admin_block

    @staticmethod
    def create_kof_coordinate_block(id: str, temakode: str, x: float, y: float, z: float) -> str:
        coord_block = f" 05 {id[0:10]:<10} {temakode:<8} {y:<12.3f} {x:<11.3f} {z:<8.3f} "
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
        swap_easting_northing: Optional[bool] = False,
    ) -> str:
        """For now, we do not do any transformation of locations positions"""

        kof_string = self.create_kof_header_lines(project_id=project_id, project_name=project_name, srid=srid)
        kof_string += self.create_admin_block(project_name, srid=srid, swap_easting_northing=swap_easting_northing)
        for location in locations:
            location.name = location.name if not None else ""
            z = location.point_z or 0
            x = location.point_easting or 0
            y = location.point_northing or 0
            if x and y and srid and location.srid and srid != location.srid:
                x, y = projector.transform(from_srid=location.srid, to_srid=srid, east=x, north=y)

            if swap_easting_northing:
                x, y = y, x

            if location.methods:
                for method in location.methods:
                    kof_string += self.create_kof_coordinate_block(
                        id=location.name,
                        temakode=self.method_type_to_temakode.get(method, ""),
                        x=x,
                        y=y,
                        z=z,
                    )
            else:
                kof_string += self.create_kof_coordinate_block(
                    id=location.name,
                    temakode="",
                    x=x,
                    y=y,
                    z=z,
                )

        return kof_string
