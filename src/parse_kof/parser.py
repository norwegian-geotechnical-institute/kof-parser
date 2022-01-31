"""
This is the parser service.
"""
from io import StringIO
from pathlib import Path
from typing import List, Dict, Union
import struct
from operator import itemgetter

from parse_kof import model


#                   2251                                                  *Berg i dagen
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


class KOFParser:
    tema_codes_mapping = {
        "2401": model.MethodTypeEnum.RWS.name,
        "2402": model.MethodTypeEnum.SA.name,
        "2403": model.MethodTypeEnum.TP.name,
        "2405": model.MethodTypeEnum.SS.name,
        "2406": model.MethodTypeEnum.RP.name,
        "2407": model.MethodTypeEnum.CPT.name,
        "2409": model.MethodTypeEnum.RS.name,
        "2410": model.MethodTypeEnum.SR.name,
        "2411": model.MethodTypeEnum.SPT.name,
        "2412": model.MethodTypeEnum.RCD.name,
        "2413": model.MethodTypeEnum.PZ.name,
        "2414": model.MethodTypeEnum.PT.name,
        "2415": model.MethodTypeEnum.SVT.name,
        "2417": model.MethodTypeEnum.INC.name,
        "2418": model.MethodTypeEnum.TOT.name,
    }

    def temakode_to_method(self, temakode: str) -> str:

        if not temakode or temakode not in self.tema_codes_mapping.keys():
            return None

        return self.tema_codes_mapping[temakode]

    def get_struct_unpacker(fieldspecs, istart, iwidth):
        """
        Build the format string for struct.unpack to use, based on the fieldspecs.
        fieldspecs is a list of [name, start, width] arrays.
        Returns a string like "6s2s3s7x7s4x9s".
        """
        unpack_len = 0
        unpack_fmt = ""
        for fieldspec in fieldspecs:
            start = fieldspec[istart] - 1
            end = start + fieldspec[iwidth]
            if start > unpack_len:
                unpack_fmt += str(start - unpack_len) + "x"
            unpack_fmt += str(end - start) + "s"
            unpack_len = end
        struct_unpacker = struct.Struct(unpack_fmt).unpack_from
        return struct_unpacker

    fieldspecs = [
        # Name, Start, Width, Type
        ["ID", 5, 10, str],
        ["TEMAKODE", 16, 8, str],
        ["x", 25, 12, float],
        ["y", 38, 11, float],
        ["z", 50, 8, float],
    ]
    iname, istart, iwidth, itype = 0, 1, 2, 3  # field indexes

    fieldspecs.sort(key=itemgetter(istart))
    struct_unpacker = get_struct_unpacker(fieldspecs, istart, iwidth)
    field_indices = range(len(fieldspecs))

    def parse(self, filepath_or_buffer: Union[str, Path, StringIO], srid:int)-> List[model.Location]:
        if self._is_file_like(filepath_or_buffer):
            f = filepath_or_buffer
            close_file = False
        else:
            # Read file with errors="replace" to catch UnicodeDecodeErrors
            # f = open(filepath_or_buffer, "r", encoding='ASCII', errors="replace")
            f = open(filepath_or_buffer, "rb")
            close_file = True
        try:
            return self.read_kof(f, srid=srid)
        finally:
            if close_file:
                f.close()

    def read_kof(self, file: StringIO, srid: int) -> List[model.Location]:
        locations: Dict[model.Location] = {}
        # data = codecs.getreader("iso-8859-1")(file)
        for line in file.readlines():
            if line[0:3] == b" 05":
                raw_fields = self.struct_unpacker(line)  # split line into field values
                line_data = {}
                for i in self.field_indices:
                    fieldspec = self.fieldspecs[i]
                    fieldname = fieldspec[self.iname]
                    cast = fieldspec[self.itype]
                    value = cast(raw_fields[i].decode().strip())
                    if value == "":
                        line_data[fieldname] = None
                    else:
                        line_data[fieldname] = value

                if line_data["ID"] not in locations.keys():
                    locations[line_data["ID"]] = model.Location(name=line_data["ID"])

                locations[line_data["ID"]].point_easting = line_data["x"]
                locations[line_data["ID"]].point_northing = line_data["y"]
                locations[line_data["ID"]].point_z = line_data["z"]
                locations[line_data["ID"]].srid = srid

                if new_method := self.temakode_to_method(line_data["TEMAKODE"]):
                    locations[line_data["ID"]].methods.append(new_method)

        return [location for name, location in locations.items()]

    @staticmethod
    def _is_file_like(obj):
        """Check if object is file like

        Returns
        -------
        bool
            Return True if obj is file like, otherwise return False
        """

        if not (hasattr(obj, 'read') or hasattr(obj, 'write')):
            return False

        if not hasattr(obj, "__iter__"):
            return False

        return True

