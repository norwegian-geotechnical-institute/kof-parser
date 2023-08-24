"""
This is the parser service.
"""
from io import BytesIO, TextIOWrapper
from typing import Optional, Any

from charset_normalizer import detect
from coordinate_projector import Projector

from kof_parser import Kof
from kof_parser.exceptions import ParseError
from kof_parser.model import Location
from kof_parser.enums import MethodType

projector = Projector()

#                   2251                                                  *Berg i dagen (RO/F)
# //  05 TEST1      2401            0.000       0.000    0.000            *dreiesondering RWS
# //  05 TEST10     2402            0.000       0.000    0.000            *prøvetaking    SA
#                   2403                                                  *prøvegrop TP
# //  05 TEST3      2405            0.000       0.000    0.000            *enkelsondering SS
# //  05 TEST2      2406            0.000       0.000    0.000            *dreietrykksondering RP
# //  05 TEST7      2407            0.000       0.000    0.000            *trykksondering CPT
# //  05 TEST4      2409            0.000       0.000    0.000            *rammsonderin   RS
#                   2410                                                  *Settlement recording / Setningsmåling, setningsbolt SR
#                   2411                                                  *standard penetration test SPT
# //  05 TEST6      2412            0.000       0.000    0.000            *fjellkontrollboring (RCD)
# //  05 TEST12     2413            0.000       0.000    0.000            *grunnvannsrør (samme kode og symbol som piezometer)
# //  05 TEST13     2413            0.000       0.000    0.000            *piezometer
# //  05 TEST14     2413            0.000       0.000    0.000            *steningsmåling (vet ikke hvorfor det har samme kode som PZ)
#                   2414                                                  *Permeability test (In-situ permeabilitetsmåling) PT
# //  05 TEST15     2415            0.000       0.000    0.000            *Vingeboring    SVT
#                   2417                                                  *Inclinometer (Helningsmåling, inklinometer) INC
# //  05 TEST5      2418            0.000       0.000    0.000            *totalsondering TOT
# //  05 TEST8      2430            0.000       0.000    0.000            *kjerneboring
# //  05 TEST9      2430            0.000       0.000    0.000            *vanntapsmåling
# //  05 TEST11     2430            0.000       0.000    0.000            *miljøprøvetaking


class KOFParser(Kof):
    tema_codes_mapping = {
        "2251": MethodType.RO,
        "F": MethodType.RO,
        "2401": MethodType.RWS,
        "2402": MethodType.SA,
        "2403": MethodType.TP,
        # 2404
        "2405": MethodType.SS,
        "2406": MethodType.RP,
        "2407": MethodType.CPT,
        # 2408
        "2409": MethodType.RS,
        "2410": MethodType.SR,
        "2411": MethodType.SPT,
        "2412": MethodType.RCD,
        "2413": MethodType.PZ,
        "GVR": MethodType.PZ,
        "2414": MethodType.PT,
        "2415": MethodType.SVT,
        "VB": MethodType.SVT,
        # 2416
        "2417": MethodType.INC,
        "2418": MethodType.TOT,
        # 2419
        # 2430 has many uses, could be mapped to the OTHER method type?
    }

    def __init__(self):
        super().__init__()
        self.use_east_north_order_as_default = True
        self.file_srid: Optional[int] = None

    def tema_code_to_method(self, code: str) -> Optional[str]:
        if not code or code not in self.tema_codes_mapping.keys():
            return None

        return self.tema_codes_mapping[code].name

    def map_line_to_coordinate_block(self, line: str, result_srid: int) -> Location:
        # template_coordinate_block: str = "-05 PPPPPPPPPP KKKKKKKK XXXXXXXX.XXX YYYYYYY.YYY ZZZZ.ZZZ Bk MMMMMMM"

        resolved_location = Location(
            name=line[4:15].strip(),
            srid=result_srid,
            point_easting=float(line[24:37]) if line[24:37].strip() else None,
            point_northing=float(line[37:49]) if line[37:49].strip() else None,
            point_z=float(line[49:58]) if line[49:58].strip() else None,
        )
        if new_method := self.tema_code_to_method(line[15:24].strip()):
            resolved_location.methods.append(new_method)

        return resolved_location

    def map_line_to_administrative_block(self, line: str, file_srid: Optional[int]) -> None:
        # template_admin_block: str = "-01 OOOOOOOOOOOO DDMMYYYY VVV KKKKKKK KKKK $RVAllllllll OOOOOOOOOOOO"
        coordinate_system = line[30:38].strip()
        if coordinate_system and not file_srid:
            self.file_srid = self.get_srid(int(coordinate_system))
        units = line[43:56]
        if units:
            dir_spec = units[1:2]
            if dir_spec == "1":
                self.use_east_north_order_as_default = False
            elif dir_spec == "2":
                self.use_east_north_order_as_default = True

    def parse(
        self,
        filepath_or_buffer: Any,
        result_srid: int,
        file_srid: Optional[int] = None,
        swap_easting_northing: Optional[bool] = False,
    ) -> list[Location]:
        """
        Parse passed kof file. Resulting locations are returned in the `result_srid` coordinate system.

        The file may or may not contain a specification of what coordinate system its coordinates are in.

        If `file_srid` is passed in, it specifies what coordinate system the file's coordinates are in.
        The `file_srid` parameter will override any coordinate system that is specified in the file. If `file_srid`
        is not passed or is `None`, then the coordinate system specified in the KOF file is used. If neither
        `file_srid` nor any coordinate system is specified in the KOF file, then the coordinate system is assumed to be
        in the `result_srid` coordinate system and no transformations are done.

        If the swap_easting_northing parameter is set to True, then the easting and northing values are swapped before
        any transformation is done.
        """
        if self._is_file_like(filepath_or_buffer):
            f = filepath_or_buffer
            close_file = False
        else:
            f = open(filepath_or_buffer, "rb")
            close_file = True
        try:
            return self._read_kof(
                f, result_srid=result_srid, file_srid=file_srid, swap_easting_northing=swap_easting_northing
            )
        finally:
            if close_file:
                f.close()

    def _read_kof(
        self, file: BytesIO, result_srid: int, file_srid: Optional[int], swap_easting_northing: Optional[bool] = False
    ) -> list[Location]:
        resolved_locations: list[Location] = []
        if file_srid:
            self.file_srid = file_srid
        else:
            self.file_srid = result_srid

        self.encoding = self.detect_char_set_from_file(file)
        wrapper = TextIOWrapper(file, encoding=self.encoding)

        for line_number, line in enumerate(wrapper.readlines(), start=1):
            try:
                if line.startswith(" 01 "):
                    self.map_line_to_administrative_block(line, file_srid)

                elif line.startswith(" 05 "):
                    location = self.map_line_to_coordinate_block(line, result_srid)

                    if not self.use_east_north_order_as_default or swap_easting_northing:
                        location.point_easting, location.point_northing = (
                            location.point_northing,
                            location.point_easting,
                        )

                    if self.file_srid and result_srid != self.file_srid:
                        if location.point_easting and location.point_northing:
                            location.point_easting, location.point_northing = projector.transform(
                                self.file_srid, result_srid, location.point_easting, location.point_northing
                            )

                    if len(resolved_locations) > 0:
                        existing_locations = list(
                            filter(lambda existing: location.name == existing.name, resolved_locations)
                        )
                        if len(existing_locations) > 0:
                            existing_location = next(
                                existing_location
                                for existing_location in existing_locations
                                if existing_location.name == location.name
                            )
                            if existing_location is not None:
                                if existing_location.methods is None:
                                    existing_location.methods = []
                                existing_location.methods += location.methods if location.methods is not None else []
                                existing_location.point_easting = location.point_easting
                                existing_location.point_northing = location.point_northing
                                existing_location.point_z = location.point_z
                        else:
                            resolved_locations.append(location)
                    else:
                        resolved_locations.append(location)
            except Exception as e:
                raise ParseError(f"Error parsing KOF file on line {line_number} - {e}")

        return resolved_locations

    def detect_char_set_from_file(
        self, file: BytesIO, default_char_set: str = "iso-8859-15", confidence: float = 0.70
    ) -> str:
        sample = file.read()
        detection = detect(sample)
        detected_confidence = detection.get("confidence", 0.0)
        if not isinstance(detected_confidence, float) or detected_confidence < confidence:
            encoding = default_char_set
        else:
            encoding = detection["encoding"] if isinstance(detection["encoding"], str) else default_char_set
        file.seek(0)
        if encoding == "ASCII":
            # Since iso-8859-15 is a superset of ascii, just return that, even if ascii was detected
            return "iso-8859-15"

        return encoding

    @staticmethod
    def _is_file_like(obj) -> bool:
        """Check if object is file like

        Returns
        -------
        bool
            Return True if obj is file like, otherwise return False
        """

        if not (hasattr(obj, "read") or hasattr(obj, "write")):
            return False

        if not hasattr(obj, "__iter__"):
            return False

        return True
