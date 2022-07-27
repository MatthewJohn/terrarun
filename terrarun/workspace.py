
import sqlalchemy
import sqlalchemy.orm

import terrarun.organisation
from terrarun.database import Base


class Workspace(Base):

    __tablename__ = 'workspace'
    id = sqlalchemy.Column(sqlalchemy.String, primary_key=True)
    name = sqlalchemy.Column(sqlalchemy.String)
    organisation_id = sqlalchemy.Column(sqlalchemy.ForeignKey("organisation.id"), nullable=False)

    organisation = sqlalchemy.orm.relationship("Organisation", back_populates="workspaces")

    @classmethod
    def get_workspace_by_organisation_and_name(cls, organisation, workspace_name):
        """Return organisation object, if it exists within an organisation, by name."""
        if cls.WORKSPACE is None:
            cls.WORKSPACE = cls(terrarun.organisation.Organisation.get_by_name("org-name"), "ws-qPhan8kDLymzv2uS")
        cls.WORKSPACE._name = workspace_name
        return cls.WORKSPACE

    @classmethod
    def get_by_id(cls, workspace_id):
        """Return workspace by ID"""
        if cls.WORKSPACE is None:
            cls.WORKSPACE = cls(terrarun.organisation.Organisation.get_by_name("org-name"), "ws-qPhan8kDLymzv2uS")
        cls.WORKSPACE._id = workspace_id
        return cls.WORKSPACE

    @property
    def auto_apply(self):
        """Whether runs are auto-apply enabled"""
        return False

    def __init__(self, organisation, workspace_id):
        """Store member variables."""
        self._organisation = organisation
        self._id = workspace_id
        self._latest_state = None
        self._latest_configuration_version = None
        self._latest_run = None
        self._name = 'blah'

    def get_api_details(self):
        """Return details for workspace."""
        return {
            "data": {
                "attributes": {
                    "actions": {
                        "is-destroyable": True
                    },
                    "allow-destroy-plan": True,
                    "apply-duration-average": 158000,
                    "auto-apply": False,
                    "auto-destroy-at": None,
                    "created-at": "2021-06-03T17:50:20.307Z",
                    "description": "An example workspace for documentation.",
                    "environment": "default",
                    "execution-mode": "remote",
                    "file-triggers-enabled": True,
                    "global-remote-state": False,
                    "latest-change-at": "2021-06-23T17:50:48.815Z",
                    "locked": False,
                    "name": self._name,
                    "operations": True,
                    "permissions": {
                        "can-create-state-versions": True,
                        "can-destroy": True,
                        "can-force-unlock": True,
                        "can-lock": True,
                        "can-manage-run-tasks": True,
                        "can-manage-tags": True,
                        "can-queue-apply": True,
                        "can-queue-destroy": True,
                        "can-queue-run": True,
                        "can-read-settings": True,
                        "can-read-state-versions": True,
                        "can-read-variable": True,
                        "can-unlock": True,
                        "can-update": True,
                        "can-update-variable": True
                    },
                    "plan-duration-average": 20000,
                    "policy-check-failures": None,
                    "queue-all-runs": False,
                    "resource-count": 0,
                    "run-failures": 6,
                    "source": "terraform",
                    "source-name": None,
                    "source-url": None,
                    "speculative-enabled": True,
                    "structured-run-output-enabled": False,
                    "terraform-version": "0.15.3",
                    "trigger-prefixes": [],
                    "updated-at": "2021-08-16T18:54:06.874Z",
                    "vcs-repo": None,
                    "vcs-repo-identifier": None,
                    "working-directory": None,
                    "workspace-kpis-runs-count": 7
                },
                "id": self._id,
                "links": {
                    "self": f"/api/v2/organizations/{self._organisation._name}/workspaces/workspace-1"
                },
                "relationships": {
                    "agent-pool": {
                        "data": {
                        "id": "apool-QxGd2tRjympfMvQc",
                        "type": "agent-pools"
                        }
                    },
                    "current-configuration-version": {
                        "data": {
                            "id": self._latest_configuration_version._id,
                            "type": "configuration-versions"
                        },
                        "links": {
                            "related": f"/api/v2/configuration-versions/{self._latest_configuration_version._id}"
                        }
                    } if self._latest_configuration_version else {},
                    "current-run": {
                        "data": {
                        "id": "run-UyCw2TDCmxtfdjmy",
                        "type": "runs"
                        },
                        "links": {
                        "related": "/api/v2/runs/run-UyCw2TDCmxtfdjmy"
                        }
                    },
                    "current-state-version": {
                        "data": {
                            "id": self._latest_state._id,
                            "type": "state-versions"
                        },
                        "links": {
                            "related": f"/api/v2/workspaces/{self._id}/current-state-version"
                        }
                    } if self._latest_state else {},
                    "latest-run": {
                        "data": {
                            "id": self._latest_run._id,
                            "type": "runs"
                        },
                        "links": {
                            "related": f"/api/v2/runs/{self._latest_run._id}"
                        }
                    } if self._latest_run else {},
                    "organization": {
                        "data": {
                            "id": "my-organization",
                            "type": "organizations"
                        }
                    },
                    "outputs": {
                        "data": []
                    },
                    "readme": {
                        "data": {
                            "id": "227247",
                            "type": "workspace-readme"
                        }
                    },
                    "remote-state-consumers": {
                        "links": {
                            "related": "/api/v2/workspaces/ws-qPhan8kDLymzv2uS/relationships/remote-state-consumers"
                        }
                    }
                },
                "type": "workspaces"
            }
        }
