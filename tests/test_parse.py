from parse_kof import KOFParser


class TestParse:
    def test_parse(self):
        parser = KOFParser()
        srid = 5110
        locations = parser.parse('tests/data/test.kof', srid)

        assert len(locations) == 7
        for location in locations:
            assert location.srid
