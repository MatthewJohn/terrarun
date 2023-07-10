
from enum import Enum


class ApiRequest:
    """Interface to interpret API requests and generate API responses"""

    class Includes(Enum):
        """Include types"""
        # @TODO How to calculate which level these includes are at.
        # Maybe register the request object type in Api Request and
        # add each level of the object "tree" to the includes
        # i.e. for a request to workspace, passing in "includes=created_by"
        # becomes "workspace.created_by" and the object checking includes ensures
        # the parent of the include is it's own type
        CONFIGURATION_VERSION = "configuration_version"
        CONFIGURATION_VERSION_INGRESS_ATTRIBUTES = "configuration_version.ingress_attributes"
        CREATED_BY = "created_by"

    def __init__(self, current_request, list_data=False):
        """Initial request"""
        self.includes = []
        for include_string in current_request.args.get("include", "").split(","):
            if include_string:
                self.includes.append(ApiRequest.Includes(include_string))
        self._errors = []
        self._included = []
        self._list_data = list_data
        self._data = None if not list_data else []

    def set_data(self, data):
        """Set data for response"""
        if self._list_data:
            self._data.append(data)
        else:
            self._data = data

    def has_include(self, include_type):
        """Whether an include has been passed"""
        return include_type in self.includes

    def add_included(self, data):
        """Add included data to response"""
        self._included.append(data)

    def add_error(self, error):
        """Register error"""
        self._errors.append(error)

    def get_response(self, status_code=200):
        """Get response data"""
        # Check for errors
        if self._errors:
            return {
                "errors": [
                    error.get_api_details()
                    for error in self._errors
                ]
            }, 409

        response_data = {
            "data": self._data
        }
        # If includes were requests, added to response, even
        # if no data was found
        if self._included:
            response_data["included"] = self._included
        
        return response_data, status_code