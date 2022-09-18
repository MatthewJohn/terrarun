# Copyright (C) Matt Comben - All Rights Reserved
# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential


import os


class Config:

    @property
    def AUTO_CREATE_WORKSPACES(self):
        return True

    @property
    def SESSION_EXPIRY_MINS(self):
        return 120

    @property
    def BASE_URL(self):
        """
        Base URL of externally accessible URL/domain for Terrarun instance,
        including protocol, domain and port (as necessary).
        E.g. https://my-terrarun-instance:5000
        """
        return os.environ.get('BASE_URL', None)
