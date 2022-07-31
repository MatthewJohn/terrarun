

class Config:

    @property
    def AUTO_CREATE_ORGANISATIONS(self):
        return True

    @property
    def AUTO_CREATE_WORKSPACES(self):
        return True

    @property
    def SESSION_EXPIRY_MINS(self):
        return 10
