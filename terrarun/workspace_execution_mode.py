
from enum import Enum


class WorkspaceExecutionMode(Enum):
    """Type of workspace execution."""

    REMOTE = "remote"
    LOCAL = "local"
    AGENT = "agent"
