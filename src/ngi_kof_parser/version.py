from importlib.metadata import metadata

_DISTRIBUTION_METADATA = metadata("ngi_kof_parser")
__version__ = _DISTRIBUTION_METADATA["Version"]
