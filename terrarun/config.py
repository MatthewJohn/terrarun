# Copyright (C) Matt Comben - All Rights Reserved
# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential


import os


class Config:

    AWS_ENDPOINT = os.environ.get('AWS_ENDPOINT')
    AWS_BUCKET_NAME = os.environ.get('AWS_BUCKET_NAME')
    AGENT_IMAGE_FILENAME = os.environ.get('AGENT_IMAGE_FILENAME')
    AGENT_PRESIGN_ENCRYPTION_KEY = os.environ.get('AGENT_PRESIGN_ENCRYPTION_KEY')

    MODULE_LOG_LEVELS = os.environ.get("MODULE_LOG_LEVELS", "TerraformBinary:debug")
    LOG_LEVEL_DEFAULT = os.environ.get("LOG_LEVEL_DEFAULT", "info")

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

    @property
    def TASK_CALL_MAX_ATTEMPTS(self):
        """Maximum number of attempts to call a remote task url"""
        return 3

    @property
    def TASK_CALL_ATTEMPT_INTERVAL(self):
        """Number of seconds to wait between attempts to call a remote task url"""
        return 10

    @property
    def DATABASE_URL(self):
        """Database URL. Use mysql+mysqlconnector://user:pass@dbhost/dbname for MySQL. Default: sqlite:///test.db."""
        return os.environ.get('DATABASE_URL', 'sqlite:///test.db')

    @property
    def AGENT_JOB_TIMEOUT(self):
        """Agent expiration in seconds"""
        return int(os.environ.get('AGENT_JOB_TIMEOUT', '300'))
