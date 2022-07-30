
import sqlalchemy
import sqlalchemy.orm

from terrarun.base_object import BaseObject
from terrarun.config import Config
import terrarun.organisation
import terrarun.run
import terrarun.configuration
from terrarun.database import Base, Database


class Workspace(Base, BaseObject):

    ID_PREFIX = 'ws'

    __tablename__ = 'workspace'
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    name = sqlalchemy.Column(sqlalchemy.String)
    organisation_id = sqlalchemy.Column(sqlalchemy.ForeignKey("organisation.id"), nullable=False)
    organisation = sqlalchemy.orm.relationship("Organisation", back_populates="workspaces")

    state_versions = sqlalchemy.orm.relation("StateVersion", back_populates="workspace")
    configuration_versions = sqlalchemy.orm.relation("ConfigurationVersion", back_populates="workspace")

    _latest_state = None
    _latest_configuration_version = None
    _latest_run = None

    @classmethod
    def get_by_organisation_and_name(cls, organisation, workspace_name):
        """Return organisation object, if it exists within an organisation, by name."""
        session = Database.get_session()
        ws = session.query(Workspace).filter(
            Workspace.name==workspace_name,
            Workspace.organisation==organisation
        ).first()

        if not ws and Config().AUTO_CREATE_WORKSPACES:
            ws = Workspace.create(organisation=organisation, name=workspace_name)
        return ws
    
    @classmethod
    def create(cls, organisation, name):
        ws = cls(organisation=organisation, name=name)
        session = Database.get_session()
        session.add(ws)
        session.commit()
        return ws

    @property
    def runs(self):
        """Return runs for workspace"""
        runs = []
        for cv in self.configuration_versions:
            runs += cv.runs
        return runs

    @property
    def auto_apply(self):
        """Whether runs are auto-apply enabled"""
        return False

    @property
    def latest_state_version(self):
        """Return latest state version."""
        pass

    @property
    def latest_configuration_version(self):
        """Return latest configuration version."""
        pass

    @property
    def latest_run(self):
        """Return latest run."""
        pass

    @property
    def latest_configuration_version(self):
        """Return latest configuration version."""
        if self.configuration_versions:
            return self.configuration_versions[-1]
        return None

    @property
    def latest_state(self):
        """Return latest state version"""
        if self.state_versions:
            return self.state_versions[-1]
        return None

    @property
    def latest_run(self):
        """Return latest state version"""
        session = Database.get_session()
        run = session.query(
            terrarun.run.Run
        ).join(
            terrarun.configuration.ConfigurationVersion
        ).filter(
            terrarun.configuration.ConfigurationVersion.workspace == self
        ).order_by(
            terrarun.run.Run.created_at.desc()
        ).first()
        return run

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
                    "name": self.name,
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
                "id": self.api_id,
                "links": {
                    "self": f"/api/v2/organizations/{self.organisation.name}/workspaces/{self.name}"
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
                            "id": self.latest_configuration_version.api_id,
                            "type": "configuration-versions"
                        },
                        "links": {
                            "related": f"/api/v2/configuration-versions/{self.latest_configuration_version.api_id}"
                        }
                    } if self.latest_configuration_version else {},
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
                            "id": self.latest_state.api_id,
                            "type": "state-versions"
                        },
                        "links": {
                            "related": f"/api/v2/workspaces/{self.api_id}/current-state-version"
                        }
                    } if self.latest_state else {},
                    "latest-run": {
                        "data": {
                            "id": self.latest_run.api_id,
                            "type": "runs"
                        },
                        "links": {
                            "related": f"/api/v2/runs/{self.latest_run.api_id}"
                        }
                    } if self._latest_run else {},
                    "organization": {
                        "data": {
                            "id": self.organisation.name,
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
