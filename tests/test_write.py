import uuid

from ngi_kof_parser import KOFParser
from ngi_kof_parser import KOFWriter


class TestWrite:
    def test_write(self):

        # ETRS89/NTM10:
        srid = 5110
        locations = KOFParser().parse("tests/data/test.kof", srid)

        kof_string = KOFWriter().writeKOF(
            project_id=uuid.uuid4(), project_name="cool-name", locations=locations, srid=srid
        )

        assert "\n 01 " in kof_string, "Administration block present"
        assert "\n 05 " in kof_string, "Coordinate block present"
        assert "05 SMPLOC2    2418     112893.150   1217079.460 2.000" in kof_string
