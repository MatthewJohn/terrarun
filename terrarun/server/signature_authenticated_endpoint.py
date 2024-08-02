# Copyright (C) 2024 Matt Comben - All Rights Reserved
# SPDX-License-Identifier: GPL-2.0


from typing import Tuple

from flask import request

from terrarun.logger import get_logger
from terrarun.models.user import User
from terrarun.presign import PresignedRequestValidator, PresignedRequestValidatorError
from terrarun.server.authenticated_endpoint import AuthenticatedEndpoint

logger = get_logger(__name__)


class SignatureAuthenticatedEndpoint(AuthenticatedEndpoint):
    """Authenticated endpoint"""

    def _get_current_user(self) -> Tuple[User | None, None]:
        """Verify the signature and return the effective user"""

        try:
            user_id = PresignedRequestValidator().validate(request)
        except PresignedRequestValidatorError as e:
            logger.warning("Failed to authenticate with signature. Error: %s", e)
            return None, None

        effective_user: User | None = User.get_by_id(user_id)

        return effective_user, None
