"""
Parser KOF exceptions
"""


class KofException(Exception):
    def __init__(self, msg: str):
        self.msg = msg

    @property
    def detail(self):
        return [{"msg": self.msg}]


class ParseError(KofException):
    def __init__(self, msg: str):
        super().__init__(msg)
