# Copyright (C) 2024 Matt Comben - All Rights Reserved
# SPDX-License-Identifier: GPL-2.0


from datetime import datetime
from typing import Tuple

import terrarun.models.user
from terrarun.models.tool import Tool

from .base_entity import (
    ATTRIBUTED_REQUIRED,
    UNDEFINED,
    Attribute,
    AttributeModifier,
    BaseEntity,
    EntityView,
)


class TerraformVersionEntity(BaseEntity):
    """Entity for terraform versions"""

    type = "terraform-versions"

    @classmethod
    def _get_attributes(cls) -> Tuple[Attribute]:
        return (
            Attribute("version", "version", str, ATTRIBUTED_REQUIRED),
            Attribute("url", "custom_url", str, None),
            Attribute("sha", "sha", str, None),
            Attribute("checksum-url", "custom_checksum_url", str, None),
            Attribute("deprecated", "deprecated", bool, None),
            Attribute("deprecated-reason", "deprecated_reason", str, None),
            Attribute("official", "official", bool, None),
            Attribute("enabled", "enabled", bool, False),
            Attribute("beta", "beta", bool, None),
            Attribute("usage", "usage", int, 0),
            Attribute("created-at", "created_at", datetime, None),
        )

    @classmethod
    def _from_object(cls, obj: Tool, effective_user: "terrarun.models.user.User"):
        """Convert object to saml settings entity"""
        return cls(
            id=obj.api_id,
            attributes={
                "version": obj.version,
                "custom_url": obj.custom_url,
                "sha": obj.sha,
                "custom_checksum_url": obj.custom_checksum_url,
                "deprecated": obj.deprecated,
                "deprecated_reason": obj.deprecated_reason,
                "official": obj.official,
                "enabled": obj.enabled,
                "beta": obj.beta,
                "usage": obj.usage,
                "created_at": obj.created_at,
            },
        )


class TerraformVersionCreateEntity(TerraformVersionEntity):
    """Entity for creating terraform versions"""

    require_id = False
    include_attributes = [
        "version",
        "custom_url",
        "sha",
        "custom_checksum_url",
        "deprecated",
        "deprecated_reason",
        "enabled",
    ]


class TerraformVersionUpdateEntity(TerraformVersionEntity):
    """Entity for updating terraform versions"""

    require_id = False
    include_attributes = [
        "version",
        "custom_url",
        "sha",
        "custom_checksum_url",
        "deprecated",
        "deprecated_reason",
        "enabled",
    ]
    attribute_modifiers = {
        "version": AttributeModifier(default=UNDEFINED),
        "url": AttributeModifier(default=UNDEFINED),
        "sha": AttributeModifier(default=UNDEFINED),
        "custom_checksum_url": AttributeModifier(default=UNDEFINED),
        "deprecated": AttributeModifier(default=UNDEFINED),
        "deprecated_reason": AttributeModifier(default=UNDEFINED),
        "enabled": AttributeModifier(default=UNDEFINED),
    }


class TerraformVersionView(TerraformVersionEntity, EntityView):
    """View for terraform-version"""

    pass
