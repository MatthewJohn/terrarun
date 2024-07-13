
import abc
from enum import EnumMeta
from datetime import datetime
from typing import Tuple, Optional, List

from flask import request

from terrarun.api_error import ApiError
from terrarun.utils import datetime_to_json, datetime_from_json


UNDEFINED = object
ATTRIBUTED_REQUIRED = object


class Attribute:

    def __init__(self, req_attribute, obj_attribute, type, default, nullable=True):
        """Store member variables"""
        self.req_attribute = req_attribute
        self.obj_attribute = obj_attribute
        self.type = type
        self.default = default
        self.nullable = nullable

    def convert_entity_data_to_api(self, value):
        """Convert data to API type"""
        if self.type in [str, bool, int]:
            return value

        # Handle None value
        elif value is None:
            return None

        # Handle enum
        elif type(self.type) is EnumMeta:
            return value.value

        elif self.type is datetime:
            return datetime_to_json(value)

        # @TODO Convert to entity type
        elif self.type is dict:
            return value

        raise Exception(f"Unknown data type: {self.type}: {value}")

    def validate_request_data(self, request_attributes):
        """Validate request attributes and return key and value from request"""
        # Ignore any attributes that don't have a request mapping
        if self.req_attribute is None:
            return None, None, None

        val = request_attributes.get(self.req_attribute, UNDEFINED)

        # If value is not present in request...
        if val is UNDEFINED:
            # If it is not required, return the default attribute
            if self.default is not ATTRIBUTED_REQUIRED:
                return None, self.obj_attribute, self.default

            # Otherwise, return an error
            return ApiError(
                "Required attribute not provided",
                f"The required attribute '{self.req_attribute}' was not provided in the request",
                pointer=f"/data/attributes/{self.req_attribute}"
            ), None, None

        # Check for null value
        if val is None:
            if not self.nullable:
                return ApiError(
                    "Null attribute not allowed",
                    f"The attribute '{self.req_attribute}' was set to null, but cannot be null.",
                    pointer=f"/data/attributes/{self.req_attribute}"
                ), None, None

        elif self.type in (str, int, bool):
            if not isinstance(val, self.type):
                return ApiError(
                    "Invalid attribute value type",
                    f"The attribute {self.req_attribute} must be type {self.type}.",
                    pointer=f"/data/attributes/{self.req_attribute}"
                ), None, None

        elif type(self.type) is EnumMeta:
            try:
                val = self.type(val)
            except ValueError:
                return ApiError(
                    "Invalid value for attribute",
                    f"The attribute '{self.req_attribute}' is set to an invalid value.",
                    pointer=f"/data/attributes/{self.req_attribute}"
                ), None, None

        elif self.type is datetime:
            try:
                val = datetime_from_json(val)
            except:
                return ApiError(
                    "Invalid datetime value for attribute",
                    f"The attribute '{self.req_attribute}' is set to an invalid datetime.",
                    pointer=f"/data/attributes/{self.req_attribute}"
                ), None, None

        else:
            raise Exception("Unsupported attribute type")

        return None, self.obj_attribute, val


class BaseEntity:
    """Base entity"""

    id: Optional[str] = None
    require_id: bool = True
    type: Optional[str] = None

    def __init__(self, id: str=None, **kwargs):
        """Assign attributes from kwargs to attributes"""
        self.id = id

        for attribute in self.get_attributes():
            setattr(
                self,
                attribute.obj_attribute,
                kwargs[attribute.obj_attribute] if attribute.obj_attribute in kwargs else UNDEFINED
            )

    def get_type(self):
        """Return entity type"""
        if self.type is None:
            raise NotImplementedError
        return self.type

    def get_id(self):
        """Return ID"""
        if self.id is None:
            raise NotImplementedError
        return self.id

    @classmethod
    @abc.abstractmethod
    def get_attributes(cls) -> Tuple[Attribute]:
        """Return attributes for entity"""
        ...

    def get_api_attributes(self):
        """Return API attributes for entity"""
        return {
            attribute.req_attribute: attribute.convert_entity_data_to_api(getattr(self, attribute.obj_attribute))
            for attribute in self.get_attributes()
        }

    def get_set_object_attributes(self):
        """Return all set object attributes, used when updating models"""
        return {
            attr.obj_attribute: getattr(self, attr.obj_attribute)
            for attr in self.get_attributes()
            if getattr(self, attr.obj_attribute) is not UNDEFINED
        }

    @classmethod
    def from_request(cls, request_args, create=False):
        """
        Obtain entity object from request
        
        If create is enabled, the ID in the request is optional
        """

        request_data = request_args.get("data", {})
        if request_data.get("type") != cls.type:
            return ApiError(
                "Invalid type",
                f"The object type was either not provided or is not valid for this request",
                pointer=f"/data/id"
            ), None

        obj_attributes = {}

        if id_ := request_data.get("id"):
            obj_attributes["id"] = id_
        elif cls.require_id:
            return ApiError(
                "ID not provided",
                f"The object ID not provided in the request",
                pointer=f"/data/id"
            ), None

        request_attributes = request_data.get("attributes")
        for attribute in cls.get_attributes():
            err, key, value = attribute.validate_request_data(request_attributes)
            if err:
                return err, None
            if key is not None:
                obj_attributes[key] = value
        
        return None, cls(**obj_attributes)


class BaseView:
    
    response_code = 200

    def to_dict(self):
        """Create response data"""
        raise NotImplementedError

    def to_response(self, code=None):
        """Create response"""
        return self.to_dict(), code if code is not None else self.response_code


class EntityView(BaseEntity, BaseView):
    """Return view for entity"""

    def to_dict(self):
        """Return view as dictionary"""
        return {
            "data": {
                "type": self.get_type(),
                "id": self.get_id(),
                "attributes": self.get_api_attributes()
            }
        }


class ApiErrorView(BaseEntity, BaseView):

    response_code = 409

    def __init__(self, error: Optional[ApiError]=None, errors: Optional[List[ApiError]]=None):
        """Return"""
        self.errors: List[ApiError] = []
        if error:
            self.errors.append(error)
        if errors:
            self.errors += errors

    def to_dict(self):
        """Return errror"""
        return {
            "errors": [
                error.get_api_details()
                for error in self.errors
            ]
        }
