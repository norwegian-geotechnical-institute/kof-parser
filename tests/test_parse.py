import pytest

from kof_parser import KOFParser
from kof_parser.enums import MethodType


class TestParse:
    def test_parse(self):
        parser = KOFParser()
        srid = 5110
        locations = parser.parse("tests/data/test.kof", srid)

        assert len(locations) == 7
        for location in locations:
            assert location.srid

    @pytest.mark.parametrize(
        "file_name, number_of_locations, ex_e, ex_n, ex_z, kof_srid, proj_srid",
        [
            # No transformations
            ("tests/data/UTM32_EN.kof", 1, 594137.802, 6589107.923, 0.000, 25832, 25832),
            ("tests/data/UTM32_NE.kof", 1, 594137.802, 6589107.923, 0.000, 25832, 25832),
            ("tests/data/UTM33_EN.kof", 1, 253851.717, 6595967.833, 0.000, 25833, 25833),
            ("tests/data/UTM33_NE.kof", 1, 253851.717, 6595967.833, 0.000, 25833, 25833),
            # No transformations, read file coordinate system from file
            ("tests/data/UTM32_EN.kof", 1, 594137.802, 6589107.923, 0.000, None, 25832),
            ("tests/data/UTM32_NE.kof", 1, 594137.802, 6589107.923, 0.000, None, 25832),
            ("tests/data/UTM33_EN.kof", 1, 253851.717, 6595967.833, 0.000, None, 25833),
            ("tests/data/UTM33_NE.kof", 1, 253851.717, 6595967.833, 0.000, None, 25833),
            # Actual transformation
            ("tests/data/UTM32_EN.kof", 1, 253851.72, 6595967.83, 0.000, None, 25833),
            ("tests/data/UTM32_NE.kof", 1, 253851.72, 6595967.83, 0.000, None, 25833),
            ("tests/data/UTM33_EN.kof", 1, 594137.802, 6589107.923, 0.000, None, 25832),
            ("tests/data/UTM33_NE.kof", 1, 594137.802, 6589107.923, 0.000, None, 25832),
            # Regression test for failed transformation
            # No transformation since the source data is in ETRS89/UTM 32N SRID 25832 (SOSI coordinate system 22)
            ("tests/data/Innmålt_UTM32.kof", 1, 6644804.528, 595870.665, 50.029, None, 25832),
            ("tests/data/Innmålt_UTM32.kof", 1, 6644804.528, 595870.665, 50.029, 25832, 25832),
            # Transformation from the source data ETRS89/UTM 32N -> UTM 33 (SRID 25833, SOSI 23)
            ("tests/data/Innmålt_UTM32.kof", 1, 5696353.09, 535410.87, 50.029, None, 25833),
            ("tests/data/Innmålt_UTM32.kof", 1, 5696353.09, 535410.87, 50.029, 25832, 25833),
            # Transformation from the source data ETRS89/UTM 32N -> ED50 UTM 31 (SRID 23031, SOSI 31)
            ("tests/data/Innmålt_UTM32.kof", 1, 7712335.00, 680539.85, 50.029, None, 23031),
            ("tests/data/Innmålt_UTM32.kof", 1, 7712335.00, 680539.85, 50.029, 25832, 23031),
            ("tests/data/15-5-18-Fossegata_linux.kof", 6, 6569635.303, 624579.208, 73.838, None, 23031),
            ("tests/data/15-5-18-Fossegata_windows.kof", 6, 6569635.303, 624579.208, 73.838, None, 23031),
        ],
    )
    def test_upload_kof_with_proj_and_meta(self, file_name, number_of_locations, ex_e, ex_n, ex_z, kof_srid, proj_srid):
        """
        Test uploading kof file

        EPSG:23033 ED50 / UTM zone 33N
        EPSG:25833 ETRS89 / UTM zone 33N
        """
        parser = KOFParser()

        locations = parser.parse(file_name, result_srid=proj_srid, file_srid=kof_srid)

        assert len(locations) == number_of_locations

        location = locations[0]
        assert location.point_easting == pytest.approx(ex_e)
        assert location.point_northing == pytest.approx(ex_n)
        assert location.point_z == ex_z
        assert location.srid == proj_srid

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
            assert method == MethodType.TOT.value

        # 05 SMPLOC7    2413     1217069.560  112901.110  0.000
        locaction7_orig_pos_x = 1217069.560
        locaction7_orig_pos_y = 112901.110
        locaction7_orig_pos_z = 0.000

        [location7] = [location for location in locations if location.name == "SMPLOC7"]
        assert location7.point_easting == locaction7_orig_pos_x, "X and Y not swapped"
        assert location7.point_northing == locaction7_orig_pos_y, "X and Y not swapped"
        assert location7.point_z == locaction7_orig_pos_z

        for method in location7.methods:
            assert method == MethodType.PZ.value
