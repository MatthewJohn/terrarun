# Copyright (C) 2024 Matt Comben - All Rights Reserved
# SPDX-License-Identifier: GPL-2.0

import json
import sqlalchemy
import sqlalchemy.orm

from terrarun.models.base_object import BaseObject
from terrarun.database import Base, Database
import terrarun.database
from terrarun.models.blob import Blob


class StateVersionOutput(Base, BaseObject):

    ID_PREFIX = 'wsout'

    __tablename__ = 'state_version_output'
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    api_id_fk = sqlalchemy.Column(sqlalchemy.ForeignKey("api_id.id"), nullable=True)
    api_id_obj = sqlalchemy.orm.relation("ApiId", foreign_keys=[api_id_fk])

    state_version_id = sqlalchemy.Column(sqlalchemy.ForeignKey("state_version.id"), nullable=False)
    state_version = sqlalchemy.orm.relationship("StateVersion", back_populates="state_version_outputs")

    name = sqlalchemy.Column(terrarun.database.Database.GeneralString, nullable=False)
    sensitive = sqlalchemy.Column(sqlalchemy.Boolean, nullable=False)
    output_type = sqlalchemy.Column(terrarun.database.Database.GeneralString, nullable=False)
    value_id = sqlalchemy.Column(sqlalchemy.ForeignKey("blob.id"), nullable=True)
    _value = sqlalchemy.orm.relation("Blob", foreign_keys=[value_id])
    detailed_type = sqlalchemy.Column(terrarun.database.Database.GeneralString, nullable=False)

    @classmethod
    def create_from_state_output(cls, state_version, name, data):
        """Create state version output from configuration in state"""
        detailed_type = data.get("type")

        if detailed_type == "string":
            type_ = "string"
        elif type(detailed_type) == list and len(detailed_type) and detailed_type[0] == "tuple":
            type_ = "array"
        else:
            type_ = "object"

        state_output = cls(
            state_version=state_version,
            name=name,
            sensitive=data.get("sensitive", False),
            output_type=type_,
            detailed_type=json.dumps(detailed_type)
        )
        session = Database.get_session()
        session.add(state_output)
        session.commit()
        state_output.value = data.get("value")
        return state_output

    @property
    def value(self):
        """Return plan output value"""
        if self._value and self._value.data:
            return json.loads(self._value.data.decode('utf-8'))
        return {}

    @value.setter
    def value(self, value):
        """Set plan output"""
        session = Database.get_session()

        if self._value:
            value_blob = self._value
            session.refresh(value_blob)
        else:
            value_blob = Blob()

        value_blob.data = bytes(json.dumps(value), 'utf-8')

        session.add(value_blob)
        self._value = value_blob
        session.add(self)
        session.commit()

    def get_relationship(self):
        """Get API relationship output"""
        return {
            "id": self.api_id,
            "type": "state-version-outputs"
        }

    def get_workspace_details(self):
        """Return API details for workspace API response"""
        return {
            "id": self.api_id,
            "type": "workspace-outputs",
            "attributes": {
                "name": self.name,
                "sensitive": self.sensitive,
                "output-type": self.output_type,
                "value": self.value if not self.sensitive else None,
                "detailed-type": json.loads(self.detailed_type),
                "workspace-attributes": {
                    "id": self.state_version.workspace.api_id,
                    "name": self.state_version.workspace.name
                },
                "organization-attributes": {
                    "id": self.state_version.workspace.organisation.api_id,
                    "name": self.state_version.workspace.organisation.name
                }
            }
        }

    def get_api_details(self, include_sensitive=False):
        """Obtain API response for state version output endpoint"""
        return {
            "id": self.api_id,
            "type": "state-version-outputs",
            "attributes": {
                "name": self.name,
                "sensitive": self.sensitive,
                "type": self.output_type,
                "value": self.value if not self.sensitive or include_sensitive else None,
                "detailed-type": json.loads(self.detailed_type)
            },
            "links": {
                "self": "/api/v2/state-version-outputs/wsout-xFAmCR3VkBGepcee"
            }
        }
