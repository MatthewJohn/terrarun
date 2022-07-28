
import sqlalchemy
import sqlalchemy.orm

from terrarun.base_object import BaseObject
from terrarun.database import Base, Database


class StateVersion(Base, BaseObject):

    ID_PREFIX = 'sv'

    __tablename__ = 'state_version'
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)

    workspace_id = sqlalchemy.Column(sqlalchemy.ForeignKey("workspace.id"), nullable=False)
    workspace = sqlalchemy.orm.relationship("Workspace", back_populates="state_versions")

    run_id = sqlalchemy.Column(sqlalchemy.ForeignKey("run.id"), nullable=False)
    run = sqlalchemy.orm.relationship("Run", back_populates="state_versions")

    # Optional references to either plan that generated state or apply
    apply = sqlalchemy.orm.relation("Apply", back_populates="state_version")
    plan = sqlalchemy.orm.relation("Plan", back_populates="state_version")

    state_json = sqlalchemy.Column(sqlalchemy.String)

    @classmethod
    def create_from_state_json(cls, run, state_json):
        """Create StateVersion from state_json."""
        sv = cls(run=run, id=id, state_json=state_json)
        with Database.get_session() as session:
            session.add(sv)
            session.commit()

        return sv

    @property
    def resources(self):
        """Return resources"""
        return self.state_json['resources']

    @property
    def providers(self):
        """Return modules"""
        providers = {}
        for res in self.resources:
            if res['provider'] not in providers:
                providers[res['provider']] = 0
            providers[res['provider']] += 1
        return providers

    @property
    def modules(self):
        """Return modules"""
        modules = {}
        for res in self.resources:
            module = res['module'] if 'module' in res else 'root'
            if module not in modules:
                modules[module] = {}
            resource_type = res['type'] if res['mode'] == 'managed' else '{mode}.{type}'.format(mode=res['mode'], type=res['type'])

            if resource_type not in modules[module]:
                modules[module][resource_type] = 0
            
            modules[module][resource_type] += 1

        return modules

    @property
    def serial(self):
        """Return serial of state"""
        return self.state_json['serial']

    @property
    def version(self):
        """Return serial of state"""
        return self.state_json['version']

    @property
    def terraform_version(self):
        return self.state_json['terraform_version']

    def get_api_details(self):
        """Return API details."""
        return {
            "id": self._id,
            "type": "state-versions",
            "attributes": {
                "created-at": "2021-06-08T01:22:03.794Z",
                "size": 940,
                "hosted-state-download-url": f"/api/v2/state-versions/{self.api_id}/download",
                "modules": self.modules,
                "providers": self.providers,
                "resources": self.resources,
                "resources-processed": False,
                "serial": self.serial,
                "state-version": self.version,
                "terraform-version": self.terraform_version,
                "vcs-commit-url": "https://gitlab.com/my-organization/terraform-test/-/commit/abcdef12345",
                "vcs-commit-sha": "abcdef12345"
            },
            "relationships": {
                "run": {
                    "data": {
                        "id": self.run.api_id,
                        "type": "runs"
                    }
                },
                "created-by": {
                    "data": {
                        "id": "user-onZs69ThPZjBK2wo",
                        "type": "users"
                    },
                    "links": {
                        "self": "/api/v2/users/user-onZs69ThPZjBK2wo",
                        "related": "/api/v2/runs/run-YfmFLWpgTv31VZsP/created-by"
                    }
                },
                "workspace": {
                    "data": {
                        "id": self.run.configuration_version.workspace.api_id,
                        "type": "workspaces"
                    }
                },
                "outputs": {
                    "data": [
                        # {
                        #     "id": "wsout-V22qbeM92xb5mw9n",
                        #     "type": "state-version-outputs"
                        # },
                        # {
                        #     "id": "wsout-ymkuRnrNFeU5wGpV",
                        #     "type": "state-version-outputs"
                        # },
                        # {
                        #     "id": "wsout-v82BjkZnFEcscipg",
                        #     "type": "state-version-outputs"
                        # }
                    ]
                }
            },
            "links": {
                "self": f"/api/v2/state-versions/{self.api_id}"
            }
        }
