# Copyright (C) 2024 Matt Comben - All Rights Reserved
# SPDX-License-Identifier: GPL-2.0


import base64
import json
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from cryptography.fernet import Fernet
from werkzeug.wrappers.request import Request

import terrarun.config
import terrarun.auth_context
from terrarun.models.user import User
from terrarun.models.run_queue import RunQueue
from terrarun.utils import datetime_from_json


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


@dataclass
class RequestSignature:
    """Class containing the request signature data."""

    user: Optional[User]
    job: Optional[RunQueue]
    path: str
    created_at: datetime

    def serialize(self) -> str:
        data = {
            "user_id": self.user.api_id if self.user else None,
            "job_id": self.job.api_id if self.job else None,
            "path": self.path,
            "created_at": self.created_at.isoformat(),
        }
        return json.dumps(data)

    @staticmethod
    def deserialise(serialized: str):
        data = json.loads(serialized)

        if data is None or not isinstance(data, dict):
            return None

        user = None
        if user_id := data.get("user_id"):
            user = User.get_by_api_id(user_id)

        job = None
        if job_id := data.get("job_id"):
            job = RunQueue.get_by_api_id(job_id)

        return RequestSignature(
            user=user,
            job=job,
            path=data.get("path"),
            created_at=datetime_from_json(data.get("created_at")),
        )


class PresignedUrlGenerator:
    """Interface to sign and verify requests"""

    ARG_NAME = "sigkey"

    def create_url(self, auth_context: 'terrarun.auth_context.AuthContext', path: str) -> str:
        """Return signature for the url"""

        signature_data = RequestSignature(
            user=auth_context.user,
            job=auth_context.job,
            path=path,
            created_at=datetime.now()
        )

        presign = Presign()
        signature = presign.encrypt(signature_data.serialize())

        return f"{terrarun.config.Config().BASE_URL}{path}?{self.ARG_NAME}={signature}"


class PresignedRequestValidatorError(Exception):
    pass


class PresignedRequestValidator:

    def validate(self, request: Request) -> 'terrarun.auth_context.AuthContext':
        """Verify the request and return the effective user id"""

        signature_list = request.args.getlist(PresignedUrlGenerator.ARG_NAME)
        if len(signature_list) < 1:
            raise PresignedRequestValidatorError("Signature not found.")
        if len(signature_list) > 1:
            raise PresignedRequestValidatorError("Multiple signatures found.")

        presign = Presign()
        signature_data_json = presign.decrypt(signature_list[0])

        if signature_data_json is None:
            raise PresignedRequestValidatorError("Failed to decode signature.")

        signature_data = RequestSignature.deserialise(signature_data_json)
        if signature_data is None:
            raise PresignedRequestValidatorError("Failed to parse signature data.")

        if signature_data.path != request.path:
            raise PresignedRequestValidatorError("Signature path does not match.")

        # @TODO Check the creation date and add a time limit

        return terrarun.auth_context.AuthContext(
            user=signature_data.user,
            job=signature_data.job,
        )
