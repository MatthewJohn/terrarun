# Copyright (C) Matt Comben - All Rights Reserved
# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential


class Config:

    @property
    def AUTO_CREATE_WORKSPACES(self):
        return True

    @property
    def SESSION_EXPIRY_MINS(self):
        return 10
