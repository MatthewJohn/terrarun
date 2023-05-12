class TerrarunError(Exception):
    """Base Terrarrun error"""

    pass


class InvalidVersionNumberError(TerrarunError):
    """Tool version number is invalid."""

    pass


class ToolVersionAlreadyExistsError(TerrarunError):
    """Tool version already exists"""

    pass


class ToolUrlPlaceholderError(TerrarunError):
    """Tool URL contains invalid placeholder"""

    pass


class ToolChecksumUrlPlaceholderError(TerrarunError):
    """Tools checksum URL contains invalid placeholder"""

    pass
