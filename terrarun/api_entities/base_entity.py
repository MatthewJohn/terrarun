
from flask import request

from terrarun.api_error import ApiError


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
        else:
            raise Exception("Unsupported attribute type")

        return None, self.obj_attribute, val


class BaseEntity:
    """Base entity"""

    id = None
    type = None

    attributes = tuple()

    def __init__(self, id=None, **kwargs):
        """Assign attributes from kwargs to attributes"""
        self.id = id

        for attribute in self.attributes:
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

    def get_attributes(self):
        """Return API attributes for entity"""
        raise NotImplementedError

    def get_set_object_attributes(self):
        """Return all set object attributes"""
        return {
            attr.obj_attribute: getattr(self, attr.obj_attribute)
            for attr in self.attributes
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

        if not request_data.get("id"):
            return ApiError(
                "ID not provided",
                f"The object ID not provided in the request",
                pointer=f"/data/id"
            ), None
        
        obj_attributes = {
            "id": request_data.get("id")
        }

        request_attributes = request_data.get("attributes")
        for attribute in cls.attributes:
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
                "attributes": self.get_attributes()
            }
        }


class ApiErrorView(BaseEntity, BaseView):

    response_code = 409

    def __init__(self, error=None, errors=None):
        """Return"""
        self.errors = []
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
