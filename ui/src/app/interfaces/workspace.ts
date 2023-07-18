export interface WorkspaceAttributes {
    "actions": {
        "is-destroyable": boolean;
    };
    "allow-destroy-plan": boolean;
    "apply-duration-average": number;
    "auto-apply": boolean;
    "auto-destroy-at": string | null;
    "created-at": string;
    "description": string | null;
    "environment": string | null;
    "execution-mode": string;
    "file-triggers-enabled": boolean;
    "global-remote-state": boolean
    "latest-change-at": string;
    "locked": boolean;
    "name": string;
    "operations": boolean;
    "permissions": {
        "can-create-state-versions": boolean;
        "can-destroy": boolean;
        "can-force-unlock": boolean;
        "can-lock": boolean;
        "can-manage-run-tasks": boolean;
        "can-manage-tags": boolean;
        "can-queue-apply": boolean;
        "can-queue-destroy": boolean;
        "can-queue-run": boolean;
        "can-read-assessment-result": boolean;
        "can-read-settings": boolean;
        "can-read-state-versions": boolean;
        "can-read-variable": boolean;
        "can-unlock": boolean;
        "can-update": boolean;
        "can-update-variable": boolean;
    };
    "plan-duration-average": number | null;
    "policy-check-failures": number | null;
    "queue-all-runs": boolean;
    "resource-count": number;
    "run-failures": number;
    "source": string;
    "source-name": string | null;
    "source-url": string | null;
    "speculative-enabled": boolean;
    "structured-run-output-enabled": boolean;
    "terraform-version": string | null;
    "trigger-prefixes": string[];
    "trigger-patterns": string[];
    "updated-at": string;
    "vcs-repo": {
        "branch": string | null;
        "ingress-submodules": string | null;
        "tags-regex": string | null;
        "identifier": string | null;
        "display-identifier": string | null;
        "oauth-token-id": string | null;
        "webhook-url": string | null;
        "repository-http-url": string | null;
        "service-provider": string | null;
    } | null;
    "vcs-repo-identifier": string | null;
    "working-directory": string | null;
    "workspace-kpis-runs-count": number;

    "overrides": {
        "allow-destroy-plan": boolean | null;
        "auto-apply": boolean | null;
        "execution-mode": string | null;
        "global-remote-state": boolean | null;
        "operations": string | null;
        "queue-all-runs": boolean | null;
        "speculative-enabled": boolean | null;
        "terraform-version": string | null;
    };
}

// Interface for workspace attributes when updating
// a workspace, allowing attributes to be nulled to revert
// them back to the project configuration
export interface WorkspaceUpdateAttributes extends Omit<WorkspaceAttributes, "queue-all-runs"> {
    "queue-all-runs": boolean | null;
}

export interface WorkspaceRelationships {
    "agent-pool": {
        "data": {
            "id": string;
            "type": string;
        }
    } | {};
    "current-configuration-version": {
        "data": {
            "id": string;
            "type": string;
        },
        "links": {
            "related": string;
        }
    } | {};
    "current-run": {
        "data": {
            "id": string;
            "type": string;
        },
        "links": {
            "related": string;
        }
    } | {};
    "project": {
        "data": {
            "id": string;
            "type": string;
        },
        "links": {
            "related": string;
        }
    },
    "current-state-version": {
        "data": {
            "id": string;
            "type": string;
        },
        "links": {
            "related": string;
        }
    } | {};
    "latest-run": {
        "data": {
            "id": string;
            "type": string;
        },
        "links": {
            "related": string;
        }
    } | {};
    "organization": {
        "data": {
            "id": string;
            "type": string;
        }
    };
    "outputs": {
        "data": {
            "id": string;
            "type": string;
        }[]
    };
    "tags": {
        "data": {
            "id": string;
            "type": string;
        }[];
    };
    "readme": {
        "data": {
            "id": string;
            "type": string;
        }
    };
    "remote-state-consumers": {
    };
}
