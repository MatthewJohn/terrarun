# Copyright (C) 2024 Matt Comben - All Rights Reserved
# SPDX-License-Identifier: GPL-2.0


from enum import Enum


class WorkspaceExecutionMode(Enum):
    """Type of workspace execution."""

    REMOTE = "remote"
    LOCAL = "local"
    AGENT = "agent"
