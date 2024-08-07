# Copyright (C) 2024 Matt Comben - All Rights Reserved
# SPDX-License-Identifier: GPL-2.0

class TerrarunError(Exception):
    """Base Terrarrun error"""

    pass


class ApiError(TerrarunError):

    def __init__(self, title, details, pointer=None, status=422):
        """Store member variables"""
        self.title = title
        self.details = details
        self.pointer = pointer
        self.status = status

        super(ApiError, self).__init__(details)

    def get_api_details(self):
        """Return API details for error"""
        return {
            "status": str(self.status),
            "title": self.title,
            "detail": self.details,
            "source": {
                "pointer": self.pointer
            } if self.pointer else {}
        }


def api_error_response(api_error):
    return api_error.get_api_details(), api_error._status


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


class RunCannotBeCancelledError(TerrarunError):
    """Run is not in a state that can be cancelled"""

    pass


class CustomTerraformVersionCannotBeUsedError(ApiError):
    """Custom version of Terraform cannot be used"""

    pass


class TerraformVersionNotSetError(ApiError):
    """Terraform version has not been set"""

    pass