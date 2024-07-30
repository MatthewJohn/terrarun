# Copyright (C) 2024 Matt Comben - All Rights Reserved
# SPDX-License-Identifier: GPL-2.0


import base64
import json

from cryptography.fernet import Fernet
from werkzeug.wrappers.request import Request

import terrarun.config
from terrarun.models.user import User


class Presign:
    """Interface to encrypt/decrypt pre-sign keys"""

    @property
    def fernet(self):
        """Obtain instance of farnet"""
        if not terrarun.config.Config().AGENT_PRESIGN_ENCRYPTION_KEY:
            raise Exception('AGENT_PRESIGN_ENCRYPTION_KEY must be set')
        return Fernet(base64.b64encode(terrarun.config.Config().AGENT_PRESIGN_ENCRYPTION_KEY.encode('utf-8')))

    def encrypt(self, input):
        """Encrypt token"""
        return self.fernet.encrypt(input.encode()).hex()

    def decrypt(self, input):
        """Decrypt token"""
        try:
            return self.fernet.decrypt(bytes.fromhex(input)).decode()
        except ValueError:
            return None


class RequestSignerException(Exception):
    pass


class RequestSigner:
    """Interface to sign and verify requests"""

    ARG_NAME = "sigkey"

    def sign(self, effective_user: User, path: str) -> str:
        """Return signature for the url"""

        signature_data = {}
        signature_data["user_id"] = effective_user.id

        # @TODO include query string and replace with a hash
        signature_data["path"] = path

        presign = Presign()
        signature = presign.encrypt(json.dumps(signature_data))

        return f'?{self.ARG_NAME}={signature}'

    def verify(self, request: Request) -> str:
        """Verify the request and return the effective user id"""

        signature_list = request.args.getlist(self.ARG_NAME)
        if len(signature_list) < 1:
            raise RequestSignerException("Signature not found.")
        if len(signature_list) > 1:
            raise RequestSignerException("Multiple signatures found.")

        presign = Presign()
        signature_data_json = presign.decrypt(signature_list[0])

        if signature_data_json is None:
            raise RequestSignerException("Failed to decode signature.")

        signature_data: dict | None = json.loads(signature_data_json)
        if signature_data is None:
            raise RequestSignerException("Failed to parse signature data.")

        if signature_data["path"] != request.path:
            raise RequestSignerException("Signature path does not match.")

        return signature_data["user_id"]
