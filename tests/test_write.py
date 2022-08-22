import io
import uuid

from ngi_kof_parser import KOFParser
from ngi_kof_parser import KOFWriter
from ngi_kof_parser.enums import MethodType


class TestWrite:
    def test_write(self):

        # ETRS89/NTM10:
        srid = 5110
        locations = KOFParser().parse("tests/data/test.kof", srid)

        # Add unknow/unhandled tema code (OTHER has non)
        locations[1].methods.append(MethodType.OTHER.name)

        kof_string = KOFWriter().writeKOF(
            project_id=uuid.uuid4(), project_name="cool-name", locations=locations, srid=srid
        )

        assert "\n 01 " in kof_string, "Administration block present"
        assert "\n 05 " in kof_string, "Coordinate block present"
        assert "05 SMPLOC2    2418     1217079.460  112893.150  2.000" in kof_string

        kof_string = KOFWriter().writeKOF(
            project_id=uuid.uuid4(),
            project_name="cool-name",
            locations=locations,
            srid=srid,
            swap_easting_northing=True,
        )
        assert "05 SMPLOC2    2418     112893.150   1217079.460 2.000" in kof_string

    def test_write_all_method_types(self):
        """
        Write all method types to kof file.

        Some (nine) method types does not have a kof code.
        """
        writer = KOFWriter()
        header = (
            " 00 KOF sample file from NGI Field Manager\r\n" " 00 Spatial Reference ID (SRID): 5110 (ETRS89/NTM10)\r\n"
        )
        location_row = " 05 SMPLOC1             112892.810   1217083.640 1.000                \r\n"
        method_row = " 05 SMPLOC2    %s     112893.150   1217079.460 2.000                \r\n"
        method_rows = ""

        for method in MethodType:
            method_rows += method_row % f"{writer.method_type_to_temakode.get(method.value, '2430')[:4]:<4}"
        for method in ["F", "VB", "GVR"]:
            method_rows += method_row % f"{method[:4]:<4}"

        file = io.BytesIO((header + location_row + method_rows).encode())
        locations = KOFParser().parse(file, 5110)

        [location1, location2] = locations
        assert len(location1.methods) == 0
        assert len(location2.methods) == len(MethodType) + 3 - 7
        assert (
            len([method for method in location2.methods if method == "OTHER"]) == 0
        ), "There are seven methods we do not have a tema code for and are therefore mapped to 2430 OTHER"
