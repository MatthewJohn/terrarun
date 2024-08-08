# Copyright (C) 2024 Matt Comben - All Rights Reserved
# SPDX-License-Identifier: GPL-2.0


import re

from flask import request, session
from flask_restful import Resource

import terrarun.database
import terrarun.models.user_token
import terrarun.auth_context
from terrarun.api_entities.base_entity import ApiErrorView
from terrarun.errors import ApiError
from terrarun.logger import get_logger

logger = get_logger(__name__)


class AuthenticatedEndpoint(Resource):
    """Authenticated endpoint"""

    def _get_auth_context(self) -> 'terrarun.auth_context.AuthContext':
        """Obtain current user based on API token key in request"""
        authorization_header = request.headers.get('Authorization', '')
        if not authorization_header:
            authorization_header = session.get('Authorization', '')

        # @TODO don't use regex
        auth_token = re.sub(r'^Bearer ', '', authorization_header)
        user_token = terrarun.models.user_token.UserToken.get_by_token(auth_token)
        if not user_token:
            return terrarun.auth_context.AuthContext(user=None, job=None)

        return terrarun.auth_context.AuthContext(user=user_token.user, job=user_token.job)

    def _error_catching_call(self, method, args, kwargs):
        """Call method, catching exceptions"""
        try:
            return method(*args, **kwargs)
        except Exception as e:
            # Rollback and remove session
            terrarun.database.Database.get_session().rollback()
            terrarun.database.Database.get_session().remove()

            if isinstance(e, ApiError):
                return ApiErrorView(error=e).to_response()

            raise

    def _validate_authentication(self, auth_context: 'terrarun.auth_context.AuthContext') -> bool:
        """Validate authentication"""
        if auth_context.user is None and auth_context.job is None:
            logger.warning('Unauthenticated request.')
            return False
        return True

    def handle_request(self, method_name: str, args, kwargs):
        """Handle method"""
        if method_name not in ["get", "post", "put", "patch", "delete"]:
            raise NotImplementedError

        auth_context = self._get_auth_context()
        if not self._validate_authentication(auth_context=auth_context):
            return {}, 403

        check_permissions_method = f"check_permissions_{method_name}"
        if not getattr(self, check_permissions_method)(*args, auth_context=auth_context, **kwargs):
            return {}, 404

        kwargs.update(auth_context=auth_context)
        method_function_name = f"_{method_name}"
        return self._error_catching_call(getattr(self, method_function_name), args, kwargs)

    def _get(self, *args, **kwargs):
        """Handle GET request method to re-implemented by overriding class."""
        raise NotImplementedError

    def check_permissions_get(self, *args, **kwargs):
        """Function to check permissions, must be implemented by overriding class."""
        raise NotImplementedError

    def get(self, *args, **kwargs):
        """Handle GET request"""
        return self.handle_request("get", args, kwargs)

    def _post(self, *args, **kwargs):
        """Handle POST request method to re-implemented by overriding class."""
        raise NotImplementedError

    def check_permissions_post(self, *args, **kwargs):
        """Function to check permissions, must be set by implementer"""
        raise NotImplementedError

    def post(self, *args, **kwargs):
        """Handle POST request"""
        return self.handle_request("post", args, kwargs)

    def _patch(self, *args, **kwargs):
        """Handle PATCH request method to re-implemented by overriding class."""
        raise NotImplementedError

    def check_permissions_patch(self, *args, **kwargs):
        """Function to check permissions, must be set by implementer"""
        raise NotImplementedError

    def patch(self, *args, **kwargs):
        """Handle PATCH request"""
        return self.handle_request("patch", args, kwargs)

    def _put(self, *args, **kwargs):
        """Handle PUT request method to re-implemented by overriding class."""
        raise NotImplementedError

    def check_permissions_put(self, *args, **kwargs):
        """Function to check permissions, must be set by implementer"""
        raise NotImplementedError

    def put(self, *args, **kwargs):
        """Handle PUT request"""
        return self.handle_request("put", args, kwargs)

    def _delete(self, *args, **kwargs):
        """Handle DELETE request method to re-implemented by overriding class."""
        raise NotImplementedError

    def check_permissions_delete(self, *args, **kwargs):
        """Function to check permissions, must be set by implementer"""
        raise NotImplementedError

    def delete(self, *args, **kwargs):
        """Handle PUT request"""
        return self.handle_request("delete", args, kwargs)
