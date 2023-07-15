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


class UnableToDownloadToolArchiveError(TerrarunError):
    """Unable to download tool zip file"""

    pass


class UnableToDownloadToolChecksumFileError(TerrarunError):
    """Unable to download tool checksum file"""

    pass


class LifecycleEnvironmentGroupHasLifecycleEnvironmentsError(TerrarunError):
    """Lifecycle environment group was attempted to be deleted whilst lifecycle environment were associated with it"""

    pass


class OrganisationMixError(TerrarunError):
    """Mixing organisationn in entities is not allowed"""
    
    pass


class RunCannotBeDiscardedError(TerrarunError):
    """Run cannot be discarded as it's in the wrong state"""

    pass


class FailedToUnlockWorkspaceError(TerrarunError):
    """failed to unlocked workspace due to an error"""

    pass
