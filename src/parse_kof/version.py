from importlib.metadata import metadata

_DISTRIBUTION_METADATA = metadata("parse_kof")
__version__ = _DISTRIBUTION_METADATA["Version"]
