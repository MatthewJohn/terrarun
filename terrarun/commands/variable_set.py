

from terrarun.api_entities.base_entity import ApiErrorView
from terrarun.api_entities.variable_set import VariableSetCreateEntity
from terrarun.api_error import ApiError
from terrarun.database import Database
from terrarun.models.workspace import Workspace
from terrarun.models.user import User
from terrarun.models.project import Project
from terrarun.models.organisation import Organisation
from terrarun.models.variable_set import VariableSet


def create_variable_set(organisation: Organisation, current_user: User, variable_set_entity: VariableSetCreateEntity):
    """Create new variable set"""
    if err := validate_new_variable_set(organisation=organisation, current_user=current_user, variable_set_entity=variable_set_entity):
        return err

    model = variable_set_entity.to_model()
    session = Database.get_session()
    session.add(model)
    session.commit()
    return model

def validate_new_variable_set(organisation: Organisation, current_user: User, variable_set_entity: VariableSetCreateEntity):
    """Validate new variable set"""

    # Check relationships for workspaces
    for workspace_relationship in variable_set_entity.get_relationship("workspaces").relationships:

        # Check if global has been defined
        if variable_set_entity.is_global:
            return ApiError(
                "Workspace relationships invalid.",
                "Workspace relationships cannot be provided when variable set is global.",
                pointer="/data/relationships/workspaces/data"
            )            

        workspace = Workspace.get_by_api_id(workspace_relationship.id)
        if workspace is None or workspace.organisation.id != organisation.id:
            return ApiError(
                "Invalid workspace relationship",
                "A referenced workspace does not exist.",
                pointer="/data/relationships/workspaces/data"
            )

    for project_relationships in variable_set_entity.get_relationship("projects").relationships:
        # Check if global has been defined
        if variable_set_entity.is_global:
            return ApiError(
                "Project relationships invalid.",
                "Project relationships cannot be provided when variable set is global.",
                pointer="/data/relationships/projects/data"
            )

        project = Project.get_by_api_id(project_relationships.id)
        if project is None or project.organisation.id != organisation.id:
            return ApiError(
                "Invalid project relationship",
                "A referenced project does not exist.",
                pointer="/data/relationships/projects/data"
            )

    # Ensure name is valid
    if 3 < len(variable_set_entity.name) < 40:
        return ApiError(
            "Invalid name",
            "The variable set name is invalid and must be greater than 3 characters nad less than 40.",
            pointer="/data/attributes/name"
        )
    if VariableSet.get_by_name(variable_set_entity.name):
        return ApiError(
            "Duplicate variable set name",
            "A variable set already exists wtih the provided name.",
            pointer="/data/attributes/name"
        )

