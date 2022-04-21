"""
This is the parser service.
"""
from io import BytesIO
from typing import List, Dict, Optional, Any
import struct
from operator import itemgetter

from ngi_projector import Projector

from ngi_kof_parser import model, Kof

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
        "2251": model.MethodTypeEnum.RO,
        "F": model.MethodTypeEnum.RO,
        "2401": model.MethodTypeEnum.RWS,
        "2402": model.MethodTypeEnum.SA,
        "2403": model.MethodTypeEnum.TP,
        # 2404
        "2405": model.MethodTypeEnum.SS,
        "2406": model.MethodTypeEnum.RP,
        "2407": model.MethodTypeEnum.CPT,
        # 2408
        "2409": model.MethodTypeEnum.RS,
        "2410": model.MethodTypeEnum.SR,
        "2411": model.MethodTypeEnum.SPT,
        "2412": model.MethodTypeEnum.RCD,
        "2413": model.MethodTypeEnum.PZ,
        "GVR": model.MethodTypeEnum.PZ,
        "2414": model.MethodTypeEnum.PT,
        "2415": model.MethodTypeEnum.SVT,
        "VB": model.MethodTypeEnum.SVT,
        # 2416
        "2417": model.MethodTypeEnum.INC,
        "2418": model.MethodTypeEnum.TOT,
        # 2419
        # 2430 has many uses, could be mapped to the OTHER method type?
    }

    def __init__(self):
        super().__init__()
        self.fieldspecs: List[List[Any]] = [
            # Name, Start, Width, Type
            ["ID", 5, 10, str],
            ["TEMAKODE", 16, 8, str],
            ["x", 25, 12, float],
            ["y", 38, 11, float],
            ["z", 50, 8, float],
        ]
        self.admin_block_specification: List[List[Any]] = [
            # Name, Start, Width, Type
            ["OPPDRAG", 5, 12, str],
            ["DATO", 18, 8, str],
            ["VERSJON", 27, 3, int],
            ["KOORDSYS", 31, 7, str],
            ["KOMMUNE", 39, 4, str],
            ["ENHET", 44, 12, str],
            ["OBERVATOR", 57, 12, str],
        ]
        self.iname, self.istart, self.iwidth, self.itype = 0, 1, 2, 3  # field indexes
        self.fieldspecs.sort(key=itemgetter(self.istart))
        self.field_indices = range(len(self.fieldspecs))
        self.struct_unpacker = self.get_struct_unpacker(self.fieldspecs, self.istart, self.iwidth)
        self.adminblock_unpacker = self.get_struct_unpacker(self.admin_block_specification, self.istart, self.iwidth)
        self.field_adminblock_indices = range(len(self.admin_block_specification))
        self.useEastNorthOrderAsDefault = True
        self.file_srid: Optional[int] = None

    def tema_code_to_method(self, code: str) -> Optional[str]:

        if not code or code not in self.tema_codes_mapping.keys():
            return None

        return self.tema_codes_mapping[code].name

    @staticmethod
    def get_struct_unpacker(field_specification, index_start, index_width):
        """
        Build the format string for struct.unpack to use, based on the fieldspecs.
        fieldspecs is a list of [name, start, width] arrays.
        Returns a string like "6s2s3s7x7s4x9s".
        """
        unpack_len = 0
        unpack_fmt = ""
        for field_specification in field_specification:
            start = field_specification[index_start] - 1
            end = start + field_specification[index_width]
            if start > unpack_len:
                unpack_fmt += str(start - unpack_len) + "x"
            unpack_fmt += str(end - start) + "s"
            unpack_len = end
        struct_unpacker = struct.Struct(unpack_fmt).unpack_from
        return struct_unpacker

    def parse(
        self,
        filepath_or_buffer: Any,
        result_srid: int,
        file_srid: Optional[int] = None,
        swap_easting_northing: Optional[bool] = False,
    ) -> List[model.Location]:
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
    ) -> List[model.Location]:
        locations: Dict[str, model.Location] = {}
        if file_srid:
            self.file_srid = file_srid
        else:
            self.file_srid = result_srid

        for line in file.readlines():
            if line[0:3] == b" 05":
                raw_fields = self.struct_unpacker(line)  # split line into field values
                line_data = self.extract_line(raw_fields, self.fieldspecs, self.field_indices)

                if line_data["ID"] not in locations.keys():
                    locations[line_data["ID"]] = model.Location(name=line_data["ID"])

                if not self.useEastNorthOrderAsDefault:
                    line_data["x"], line_data["y"] = line_data["y"], line_data["x"]

                if swap_easting_northing:
                    line_data["x"], line_data["y"] = line_data["y"], line_data["x"]

                if self.file_srid and result_srid != self.file_srid:
                    line_data["x"], line_data["y"] = projector.transform(
                        self.file_srid, result_srid, line_data["x"], line_data["y"]
                    )

                locations[line_data["ID"]].point_easting = line_data["x"]
                locations[line_data["ID"]].point_northing = line_data["y"]
                locations[line_data["ID"]].point_z = line_data["z"]
                locations[line_data["ID"]].srid = result_srid

                if new_method := self.tema_code_to_method(line_data["TEMAKODE"]):
                    locations[line_data["ID"]].methods.append(new_method)
            elif line[0:3] == b" 01":
                raw_fields = self.adminblock_unpacker(line)  # split line into field values
                line_data = self.extract_line(raw_fields, self.admin_block_specification, self.field_adminblock_indices)
                code = line_data["KOORDSYS"]
                if code and not file_srid:
                    self.file_srid = self.get_srid(int(code))

                enhet = line_data["ENHET"]
                if enhet:
                    dirSpec = enhet[1:2]
                    if dirSpec == "1":
                        self.useEastNorthOrderAsDefault = False
                    elif dirSpec == "2":
                        self.useEastNorthOrderAsDefault = True

        return [location for name, location in locations.items()]

    def extract_line(self, raw_fields, fieldspecs, indices) -> Dict[str, Any]:
        line_data: dict[str, Any] = {}
        for i in indices:
            fieldspec = fieldspecs[i]
            fieldname = fieldspec[self.iname]
            cast = fieldspec[self.itype]
            value = cast(raw_fields[i].decode().strip())
            if value == "":
                line_data[fieldname] = None
            else:
                line_data[fieldname] = value

        return line_data

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
