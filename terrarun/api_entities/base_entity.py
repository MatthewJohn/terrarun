# Copyright (C) 2024 Matt Comben - All Rights Reserved
# SPDX-License-Identifier: GPL-2.0


import abc
from enum import EnumMeta
from datetime import datetime
from typing import Tuple, Optional, List, Dict, Any

from flask import request

from terrarun.api_error import ApiError
import terrarun.models.user
from terrarun.utils import datetime_to_json, datetime_from_json


UNDEFINED = object()
ATTRIBUTED_REQUIRED = object()


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



class AttributeModifier:
    """Provide encapulsation of modifications to be mae to Attribute"""

    UNSET = object()

    def __init__(self, req_attribute=UNSET, type=UNSET, default=UNSET, nullable=UNSET):
        """Store modifications"""
        self._req_attribute = req_attribute
        self._type = type
        self._default = default
        self._nullable = nullable

    def apply(self, attribute: Attribute):
        """Apply modifications to attribute"""
        if self._req_attribute is not self.UNSET:
            attribute.req_attribute = self._req_attribute
        if self._type is not self.UNSET:
            attribute.type = self._type
        if self._default is not self.UNSET:
            attribute.default = self._default
        if self._nullable is not self.UNSET:
            attribute.nullable = self._nullable


class BaseEntity(abc.ABC):
    """Base entity"""

    id: Optional[str] = None
    require_id: bool = True
    type: Optional[str] = None
    include_attributes: Optional[Tuple[str]] = None
    attribute_modifiers: Dict[str, AttributeModifier] = {}

    def __init__(self, id: str=None, attributes: Optional[Dict[str, Any]]=None):
        """Assign attributes from kwargs to attributes"""
        self.id = id
        self._attribute_values = {}

        attributes = attributes or {}
        for attribute in self.get_attributes():
            self._attribute_values[attribute.obj_attribute] = (
                attributes[attribute.obj_attribute]
                if attribute.obj_attribute in attributes
                else UNDEFINED
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
    def _get_attributes(cls) -> Tuple[Attribute]:
        """Return attributes for entity"""
        ...

    @classmethod
    def get_attributes(cls) -> List[Attribute]:
        """Obtain all attributes, with filtering and modifications"""
        attributes = []
        for attribute in cls._get_attributes():
            # If include_attributes has been set and attribute is not included, ignore it
            if cls.include_attributes is not None and attribute.obj_attribute not in cls.include_attributes:
                continue

            # Apply modificiations if set
            if attribute.obj_attribute in cls.attribute_modifiers:
                cls.attribute_modifiers[attribute.obj_attribute].apply(attribute=attribute)

            attributes.append(attribute)
        return attributes

    def get_api_attributes(self):
        """Return API attributes for entity"""
        return {
            attribute.req_attribute: attribute.convert_entity_data_to_api(self._attribute_values[attribute.obj_attribute])
            for attribute in self.get_attributes()
        }

    def get_set_object_attributes(self):
        """Return all set object attributes, used when updating models"""
        return {
            attr.obj_attribute: self._attribute_values[attr.obj_attribute]
            for attr in self.get_attributes()
            if self._attribute_values[attr.obj_attribute] is not UNDEFINED
        }

    @classmethod
    @abc.abstractmethod
    def _from_object(cls, obj: Any, effective_user: 'terrarun.models.user.User') -> 'BaseEntity':
        """Return entity from object"""
        ...

    @classmethod
    def from_object(cls, obj: Any, effective_user: 'terrarun.models.user.User') -> 'BaseEntity':
        """Return entity from object"""
        return cls._from_object(obj=obj, effective_user=effective_user)

    @staticmethod
    def generate_link(obj: Any):
        """Generate self link from given objects"""
        return None

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


class BaseView(abc.ABC):
    
    response_code = 200

    @abc.abstractmethod
    def to_dict(self):
        """Create response data"""
        ...

    def to_response(self, code=None):
        """Create response"""
        return self.to_dict(), code if code is not None else self.response_code


class EntityView(BaseEntity, BaseView):
    """Return view for entity"""

    RELATIONSHIPS: Dict[str, 'BaseRelationshipView'] = {}

    def __init__(
            self,
            id: str = None,
            attributes: Optional[Dict[str, Any]]= None):
        """Store member variables for relationships"""
        super().__init__(id, attributes)
        self.relationships: Dict[str, 'BaseRelationshipView'] = {}
        self.link: Optional[str] = None

    @classmethod
    def from_object(cls, obj: Any, effective_user: 'terrarun.models.user.User') -> 'BaseEntity':
        """Return entity from object"""
        entity = cls._from_object(obj=obj, effective_user=effective_user)
        entity.link = cls.generate_link(obj=obj)
        entity.relationships = {
            relationship_name: relationship_class.from_object(obj=obj, parent_view=entity)
            for relationship_name, relationship_class in cls.RELATIONSHIPS.items()
        }
        return entity

    def to_dict(self):
        """Return view as dictionary"""
        response = {
            "data": {
                "type": self.get_type(),
                "id": self.get_id(),
                "attributes": self.get_api_attributes()
            }
        }
        if self_link := self.get_self_link():
            response["links"] = self_link

        relationships = {}
        for relationship_name, relationship in self.relationships.items():
            if relationship_data := relationship.to_dict():
                relationships[relationship_name] = relationship_data
        if relationships:
            response['relationships'] = relationships

        return response

    def get_self_link(self):
        """Get link for self"""
        if self.link:
            return {
                "self": self.link
            }
        return None


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


class BaseRelationshipView(BaseView):
    """Base relationship view"""

    @classmethod
    @abc.abstractmethod
    def from_object(cls, obj: Any, parent_view: 'EntityView') -> 'BaseEntity':
        """Return entity from object"""
        ...


class RelatedRelationshipView(BaseRelationshipView):
    """Base relationship for related"""

    CHILD_PATH: Optional[str] = None

    def __init__(self, parent_view: 'EntityView'):
        """Store member variables"""
        if self.CHILD_PATH is None:
            raise NotImplementedError("Name not set on relationship")
        self._parent_view = parent_view

    @classmethod
    def from_object(cls, obj: Any, parent_view: 'EntityView') -> 'BaseEntity':
        """Return entity from object"""
        return cls(parent_view=parent_view)

    def to_dict(self):
        """Return API repsonse data"""
        if self._parent_view.link:
            return {
                "links": {
                    "related": f"{self._parent_view.link}/{self.CHILD_PATH}"
                }
            }
        return None


class RelatedWithDataRelationshipView(BaseRelationshipView):
    """Base relationship for related"""

    CHILD_PATH: Optional[str] = None
    TYPE: Optional[str] = None

    def __init__(self, id: str, parent_view: 'EntityView'):
        """Store member variables"""
        self.id = id
        if self.CHILD_PATH is None:
            raise NotImplementedError("Name not set on relationship")
        self._parent_view = parent_view

    def get_type(self):
        """Return entity type"""
        if self.TYPE is None:
            raise NotImplementedError
        return self.TYPE

    def get_id(self):
        """Return ID"""
        if self.id is None:
            raise NotImplementedError
        return self.id

    @classmethod
    @abc.abstractmethod
    def get_id_from_object(cls, obj: Any) -> str:
        """Obtain ID from object"""
        ...

    @classmethod
    def from_object(cls, obj: Any, parent_view: 'EntityView') -> 'BaseEntity':
        """Return entity from object"""
        return cls(parent_view=parent_view, id=cls.get_id_from_object(obj=obj))

    def to_dict(self) -> dict:
        """Return API repsonse data"""
        data = {}
        if self._parent_view.link:
            data["links"] = {
                "related": f"{self._parent_view.link}/{self.CHILD_PATH}"
            }
        data["data"] = {
            "id": self.get_id(),
            "type": self.get_type(),
        }
        return data
