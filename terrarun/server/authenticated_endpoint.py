
import re

from flask_restful import Resource
from flask import request, session

import terrarun.database
import terrarun.models.user_token


class AuthenticatedEndpoint(Resource):
    """Authenticated endpoint"""

    def _get_current_user(self):
        """Obtain current user based on API token key in request"""
        authorization_header = request.headers.get('Authorization', '')
        if not authorization_header:
            authorization_header = session.get('Authorization', '')

        # @TODO don't use regex
        auth_token = re.sub(r'^Bearer ', '', authorization_header)
        user_token = terrarun.models.user_token.UserToken.get_by_token(auth_token)
        if not user_token:
            return None, None
        return user_token.user, user_token.job

    def _error_catching_call(self, method, args, kwargs):
        """Call method, catching exceptions"""
        try:
            return method(*args, **kwargs)
        except:
            # Rollback and remove session
            terrarun.database.Database.get_session().rollback()
            terrarun.database.Database.get_session().remove()
            raise

    def _get(self, *args, **kwargs):
        """Handle GET request method to re-implemented by overriding class."""
        raise NotImplementedError

    def check_permissions_get(self, *args, **kwargs):
        """Function to check permissions, must be implemented by overriding class."""
        raise NotImplementedError

    def get(self, *args, **kwargs):
        """Handle GET request"""
        current_user, job = self._get_current_user()
        if not current_user and not job:
            print('No user')
            return {}, 403

        if not self.check_permissions_get(*args, current_job=job, current_user=current_user, **kwargs):
            return {}, 404

        kwargs.update(current_user=current_user)
        kwargs.update(current_job=job)
        return self._error_catching_call(self._get, args, kwargs)

    def _post(self, *args, **kwargs):
        """Handle POST request method to re-implemented by overriding class."""
        raise NotImplementedError

    def check_permissions_post(self, *args, **kwargs):
        """Function to check permissions, must be set by implementer"""
        raise NotImplementedError

    def post(self, *args, **kwargs):
        """Handle POST request"""
        current_user, job = self._get_current_user()
        if not current_user and not job:
            return {}, 403

        if not self.check_permissions_post(*args, current_job=job, current_user=current_user, **kwargs):
            return {}, 404

        kwargs.update(current_user=current_user)
        kwargs.update(current_job=job)
        return self._error_catching_call(self._post, args, kwargs)

    def _patch(self, *args, **kwargs):
        """Handle PATCH request method to re-implemented by overriding class."""
        raise NotImplementedError

    def check_permissions_patch(self, *args, **kwargs):
        """Function to check permissions, must be set by implementer"""
        raise NotImplementedError

    def patch(self, *args, **kwargs):
        """Handle PATCH request"""
        current_user, job = self._get_current_user()
        if not current_user and not job:
            return {}, 403

        if not self.check_permissions_patch(*args, current_job=job, current_user=current_user, **kwargs):
            return {}, 404

        kwargs.update(current_user=current_user)
        kwargs.update(current_job=job)
        return self._error_catching_call(self._patch, args, kwargs)

    def _put(self, *args, **kwargs):
        """Handle PUT request method to re-implemented by overriding class."""
        raise NotImplementedError

    def check_permissions_put(self, *args, **kwargs):
        """Function to check permissions, must be set by implementer"""
        raise NotImplementedError

    def put(self, *args, **kwargs):
        """Handle PUT request"""
        current_user, job = self._get_current_user()
        if not current_user and not job:
            return {}, 403

        if not self.check_permissions_put(*args, current_job=job, current_user=current_user, **kwargs):
            return {}, 404

        kwargs.update(current_user=current_user)
        kwargs.update(current_job=job)
        return self._error_catching_call(self._put, args, kwargs)

    def _delete(self, *args, **kwargs):
        """Handle DELETE request method to re-implemented by overriding class."""
        raise NotImplementedError

    def check_permissions_delete(self, *args, **kwargs):
        """Function to check permissions, must be set by implementer"""
        raise NotImplementedError

    def delete(self, *args, **kwargs):
        """Handle PUT request"""
        current_user, job = self._get_current_user()
        if not current_user and not job:
            return {}, 403

        if not self.check_permissions_delete(*args, current_job=job, current_user=current_user, **kwargs):
            return {}, 404

        kwargs.update(current_user=current_user)
        kwargs.update(current_job=job)
        return self._error_catching_call(self._delete, args, kwargs)
