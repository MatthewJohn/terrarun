
from terrarun.models.saml_settings import SamlSettings as SamlSettingsModel

from .base_entity import BaseEntity, BaseRelationshipType, EntityView, Attribute, ATTRIBUTED_REQUIRED, ListRelationshipHandler


class WorkspacesRelationshipType(BaseRelationshipType):
    TYPE = "workspaces"


class WorkspaceRelationshipList(ListRelationshipHandler):
    relationship_type = WorkspacesRelationshipType
    name = "workspaces"


class ProjectsRelationshipType(BaseRelationshipType):
    TYPE = "projects"


class ProjectsRelationshipList(ListRelationshipHandler):
    relationship_type = ProjectsRelationshipType
    name = "projects"



class VariableSetEntity(BaseEntity):

    type = "varsets"
    ATTRIBUTES = (
        Attribute("name", "name", str, ATTRIBUTED_REQUIRED),
        Attribute("description", "description", str, ""),
        Attribute("global", "is_global", bool, False)
    )
    RELATIONSHIP_TYPES = (
        WorkspaceRelationshipList,
        ProjectsRelationshipList
    )

    def get_attributes(self):
        """Return saml provider attributes"""
        return {
            "name": self.name,
            "description": self.description,
            "global": self.is_global
        }

    @classmethod
    def from_object(cls, obj: SamlSettingsModel):
        """Convert object to saml settings entity"""
        return cls(
            id="saml",
            enabled=obj.enabled,
            debug=obj.debug,
            old_idp_cert=obj.old_idp_cert,
            idp_cert=obj.idp_cert,
            slo_endpoint_url=obj.slo_endpoint_url,
            sso_endpoint_url=obj.sso_endpoint_url,
            attr_username=obj.attr_username,
            attr_groups=obj.attr_groups,
            attr_site_admin=obj.attr_site_admin,
            site_admin_role=obj.site_admin_role,
            sso_api_token_session_timeout=obj.sso_api_token_session_timeout,
            acs_consumer_url=obj.acs_consumer_url,
            metadata_url=obj.metadata_url
        )


class VariableSetCreateEntity(VariableSetEntity):
    ID_REQUIRED = False



class VariableSetView(VariableSetEntity, EntityView):
    """View for variable set"""
    pass
