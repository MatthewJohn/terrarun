# Copyright (C) 2024 Matt Comben - All Rights Reserved
# SPDX-License-Identifier: GPL-2.0


from flask import request

import terrarun.auth_context
from terrarun.api_entities.terraform_version import (
    TerraformVersionCreateEntity,
    TerraformVersionUpdateEntity,
    TerraformVersionView,
    TerraformVersionListView,
)
from terrarun.errors import (
    ApiError,
    InvalidVersionNumberError,
    ToolChecksumUrlPlaceholderError,
    ToolUrlPlaceholderError,
    ToolVersionAlreadyExistsError,
    UnableToDownloadToolArchiveError,
    UnableToDownloadToolChecksumFileError,
)
from terrarun.models.tool import Tool, ToolType
from terrarun.server.authenticated_endpoint import AuthenticatedEndpoint
from terrarun.server.route_registration import RouteRegistration


class ApiAdminTerraformVersionsBase(AuthenticatedEndpoint):
    def _tool_error_catching_call(self, method, kwargs):
        """Call method and convert tool errors into ApiError"""
        try:
            return method(**kwargs)
        except ToolVersionAlreadyExistsError:
            raise ApiError(
                "Version already exists",
                "A record with this terraform version already exists.",
                pointer="/data/attributes/version",
            )
        except UnableToDownloadToolArchiveError:
            raise ApiError(
                "Unable to download Terraform archive",
                "The Terraform archive could not be downloaded - either version number is wrong or URL is incorrect.",
                pointer="/data/attributes/url",
            )
        except UnableToDownloadToolChecksumFileError:
            raise ApiError(
                "Unable to download Terraform checksum file",
                "The Terraform checksum file could not be downloaded - either version number is wrong or URL is incorrect.",
                pointer="/data/attributes/checksum-url",
            )
        except InvalidVersionNumberError:
            raise ApiError(
                "Invalid version number",
                "The version number is invalid - it must be in the form x.y.z or x.y.z-something.",
                pointer="/data/attributes/version",
            )
        except ToolUrlPlaceholderError:
            raise ApiError(
                "Invalid placeholders in download URL",
                "Only the placeholders {platform} (e.g. linux) and {arch} (e.g. amd64) are supported.",
                pointer="/data/attributes/url",
            )
        except ToolChecksumUrlPlaceholderError:
            raise ApiError(
                "Invalid placeholders in checksum file URL",
                "Only the placeholders {platform} (e.g. linux) and {arch} (e.g. amd64) are supported.",
                pointer="/data/attributes/checksum-url",
            )


class ApiAdminTerraformVersions(ApiAdminTerraformVersionsBase):
    """Interface to view/create terraform versions"""

    def check_permissions_get(self, auth_context: 'terrarun.auth_context.AuthContext'):
        """Can only be access by site admins"""
        return auth_context.user and auth_context.user.site_admin

    def _get(self, auth_context: 'terrarun.auth_context.AuthContext'):
        """Provide list of terraform versions"""
        version_filter = request.args.get("filter[version]", None)
        version_search = request.args.get("search[version]", None)
        if version_filter:
            version = version_filter
            version_exact = True
        elif version_search:
            version = version_search
            version_exact = False
        else:
            version = version_exact = None

        tool_list = Tool.get_list(
            tool_type=ToolType.TERRAFORM_VERSION,
            version=version,
            version_exact=version_exact,
        )
        view = TerraformVersionListView.from_object(
            obj=tool_list,
            auth_context=auth_context
        )
        return view.to_response()

    def check_permissions_post(self, auth_context: 'terrarun.auth_context.AuthContext'):
        """Can only be access by site admins"""
        return auth_context.user and auth_context.user.site_admin

    def _post(self, auth_context: 'terrarun.auth_context.AuthContext'):
        """Create terraform version"""
        err, create_entity = TerraformVersionCreateEntity.from_request(request.json)
        if err:
            raise err

        create_kwargs = create_entity.get_set_object_attributes()
        create_kwargs["tool_type"] = ToolType.TERRAFORM_VERSION
        create_kwargs["only_create"] = True
        tool = self._tool_error_catching_call(
            Tool.upsert_by_version, create_kwargs
        )

        view = TerraformVersionView.from_object(
            tool, auth_context=auth_context
        )
        return view.to_response()


class ApiAdminTerraformVersionsItem(ApiAdminTerraformVersionsBase):
    """Interface to view terraform version"""

    def check_permissions_get(self, auth_context: 'terrarun.auth_context.AuthContext', tool_id):
        """Can only be access by site admins"""
        return auth_context.user and auth_context.user.site_admin

    def _get(self, auth_context: 'terrarun.auth_context.AuthContext', tool_id):
        """Provide details about terraform version"""
        tool = Tool.get_by_api_id(tool_id)
        
        if tool is None:
            raise ApiError("Tool not found", "Tool not found", status = 404)

        view = TerraformVersionView.from_object(tool, auth_context=auth_context)
        return view.to_response()

    def check_permissions_patch(self, auth_context: 'terrarun.auth_context.AuthContext', tool_id):
        """Can only be access by site admins"""
        return auth_context.user and auth_context.user.site_admin

    def _patch(self, auth_context: 'terrarun.auth_context.AuthContext', tool_id):
        """Update attributes of terraform version"""
        tool = Tool.get_by_api_id(tool_id)
        
        if tool is None:
            raise ApiError("Tool not found", "Tool not found", status = 404)

        err, update_entity = TerraformVersionUpdateEntity.from_request(request.json)
        if err:
            raise err

        update_kwargs = update_entity.get_set_object_attributes()
        self._tool_error_catching_call(
            tool.update_attributes, update_kwargs
        )

        view = TerraformVersionView.from_object(
            tool, auth_context=auth_context
        )
        return view.to_response()

    def check_permissions_delete(self, auth_context: 'terrarun.auth_context.AuthContext', tool_id):
        """Can only be access by site admins"""
        return auth_context.user and auth_context.user.site_admin

    def _delete(self, auth_context: 'terrarun.auth_context.AuthContext', tool_id):
        """Delete terraform version"""

        tool = Tool.get_by_api_id(tool_id)
        
        if tool is None:
            raise ApiError("Tool not found", "Tool not found", status = 404)
 
        tool.delete()

        return {}, 200


class AdminTerraformVersionsRegistration(RouteRegistration):
    """Register admin settings routes"""

    def register_routes(self, app, api):
        """Register routes"""
        api.add_resource(
            ApiAdminTerraformVersions,
            "/api/v2/admin/terraform-versions"
        )

        api.add_resource(
            ApiAdminTerraformVersionsItem,
            "/api/v2/admin/terraform-versions/<string:tool_id>",
        )
