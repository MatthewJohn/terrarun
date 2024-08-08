# Copyright (C) 2024 Matt Comben - All Rights Reserved
# SPDX-License-Identifier: GPL-2.0

from typing import Union
import datetime

import terrarun.models.user
import terrarun.models.plan
import terrarun.models.apply
import terrarun.terraform_command
import terrarun.auth_context

from .base_entity import (
    NestedAttributes,
    Attribute,
)


class ExecutionStatusTimestampsEntity(NestedAttributes):
    """Plan execution defailts entity for plan/apply"""

    @classmethod
    def _get_attributes(cls):
        return (
            Attribute("queued-at", "queued_at", datetime.datetime, None, omit_none=True),
            Attribute("started-at", "started_at", datetime.datetime, None, omit_none=True),
            Attribute("finished-at", "finished_at", datetime.datetime, None, omit_none=True),
        )

    @classmethod
    def _from_object(cls, obj: Union['terrarun.models.plan.Plan', 'terrarun.models.apply.Apply'], auth_context: 'terrarun.auth_context.AuthContext'):
        """Convert plan object to status timestamps entity"""
        timestamps = obj.get_status_change_timestamps()
        return cls(
            attributes={
                'queued_at': timestamps.get(terrarun.terraform_command.TerraformCommandState.QUEUED),
                'started_at': timestamps.get(terrarun.terraform_command.TerraformCommandState.RUNNING),
                # Obtain finished status and fallback to errored status
                'finished_at': timestamps.get(
                    terrarun.terraform_command.TerraformCommandState.FINISHED,
                    timestamps.get(terrarun.terraform_command.TerraformCommandState.ERRORED)
                ),
            }
        )
