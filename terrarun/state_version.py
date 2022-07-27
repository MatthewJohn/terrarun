
class StateVersion:


    INSTANCES = {}

    @classmethod
    def get_by_id(cls, id_):
        """Obtain plan instance by ID."""
        if id_ in cls.INSTANCES:
            return cls.INSTANCES[id_]
        return None

    @classmethod
    def create_from_state_json(cls, run, state_json):
        """Create StateVersion from state_json."""
        id_ = 'sv-ntv3HbhJqvFzam{id}'.format(
            id=str(len(cls.INSTANCES)).zfill(2))
        sv = cls(run=run, id_=id_, state_json=state_json)
        cls.INSTANCES[id_] = sv

        return sv

    def __init__(self, id_, run, state_json):
        """Store member variables"""
        self._run = run
        self._id = id_
        self._state_json = state_json

    @property
    def resources(self):
        """Return resources"""
        return self._state_json['resources']

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
        return self._state_json['serial']

    @property
    def serial(self):
        """Return serial of state"""
        return self._state_json['version']

    @property
    def terraform_version(self):
        return self._state_json['terraform_version']

    def get_api_details(self):
        """Return API details."""
        return {
            "id": self._id,
            "type": "state-versions",
            "attributes": {
                "created-at": "2021-06-08T01:22:03.794Z",
                "size": 940,
                "hosted-state-download-url": f"/api/v2/state-versions/{self._id}/download",
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
                        "id": self._run._id,
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
                        "id": self._run._workspace._id,
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
                "self": f"/api/v2/state-versions/{self._id}"
            }
        }
