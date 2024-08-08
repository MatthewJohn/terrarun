# Copyright (C) 2024 Matt Comben - All Rights Reserved
# SPDX-License-Identifier: GPL-2.0


from typing import Tuple, Optional

from flask import request

import terrarun.auth_context
from terrarun.logger import get_logger
from terrarun.presign import PresignedRequestValidator, PresignedRequestValidatorError
from terrarun.server.authenticated_endpoint import AuthenticatedEndpoint

logger = get_logger(__name__)


class SignatureAuthenticatedEndpoint(AuthenticatedEndpoint):
    """Authenticated endpoint"""

    def _get_auth_context(self) -> terrarun.auth_context.AuthContext:
        """Verify the signature and return an auth context based on the signature data"""

        try:
            presign_data = PresignedRequestValidator().validate(request)
        except PresignedRequestValidatorError as e:
            logger.warning("Failed to authenticate with signature. Error: %s", e)
            return terrarun.auth_context.AuthContext(user=None, job=None)

        return terrarun.auth_context.AuthContext(user=presign_data.user, job=presign_data.job)
