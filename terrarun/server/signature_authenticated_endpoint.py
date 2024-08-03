# Copyright (C) 2024 Matt Comben - All Rights Reserved
# SPDX-License-Identifier: GPL-2.0


from typing import Tuple, Optional

from flask import request

from terrarun.logger import get_logger
from terrarun.models.user import User
from terrarun.models.run_queue import RunQueue
from terrarun.presign import PresignedRequestValidator, PresignedRequestValidatorError
from terrarun.server.authenticated_endpoint import AuthenticatedEndpoint

logger = get_logger(__name__)


class SignatureAuthenticatedEndpoint(AuthenticatedEndpoint):
    """Authenticated endpoint"""

    def _get_current_user(self) -> Tuple[Optional[User], Optional[RunQueue]]:
        """Verify the signature and return the effective user"""

        try:
            presign_data = PresignedRequestValidator().validate(request)
        except PresignedRequestValidatorError as e:
            logger.warning("Failed to authenticate with signature. Error: %s", e)
            return None, None

        return presign_data.user, presign_data.job
