# Copyright (C) 2024 Matt Comben - All Rights Reserved
# SPDX-License-Identifier: GPL-2.0


import abc
from enum import EnumMeta
from datetime import datetime
from typing import Tuple, Optional, List, Dict, Any, TypeVar, Generic, Union
from typing_extensions import Self

from flask import request

from terrarun.api_error import ApiError
import terrarun.models.user
import terrarun.models.base_object
import terrarun.auth_context
from terrarun.utils import datetime_to_json, datetime_from_json


UNDEFINED = object()
ATTRIBUTED_REQUIRED = object()


class Attribute:

    def __init__(self,
                 # Name of attribute in request
                 req_attribute: str,
                 # Name of object attribute
                 obj_attribute: str,
                 # object attribute type
                 type: Any,
                 # Default value, if not included in request
                 default: Any,
                 # Whether value is allowed to be nullable
                 nullable: bool=True,
                 # Whether to omit from generated response,
                 # if value is None
                 omit_none: bool=False,
                 # Whether to omit undefined attribute from
                 # generated response.
                 # Otherwise, undefined values will
                 # be set to default in view
                 omit_undefined: bool=False):
        """Store member variables"""
        self.req_attribute = req_attribute
        self.obj_attribute = obj_attribute
        self.type = type
        self.default = default
        self.nullable = nullable
        self.omit_none = omit_none
        self.omit_undefined = omit_undefined

    def convert_entity_data_to_api(self, value):
        """Convert data to API type"""
        if value is UNDEFINED:
            if self.default is ATTRIBUTED_REQUIRED:
                raise Exception(
                    f"Attempted to return API response for object with required attribute ({self.obj_attribute}) without a definition"
                )

            if self.omit_undefined:
                return UNDEFINED

            return self.default

        if self.type in [str, bool, int]:
            return value

        # Handle None value
        elif value is None:
            # If none values are omitted, return undefined
            if self.omit_none:
                return UNDEFINED
            return None

        # Handle enum
        elif type(self.type) is EnumMeta:
            return value.value

        elif self.type is datetime:
            return datetime_to_json(value)

        # @TODO Convert to entity type
        elif self.type is dict:
            return value

        elif issubclass(self.type, terrarun.models.base_object.BaseObject):
            return value.api_id

        elif issubclass(self.type, NestedAttributes):
            return value.to_dict()

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

        elif issubclass(self.type, terrarun.models.base_object.BaseObject):
            val = self.type.get_by_api_id(val)
            if val is None:
                return ApiError(
                    "Entity does not exist",
                    f"The attribute '{self.req_attribute}' is set to an invalid/non-existent ID.",
                    pointer=f"/data/attributes/{self.req_attribute}"
                ), None, None

        elif issubclass(self.type, NestedAttributes):
            if not isinstance(val, dict):
                return ApiError(
                    "Invalid attribute value type",
                    f"The attribute {self.req_attribute} must be an object.",
                    pointer=f"/data/attributes/{self.req_attribute}"
                ), None, None
            val = self.type.from_request(request_args=val)

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
    RELATIONSHIPS: Dict[str, 'BaseRelationshipEntity'] = {}

    def __init__(self,
                 id: str=None,
                 attributes: Optional[Dict[str, Any]]=None,
                 relationships: Optional[Dict[str, 'BaseRelationshipEntity']]=None):
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

        self.relationships: Dict[str, 'BaseRelationshipEntity'] = relationships if relationships else {}

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
            # Strip any UNDEFINED values
            k: v
            for k, v in {
                attribute.req_attribute: attribute.convert_entity_data_to_api(self._attribute_values[attribute.obj_attribute])
                for attribute in self.get_attributes()
            }.items()
            if v is not UNDEFINED
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
    def _from_object(cls, obj: Any, auth_context: 'terrarun.auth_context.AuthContext') -> 'Self':
        """Return entity from object"""
        ...

    @classmethod
    def from_object(cls, obj: Any, auth_context: 'terrarun.auth_context.AuthContext') -> 'Self':
        """Return entity from object"""
        entity = cls._from_object(obj=obj, auth_context=auth_context)
        entity.relationships = {
            relationship_name: relationship_class.from_object(obj=obj, parent_view=entity)
            for relationship_name, relationship_class in cls.RELATIONSHIPS.items()
        }
        return entity

    @staticmethod
    def generate_link(obj: Any):
        """Generate self link from given objects"""
        return None

    @classmethod
    def _attributes_from_request(cls, request_attributes: Dict[Any, Any]) -> Dict[Any, Any]:
        """Convert request attributes to dict"""
        obj_attributes = {}

        for attribute in cls.get_attributes():
            err, key, value = attribute.validate_request_data(request_attributes)
            if err:
                return err, None
            if key is not None:
                obj_attributes[key] = value

        return obj_attributes

    @classmethod
    def from_request(cls, request_args, create=False) -> Union[Tuple['ApiError', None], Tuple[None, Self]]:
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

        if id_ := request_data.get("id"):
            pass
        elif cls.require_id:
            return ApiError(
                "ID not provided",
                f"The object ID not provided in the request",
                pointer=f"/data/id"
            ), None

        obj_attributes = cls._attributes_from_request(request_data.get("attributes", {}))

        entity = cls(id=id_, attributes=obj_attributes)

        for relationship_name, relationship_data in request_data.get("relationships", {}).items():
            if relationship_name in cls.RELATIONSHIPS:
                err, relationship_entity = cls.RELATIONSHIPS.get(relationship_name).from_request(request_args=relationship_data, parent_view=entity)
                if err:
                    # Update error pointer
                    err.pointer = f"/relationships/{relationship_name}/{err.pointer}"
                    return err, None
                entity.relationships[relationship_name] = relationship_entity

        return None, entity


class BaseView(abc.ABC):
    
    response_code = 200

    @abc.abstractmethod
    def get_data(self):
        """Create response data for data"""
        ...

    def to_dict(self):
        """Create response data"""
        return {
            "data": self.get_data()
        }

    def to_response(self, code=None):
        """Create response"""
        return self.to_dict(), code if code is not None else self.response_code



class NestedAttributes(BaseEntity, BaseView):
    """Nested attributes for entity"""

    def get_type(self):
        """Return entity type"""
        return None

    def get_id(self):
        """Return ID"""
        return None

    def to_dict(self):
        """Return just attributes"""
        return self.get_api_attributes()

    def get_data(self):
        """Implement abstract method"""
        pass

    @classmethod
    def from_request(cls, request_args):
        """Obtain entity object from request"""
        obj_attributes = cls._attributes_from_request(request_args.get("attributes", {}))

        return None, cls(id=None, attributes=obj_attributes)


class EntityView(BaseEntity, BaseView):
    """Return view for entity"""

    def __init__(
            self,
            id: str = None,
            attributes: Optional[Dict[str, Any]]=None,
            relationships: Optional[Dict[str, Any]]=None):
        """Store member variables for relationships"""
        super().__init__(id, attributes=attributes, relationships=relationships)
        self.link: Optional[str] = None

    @classmethod
    def from_object(cls, obj: Any, auth_context: 'terrarun.auth_context.AuthContext') -> 'BaseEntity':
        """Return entity from object"""
        entity = super().from_object(obj=obj, auth_context=auth_context)
        entity.link = cls.generate_link(obj=obj)
        return entity

    def get_data(self) -> Dict[str, Any]:
        """Get data for entity"""
        return {
            "type": self.get_type(),
            "id": self.get_id(),
            "attributes": self.get_api_attributes()
        }

    def to_dict(self) -> Dict[str, Any]:
        """Return view as dictionary"""
        response = {
            "data": self.get_data()
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
    def __init__(self, error: Optional[ApiError]=None, errors: Optional[List[ApiError]]=None):
        """Return"""
        self.errors: List[ApiError] = []
        if error:
            self.errors.append(error)
        if errors:
            self.errors += errors

        if len(self.errors) > 0:
            self.response_code = self.errors[0]._status
        else:
            self.response_code = 500

    def to_dict(self):
        """Return errror"""
        return {
            "errors": [
                error.get_api_details()
                for error in self.errors
            ]
        }

    def get_data(self):
        """Handle abstract methods"""
        pass

    def _from_object(**kwargs):
        """Handle abstract methods"""
        pass

    def _get_attributes(**kwargs):
        """Handle abstract methods"""
        pass


class BaseRelationshipEntity(BaseView):
    """Base relationship view"""

    def get_data(self):
        """Implement unused abstract method"""
        pass

    @classmethod
    @abc.abstractmethod
    def from_object(cls, obj: Any, parent_view: 'EntityView') -> 'BaseEntity':
        """
        Return entity from object
        @TODO This method mixes replicates methods from BaseEntity
        """
        ...

    @classmethod
    @abc.abstractmethod
    def from_request(cls, request_args: Dict[str, str], parent_view: 'EntityView') -> Union[Tuple['ApiError', None], Tuple[None, Self]]:
        """Generate relationship from relationship data"""
        ...


class RelatedWithDataRelationshipView(BaseRelationshipEntity):
    """Base relationship for related"""

    CHILD_PATH: Optional[str] = None
    TYPE: Optional[str] = None
    OPTIONAL: bool = False

    def __init__(self, id: str, parent_view: 'EntityView'):
        """Store member variables"""
        self.id = id
        self._parent_view = parent_view
        # Validate child path
        self._get_child_path()

    def _get_child_path(self):
        """Get child path"""
        if self.CHILD_PATH is None:
            raise NotImplementedError
        return self.CHILD_PATH

    def get_type(self) -> str:
        """Return entity type"""
        if self.TYPE is None:
            raise NotImplementedError
        return self.TYPE

    def get_id(self) -> str:
        """Return ID"""
        if self.id is None:
            if self.OPTIONAL:
                return None
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

    def get_data(self) -> Optional[Dict[str, str]]:
        """Get data"""
        if (id_ := self.get_id()) and (type_ := self.get_type()):
            return {
                "id": id_,
                "type": type_,
            }
        return None

    def get_related_link(self) -> Optional[str]:
        """Get related link"""
        if (parent_link := self._parent_view.link) and (child_path := self._get_child_path()):
            return f"{parent_link}/{child_path}"

    def to_dict(self) -> dict:
        """Return API repsonse data"""
        response = {}
        if related_link := self.get_related_link():
            response["links"] = {
                "related": related_link
            }
        if data := self.get_data():
            response["data"] = data
        return response

    @classmethod
    def from_request(cls, request_args: Dict[str, str], parent_view: 'EntityView') -> Union[Tuple['ApiError', None], Tuple[None, Self]]:
        """Generate relationship from relationship data"""
        data = request_args.get("data")
        if not isinstance(data, dict):
            return ApiError(
                "Invalid relationship data",
                "Relationship must contain a data object",
                pointer='data'
            )

        type_ = data.get("type")
        if type_ != cls.TYPE:
            return ApiError(
                'Relationship type does not match expected type',
                f'Relationships type \'{cls.TYPE}\' expected',
                pointer='data/type'
            ), None

        id_ = data.get("id")
        if id_ is None:
            return ApiError(
                'Relationship id not set',
                f'Relationship ID must be set',
                pointer='data/id'
            ), None
        return None, cls(id=id_, parent_view=parent_view)


class RelatedRelationshipView(RelatedWithDataRelationshipView):
    """Base relationship for related"""

    def get_type(self) -> None:
        """Return entity type"""
        pass

    def get_id(self) -> None:
        """Return ID"""
        pass

    @classmethod
    def get_id_from_object(cls, obj: Any) -> None:
        """Obtain ID from object"""
        pass

    @classmethod
    def from_object(cls, obj: Any, parent_view: 'EntityView') -> 'BaseEntity':
        """Return entity from object"""
        return cls(id=None, parent_view=parent_view)

    @classmethod
    def from_request(cls, request_args: Dict[str, str], parent_view: 'EntityView') -> Union[Tuple['ApiError', None], Tuple[None, Self]]:
        """Generate relationship from relationship data"""
        return None, cls(id=None, parent_view=parent_view)


class DataRelationshipView(RelatedWithDataRelationshipView):
    """Base relationship for related objects with data"""

    TYPE: Optional[str] = None

    def _get_child_path(self) -> None:
        """Get child path"""
        pass


TListEntityParent = TypeVar('TListEntityParent', bound=BaseEntity)

class ListEntity(BaseEntity, Generic[TListEntityParent]):
    """Wrapper for handling multiple entities"""

    ENTITY_CLASS: 'TListEntityParent' = None

    def __init__(self, entities: List['TListEntityParent']):
        """Store member variables"""
        self.entities: List['TListEntityParent'] = entities

    @classmethod
    def _get_entity_class(cls):
        """Obtain entity class"""
        if cls.ENTITY_CLASS is None:
            raise NotImplementedError
        return cls.ENTITY_CLASS

    @classmethod
    def from_object(cls, obj: List[Any], auth_context: 'terrarun.auth_context.AuthContext') -> 'ListEntity':
        """Create list entity object from list of model objects"""
        return cls(
            entities=[
                cls._get_entity_class().from_object(obj=obj_itx, auth_context=auth_context)
                for obj_itx in obj
            ]
        )

    @classmethod
    def _from_object(cls, obj: Any, auth_context: 'terrarun.auth_context.AuthContext') -> 'ListEntity':
        """Implement unused abstract method"""
        pass


class ListEntityView(BaseView, ListEntity[EntityView]):
    """View containing list of entities"""

    def get_data(self):
        """Return data"""
        return [
            # Create nested list to allow inline conditional
            # without running to_dict twice
            view
            for view in [
                view.get_data()
                for view in self.entities
            ]
            if view
        ]

    def to_dict(self):
        """Response dict"""
        return {
            "data": self.get_data()
        }

    def _get_attributes(**kwargs):
        """Handle abstract methods"""
        pass


class ListRelationshipView(BaseRelationshipEntity, ListEntity[BaseRelationshipEntity]):

    @classmethod
    @abc.abstractmethod
    def _get_objects(cls, obj: Any) -> List[Any]:
        """Get list of relationship objects from entity object"""
        ...

    @classmethod
    def from_object(cls, obj: Any, parent_view: 'EntityView') -> 'ListEntity':
        """Create list entity object from list of model objects"""
        return cls(
            entities=[
                cls._get_entity_class().from_object(obj=obj_itx, parent_view=parent_view)
                for obj_itx in cls._get_objects(obj=obj)
            ]
        )

    @classmethod
    def from_request(cls, request_args: Dict[str, str], parent_view: EntityView) -> Tuple[ApiError | None] | Tuple[None | Self]:
        pass

    def _get_attributes(**kwargs):
        """Handle abstract methods"""
        pass

    def get_data(self):
        """Return data"""
        return [
            entity.get_data()
            for entity in self.entities
        ]

