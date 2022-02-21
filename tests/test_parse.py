import pytest

from ngi_kof_parser import KOFParser
from ngi_kof_parser import MethodTypeEnum


class TestParse:
    def test_parse(self):
        parser = KOFParser()
        srid = 5110
        locations = parser.parse("tests/data/test.kof", srid)

        assert len(locations) == 7
        for location in locations:
            assert location.srid

    @pytest.mark.parametrize(
        "file_name, ex_e, ex_n, ex_z,kof_srid,proj_srid",
        [
            ("tests/data/UTM32_EN.kof", 594137.802, 6589107.923, 0.000, 25832, 25832),
            ("tests/data/UTM32_NE.kof", 594137.802, 6589107.923, 0.000, 25832, 25832),
            ("tests/data/UTM33_EN.kof", 253851.717, 6595967.833, 0.000, 23033, 23033),
            ("tests/data/UTM33_NE.kof", 253851.717, 6595967.833, 0.000, 23033, 23033),
        ],
    )
    def test_upload_kof_with_proj_and_meta(self, file_name, ex_e, ex_n, ex_z, kof_srid, proj_srid):
        """
        Test uploading kof file
        """
        parser = KOFParser()

        assert kof_srid == proj_srid, "For now, the parser does not project any positions"

        locations = parser.parse(file_name, proj_srid, kof_srid)

        assert len(locations) == 1

        [location] = locations
        assert location.point_easting == ex_e, "X and Y not swapped"
        assert location.point_northing == ex_n, "X and Y not swapped"
        assert location.point_z == ex_z
        assert location.srid == proj_srid

        # Until we handle transformations, we expect an Exception here:
        new_srid = 23032
        with pytest.raises(Exception):
            parser.parse(file_name, new_srid)

    @pytest.mark.parametrize("file", ["tests/data/import_template.kof", open("tests/data/import_template.kof", "rb")])
    def test_upload_kof(self, file):
        """
        Test uploading kof file
        """
        srid = 5110  # (ETRS89/NTM10)

        parser = KOFParser()

        locations = parser.parse(file, srid)

        location2_orig_pos_x = 112893.150
        location2_orig_pos_y = 1217079.460
        location2_orig_pos_z = 2.000

        assert len(locations) == 7

        # 05 SMPLOC2    2418     112893.150   1217079.460 2.000
        [location2] = [location for location in locations if location.name == "SMPLOC2"]
        assert location2.point_easting == location2_orig_pos_x, "X and Y not swapped"
        assert location2.point_northing == location2_orig_pos_y, "X and Y not swapped"
        assert location2.point_z == location2_orig_pos_z
        for method in location2.methods:
            assert method == MethodTypeEnum.TOT

        # 05 SMPLOC7    2413     1217069.560  112901.110  0.000
        locaction7_orig_pos_x = 1217069.560
        locaction7_orig_pos_y = 112901.110
        locaction7_orig_pos_z = 0.000

        [location7] = [location for location in locations if location.name == "SMPLOC7"]
        assert location7.point_easting == locaction7_orig_pos_x, "X and Y not swapped"
        assert location7.point_northing == locaction7_orig_pos_y, "X and Y not swapped"
        assert location7.point_z == locaction7_orig_pos_z

        for method in location7.methods:
            assert method == MethodTypeEnum.PZ

    @pytest.mark.parametrize(
        "file, expected_exception",
        [
            ("tests/data/15-5-18-Fossegata_linux.kof", ValueError),
            ("tests/data/15-5-18-Fossegata_windows.kof", UnicodeDecodeError),
        ],
    )
    def test_upload_kof_wrong_encoding(self, file, expected_exception):
        """
        Test uploading kof with wrong encoding. Kof only support ASCII (7 bits) for now.
        """
        # TODO: Should make the kof parser more resilient to other character sets than 7 bits ASCII
        srid = 5110  # (ETRS89/NTM10) not knowing that this is correct, but don't care for now

        parser = KOFParser()
        with pytest.raises(expected_exception):
            parser.parse(file, srid)
