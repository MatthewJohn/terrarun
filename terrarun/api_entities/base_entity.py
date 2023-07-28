
from flask import request

from terrarun.api_error import ApiError
from terrarun.errors import RelationshipDoesNotExistError


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


class BaseRelationshipType:

    TYPE = None

    def __init__(self, id):
        """Store member variables"""
        self.id = id

    @classmethod
    def from_object(cls, obj):
        """Return instance from obj"""
        return cls(id=obj.api_id)

    @property
    def type(self):
        """Return type"""
        if self.TYPE is None:
            raise Exception("Unset type of relationship object")
        return self.TYPE

    def to_dict(self):
        """Return dictionary for view data"""
        return {
            "id": self.id,
            "type": self.type
        }
    
    @classmethod
    def from_request(cls, relationship_data):
        """Create instance from request data"""
        if type(relationship_data) is not dict:
            return ApiError(
                "Invalid relationship data",
                f"Relationship type should be an object with id and type, but {type(relationship_data)} was provided.",
                pointer=f"@TODO"
            ), None

        type_ = relationship_data.get("type")
        if type_ != cls.TYPE:
            return ApiError(
                "Invalid relationship type",
                f"Relationship type value should expected {cls.TYPE}, but {type_} was provided.",
                pointer=f"@TODO"
            ), None

        id = relationship_data.get("id")
        if not id:
            return ApiError(
                "Invalid relationship id",
                f"Relationship id was not provided.",
                pointer=f"@TODO"
            ), None

        return None, cls(id=id)


class BaseRelationshipHandler:

    # Key in relationships dict
    name = None
    # Type of relationship
    relationship_type = None

    def to_dict(self):
        """Return dictionary to provide to view"""
        raise NotImplementedError

    @classmethod
    def from_request(cls, relationships_data):
        """Create relationship from request"""
        raise NotImplementedError


class DirectRelationshipHandler(BaseRelationshipHandler):

    def __init__(self, relationship):
        """Handle relationship data"""
        self.relationship = relationship

    @classmethod
    def from_request(cls, relationships_data):
        """Create relationship from request"""
        relationship_data = relationships_data.get(cls.name, {}).get("data", {})
        err, relationship = cls.relationship_type.from_request(relationship_data)
        if err:
            return err, None
        return None, cls(relationship=relationship)

    def to_dict(self):
        """Return dictionary to provide to view"""
        return {
            "data": self.relationship.to_dict()
        }


class ListRelationshipHandler(BaseRelationshipHandler):

    def __init__(self, relationships):
        """Handle data list relationship"""
        self.relationships = relationships

    def to_dict(self):
        """Return dictionary to provide to view"""
        return {
            "data": [
                relationship.to_dict()
                for relationship in self.relationships
            ]
        }

    @classmethod
    def from_request(cls, relationships_data):
        """Create relationship from request"""
        relationships = []
        for relationship_data in relationships_data.get(cls.name, {}).get("data", []):
            err, relationship = cls.relationship_type.from_request(relationship_data)
            if err:
                return err, None, None
            relationships.append(relationship)
        return None, cls.name, cls(relationships=relationships)


class BaseEntity:
    """Base entity"""

    id = None
    type = None
    ID_EMPTY = False

    ATTRIBUTES = tuple()
    RELATIONSHIP_TYPES = tuple()

    def __init__(self, relationships, id=None, **kwargs):
        """Assign attributes from kwargs to attributes"""
        self.id = id
        self.relationships = relationships

        for attribute in self.ATTRIBUTES:
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

    def get_relationship(self, relationship) -> BaseRelationshipHandler:
        """Get relationship by name"""
        relationship_obj = self.relationships.get(relationship)
        if not relationship_obj:
            raise RelationshipDoesNotExistError("Relationship does not exist")
        return relationship_obj

    def get_relationships(self):
        """Return view relationships"""
        return {
            relationship: self.relationships[relationship].to_dict()
            for relationship in self.relationships
        }

    def get_set_object_attributes(self):
        """Return all set object attributes"""
        return {
            attr.obj_attribute: getattr(self, attr.obj_attribute)
            for attr in self.ATTRIBUTES
            if getattr(self, attr.obj_attribute) is not UNDEFINED
        }

    @classmethod
    def from_object(cls, obj):
        """Create entity from model object"""
        raise NotImplementedError

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
                pointer=f"/data/type"
            ), None

        id_ = request_data.get("id")
        if not id_ and cls.ID_EMPTY:
            return ApiError(
                "ID not provided",
                f"The object ID not provided in the request",
                pointer=f"/data/id"
            ), None
        elif id_ and not cls.ID_EMPTY:
            return ApiError(
                "ID should not be provided",
                f"The object ID should not be present in this request",
                pointer=f"/data/id"
            ), None

        obj_attributes = {
            "id": id_ if not cls.ID_EMPTY else None
        }

        request_attributes = request_data.get("attributes")
        for attribute in cls.ATTRIBUTES:
            err, key, value = attribute.validate_request_data(request_attributes)
            if err:
                return err, None
            if key is not None:
                obj_attributes[key] = value
        
        relationships = {}
        for relationship in cls.RELATIONSHIP_TYPES:
            err, key, value = relationship.from_request(request_data.get("relationships", {}))
            if err:
                return err, None
            relationships[key] = value

        return None, cls(relationships=relationships, **obj_attributes)


class BaseView:
    
    response_code = 200

    def to_dict(self):
        """Create response data"""
        raise NotImplementedError

    def to_response(self, code=None):
        """Create response"""
        return self.to_dict(), code if code is not None else self.response_code


class EntityView(BaseView):
    """Return view for entity"""

    def to_dict(self):
        """Return view as dictionary"""
        data = {
            "type": self.get_type(),
            "id": self.get_id(),
            "attributes": self.get_attributes()
        }
        if self.RELATIONSHIP_TYPES:
            data["relationships"] = self.get_relationships()

        return {"data": data}


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
